from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime


@csrf_exempt
@account.is_token(models.UserProfile)
def role(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        role_data = models.Role.objects.values('id', 'name')
        print(role_data)
        response.code = 200
        response.data = {
            'role_data': list(role_data)
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


@csrf_exempt
@account.is_token(models.UserProfile)
def role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            name = request.POST.get('name')
            role_objs = models.Role.objects.filter(name=name)
            if not role_objs:
                models.Role.objects.create(name=name)
                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 300
                response.msg = "角色名已存在"

        elif oper_type == "delete":
            role_objs = models.Role.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            name = request.POST.get('name')
            role_update = models.Role.objects.filter(id=o_id)
            if role_update:
                role_update.update(name=name)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
