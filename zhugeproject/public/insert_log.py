import datetime

from django.http import request
from zhugeproject import models


# def xuqiu_log(request, remark):
#     now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
#     user_id = request.GET.get('user_id')
#     models.project_DemandLog.objects.create(
#         name_id=user_id,
#         create_time=now_time,
#         is_remark=remark
#     )


def caozuo(user_id, quanxian_id, oper_type, remark=''):
    models.project_caozuo_log.objects.create(
        user_id=user_id,
        remark=remark,
        oper_type=oper_type,
        quanxian_id=quanxian_id
    )
