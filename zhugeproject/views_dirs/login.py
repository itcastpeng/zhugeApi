from django.shortcuts import render, HttpResponse, redirect, HttpResponsePermanentRedirect
from django.http import JsonResponse
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
import datetime
import random
from django.db.models import Q
from django.db.models import Count
import re
import json
from publickFunc import Response, account
from zhugeproject import models
from django.http import HttpResponse

@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    username = request.POST.get('username')
    pwd = request.POST.get('password')
    user_id = request.GET.get('user_id')
    print('username -- pwd ---->',username,pwd)
    user_obj = models.ProjectUserProfile.objects.filter(username=username,password=account.str_encrypt(pwd))
    if user_obj:
        token = user_obj[0].token
        if not token:
            token = str(ObjectId())
            user_obj.update(token=token)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        print('user_id -->',user_id,now_time)
        models.ProjectWork_Log.objects.create(
            name_id=user_id,
            create_time=now_time,
            remark='xx在xx时间登陆了'
        )
        response.code = 200
        response.msg = '登陆成功'
        response.data = {
            'token':token
        }
    else:
        response.code = 305
        response.msg = '登陆失败,用户名或密码错误'
    return JsonResponse(response.__dict__)




















