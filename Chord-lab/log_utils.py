import sys
import os

debug_file = open('debug_log', mode='w')
# debug_file = sys.stdout
# debug_file = open(os.devnull, mode='w')


def log_action(*args, severity='DEBUG'):
    if severity == 'ERROR':
        print('ERROR:', *args, file=sys.stderr)
    elif severity == 'DEBUG':
        print(*args, file=debug_file, flush=True)
    else:
        print(*args)
