import ipaddress
import hashlib
import struct


def readable_ip(binary_ip):
    as_int = struct.unpack('>I', binary_ip)[0]
    return str(ipaddress.IPv4Address(as_int))


def my_hash(s):
    hasher = hashlib.sha1()
    hasher.update(s)
    return hasher.digest()
