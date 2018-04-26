from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime

@csrf_exempt
def role(request):
    response = Response.ResponseObj()
    role_data = models.Role.objects.values('id', 'name')
    print(role_data)
    response.code = 200
    response.data = {
        'role_data': list(role_data)
    }
    return JsonResponse(response.__dict__)

@csrf_exempt
def role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
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
        models.Role.objects.filter(id=o_id).delete()
        response.code = 200
        response.msg = "删除成功"

    elif oper_type == "update":
        name = request.POST.get('name')
        models.Role.objects.filter(id=o_id).update(name=name)
        response.code = 200
        response.msg = "修改成功"

    return JsonResponse(response.__dict__)
