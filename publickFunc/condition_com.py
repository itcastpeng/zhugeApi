
# 构造搜索条件 q

from django.db.models import Q


def conditionCom(request, field_dict):
	q = Q()
	for key, value in field_dict.items():
		value = request.GET.get(key)
		if value:
			if value == '__contains':
				# 模糊查询
				q.add(Q(**{key + '__contains': value}), Q.AND)
			else:
				q.add(Q(**{key: value}), Q.AND)

	return q
