import sys

import UDPListener
import TCPListener
from node import Node


def main():
    node = Node()
    try:
        udp_listener = UDPListener.Listener(node)
        udp_listener.start()
    except OSError as e:
        sys.stderr.write("Couldn't launch UDP thread, aborting:\n" + str(e))
        sys.exit(1)
    try:
        tcp_listener = TCPListener.Listener(node)
        tcp_listener.start()
    except OSError as e:
        sys.stderr.write("Couldn't launch TCP thread, aborting:\n" + str(e))
        sys.exit(1)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        tcp_listener.socket.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
