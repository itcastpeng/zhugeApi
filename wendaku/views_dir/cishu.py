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

from django.db.models import Q


# 数据的展示
@csrf_exempt
@account.is_token(models.UserProfile)
def cishu(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        is_today = request.GET.get('is_today', False)
        q = Q()
        q.add(Q(**{'oper_user_id__isnull': False}), Q.AND)
        if is_today:
            q.add(Q(**{'update_date__gte': datetime.datetime.now().strftime('%Y-%m-%d')}), Q.AND)
        objs = models.DaAnKu.objects.filter(q).values(
            'oper_user__username',
            'oper_user_id',
            'update_date'
        ).annotate(Count('id'))

        data_dict = {}
        for obj in objs:

            oper_user_id = obj['oper_user_id']
            count = obj['id__count']
            username = obj['oper_user__username']
            update_date = obj['update_date'].strftime('%Y-%m-%d')
            # 如果操作人ID在字典里
            if oper_user_id in data_dict:
                # print('在')
                # 如果更新时间在字典里
                if update_date in data_dict[oper_user_id]:
                    # 加总数量
                    data_dict[oper_user_id][update_date][1] += count
                else:
                    # 如果更新时间不在字典里更改修改时间的名字和总数
                    data_dict[oper_user_id][update_date]  = [username,count]

            else:
                # print('不在')
                data_dict[oper_user_id] = {
                    update_date :[username,count]
                }
        print('data_dict--->',data_dict)

        response.code = 200
        response.data = data_dict


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)