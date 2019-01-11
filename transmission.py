import rsa
import socket
from re import findall

APP_PORT = 9073
MAX_CONN = 5
SIZE_TRANSFER = 200  # в Байтах
SERVER_ADDRESS = "localhost"


def registration(login="log", pwd="pwd"):
    if lexicographic_check(login, pwd) == 0 and uniq_check(login, pwd) == 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        sock.send(check_log_pwd(login, pwd, "1").encode())
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] == "s":
            keys = generate_key(login)
            sock.send(keys.encode())
            answer = sock.recv(SIZE_TRANSFER).decode()
            if answer[2] == "f":
                print("Error in reg_key")
        sock.close()
        return 0
    print("ERROR IN CHECKS ", registration.__name__)
    return -1


def authorization(login="log", pwd="pwd"):
    if lexicographic_check(login, pwd) == 0 and uniq_check(login, pwd) == 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        sock.send(check_log_pwd(login, pwd, "2").encode())
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] != "f":
            print_available_locks(answer[3:])
        sock.close()
        return 0
    print("ERROR IN CHECKS", authorization.__name__)
    return -1


def add_lock(login="log", id_lock="0", pwd_lock="pwd"):
    if lexicographic_check(login, pwd_lock) == 0 and int(id_lock) >= 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        sock.send(check_this_lock(login, id_lock, pwd_lock, "3").encode())
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] != "f":
            print_available_locks(answer[3:])
        sock.close()
        return 0
    print("ERROR IN CHECKS", add_lock.__name__)
    return -1


def open_lock(login="log", id_lock="0"):
    if lexicographic_check(login) == 0 and int(id_lock) >= 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        sock.send(check_access_to_lock(login, id_lock, "4").encode())
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] != "f":
            sign = code_challenge(login, answer[3:], id_lock)
            sock.send(sign.encode())
            answer = sock.recv(SIZE_TRANSFER).decode()
            if answer[2] == "s":
                print("Lock is open")
            else:
                print("Error when opening")
        sock.close()
        return 0
    print("ERROR IN CHECKS", open_lock.__name__)
    return -1


def filling(function_to_decorate):
    def wrapper(*args):
        result = function_to_decorate(*args)
        result += "$END$"
        while len(result) != SIZE_TRANSFER:
            result += "0"
        return result
    return wrapper


@filling
def check_log_pwd(login, pwd, oper):
    if login and pwd:
        send = oper + "1" + login + "$" + pwd
    else:
        send = oper + "0"
    return send


@filling
def generate_key(login):
    public_key, private_key = rsa.newkeys(512)
    # write private_key in file
    # TODO (WITH FILES IN ANDROID)
    send = "12" + login + "$PUB$" + str(public_key.n) + "," + str(public_key.e)
    return send


@filling
def check_this_lock(login, id_lock, pwd_lock, oper):
    if login and id_lock and pwd_lock:
        send = oper + "1" + login + "$" + id_lock + "$" + pwd_lock
    else:
        send = oper + "0"
    print("send: ", send)
    return send


@filling
def check_access_to_lock(login, id_lock, oper):
    if login and id_lock:
        send = oper + "1" + login + "$" + id_lock
    else:
        send = oper + "0"
    print("send: ", send)
    return send


def code_challenge(login, challenge, id_lock):
    private_key = "12345"  # TODO  (with file)
    if private_key and login and id_lock:
        #signature = rsa.sign(challenge.encode(), private_key, 'SHA-1')
        signature = "sign_true"  # 4 DEBUG
        send = "32" + login + "$" + signature + "$" + id_lock
    else:
        send = "30"
    return send


def lexicographic_check(login, pwd="correct"):
    if not (5 <= len(login) <= 16):
        return "wrong length login"
    if not (6 <= len(pwd) <= 16):
        return "wrong length pwd"
    if not len(findall(r"[a-zA-Z_0-9]", pwd)) == len(pwd):
        return "pwd must contain only letters and digits and _"
    if not len(findall(r"[a-zA-Z_0-9]", login)) == len(login):
        return "login must contain only letters and digits and _"
    return 0


def uniq_check(login, pwd):
    return 0
    # TODO (WITH DB)


def print_available_locks(list_av_locks):
    print("list_av_locks", list_av_locks)
    pass
    # TODO (with GUI)







