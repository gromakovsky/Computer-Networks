import socket
import threading

from log_utils import log_action
import protocol


UDP_BUFFER_SIZE = 2**10


class Listener(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='UDP Listener', daemon=True)
        self.node = node
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(10)
        self.socket.bind(('', protocol.port))

    def run(self):
        log_action('Listening on UDP port', protocol.port, severity='INFO')
        while True:
            try:
                data, address = self.socket.recvfrom(UDP_BUFFER_SIZE)
                if data[0] == protocol.message_codes['INIT']:
                    log_action("Received `INIT' message from", address)
                    ip_bytes = data[1:]
                    if len(ip_bytes) != 4:
                        log_action("`INIT' message from", address, 'is malformed', severity='ERROR')
                    else:
                        self.node.process_init(ip_bytes)
                elif data[0] == protocol.message_codes['KEEP_ALIVE']:
                    # log_action("Received `KEEP_ALIVE' message from", address)
                    self.node.process_keep_alive()
                else:
                    log_action('Received malformed UDP message from', address, 'code:', hex(data[0]), severity='ERROR')
            except Exception as e:
                    log_action('Error occurred in sending UDPListener:', e, severity='ERROR')
