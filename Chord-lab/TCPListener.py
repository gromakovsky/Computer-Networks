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
        try:
            if not chunk:
                log_action('Connection from', self.address, 'unexpectedly closed', severity='ERROR')
                return
            if chunk[0] == protocol.message_codes['PICK_UP']:
                log_action("Received `PICK_UP' message from", self.address)
                ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
                self.node.process_pick_up(ip_bytes)
            elif chunk[0] == protocol.message_codes['FIND_SUCCESSOR']:
                log_action("Received `FIND_SUCCESSOR' message from", self.address)
                ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
                res = self.node.find_successor(util.my_hash(ip_bytes))
                msg = protocol.message_code('OK_RESPONSE') + res
                util.send_all(self.socket, msg)
            elif chunk[0] == protocol.message_codes['GET_PREDECESSOR']:
                log_action("Received `GET_PREDECESSOR' message from", self.address)
                res = self.node.predecessor
                msg = protocol.message_code('OK_RESPONSE') + res if res else protocol.message_code('ERROR')
                util.send_all(self.socket, msg)
            elif chunk[0] == protocol.message_codes['NOTIFY']:
                log_action("Received `NOTIFY' message from", self.address)
                ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
                self.node.process_notify(ip_bytes)
            elif chunk[0] == protocol.message_codes['PRED_FAILED']:
                log_action("Received `PRED_FAILED' message from", self.address)
                ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
                self.node.deploy_and_update_backup(ip_bytes)
            elif chunk[0] in protocol.message_codes.keys():
                log_action('Received message from', self.address, 'with unexpected code:', hex(chunk[0]))
            else:
                log_action('Received malformed message from', self.address, ', code:', hex(chunk[0]))
        except Exception as e:
            log_action("Error occurred in TCP Connection handler:", e, severity='ERROR')
        self.socket.close()


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
