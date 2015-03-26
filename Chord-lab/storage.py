import socket

from log_utils import log_action
import protocol
import myip
import udp_server
from node import Node


def init():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = protocol.message_code('init') + myip.my_binary_ip()
    log_action('Broadcasting init message with IP:', myip.get_readable_ip())
    s.sendto(msg, ('<broadcast>', protocol.port))
    s.close()


def main():
    # try:
    node = Node()
    udp_serv = udp_server.UPDServer(node)
    udp_serv.start()
    init()
    # except KeyboardInterrupt:
    #     pass
        # if u_serv is not None:
        #     u_serv.finish()
        #     u_serv.join()


if __name__ == '__main__':
    main()
