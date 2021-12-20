import socket
import re

HOST = 'localhost'
PORT = 65432


def user_conf():
    ip = re.search(r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', input(
        'enter ip u want to connect: '))
    ip = ip.group() if ip else HOST
    port = input('enter port u want to connect: ')
    port = int(port) if port != '' else PORT
    port = port if -1 < port < 65537 else PORT
    return ip, port


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    ip, port = user_conf()
    try:
        s.connect((ip, port))  # connect to server
        print('connection with server was successfull')
    except:
        print('Connection can not be complete')
        raise SystemExit
    try:
        while True:
            text = s.recv(1024).decode()
            if '%' in text:
                break
            s.send(input(f'{text}').encode())
        while True:
            message = input(f'{text}')
            s.send(message.encode())
            if message == 'exit':
                break
            text = s.recv(1024).decode()
        s.close()
    except:
        print('connection was lost')
