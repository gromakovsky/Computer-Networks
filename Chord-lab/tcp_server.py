import socket
import threading

from log_utils import log_action
import protocol
import util


class ConnectionHandler(threading.Thread):
    def __init__(self, sock, address, node):
        threading.Thread.__init__(self, name='TCP Connection Handler')
        self.socket = sock
        self.socket.settimeout(10)
        self.address = address
        self.node = node

    def run(self):
        chunk = self.socket.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            log_action('Connection from', self.address, 'unexpectedly closed', severity='ERROR')
            return
        if chunk[0] == protocol.message_code('PICK_UP')[0]:
            log_action("Received `PICK_UP' message from", self.address)
            ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
            self.node.process_pick_up(ip_bytes)
        elif chunk[0] == protocol.message_code('FIND_SUCCESSOR')[0]:
            log_action("Received `FIND_SUCCESSOR' message from", self.address)
            ip_bytes = util.read_msg(self.socket, 4, chunk[1:])
            res = self.node.find_successor(util.my_hash(ip_bytes))
            msg = protocol.message_code('OK_RESPONSE') + res
            util.send_all(self.socket, msg)
        elif chunk[0] in protocol.message_codes.keys():
            log_action('Received message from', self.address, 'with unexpected code:', hex(chunk[0]))
        else:
            log_action('Received malformed message from', self.address, ', code: ', hex(chunk[0]))


class TCPServer(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='TCP Server')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', protocol.port))
        self.socket.listen(8)
        self.node = node

    def run(self):
        log_action('TCP server is listening on port', protocol.port)
        while True:
            client_socket, address = self.socket.accept()
            log_action('TCP Server received a connection from', address)
            connection_processor = ConnectionHandler(client_socket, address, self.node)
            connection_processor.start()
