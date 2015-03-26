from log_utils import log_action
import util


class Node(object):
    def __init__(self):
        self.fingers = []

    def process_init(self, binary_ip):
        log_action("Processing `init' from", util.readable_ip(binary_ip))
        return False
