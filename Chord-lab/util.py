import ipaddress
import hashlib
import struct
import socket

import protocol


TCP_BUFFER_SIZE = 2**15


def readable_ip(ip_bytes):
    as_int = struct.unpack('>I', ip_bytes)[0]
    return str(ipaddress.IPv4Address(as_int))


def my_hash(s):
    hasher = hashlib.sha1()
    hasher.update(s)
    hash_bytes = hasher.digest()[:int(protocol.hash_size_bits / 8)]
    return struct.unpack('>I', hash_bytes)[0]


def pack_hash(hash_int):
    return struct.pack('>I', hash_int)


def unpack_hash(hash_bytes):
    return struct.unpack('>I', hash_bytes)[0]


# currently it is assumed that length always must be packed in 4 bytes
def pack_length(length):
    return struct.pack('>I', length)


def unpack_length(length_bytes):
    return struct.unpack('>I', length_bytes)[0]


def in_range(val, lo, hi):
    if lo > hi:
        return not (hi < val < lo)
    else:
        return lo <= val <= hi


def inc(x, i=1):   # x + i
    return (x + i) % protocol.modulo


def dec(x, i=1): # x - i
    return (x - i + protocol.modulo) % protocol.modulo


def distance(lo, hi):
    return (hi - lo + protocol.modulo) % protocol.modulo


def read_msg(sock, length, already_read):
    total_read = len(already_read)
    chunks = [already_read]
    while total_read < length:
        chunk = sock.recv(TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        chunks.append(chunk)
        total_read += len(chunk)

    return b''.join(chunks)


def read_length_then_msg(sock, bytes_for_length, already_read):
    total_read = len(already_read)
    chunks = [already_read]
    while total_read < bytes_for_length:
        chunk = sock.recv(TCP_BUFFER_SIZE)
        if not chunk:
            raise RuntimeError('Socket connection was unexpectedly broken')
        chunks.append(chunk)
        total_read += len(chunk)

    read_bytes = b''.join(chunks)
    length = unpack_length(read_bytes[:bytes_for_length])
    return read_msg(sock, length, read_bytes[bytes_for_length:])


def send_all(sock, msg):
    to_send = len(msg)
    total_sent = 0
    while total_sent < to_send:
        sent = sock.send(msg[total_sent:])
        if sent == 0:
            raise RuntimeError('Socket connection was unexpectedly broken')
        total_sent += sent


class MySocket(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        send_all(self.sock, msg)

    def close(self):
        self.sock.close()
