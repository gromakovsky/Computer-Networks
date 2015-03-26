import sys

import udp_server
import tcp_server
from node import Node


def main():
    node = Node()
    try:
        udp_serv = udp_server.UPDServer(node)
        udp_serv.start()
    except OSError as e:
        sys.stderr.write("Couldn't launch UDP thread, aborting:\n" + str(e))
        sys.exit(1)
    try:
        tcp_serv = tcp_server.TCPServer(node)
        tcp_serv.start()
    except OSError as e:
        sys.stderr.write("Couldn't launch TCP thread, aborting:\n" + str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
