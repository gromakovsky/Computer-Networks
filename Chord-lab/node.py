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
        self.predecessor = self.ip_bytes
        self.successor2 = None
        self.picked_up = False

        def run_initializer():
            while not self.picked_up:
                communication.send_init()
                time.sleep(protocol.init_interval)
        self.initializer_thread = threading.Thread(target=run_initializer, name='Initializer')
        self.initializer_thread.start()

        def run_keep_alive():
            if self.predecessor:
                communication.send_keep_alive(self.predecessor)
                time.sleep(protocol.keep_alive_interval)
        self.keep_alive_thread = threading.Thread(target=run_keep_alive, name='Alive keeper')
        self.keep_alive_thread.start()

    def process_init(self, ip_bytes):
        log_action("Processing `INIT' from", util.readable_ip(ip_bytes))
        if util.in_range(util.my_hash(ip_bytes), self.ip_hash, self.fingers_hash[0]):
            try:
                communication.send_pick_up(ip_bytes)
            except Exception as e:
                log_action("Failed to send `PICK_UP' to", util.readable_ip(ip_bytes), "\nReason:", e,  severity='ERROR')

    def process_pick_up(self, ip_bytes):
        if self.picked_up or not ip_bytes:
            return
        self.predecessor = ip_bytes
        self.fingers[0] = communication.get_successor(ip_bytes, self.ip_hash)
        self.fingers_hash[0] = util.my_hash(self.fingers[0])
        self.successor2 = communication.get_successor(ip_bytes, self.fingers_hash[0])
        self.picked_up = True

    def find_successor(self, key_hash):
        if util.in_range(key_hash, util.my_hash(self.predecessor), self.ip_hash - 1):
            return self.ip_bytes
        for ip_bytes in reversed(self.fingers):
            if util.in_range(util.my_hash(ip_bytes), self.ip_hash, key_hash - 1):
                try:
                    x = communication.get_successor(ip_bytes, key_hash)
                    return x
                except Exception as e:
                    log_action('Failed to get successor from', util.readable_ip(ip_bytes), '\nReason:', e)

        return self.fingers[0]
