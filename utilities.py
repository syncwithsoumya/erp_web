import re, uuid
import socket


def get_mac():
    # print(':'.join(re.findall('..', '%012x' % uuid.getnode())))
    return str(':'.join(re.findall('..', '%012x' % uuid.getnode())))


def get_ip():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return str(IPAddr)