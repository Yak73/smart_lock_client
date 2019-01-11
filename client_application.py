from transmission import *

if __name__ == '__main__':

    press_key = 4  # 4DEBUG

    if press_key == 1:
        registration("some_login", "some_password")
    elif press_key == 2:
        authorization("some_login", "some_password")
    elif press_key == 3:
        add_lock("some_login", "1", "some_pwd_lock")
    elif press_key == 4:
        open_lock("some_login", "1")
