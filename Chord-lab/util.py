import ipaddress
import hashlib
import struct

import protocol


def readable_ip(ip_bytes):
    as_int = struct.unpack('>I', ip_bytes)[0]
    return str(ipaddress.IPv4Address(as_int))


def my_hash(s):
    hasher = hashlib.sha1()
    hasher.update(s)
    hash_bytes = hasher.digest()[:int(protocol.hash_size_bits / 8)]
    return struct.unpack('>I', hash_bytes)[0]


def in_range(val, lo, hi):
    if lo > hi:
        return not (hi <= val <= lo)
    else:
        return lo <= val <= hi
