
import hashlib
import time

# 用户输入的密码加密
def str_encrypt(pwd):
    """
    :param pwd: 密码
    :return:
    """
    pwd = str(pwd)
    hash = hashlib.md5()
    hash.update(pwd.encode())
    return hash.hexdigest()


# 生产token值
def get_token(pwd):
    tmp_str = str(int(time.time()*1000)) + pwd
    token = str_encrypt(tmp_str)
    return token


