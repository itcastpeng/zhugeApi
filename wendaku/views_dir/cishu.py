from django.db.models import Count
from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publickFunc.condition_com import conditionCom
import json
import datetime


# 数据的展示
@csrf_exempt
@account.is_token(models.UserProfile)
def cishu(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认
            objs = models.DaAnKu.objects.values(
                'oper_user__username',
                'oper_user_id',
                'update_date',
            ).annotate(Count('id'))
            data_list = []

            for obj in objs:
                # print('type(obj) --> ',type(obj))
                data_list.append({
                    'oper_user_id':obj['oper_user_id'],
                    'oper_user__username':obj['oper_user__username'],
                    'update_date':obj['update_date']
                })
            response.code = 200
            response.data = {
                'data_list':data_list
            }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)






