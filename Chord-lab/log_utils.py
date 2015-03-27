import sys
import os

debug_file = open('debug_log', mode='w')
# debug_file = sys.stdout
# debug_file = open(os.devnull, mode='w')


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log_action(*args, severity='DEBUG'):
    if severity == 'ERROR':
        args_list = [Colors.FAIL + '[ERROR]']
        args_list.extend(args)
        args_list.append(Colors.ENDC)
        print(*args_list, file=sys.stderr)
    elif severity == 'DEBUG':
        print(*args, file=debug_file, flush=True)
    elif severity == 'INFO':
        args_list = [Colors.OKBLUE + '[INFO]']
        args_list.extend(args)
        args_list.append(Colors.ENDC)
        print(*args_list)
