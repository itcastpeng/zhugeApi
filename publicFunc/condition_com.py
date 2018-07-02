# 构造搜索条件 q
from django.db.models import Q
from zhugeleida import models
import datetime
from publicFunc import Response

def conditionCom(request, field_dict):
    q = Q()
    for k, v in field_dict.items():
        value = request.GET.get(k)
        print('value ---->', value)
        if value:
            if v == '__contains':
                # 模糊查询
                q.add(Q(**{k + '__contains': value}), Q.AND)
            elif value == '__in':
                # 模糊查询
                q.add(Q(**{k + '__in': value}), Q.AND)
            else:
                q.add(Q(**{k: value}), Q.AND)

    return q


def action_record(data,remark):
    response = Response.ResponseObj()
    user_id = data.get('uid')  # 用户 id
    customer_id = data.get('user_id')  # 客户 id
    action = data.get('action')

    obj = models.zgld_accesslog.objects.create(
        user_id=user_id,
        customer_id=customer_id,
        remark=remark,
        action=action
    )

    follow_objs = models.zgld_user_customer_flowup.objects.filter(user_id=user_id, customer_id=customer_id)
    if follow_objs.count() == 1:
        obj.activity_time_id = follow_objs[0].id
        follow_objs.update(last_activity_time=datetime.datetime.now())
        obj.save()
        follow_objs[0].save()
        response.code = 200
        response.msg = '记录日志成功'


    elif follow_objs.count() == 0:
        flowup_create_obj = models.zgld_user_customer_flowup.objects.create(user_id=user_id,
                                                                            customer_id=customer_id,
                                                                            last_activity_time=datetime.datetime.now())
        obj.activity_time_id = flowup_create_obj.id
        obj.save()
        response.code = 200
        response.msg = '记录日志成功'

    else:
        response.code = 301
        response.msg = '用户-客户跟进信息-关系绑定表数据重复'

    return response
