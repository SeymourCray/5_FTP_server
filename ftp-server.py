import os
from shutil import rmtree, copytree
import shutil
import socket
import json
import threading
import datetime
import fileinput


user_path = {}
settings = {}
name_password = []
MAIN_FOLDER = ""
ADMIN = 'admin'


def load_settings():
    global settings
    global MAIN_FOLDER
    with open('settings.json', 'r') as file:
        settings = json.load(file)
        MAIN_FOLDER = settings["absolute_path"].split('/')[-1]


def help_(name):
    return "pwd - выводит путь текущего каталога\n" \
           "ls DIRECTORY- выводит содержимое каталога\n" \
           "cd DIRECTORY- изменяет текущий каталог\n" \
           "mkdir DIRECTORY - создает каталог\n" \
           "rm PATH - удаляет директорию или файл\n" \
           "mv SOURCE DESTINATION - перемещает или переименовывает файл\n" \
           "cat FILE - выводит содержимое файла\n" \
           "touch FILE - создает пустой файл\n" \
           "echo FILE TEXT - добавляет текст в файл\n" \
           "cp SOURCE DESTINATION - копирует файл\n" \
           "free - выводит информацию о памяти\n" \
           "exit - разрыв соединения с сервером\n" \
           "help - выводит справку по командам\n"


def pwd(name):
    return user_path[name][1]


def ls(name):
    return '\n'.join(os.listdir(user_path[name][0]+user_path[name][1]))


def cd(name, array):
    if os.path.exists(user_path[name][0]+array[0]):
        user_path[name][1] = array[0]
        return True
    else:
        return False


def mkdir(name, array):
    delim = "" if user_path[name][1] == os.sep else os.sep
    print(user_path[name][1], delim)
    os.mkdir(user_path[name][0]+user_path[name][1]+delim+array[0])
    if free(name) > settings["storage"]:
        os.rmdir(user_path[name][0]+user_path[name][1]+delim+array[0])
        return False
    return True


def rm(name, array):
    delim = "" if user_path[name][1] == os.sep else os.sep
    if os.path.isfile(user_path[name][0]+user_path[name][1]+delim+array[0]):
        os.remove(user_path[name][0]+user_path[name][1]+delim+array[0])
        return True
    elif os.path.isdir(user_path[name][0]+user_path[name][1]+delim+array[0]):
        rmtree(user_path[name][0]+user_path[name][1]+delim+array[0])
        return True
    return False


def mv(name, array):
    delim = "" if user_path[name][1] == os.sep else os.sep
    shutil.move(user_path[name][0]+user_path[name][1] +
                delim+array[0], user_path[name][0]+array[1])
    return True


def cat(name, array):
    text = ''
    delim = "" if user_path[name][1] == os.sep else os.sep
    for i in fileinput.input(user_path[name][0]+user_path[name][1]+delim+array[0]):
        text += i
    return text


def touch(name, array):
    delim = "" if user_path[name][1] == os.sep else os.sep
    with open(user_path[name][0]+user_path[name][1]+delim+array[0], 'w') as s:
        pass
    print(free(name))
    if free(name) > settings["storage"]:
        os.remove(user_path[name][0]+user_path[name][1]+delim+array[0])
        return False
    return True


def echo(name, array):
    delim = "" if user_path[name][1] == os.sep else os.sep
    with open(user_path[name][0]+user_path[name][1]+delim+array[0], 'w') as s:
        s.write(array[1])
    if free(name) > settings["storage"]:
        os.remove(user_path[name][0]+user_path[name][1]+delim+array[0])
        return False
    return True


def cp(name, array):
    delim = "" if user_path[name][1] == os.sep else os.sep
    shutil.copy(user_path[name][0]+user_path[name]
                [1]+delim+array[0], user_path[name][0] + array[1])
    if free(name) > settings["storage"]:
        os.remove(array[1])
        return False
    return True


def free(name):
    return sum(os.path.getsize(f) for f in os.listdir(user_path[name][0]) if os.path.isfile(f))


def create_userfile():
    global name_password
    if settings["for_users"] in os.listdir(settings["absolute_path"]):
        with open(settings["absolute_path"] + os.sep + settings["for_users"], encoding='utf-8') as s:
            text = s.read()
            try:
                name_password = [(row.split(';')[0], row.split(';')[1])
                                 for row in text.split('/n')]
            except:
                pass
    else:
        a = open(settings["absolute_path"] + os.sep +
                 settings["for_users"], 'w', encoding='utf-8')
        a.close()


def sync():
    with open(settings["absolute_path"] + os.sep + settings["for_users"], 'w', encoding='utf-8') as s:
        s.write('/n'.join([pair[0]+';'+pair[1] for pair in name_password]))


def log(message):
    path = settings["absolute_path"] + os.sep + settings["logfile"]
    if os.path.isfile(path):
        with open(path, 'a', encoding='utf-8') as file:
            file.write(message + '\t' +
                       str(datetime.datetime.now())+'\n')
    else:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(message + '\t' +
                       str(datetime.datetime.now())+'\n')


def listening(sock):
    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(
            target=run_conn, args=(conn,))
        thread.start()


def run(port, host):
    log("Запуск сервера")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:
            try:
                s.bind((host, port))
                break
            except:
                port += 1
        s.listen(5)
        log(f'слушает {port}')
        print(f'слушает {port}')
        listening(s)


def start_program():
    load_settings()
    create_userfile()
    run(settings["Def_PORT"], settings["Def_HOST"])


def create_userfolder(name):
    if name == ADMIN:
        return settings["absolute_path"]
    else:
        try:
            os.mkdir(settings["absolute_path"]+os.sep+name)
        except:
            pass
        return settings["absolute_path"]+os.sep+name


def run_conn(conn):
    name = ident(conn)
    log('идентификация')
    while True:
        answer = recv_(conn, name)
        if answer == None:
            conn.close()
            break
        send_(conn, name, answer)


def new_user(sock, name):
    sock.send(f'enter password,{name}: '.encode())
    password = sock.recv(settings["max_byte"]).decode()
    name_password.append([name, password])
    user_path[name] = [create_userfolder(name), f'{os.sep}']
    sock.send(f'{name} {user_path[name][1]}'.encode())
    sync()
    return name


def ident(sock):
    sock.send('enter name: '.encode())
    name = sock.recv(settings["max_byte"]).decode()
    if name == ADMIN:
        sock.send(f'enter password,{name}: '.encode())
        password = sock.recv(settings["max_byte"]).decode()
        if password == ADMIN:
            user_path[name] = [create_userfolder(name), f'{os.sep}']
            sock.send(f'{name} {user_path[name][1]}'.encode())
            return ADMIN
        else:
            sock.send(f'wrong password,{name}% '.encode())
            ident(sock)
    else:
        for row in name_password:
            if row[0] == name:
                sock.send(f'enter password,{name}: '.encode())
                password = sock.recv(settings["max_byte"]).decode()
                if password == row[1]:
                    user_path[name] = [create_userfolder(name), f'{os.sep}']
                    sock.send(f'{name} {user_path[name][1]}% '.encode())
                    return row[0]
                else:
                    sock.send(f'wrong password,{name}'.encode())
                    ident(sock)
        else:
            return new_user(sock, name)


COMMANDS = {
    "pwd": (pwd, 0),
    "ls": (ls, 0),
    "cd": (cd, 1),
    "mkdir": (mkdir, 1),
    "rm": (rm, 1),
    "mv": (mv, 2),
    "cat": (cat, 1),
    "touch": (touch, 1),
    "echo": (echo, 2),
    "cp": (cp, 2),
    "free": (free, 0),
    "help": (help_, 0),
    "exit": (exit, 0)
}


def recv_(conn, name):
    request = conn.recv(settings["max_byte"]).decode()
    command = request.split(' ')[0]
    if not command in COMMANDS.keys():
        return False
    else:
        if command == 'exit':
            return None
        if len(request.split(' ')[1:]) != COMMANDS[command][1]:
            return False
        else:
            args = [i for i in request.split(' ')[1:]] if len(
                request.split(' ')[1:]) > 0 else None
            return COMMANDS[command][0](name, args) \
                if args != None else COMMANDS[command][0](name)


def send_(conn, name, answer):
    if type(answer) == bool:
        conn.send(f'\n\n{name} {user_path[name][1]}% '.encode()) if answer == True else conn.send(
            f'Ошибка!\n\n{name} {user_path[name][1]}% '.encode())
    else:
        conn.send(f'{answer}\n\n{name} {user_path[name][1]}% '.encode())


if __name__ == '__main__':
    start_program()
