
import hashlib, time, random
from django.http import JsonResponse
from django.shortcuts import redirect,render
from publicFunc import Response


# 生产随机字符串
def randon_str():
    STR = [chr(i) for i in range(65, 91)]       # 65-91对应字符A-Z
    str = [chr(i) for i in range(97, 123)]      # a-z
    number = [chr(i) for i in range(48, 58)]    # 0-9

    str_list = []
    str_list.extend(STR)
    str_list.extend(str)
    str_list.extend(number)

    random_num = random.randrange(10, 15)
    random.shuffle(str_list)
    return ''.join(str_list[:random_num])

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


def str_sha_encrypt(str):
    """
    使用sha1加密算法，返回str加密后的字符串
    """
    sha = hashlib.sha1(str)
    encrypts = sha.hexdigest()
    return encrypts



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
                # print('str_encrypt(timestamp + obj.token) -->', str_encrypt(timestamp + obj.token))
                # print('rand_str -->', rand_str)
                if str_encrypt(timestamp + obj.token) == rand_str:
                    # print("已经登录")
                    flag = True
                else:
                    flag = False

                # print('flag -->', flag)
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



# 装饰器 判断token 是否正确
def socket_is_token(table_obj,data):

    rand_str = data.get('rand_str')
    timestamp = data.get('timestamp', '')
    user_id = data.get('user_id')

    objs = table_obj.objects.filter(id=user_id)
    if objs:
        obj = objs[0]
        # print('----- str_encrypt(timestamp + obj.token) ------>', str_encrypt(timestamp + obj.token))
        # print('----- rand_str -->', rand_str)
        if str_encrypt(timestamp + obj.token) == rand_str:
            # print("------ 已经登录 ----->>")
            flag = True
        else:
            flag = False
    else:
        flag = False
    # print('---- flag ----->',flag)

    return flag









