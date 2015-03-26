import struct


port = 7777

message_codes = {
    'init': 0x7,
}


def message_code(key):
    return struct.pack('B', message_codes[key])
