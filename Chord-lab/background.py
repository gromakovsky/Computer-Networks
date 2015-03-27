import threading
import time

from log_utils import log_action
import communication
import protocol


class NodeInitializer(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='Node Initializer', daemon=True)
        self.node = node

    def run(self):
        while self.node.ip_bytes == self.node.predecessor == self.node.successor2 == self.node.fingers[0]\
                and not self.node.picked_up:
            try:
                communication.send_init()
            except Exception as e:
                log_action("Error occurred in sending `INIT':", e, severity='ERROR')
            time.sleep(protocol.init_interval)


class AliveKeeper(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='Alive Keeper', daemon=True)
        self.node = node

    def run(self):
        time.sleep(protocol.keep_alive_interval)
        while True:
            if self.node.predecessor:
                try:
                    communication.send_keep_alive(self.node.predecessor)
                except Exception as e:
                    log_action("Error occurred in sending `KEEP_ALIVE':", e, severity='ERROR')
                time.sleep(protocol.keep_alive_interval)


class Stabilizer(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='Stabilizer', daemon=True)
        self.node = node

    def run(self):
        time.sleep(protocol.stabilize_interval)
        while True:
            try:
                self.node.stabilize()
            except Exception as e:
                log_action('Error occurred in stabilization:', e, severity='ERROR')
            time.sleep(protocol.stabilize_interval)


class FingersFixer(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='Fingers Fixer', daemon=True)
        self.node = node

    def run(self):
        time.sleep(protocol.fix_fingers_interval)
        while True:
            try:
                self.node.fix_fingers()
            except Exception as e:
                log_action('Error occurred in fingers fixing:', e, severity='ERROR')
            time.sleep(protocol.fix_fingers_interval)


class KeepAliveTracker(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self, name='Keep Alive Tracker', daemon=True)
        self.node = node

    def run(self):
        time.sleep(protocol.max_no_keep_alive)
        while True:
            if time.time() - self.node.last_keep_alive > protocol.max_no_keep_alive:
                try:
                    self.node.successor_failed()
                except Exception as e:
                    log_action("Error occurred in processing successor's failure:", e, severity='ERROR')
            time.sleep(protocol.max_no_keep_alive)


background_thread_classes = [NodeInitializer, AliveKeeper, Stabilizer, FingersFixer, KeepAliveTracker]