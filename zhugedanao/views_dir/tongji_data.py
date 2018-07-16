from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count
from publicFunc.Response import ResponseObj
from publicFunc.account import is_token
from zhugedanao import models
from publicFunc.condition_com import conditionCom
from django.db.models import Q

import datetime


# 统计数据
def tongji_data(request):
    response = ResponseObj()
    nowDate = datetime.datetime.now().strftime("%Y-%m-%d")

    start_date = request.GET.get('create_date__gte', nowDate)
    stop_date = request.GET.get('create_date__lt', '')

    # 获取参数
    field_dict = {
        'id': '',
        'name': '__contains',
        'create_date__gte': start_date,
        'create_date__lt': stop_date,
    }
    print('field_dict -->', field_dict)
    q = conditionCom(request, field_dict)
    print('q -->', q)

    userCount = models.zhugedanao_userprofile.objects.count()       # 所有用户
    userNewCount = models.zhugedanao_userprofile.objects.filter(q).count()    # 新用户

    todayHuoyueCount = len(models.zhugedanao_oper_log.objects.filter(q).values('user_id').annotate(Count('id')))   # 今日活跃

    data2 = []
    gongneng_objs = models.zhugedanao_gongneng.objects.filter(pid__isnull=True)

    for gongneng_obj in gongneng_objs:
        oper_log_q = Q(gongneng_id=gongneng_obj.id) | Q(gongneng__pid=gongneng_obj.id)
        if stop_date:
            gongneng_count = models.zhugedanao_oper_log.objects.filter(q).filter(oper_log_q).count()
        else:
            gongneng_count = models.zhugedanao_oper_log.objects.filter(oper_log_q).count()
        data2.append({
            "title": gongneng_obj.name,
            "value": gongneng_count
        })
    
    response.code = 200
    response.data = {
        "data1": [
            {
                "title": "用户总数",
                "value": userCount
            },
            {
                "title": "新增用户数",
                "value": userNewCount
            },
            {
                "title": "活跃用户数",
                "value": todayHuoyueCount
            },
        ],
        "data2": data2
    }

    return JsonResponse(response.__dict__)

