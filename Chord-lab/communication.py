import socket

from log_utils import log_action
import protocol
import util
import myip

# UDP
def send_init(ip_bytes):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = protocol.message_code('INIT') + ip_bytes
    log_action('Broadcasting INIT message with IP:', util.readable_ip(ip_bytes))
    s.sendto(msg, ('<broadcast>', protocol.port))
    s.close()


# TCP
class MySocket(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
        except ConnectionError as e:
            log_action('Failed to connect to', host, '\nReason:', e, severity='ERROR')
            return False
        return True

    def send(self, msg):
        to_send = len(msg)
        total_sent = 0
        while total_sent < to_send:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                return False
            total_sent += sent

    # def myreceive(self):
    #     chunks = []
    #     bytes_recd = 0
    #     while bytes_recd < MSGLEN:
    #         chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
    #         if chunk == b'':
    #             raise RuntimeError("socket connection broken")
    #         chunks.append(chunk)
    #         bytes_recd = bytes_recd + len(chunk)
    #     return b''.join(chunks)


def send_pick_up(ip_bytes):
    s = MySocket()
    if not s.connect(util.readable_ip(ip_bytes), protocol.port):
        return False
    msg = protocol.message_code('PICK_UP') + myip.get_ip_bytes()
    log_action('Sending PICK_UP message to', util.readable_ip(ip_bytes))
    if not s.send(msg):
        return False
