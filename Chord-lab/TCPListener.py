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
        chunk = self.socket.recv(util.TCP_BUFFER_SIZE)
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
            if not chunk:
                log_action('Connection from', self.address, 'unexpectedly closed', severity='ERROR')
            elif chunk[0] in code_to_handler:
                code_to_handler[[chunk[0]]](chunk)
            elif chunk[0] in protocol.message_codes:
                log_action('Received message from', self.address, 'with unexpected code:', hex(chunk[0]),
                           severity='ERROR')
            else:
                log_action('Received malformed message from', self.address, ', code:', hex(chunk[0]),
                           severity='ERROR')
        except Exception as e:
            log_action("Error occurred in TCP Connection handler:", e, severity='ERROR')
        finally:
            self.socket.close()

    def log_message_receiving(self, msg_type):
        log_action("Received `{}' message from".format(msg_type), self.address)

    def handle_find_successor(self, chunk):
        self.log_message_receiving('FIND_SUCCESSOR')
        ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
        res = self.node.find_successor(util.my_hash(ip_bytes))
        msg = protocol.message_code('OK_RESPONSE') + res if res else protocol.message_code('ERROR')
        util.send_all(self.socket, msg)

    def handle_get_predecessor(self, chunk):
        self.log_message_receiving('GET_PREDECESSOR')
        res = self.node.predecessor
        msg = protocol.message_code('OK_RESPONSE') + res if res else protocol.message_code('ERROR')
        util.send_all(self.socket, msg)

    def handle_notify(self, chunk):
        self.log_message_receiving('NOTIFY')
        ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
        self.node.process_notify(ip_bytes)

    def handle_add_entry(self, chunk):
        self.log_message_receiving('ADD_ENTRY')
        # TODO

    def handle_get_ip(self, chunk):
        self.log_message_receiving('GET_IP')
        # TODO

    def handle_get_data(self, chunk):
        self.log_message_receiving('GET_DATA')
        # TODO

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
        # TODO

    def handle_add_to_backup(self, chunk):
        self.log_message_receiving('ADD_TO_BACKUP')
        # TODO

    def handle_delete_entry(self, chunk):
        self.log_message_receiving('DELETE_ENTRY')
        # TODO

    def handle_delete_from_backup(self, chunk):
        self.log_message_receiving('DELETE_FROM_BACKUP')
        # TODO


class Listener(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='TCP Listener', daemon=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', protocol.port))
        self.socket.listen(8)
        self.node = node

    def run(self):
        log_action('Listening on TCP port', protocol.port, severity='INFO')
        while True:
            client_socket, address = self.socket.accept()
            log_action('TCP Listener received a connection from', address)
            connection_processor = ConnectionHandler(client_socket, address, self.node)
            connection_processor.start()
