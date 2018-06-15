# 构造搜索条件 q

from django.db.models import Q


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
