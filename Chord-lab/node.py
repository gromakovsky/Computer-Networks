import threading
import time
import random

from log_utils import log_action
import util
import myip
import communication
import protocol
import background


class Node(object):
    def __init__(self):
        self.ip_bytes = myip.get_ip_bytes()
        self.ip_hash = util.my_hash(myip.get_ip_bytes())
        self.fingers = [self.ip_bytes] * protocol.hash_size_bits
        self.fingers_hash = [self.ip_hash] * protocol.hash_size_bits
        self.predecessor = self.ip_bytes
        self.successor2 = self.ip_bytes
        self.picked_up = False
        self.lock = threading.Lock()
        self.last_keep_alive = time.time()
        self.addresses = dict()
        self.backup = dict()
        self.storage = dict()
        self.background_workers = []
        for background_thread_class in background.background_thread_classes:
            worker = background_thread_class(self)
            self.background_workers.append(worker)
            worker.start()

    def update_finger(self, idx, ip_bytes, need_lock=True):
        log_action('Updating {}-th finger to'.format(idx), util.readable_ip(ip_bytes), severity='INFO')
        if need_lock:
            self.lock.acquire()
        self.fingers[idx] = ip_bytes
        self.fingers_hash[idx] = util.my_hash(ip_bytes)
        if need_lock:
            self.lock.release()

    def update_successor2(self, ip_bytes, need_lock=True):
        log_action('Updating successor2 to', util.readable_ip(ip_bytes), severity='INFO')
        if need_lock:
            self.lock.acquire()
        self.successor2 = ip_bytes
        if need_lock:
            self.lock.release()

    def update_predecessor(self, ip_bytes, need_lock=True):
        if need_lock:
            self.lock.acquire()
        self.predecessor = ip_bytes
        if need_lock:
            self.lock.release()

    def process_init(self, ip_bytes):
        log_action("Processing `INIT' from", util.readable_ip(ip_bytes))
        if self.ip_bytes == ip_bytes:
            return
        if util.in_range(util.my_hash(ip_bytes), self.ip_hash, util.dec(self.fingers_hash[0])):
            log_action('Picking up', util.readable_ip(ip_bytes), severity='INFO')
            try:
                communication.send_pick_up(ip_bytes)
            except Exception as e:
                log_action("Failed to send `PICK_UP' to", util.readable_ip(ip_bytes), "\nReason:", e,
                           severity='ERROR')

    def process_pick_up(self, ip_bytes, attempts_count=protocol.join_attempts_count):
        if self.picked_up or not attempts_count:
            return
        log_action(util.readable_ip(ip_bytes), 'wants to pick us', severity='INFO')
        try:
            successor = communication.get_successor(ip_bytes, self.ip_hash)
            successor2 = communication.get_successor(ip_bytes, util.my_hash(successor))
        except Exception as e:
            log_action("Error occurred in processing `PICK_UP':", e, severity='ERROR')
            self.process_pick_up(ip_bytes, attempts_count - 1)
            return
        self.lock.acquire()
        if not self.picked_up:
            self.update_predecessor(ip_bytes, False)
            self.update_finger(0, successor, False)
            self.update_successor2(successor2, False)
            self.picked_up = True
        self.lock.release()

    def find_successor(self, key_hash):
        if util.in_range(key_hash, util.my_hash(self.predecessor), util.dec(self.ip_hash)):
            return self.ip_bytes
        for ip_bytes in reversed(self.fingers):
            if util.in_range(util.my_hash(ip_bytes), self.ip_hash, util.dec(key_hash)):
                try:
                    x = communication.get_successor(ip_bytes, key_hash)
                    return x
                except Exception as e:
                    log_action('Failed to get successor from', util.readable_ip(ip_bytes), '\nReason:', e,
                               severity='ERROR')

        return self.fingers[0]

    def process_keep_alive(self):
        self.lock.acquire()
        self.last_keep_alive = time.time()
        self.lock.release()

    def successor_failed(self):
        log_action('Successor {} failed'.format(util.readable_ip(self.fingers[0])), severity='INFO')
        communication.send_pred_failed(self.successor2)
        self.update_finger(0, self.successor2)
        self.update_successor2(communication.get_successor(self.fingers[0], self.fingers_hash[0]))

    def stabilize(self):
        x = communication.get_predecessor(self.fingers[0])
        if util.distance(self.ip_hash, self.fingers_hash[0]) > 1:
            if util.in_range(util.my_hash(x), util.inc(self.ip_hash), util.dec(self.fingers_hash[0])):
                self.update_finger(0, x)
                self.update_successor2(communication.get_successor(x, self.fingers_hash[0]))

        communication.send_notify(self.fingers[0])

    def fix_fingers(self):
        idx = random.randint(0, protocol.hash_size_bits - 1)
        finger = self.find_successor(util.inc(self.ip_hash, 2**idx - 1))
        if finger != self.fingers[idx]:
            self.update_finger(idx, finger)

    def process_notify(self, ip_bytes):
        if util.in_range(util.my_hash(ip_bytes), util.inc(util.my_hash(self.predecessor)), util.dec(self.ip_hash)):
            old_predecessor = self.predecessor
            self.update_predecessor(ip_bytes)
            self.share_table(old_predecessor)
            self.clean_table(old_predecessor)

    def share_table(self, old_predecessor):
        for key, value in self.addresses.items():
            if util.in_range(key, util.my_hash(old_predecessor), util.dec(util.my_hash(self.predecessor))):
                communication.add_entry(self.predecessor, key, value)

    def clean_table(self, old_predecessor):
        to_remove = set()
        for key, value in self.addresses.items():
            if util.in_range(key, util.my_hash(old_predecessor), util.dec(util.my_hash(self.predecessor))):
                attempt = 0
                while not communication.delete_from_backup(self.fingers[0], key):
                    attempt += 1
                    if attempt >= protocol.delete_from_backup_attempts_count:
                        break
                to_remove.add(key)
        for key in to_remove:
            del self.addresses[key]

    def deploy_and_update_backup(self, ip_bytes):
        for key, value in self.backup.items():
            while not communication.send_add_to_backup(self.fingers[0], key, value):
                pass
            self.addresses[key] = value
        self.update_predecessor(ip_bytes)
        self.backup = communication.get_backup(self.fingers[0])

    def put(self, key, value):
        key_hash = util.my_hash(key)
        node_address = self.find_successor(key_hash)
        if communication.add_entry(node_address, key_hash, self.ip_bytes):
            self.storage[key_hash] = value
            return True

        return False

    # key must be a null-terminated string presented as bytes
    def get(self, key):
        key_hash = util.my_hash(key)
        maybe_res = self.storage.get(key_hash)
        if maybe_res is not None:
            return maybe_res

        node_address = self.find_successor(key_hash)
        data_address = communication.get_ip(node_address, key_hash)
        for _ in range(protocol.get_attempts_count):
            try:
                data = communication.get_data(data_address, key_hash)
                return data
            except Exception as e:
                log_action("Failed to get data: ", e, severity='ERROR')

        return None
