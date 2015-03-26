import socket
import threading
import struct

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
        self.stopped = False

    def run(self):
        log_action('UDP server is listening on port', protocol.port)
        while True:
            if self.stopped:
                break
            data, address = self.socket.recvfrom(BUFFER_SIZE)
            if data[0] == protocol.message_codes['init']:
                log_action("Received `init' message from", address)
                binary_ip = data[1:]
                if len(binary_ip) != 4:
                    log_action("`init' message from", address, 'is malformed')
                else:
                    self.node.process_init(binary_ip)
            else:
                log_action("Received malformed message from", address)

    def finish(self):
        self.stopped = True
