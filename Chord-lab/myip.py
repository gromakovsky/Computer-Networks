import ipaddress
import os
import socket
import struct


if os.name != "nt":
    import fcntl

    def _get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])


def get_readable_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = _get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


def get_ip_bytes():
    return struct.pack('>I', int(ipaddress.IPv4Address(get_readable_ip())))
