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
    # log_action("Sending `KEEP_ALIVE' message to", util.readable_ip(ip_bytes))
    s.sendto(msg, (util.readable_ip(ip_bytes), protocol.port))
    s.close()


# TCP
def send_msg(ip_bytes, msg):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        s.send(msg)
    finally:
        s.close()


def send_pick_up(ip_bytes):
    msg = protocol.message_code('PICK_UP') + myip.get_ip_bytes()
    log_action("Sending `PICK_UP' message to", util.readable_ip(ip_bytes))
    send_msg(ip_bytes, msg)


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
            return ip_bytes
        elif chunk[0] == protocol.message_code('ERROR')[0]:
            raise RuntimeError("Received `ERROR' in response to `FIND_SUCCESSOR'")
        else:
            raise RuntimeError("Received malformed message in response to `FIND_SUCCESSOR' (code: {})".
                               format(hex(chunk[0])))
    finally:
        s.close()


def get_predecessor(ip_bytes):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        msg = protocol.message_code('GET_PREDECESSOR')
        log_action("Sending `GET_PREDECESSOR' message to", util.readable_ip(ip_bytes))
        s.send(msg)
        chunk = s.sock.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        if chunk[0] == protocol.message_code('OK_RESPONSE')[0]:
            log_action("Received response to `GET_PREDECESSOR' message from", util.readable_ip(ip_bytes))
            ip_bytes = util.read_msg(s.sock, 4, chunk[1:])
            return ip_bytes
        elif chunk[0] == protocol.message_code('ERROR')[0]:
            raise RuntimeError("Received `ERROR' in response to `GET_PREDECESSOR'")
        else:
            raise RuntimeError("Received malformed message in response to `GET_PREDECESSOR' (code: {})".
                               format(hex(chunk[0])))
    finally:
        s.close()


def send_notify(ip_bytes):
    msg = protocol.message_code('NOTIFY') + myip.get_ip_bytes()
    log_action("Sending `NOTIFY' message to", util.readable_ip(ip_bytes))
    send_msg(ip_bytes, msg)


def send_pred_failed(ip_bytes):
    msg = protocol.message_code('PRED_FAILED') + myip.get_ip_bytes()
    log_action("Sending `PRED_FAILED' message to", util.readable_ip(ip_bytes))
    send_msg(ip_bytes, msg)


def send_add_entry(ip_bytes, key, value):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        msg = protocol.message_code('ADD_ENTRY') + util.pack_hash(key) + value
        log_action("Sending `ADD_ENTRY' message to", util.readable_ip(ip_bytes))
        s.send(msg)
        chunk = s.sock.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            log_action("Received response to `ADD_ENTRY' message from", util.readable_ip(ip_bytes))
            return True
        elif chunk[0] == protocol.message_codes['COLLISION']:
            log_action("Received `COLLISION' in response to `ADD_ENTRY'", 'INFO')
            return False
        elif chunk[0] == protocol.message_codes['ERROR']:
            log_action("Received `ERROR' in response to `ADD_ENTRY'", 'ERROR')
            return False
        else:
            raise RuntimeError("Received malformed message in response to `ADD_ENTRY' (code: {})".
                               format(hex(chunk[0])))
    finally:
        s.close()


def delete_from_backup(ip_bytes, key):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        msg = protocol.message_code('DELETE_FROM_BACKUP') + util.pack_hash(key)
        log_action("Sending `DELETE_FROM_BACKUP' message to", util.readable_ip(ip_bytes))
        s.send(msg)
        chunk = s.sock.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            log_action("Received response to `ADD_ENTRY' message from", util.readable_ip(ip_bytes))
            return True
        elif chunk[0] == protocol.message_codes['ERROR']:
            log_action("Received `ERROR' in response to `ADD_ENTRY'", 'ERROR')
            return False
        else:
            raise RuntimeError("Received malformed message in response to `ADD_ENTRY' (code: {})".
                               format(hex(chunk[0])))
    finally:
        s.close()


def send_delete_entry(ip_bytes, key):
    msg = protocol.message_code('DELETE_ENTRY') + util.pack_hash(key)
    log_action("Sending `DELETE_ENTRY' message to", util.readable_ip(ip_bytes))
    send_msg(ip_bytes, msg)


def send_add_to_backup(ip_bytes, key, value):
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(ip_bytes), protocol.port)
        msg = protocol.message_code('ADD_TO_BACKUP') + util.pack_hash(key) + value
        log_action("Sending `ADD_TO_BACKUP' message to", util.readable_ip(ip_bytes))
        s.send(msg)
        chunk = s.sock.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            log_action("Received response to `ADD_ENTRY' message from", util.readable_ip(ip_bytes))
            return True
        elif chunk[0] == protocol.message_codes['ERROR']:
            log_action("Received `ERROR' in response to `ADD_ENTRY'", 'ERROR')
            return False
        else:
            raise RuntimeError("Received malformed message in response to `ADD_ENTRY' (code: {})".
                               format(hex(chunk[0])))
    finally:
        s.close()


def get_backup():
    pass
