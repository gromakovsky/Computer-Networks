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

    # user interface
    def put(self, key, value):
        key_hash = util.my_hash(key)
        node_address = self.find_successor(key_hash)
        log_action('Node responsible for key {} (hash: {}):'.format(key, key_hash), util.readable_ip(node_address),
                   severity='INFO')
        if communication.add_entry(node_address, key_hash, self.ip_bytes):
            # concurrent access is not possible
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
        log_action('Node responsible for key {} (hash: {}):'.format(key, key_hash), util.readable_ip(node_address),
                   severity='INFO')
        data_address = communication.get_ip(node_address, key_hash)
        log_action('Node with key {} (hash: {}):'.format(key, key_hash), util.readable_ip(node_address),
                   severity='INFO')
        for _ in range(protocol.get_attempts_count):
            try:
                data = communication.get_data(data_address, key_hash)
                return data
            except Exception as e:
                log_action("Attempt to get data failed with the following reason: ", e, severity='ERROR')

        return None

    # Background jobs
    def process_keep_alive(self):
        self.lock.acquire()
        self.last_keep_alive = time.time()
        self.lock.release()

    def stabilize(self):
        x = communication.get_predecessor(self.fingers[0]) if self.fingers[0] != self.ip_bytes else self.predecessor

        def do_update():
            self._update_finger(0, x)
            self._update_successor2(communication.get_successor(x, self.fingers_hash[0], self))
        if util.distance(self.ip_hash, self.fingers_hash[0]) > 1:
            if util.in_range(util.my_hash(x), util.inc(self.ip_hash), util.dec(self.fingers_hash[0])):
                do_update()
        elif self.ip_hash == self.fingers_hash[0] and x != self.ip_hash:
                do_update()

        communication.send_notify(self.fingers[0])

    def fix_fingers(self):
        idx = random.randint(0, protocol.hash_size_bits - 1)
        finger = self.find_successor(util.inc(self.ip_hash, 2**idx - 1))
        if finger != self.fingers[idx]:
            self._update_finger(idx, finger)

    def successor_failed(self):
        log_action('Successor {} failed'.format(util.readable_ip(self.fingers[0])), severity='INFO')
        communication.send_pred_failed(self.successor2)
        self._update_finger(0, self.successor2)
        self._update_successor2(communication.get_successor(self.fingers[0], self.fingers_hash[0]), self)

    # Chord implementation
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
        successor = None
        successor2 = None
        try:
            successor = communication.get_successor(ip_bytes, self.ip_hash, self)
            successor2 = communication.get_successor(ip_bytes, util.my_hash(successor), self)
        except Exception as e:
            log_action("Error occurred in processing `PICK_UP':", e, severity='ERROR')
            if successor is None:
                self.process_pick_up(ip_bytes, attempts_count - 1)
                return
        self.lock.acquire()
        if not self.picked_up:
            self._update_predecessor(ip_bytes, False)
            self._update_finger(0, successor, False)
            if successor is not None:
                self._update_successor2(successor2 if successor2 != successor else self.ip_bytes, False)
            self.picked_up = True
        self.lock.release()

    def find_successor(self, key_hash):
        if util.in_range(key_hash, util.my_hash(self.predecessor), util.dec(self.ip_hash)):
            return self.ip_bytes
        for ip_bytes in reversed(self.fingers):
            if util.in_range(util.my_hash(ip_bytes), self.ip_hash, util.dec(key_hash)):
                if ip_bytes == self.ip_bytes:
                    continue
                try:
                    x = communication.get_successor(ip_bytes, key_hash, self)
                    return x
                except Exception as e:
                    log_action('Failed to get successor from', util.readable_ip(ip_bytes), '\nReason:', e,
                               severity='ERROR')

        return self.fingers[0]

    def process_notify(self, ip_bytes):
        if util.in_range(util.my_hash(ip_bytes), util.inc(util.my_hash(self.predecessor)), util.dec(self.ip_hash)):
            old_predecessor = self.predecessor
            self._update_predecessor(ip_bytes)
            self.share_table(old_predecessor)
            self.clean_table(old_predecessor)

    def share_table(self, old_predecessor):
        for key, value in self.addresses.items():
            if util.in_range(key, util.my_hash(old_predecessor), util.dec(util.my_hash(self.predecessor))):
                try:
                    communication.add_entry(self.predecessor, key, value)
                except Exception as e:
                    log_action('Failed to send entry to', util.readable_ip(self.predecessor), '\nReason:', e,
                               severity='ERROR')

    def clean_table(self, old_predecessor):
        to_remove = set()
        for key, value in self.addresses.items():
            if util.in_range(key, util.my_hash(old_predecessor), util.dec(util.my_hash(self.predecessor))):
                attempt = 0
                while True:
                    success = communication.delete_from_backup(self.fingers[0], key)
                    attempt += 1
                    if success or attempt >= protocol.delete_from_backup_attempts_count:
                        break
                to_remove.add(key)
        with self.lock:
            for key in to_remove:
                del self.addresses[key]

    def deploy_and_update_backup(self, ip_bytes):
        for key, value in self.backup.items():
            attempt = 0
            while True:
                success = communication.add_to_backup(self.fingers[0], key, value)
                attempt += 1
                if success or attempt >= protocol.add_to_backup_attempts_count:
                    break
            with self.lock:
                self.addresses[key] = value
        self._update_predecessor(ip_bytes)
        backup = communication.get_backup(self.fingers[0])
        with self.lock:
            self.backup = backup

    def add_to_addresses(self, key_hash, ip_bytes):
        if not util.in_range(key_hash, util.my_hash(self.predecessor), util.dec(self.ip_hash)):
            return False

        if communication.add_to_backup(self.fingers[0], key_hash, ip_bytes):
            self._add_address(key_hash, ip_bytes)
            return True
        else:
            return False

    def add_to_backup(self, key_hash, ip_bytes):
        if key_hash in self.addresses:
            return False

        with self.lock:
            self.backup[key_hash] = ip_bytes

        return True

    def delete_entry(self, key_hash):
        if key_hash in self.addresses:
            self._delete_address(key_hash)
            return True

        return False

    def delete_from_backup(self, key_hash):
        if key_hash in self.backup:
            with self.lock:
                del self.backup[key_hash]
            return True

        return False

    # logging
    def dump_fingers(self):
        log_action('Fingers:', severity='FINGERS')
        for i in range(len(self.fingers)):
            log_action(i, util.readable_ip(self.fingers[i]), self.fingers_hash[i], severity='FINGERS')

    def dump_addresses(self):
        log_action('Addresses:', severity='ADDRESSES')
        for key_hash, ip_bytes in self.addresses.items():
            log_action(key_hash, util.readable_ip(ip_bytes), severity='ADDRESSES')

    # internal modifiers
    def _update_finger(self, idx, ip_bytes, need_lock=True):
        if self.fingers[idx] == ip_bytes:
            return
        log_action('Updating {}-th finger to'.format(idx), util.readable_ip(ip_bytes), severity='INFO')
        if need_lock:
            self.lock.acquire()
        self.fingers[idx] = ip_bytes
        self.fingers_hash[idx] = util.my_hash(ip_bytes)
        if need_lock:
            self.lock.release()
        self.dump_fingers()

    def _update_successor2(self, ip_bytes, need_lock=True):
        if self.successor2 == ip_bytes:
            return
        log_action('Updating successor2 to', util.readable_ip(ip_bytes), severity='INFO')
        if need_lock:
            self.lock.acquire()
        self.successor2 = ip_bytes
        if need_lock:
            self.lock.release()

    def _update_predecessor(self, ip_bytes, need_lock=True):
        if self.predecessor == ip_bytes:
            return
        log_action('Updating predecessor to', util.readable_ip(ip_bytes), severity='INFO')
        if need_lock:
            self.lock.acquire()
        self.predecessor = ip_bytes
        if need_lock:
            self.lock.release()

    def _add_address(self, key_hash, ip_bytes):
        with self.lock:
            self.addresses[key_hash] = ip_bytes
            self.dump_addresses()

    def _delete_address(self, key_hash):
        with self.lock:
            del self.addresses[key_hash]
