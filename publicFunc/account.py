
import hashlib
import time

from django.http import JsonResponse
from django.shortcuts import redirect,render

from publicFunc import Response


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
def is_token(table_obj):
    def is_token_decorator(func):
        def inner(request, *args, **kwargs):
            rand_str = request.GET.get('rand_str')
            timestamp = request.GET.get('timestamp', '')
            user_id = request.GET.get('user_id')
            objs = table_obj.objects.filter(id=user_id)
            if objs:
                obj = objs[0]
                print('str_encrypt(timestamp + obj.token) -->', str_encrypt(timestamp + obj.token))
                print('rand_str -->', rand_str)
                if str_encrypt(timestamp + obj.token) == rand_str:
                    print("已经登录")
                    flag = True
                else:
                    flag = False
            else:
                flag = False

            if not flag:
                response = Response.ResponseObj()
                response.code = 400
                response.msg = "token异常"
                return JsonResponse(response.__dict__)
            return func(request, *args, **kwargs)
        return inner

    return is_token_decorator










