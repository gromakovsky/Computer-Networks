import socket

from log_utils import log_action
import protocol
import util
import myip


# UDP
def send_init():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    my_ip_bytes = myip.get_ip_bytes()
    msg = protocol.message_code('INIT') + my_ip_bytes
    log_action("Broadcasting `INIT' message with IP:", util.readable_ip(my_ip_bytes))
    s.sendto(msg, ('<broadcast>', protocol.port))
    s.close()


def send_keep_alive(ip_bytes):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = protocol.message_code('KEEP_ALIVE')
    s.sendto(msg, (util.readable_ip(ip_bytes), protocol.port))
    s.close()


# TCP
def send_pick_up(ip_bytes):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        msg = protocol.message_code('PICK_UP') + myip.get_ip_bytes()
        log_action("Sending `PICK_UP' message to", util.readable_ip(ip_bytes))
        s.send(msg)
    finally:
        s.close()


def get_successor(ip_bytes, key_hash):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        msg = protocol.message_code('FIND_SUCCESSOR') + util.pack_hash(key_hash)
        log_action("Sending `FIND_SUCCESSOR' message to", util.readable_ip(ip_bytes))
        s.send(msg)
        chunk = s.sock.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        if chunk[0] == protocol.message_code('OK_RESPONSE')[0]:
            log_action("Received response to `FIND_SUCCESSOR' message from", util.readable_ip(ip_bytes))
            ip_bytes = util.read_msg(s.sock, 4, chunk[1:])
            s.close()
            return ip_bytes
        elif chunk[0] == protocol.message_code('ERROR')[0]:
            raise RuntimeError("Received `ERROR' in response to `FIND_SUCCESSOR'")
        else:
            raise RuntimeError("Received malformed message in response to `FIND_SUCCESSOR' (code: {})".
                               format(hex(chunk[0])))
    finally:
        s.close()
