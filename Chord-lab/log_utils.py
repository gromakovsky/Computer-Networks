import sys


def log_action(*args, severity='DEBUG'):
    if severity == 'ERROR':
        print(*args, file=sys.stderr)
    else:
        print(*args)
