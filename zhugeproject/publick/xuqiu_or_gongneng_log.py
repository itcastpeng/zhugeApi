import datetime

from django.http import request
from zhugeproject import models


def xuqiu_log(request,remark):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    user_id = request.GET.get('user_id')
    models.ProjectDemand_Log.objects.create(
        name_id=user_id,
        create_time=now_time,
        is_remark=remark
    )


def gongneng_log(request,remark):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    user_id = request.GET.get('user_id')
    models.ProjectWork_Log.objects.create(
        name_id=user_id,
        create_time=now_time,
        remark=remark
    )






