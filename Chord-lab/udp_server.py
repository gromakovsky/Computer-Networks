import socket
import threading

from log_utils import log_action
import protocol
from node import Node


BUFFER_SIZE = 2**10


class UPDServer(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='UDP Server')
        self.node = node
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', protocol.port))

    def run(self):
        log_action('UDP server is listening on port', protocol.port)
        while True:
            data, address = self.socket.recvfrom(BUFFER_SIZE)
            if data[0] == protocol.message_codes['INIT']:
                log_action("Received `INIT' message from", address)
                ip_bytes = data[1:]
                if len(ip_bytes) != 4:
                    log_action("`INIT' message from", address, 'is malformed', severity='ERROR')
                else:
                    self.node.process_init(ip_bytes)
            else:
                log_action('Received malformed message from', address)
