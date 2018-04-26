
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


# 装饰器 判断token 是否正确
def is_token(func):
    def inner(request, *args, **kwargs):
        # return redirect("/statics/err_page/wzwhz.html")
        request.GET.get('token')
        if not is_login:
            return redirect("/account/login/")
        return func(request, *args, **kwargs)
    return inner














