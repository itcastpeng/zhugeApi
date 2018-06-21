from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom, action_record
from zhugeleida.forms.xiaochengxu.user_verify import UserAddForm, UserUpdateForm, UserSelectForm
import json
from django.db.models import Q
from django.db.models import F


# 展示单个的名片信息
@csrf_exempt
@account.is_token(models.zgld_customer)
def product(request):
    remark = '正在查看你发布的产品,尽快把握商机'
    response = action_record(request, remark)


    return JsonResponse(response.__dict__)


# 展示全部的名片、记录各种动作到日志中
@csrf_exempt
@account.is_token(models.zgld_customer)
def product_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == 'GET':
        if oper_type == '竞价排名':
            remark = '正在查看你发布的产品,尽快把握商机'
            response = action_record(request, remark)
        elif oper_type == '转发':
            remark = '转发了竞价排名。'
            response = action_record(request, remark)


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
