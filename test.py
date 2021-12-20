import socket
import time


def auth():
    sock = socket.socket()
    sock.connect(("127.0.0.1", 65433))
    sock.recv(1024)
    sock.send("admin".encode())
    sock.recv(1024)
    sock.send("admin".encode())
    sock.recv(1024)
    main(sock)


def main(sock):
    tests = [("pwd", "/"),
             ("mkdir new_dir", ""),
             ("touch new_file", ""),
             ("cp new_file /new_dir", ""),
             ("rm new_file", ""),
             ("cd /new_dir", ""),
             ("mv new_file /new_dir/renamed_file", ""),
             ("echo renamed_file some text", ""),
             ("cat renamed_file", "some text"),
             ("cd /", ""),
             ("rm new_dir", "")]
    for index, test in enumerate(tests):
        request = test[0]
        sock.send(request.encode())
        time.sleep(1)
        res = sock.recv(1024).decode()
        response = res.split('\n\n')[0]
        print(
            f"Тест {index + 1}, {'успех' if test[1] == response else 'неудача'}")
        print(f"Команда: {test[0]}")
        print(f"Ожидаемый результат: {test[1]}")
        print(f"Фактический результат: {response}")
        print("*" * 50 + "\n")


if __name__ == '__main__':
    auth()
