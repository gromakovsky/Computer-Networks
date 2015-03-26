import udp_server
from node import Node


def main():
    node = Node()
    udp_serv = udp_server.UPDServer(node)
    udp_serv.start()


if __name__ == '__main__':
    main()
