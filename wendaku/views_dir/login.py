from django.shortcuts import render
from wendaku import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime


@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    username = request.POST.get('username')
    password = request.POST.get('password')
    print('username, account.str_encrypt(password)',username, account.str_encrypt(password))

    # 查询数据库
    userprofile_objs = models.UserProfile.objects.filter(
        username=username,
        # md5加密 密码
        password=account.str_encrypt(password),
        status=1
    )

    if userprofile_objs:
        # 如果有数据 查询第一条对象
        userprofile_obj = userprofile_objs[0]
        # 如果没有token 则生成 token
        if not userprofile_obj.token:
            token = account.get_token(account.str_encrypt(password))
            userprofile_obj.token = token
        else:
            token = userprofile_obj.token

        response.code = 200
        response.msg = '登录成功'
        time.time()
        response.data = {
            'token': token,
            'user_id': userprofile_obj.id,
            'set_avator': userprofile_obj.set_avator
        }

        userprofile_obj.last_login_date = datetime.datetime.now()
        userprofile_obj.save()
    else:
        response.code = 401
        response.msg = "账号或密码错误"

    return JsonResponse(response.__dict__)

