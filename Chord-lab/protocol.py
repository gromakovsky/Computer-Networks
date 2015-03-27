import struct


port = 7777
hash_size_bits = 32
modulo = 2**hash_size_bits
init_interval = 8
keep_alive_interval = 4
max_no_keep_alive = 30
stabilize_interval = 6
fix_fingers_interval = 6
join_attempts_count = 2
join_interval = 3

message_codes = {
    'OK_RESPONSE': 0x0,
    'FIND_SUCCESSOR': 0x1,
    'GET_PREDECESSOR': 0x2,
    'NOTIFY': 0x3,
    'ADD_ENTRY': 0x4,
    'GET_IP': 0x5,
    'GET_DATA': 0x6,
    'INIT': 0x7,
    'PICK_UP': 0x8,
    'PRED_FAILED': 0x9,
    'GET_BACKUP': 0xA,
    'ADD_TO_BACKUP': 0xB,
    'DELETE_ENTRY': 0xD,
    'DELETE_FROM_BACKUP': 0xE,
    'KEEP_ALIVE': 0xF,

    'COLLISION': 0xFE,
    'ERROR': 0xFF,
}


def message_code(key):
    return struct.pack('B', message_codes[key])
