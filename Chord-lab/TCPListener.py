import socket
import threading

from log_utils import log_action
import protocol
import util


class ConnectionHandler(threading.Thread):
    def __init__(self, sock, address, node):
        threading.Thread.__init__(self, name='TCP Connection Handler', daemon=True)
        self.socket = sock
        self.socket.settimeout(10)
        self.address = address
        self.node = node

    def run(self):
        code_to_handler = {
            protocol.message_codes['FIND_SUCCESSOR']: self.handle_find_successor,
            protocol.message_codes['GET_PREDECESSOR']: self.handle_get_predecessor,
            protocol.message_codes['NOTIFY']: self.handle_notify,
            protocol.message_codes['ADD_ENTRY']: self.handle_add_entry,
            protocol.message_codes['GET_IP']: self.handle_get_ip,
            protocol.message_codes['GET_DATA']: self.handle_get_data,
            protocol.message_codes['PICK_UP']: self.handle_pick_up,
            protocol.message_codes['PRED_FAILED']: self.handle_pred_failed,
            protocol.message_codes['GET_BACKUP']: self.handle_get_backup,
            protocol.message_codes['ADD_TO_BACKUP']: self.handle_add_to_backup,
            protocol.message_codes['DELETE_ENTRY']: self.handle_delete_entry,
            protocol.message_codes['DELETE_FROM_BACKUP']: self.handle_delete_from_backup,
        }
        try:
            chunk = self.socket.recv(util.TCP_BUFFER_SIZE)
            if not chunk:
                log_action('Connection from', self.address, 'unexpectedly closed', severity='ERROR')
            elif chunk[0] in code_to_handler:
                code_to_handler[chunk[0]](chunk)
            elif chunk[0] in protocol.message_codes:
                log_action('Received message from', self.address, 'with unexpected code:', hex(chunk[0]),
                           severity='ERROR')
            else:
                log_action('Received malformed message from', self.address, ', code:', hex(chunk[0]),
                           severity='ERROR')
        except Exception as e:
            log_action('Something went wrong in TCP Connection Handler:', e, severity='ERROR')
            self.reply_error()
        finally:
            self.socket.close()

    def log_message_receiving(self, msg_type):
        log_action("Received `{}' message from".format(msg_type), self.address)

    def send_all(self, msg):
        util.send_all(self.socket, msg)

    def reply_ok(self):
        self.send_all(protocol.message_code('OK_RESPONSE'))

    def reply_collision(self):
        self.send_all(protocol.message_code('COLLISION'))

    def reply_error(self):
        self.send_all(protocol.message_code('ERROR'))

    def handle_find_successor(self, chunk):
        self.log_message_receiving('FIND_SUCCESSOR')
        key_hash = util.unpack_hash(util.read_msg(self.socket, 4, chunk[1:]))
        res = self.node.find_successor(key_hash)
        log_action('Successor of {} is {}'.format(key_hash, util.readable_ip(res)))
        msg = protocol.message_code('OK_RESPONSE') + res if res else protocol.message_code('ERROR')
        self.send_all(msg)

    def handle_get_predecessor(self, chunk):
        self.log_message_receiving('GET_PREDECESSOR')
        res = self.node.predecessor
        msg = protocol.message_code('OK_RESPONSE') + res if res else protocol.message_code('ERROR')
        self.send_all(msg)

    def handle_notify(self, chunk):
        self.log_message_receiving('NOTIFY')
        ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
        self.node.process_notify(ip_bytes)

    def handle_add_entry(self, chunk):
        self.log_message_receiving('ADD_ENTRY')
        rest = util.read_msg(self.socket, 8, chunk[1:])
        key_hash = util.unpack_hash(rest[:4])
        ip_bytes = rest[4:]
        if key_hash in self.node.addresses:
            self.reply_collision()
        elif self.node.add_to_addresses(key_hash, ip_bytes):
            self.reply_ok()
        else:
            self.reply_error()

    def handle_get_ip(self, chunk):
        self.log_message_receiving('GET_IP')
        key_hash = util.unpack_hash(util.read_msg(self.socket, 4, chunk[1:]))
        res = self.node.addresses.get(key_hash)
        if res is None:
            self.reply_error()
        else:
            self.send_all(protocol.message_code('OK_RESPONSE') + res)

    def handle_get_data(self, chunk):
        self.log_message_receiving('GET_DATA')
        key_hash = util.unpack_hash(util.read_msg(self.socket, 4, chunk[1:]))
        res = self.node.storage.get(key_hash)
        if res is None:
            self.reply_error()
        else:
            self.send_all(protocol.message_code('OK_RESPONSE') + util.pack_length(len(res)) + res)

    def handle_pick_up(self, chunk):
        self.log_message_receiving('PICK_UP')
        ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
        self.node.process_pick_up(ip_bytes)

    def handle_pred_failed(self, chunk):
        self.log_message_receiving('PRED_FAILED')
        ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
        self.node.deploy_and_update_backup(ip_bytes)

    def handle_get_backup(self, chunk):
        self.log_message_receiving('GET_BACKUP')
        raw_backup_items = [util.pack_hash(k) + v for k, v in self.node.backup.items()]
        msg = protocol.message_code('OK_RESPONSE') + b''.join(raw_backup_items)
        self.send_all(msg)

    def handle_add_to_backup(self, chunk):
        self.log_message_receiving('ADD_TO_BACKUP')
        rest = util.read_msg(self.socket, 8, chunk[1:])
        key_hash = util.unpack_hash(rest[:4])
        ip_bytes = rest[4:]
        if self.node.add_to_backup(key_hash, ip_bytes):
            self.reply_ok()
        else:
            self.reply_error()

    def handle_delete_entry(self, chunk):
        self.log_message_receiving('DELETE_ENTRY')
        key_hash = util.unpack_hash(util.read_msg(self.socket, 4, chunk[1:]))
        self.node.delete_entry(key_hash)

    def handle_delete_from_backup(self, chunk):
        self.log_message_receiving('DELETE_FROM_BACKUP')
        key_hash = util.unpack_hash(util.read_msg(self.socket, 4, chunk[1:]))
        if self.node.delete_entry(key_hash):
            self.reply_ok()
        else:
            self.reply_error()


class Listener(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='TCP Listener', daemon=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', protocol.port))
        self.socket.listen(8)
        self.node = node

    def run(self):
        log_action('Listening on TCP port', protocol.port, severity='INFO')
        while True:
            try:
                client_socket, address = self.socket.accept()
            except OSError as e:
                log_action('Error occurred in TCP Listener:', e, severity='ERROR')
                continue
            log_action('TCP Listener received a connection from', address)
            connection_processor = ConnectionHandler(client_socket, address, self.node)
            connection_processor.start()
