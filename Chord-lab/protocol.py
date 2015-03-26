import struct


port = 7777
hash_size_bits = 32
modulo = 2**hash_size_bits

message_codes = {
    'INIT': 0x7,
    'PICK_UP': 0x8,
}


def message_code(key):
    return struct.pack('B', message_codes[key])
