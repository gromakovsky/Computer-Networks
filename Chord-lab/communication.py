import socket

from log_utils import log_action
import protocol
import util
import myip


# UDP
def send_init():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        my_ip_bytes = myip.get_ip_bytes()
        msg = protocol.message_code('INIT') + my_ip_bytes
        log_action("Broadcasting `INIT' message with IP:", util.readable_ip(my_ip_bytes))
        s.sendto(msg, ('<broadcast>', protocol.port))
    finally:
        s.close()


def send_keep_alive(ip_bytes):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        msg = protocol.message_code('KEEP_ALIVE')
        # log_action("Sending `KEEP_ALIVE' message to", util.readable_ip(ip_bytes))
        s.sendto(msg, (util.readable_ip(ip_bytes), protocol.port))
    finally:
        s.close()


# TCP
def log_sending(msg_type, address_bytes):
    log_action("Sending `{}' message to".format(msg_type), util.readable_ip(address_bytes))


def send_msg_tcp(address_bytes, msg, msg_type):
    log_sending(msg_type, address_bytes)
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(address_bytes), protocol.port)
        s.send(msg)
    finally:
        s.close()


def log_receiving(msg_type, address_bytes):
    log_action("Received response to `{}' message from".format(msg_type), util.readable_ip(address_bytes))


def send_and_receive_tcp(address_bytes, msg, callback, expected_codes, msg_type):
    log_sending(msg_type, address_bytes)
    s = util.MySocket()
    try:
        s.connect(util.readable_ip(address_bytes), protocol.port)
        s.send(msg)
        chunk = s.sock.recv(util.TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        elif chunk[0] in expected_codes:
            log_receiving(msg_type, address_bytes)
            return callback(s.sock, chunk)
        elif chunk[0] in protocol.message_codes:
            raise RuntimeError("Received message with unexpected code in response to `{}' (code: {})".
                               format(msg_type, hex(chunk[0])))
        else:
            raise RuntimeError("Received malformed message in response to `{}' (code: {})".
                               format(msg_type, hex(chunk[0])))
    finally:
        s.close()


# Simple messages with no response
def send_notify(address_bytes):
    msg = protocol.message_code('NOTIFY') + myip.get_ip_bytes()
    send_msg_tcp(address_bytes, msg, 'NOTIFY')


def send_pick_up(address_bytes):
    msg = protocol.message_code('PICK_UP') + myip.get_ip_bytes()
    send_msg_tcp(address_bytes, msg, 'PICK_UP')


def send_pred_failed(address_bytes):
    msg = protocol.message_code('PRED_FAILED') + myip.get_ip_bytes()
    send_msg_tcp(address_bytes, msg, 'PRED_FAILED')


def send_delete_entry(address_bytes, key):
    msg = protocol.message_code('DELETE_ENTRY') + util.pack_hash(key)
    send_msg_tcp(address_bytes, msg, 'DELETE_ENTRY')


# More complex messages expecting response
def get_successor(address_bytes, key_hash, node):
    if address_bytes == node.ip_bytes:
        return node.find_successor(key_hash)

    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            ip_bytes = util.read_msg(sock, 4, chunk[1:])
            return ip_bytes
        elif chunk[0] == protocol.message_codes['ERROR']:
            raise RuntimeError("Received `ERROR' in response to `FIND_SUCCESSOR'")

    msg = protocol.message_code('FIND_SUCCESSOR') + util.pack_hash(key_hash)
    expected_codes = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_codes, 'FIND_SUCCESSOR')


def get_predecessor(address_bytes):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            ip_bytes = util.read_msg(sock, 4, chunk[1:])
            return ip_bytes
        elif chunk[0] == protocol.message_codes['ERROR']:
            raise RuntimeError("Received `ERROR' in response to `GET_PREDECESSOR'")

    msg = protocol.message_code('GET_PREDECESSOR')
    expected_codes = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_codes, 'GET_PREDECESSOR')


def add_entry(address_bytes, key_hash, value_ip_bytes):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            return True
        elif chunk[0] == protocol.message_codes['COLLISION']:
            log_action("Received `COLLISION' in response to `ADD_ENTRY'", severity='INFO')
            return False
        elif chunk[0] == protocol.message_codes['ERROR']:
            log_action("Received `ERROR' in response to `ADD_ENTRY'", severity='ERROR')
            return False

    msg = protocol.message_code('ADD_ENTRY') + util.pack_hash(key_hash) + value_ip_bytes
    expected_codes = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['COLLISION'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_codes, 'ADD_ENTRY')


def get_ip(address_bytes, key_hash):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            ip_bytes = util.read_msg(sock, 4, chunk[1:])
            return ip_bytes
        elif chunk[0] == protocol.message_codes['ERROR']:
            raise RuntimeError("Received `ERROR' in response to `GET_IP'")

    msg = protocol.message_code('GET_IP') + util.pack_hash(key_hash)
    expected_code = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_code, 'GET_IP')


def get_data(address_bytes, key_hash):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            raw_data = util.read_length_then_msg(sock, 4, chunk[1:])
            return raw_data
        elif chunk[0] == protocol.message_codes['ERROR']:
            raise RuntimeError("Received `ERROR' in response to `GET_DATA'")

    msg = protocol.message_code('GET_DATA') + util.pack_hash(key_hash)
    expected_code = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_code, 'GET_DATA')


def get_backup(address_bytes):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            raw_backup = util.read_length_then_msg(sock, 4, chunk[1:])
            if len(raw_backup) % 8 != 0:
                raise RuntimeError("Received malformed message in response to `GET_BACKUP'. Size must be multiple of 8")
            backup = dict()
            for i in range(raw_backup / 8):
                key = util.unpack_hash(raw_backup[i * 8:i * 8 + 4])
                value = raw_backup[i * 8 + 4:i * 8 + 8]
                backup[key] = value
            return backup
        elif chunk[0] == protocol.message_codes['ERROR']:
            raise RuntimeError("Received `ERROR' in response to `GET_BACKUP'")

    msg = protocol.message_code('GET_BACKUP')
    expected_codes = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_codes, 'GET_BACKUP')


def add_to_backup(address_bytes, key_hash, value_ip_bytes):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            return True
        elif chunk[0] == protocol.message_codes['ERROR']:
            log_action("Received `ERROR' in response to `ADD_TO_BACKUP'", severity='ERROR')
            return False

    msg = protocol.message_code('ADD_TO_BACKUP') + util.pack_hash(key_hash) + value_ip_bytes
    expected_codes = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_codes, 'ADD_TO_BACKUP')


def delete_from_backup(address_bytes, key_hash):
    def on_receive(sock, chunk):
        if chunk[0] == protocol.message_codes['OK_RESPONSE']:
            return True
        elif chunk[0] == protocol.message_codes['ERROR']:
            log_action("Received `ERROR' in response to `DELETE_FROM_BACKUP'", severity='ERROR')
            return False

    msg = protocol.message_code('DELETE_FROM_BACKUP') + util.pack_hash(key_hash)
    expected_codes = [
        protocol.message_codes['OK_RESPONSE'],
        protocol.message_codes['ERROR'],
    ]
    return send_and_receive_tcp(address_bytes, msg, on_receive, expected_codes, 'DELETE_FROM_BACKUP')
