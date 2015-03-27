import sys
import os
import datetime

debug_file = open(os.path.expanduser('~/Chord-debug'), mode='w')
fingers_file = open(os.path.expanduser('~/Chord-fingers'), mode='w')
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
    args_with_time = ['[' + str(datetime.datetime.now()) + ']']
    args_with_time.extend(args)
    if severity == 'ERROR':
        args_list = [Colors.FAIL + '[ERROR]']
        args_list.extend(args_with_time)
        args_list.append(Colors.ENDC)
        print(*args_list, file=sys.stderr)
    elif severity == 'DEBUG':
        print(*args_with_time, file=debug_file, flush=True)
    elif severity == 'INFO':
        args_list = [Colors.OKBLUE + '[INFO]']
        args_list.extend(args_with_time)
        args_list.append(Colors.ENDC)
        print(*args_list)
    elif severity == 'FINGERS':
        print(*args, file=fingers_file, flush=True)
