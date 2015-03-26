import threading
import time

from log_utils import log_action
import util
import myip
import communication
import protocol


class Node(object):
    def __init__(self):
        self.ip_bytes = myip.get_ip_bytes()
        self.ip_hash = util.my_hash(myip.get_ip_bytes())
        self.fingers = [self.ip_bytes] * protocol.hash_size_bits
        self.fingers_hash = [self.ip_hash] * protocol.hash_size_bits
        self.picked_up = False

        def run_initializer():
            while not self.picked_up:
                communication.send_init(self.ip_bytes)
                time.sleep(2)
        self.initializer_thread = threading.Thread(target=run_initializer, name='Initializer')
        self.initializer_thread.start()

    def process_init(self, ip_bytes):
        log_action("Processing `INIT' from", util.readable_ip(ip_bytes))
        if util.in_range(util.my_hash(ip_bytes), self.ip_hash, self.fingers_hash[0]):
            communication.send_pick_up(ip_bytes)
