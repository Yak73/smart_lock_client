import rsa
import socket
from re import findall

APP_PORT = 9073
MAX_CONN = 5
SIZE_TRANSFER = 200  # в Байтах
SERVER_ADDRESS = "localhost"


def registration(login="log", pwd="pwd"):
    if lexicographic_check(login, pwd) == 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        send_str = form_send_to_reg_or_aut(login, pwd, "1").encode()
        sock.send(send_str)
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
    if lexicographic_check(login, pwd) == 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        send_str = form_send_to_reg_or_aut(login, pwd, "2").encode()
        sock.send(send_str)
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] != "f":
            print_available_locks(answer[3:])
        sock.close()
        return 0
    print("ERROR IN CHECKS", authorization.__name__)
    return -1


def add_lock(login="log", name_lock=None, code_lock=123, pwd_lock="pwd"):
    if lexicographic_check(login) == 0 and name_lock and code_lock >= 0:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        send_str = form_send_to_add_lock(login, name_lock, code_lock, pwd_lock, "3").encode()
        sock.send(send_str)
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] != "f":
            print_available_locks(answer[3:])
        sock.close()
        return 0
    print("ERROR IN CHECKS", add_lock.__name__)
    return -1


def open_lock(login="log", pwd="some_pwd", name_lock="some_name_lock"):
    if lexicographic_check(login, pwd) == 0 and name_lock:
        sock = socket.socket()
        sock.connect((SERVER_ADDRESS, APP_PORT))  # подключаемся по адресу - х.х.х.х
        send_str = form_send_to_open_lock(login, pwd, name_lock, "4").encode()
        sock.send(send_str)
        answer = sock.recv(SIZE_TRANSFER).decode()
        if answer[2] != "f":
            sign = form_send_to_sign_challenge(login, answer[3:], name_lock)  # TODO change [3:]
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
def form_send_to_reg_or_aut(login, pwd, oper):
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
    send = "12" + login + "$" + str(public_key.n) + "$" + str(public_key.e)
    return send


@filling
def form_send_to_add_lock(login, name_lock, code_lock, pwd_lock, oper):
    if login and name_lock and code_lock and pwd_lock:
        send = oper + "1" + login + "$" + code_lock + "$" + pwd_lock + "$" + name_lock
    else:
        send = oper + "0"
    print("send: ", send)
    return send


@filling
def form_send_to_open_lock(login, pwd, name_lock, oper):
    if login and pwd and name_lock:
        send = oper + "1" + login + "$" + pwd + "$" + name_lock
    else:
        send = oper + "0"
    print("send: ", send)
    return send


def form_send_to_sign_challenge(login, challenge, name_lock):
    private_key = "12345"  # TODO  (with file)
    if private_key and login and name_lock:
        #signature = rsa.sign(challenge.encode(), private_key, 'SHA-1')
        signature = "sign_true"  # 4 DEBUG
        send = "42" + login + "$" + signature + "$" + name_lock
    else:
        send = "40"
    return send


def lexicographic_check(login, pwd=None):
    if not (5 <= len(login) <= 16):
        return "wrong length login"
    if not (6 <= len(pwd) <= 16) and pwd:
        return "wrong length pwd"
    if not len(findall(r"[a-zA-Z_0-9]", pwd)) == len(pwd) and pwd:
        return "pwd must contain only letters and digits and _"
    if not len(findall(r"[a-zA-Z_0-9]", login)) == len(login):
        return "login must contain only letters and digits and _"
    return 0




def print_available_locks(list_av_locks):
    print("list_av_locks", list_av_locks)
    pass
    # TODO (with GUI)







