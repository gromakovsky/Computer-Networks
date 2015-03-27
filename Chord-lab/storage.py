import sys

import UDPListener
import TCPListener
from node import Node
import myip


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

    def finish():
        udp_listener.socket.close()
        tcp_listener.socket.close()
        sys.exit(0)

    print('Your IP is:', myip.get_readable_ip())
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
            elif inp[:4].lower() == 'exit':
                finish()
            else:
                print("Supported commands are `get', `put' and `finish'")
        except KeyboardInterrupt:
            print('Aborting on keyboard interrupt')
            finish()
        except Exception as e:
            print('Error occurred:', e)


if __name__ == '__main__':
    main()
