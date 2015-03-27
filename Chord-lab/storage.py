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

    while True:
        try:
            inp = input('Enter command: ')
            if inp[:3].lower() == 'get':
                key = input('Enter key: ')
                value = node.get(key.encode())
                if value is None:
                    print('Not found')
                else:
                    print('Value:', value)
            elif inp[:3].lower() == 'put':
                key = input('Enter key: ')
                value = input('Enter value: ')
                if node.put(key.encode(), value.encode()):
                    print('Success')
                else:
                    print('Fail')
        except KeyboardInterrupt:
            print('Aborting on keyboard interrupt')
            udp_listener.socket.close()
            tcp_listener.socket.close()
            sys.exit(0)
        except Exception as e:
            print('Error occurred:', e)


if __name__ == '__main__':
    main()
