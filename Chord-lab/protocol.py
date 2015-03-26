import struct


port = 7777
hash_size_bits = 32
modulo = 2**hash_size_bits
init_interval = 5
keep_alive_interval = 2

message_codes = {
    'OK_RESPONSE': 0x0,
    'FIND_SUCCESSOR': 0x1,
    'INIT': 0x7,
    'PICK_UP': 0x8,
    'KEEP_ALIVE': 0xF,

    'ERROR': 0xFF,
}


def message_code(key):
    return struct.pack('B', message_codes[key])
