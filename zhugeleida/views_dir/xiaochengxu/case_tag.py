from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.case_tag_verify import CaseTagAddForm,CaseTagUpdateAddForm,CaseTagSingleAddForm
import time
import datetime
import json

from publicFunc.condition_com import conditionCom

# 文章的标签查询
@csrf_exempt
@account.is_token(models.zgld_customer)
def case_tag(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1

        user_id = request.GET.get('user_id')
        company_id = request.GET.get('company_id')

        field_dict = {
            'tag_id': '',
            'name': '__contains', #标签搜索
        }
        q = conditionCom(request, field_dict)
        print('q -->', q)
        q.add('company_id',company_id)

        tag_list = models.zgld_case_tag.objects.filter(q).values('id','name')
        tag_data = list(tag_list)

        response.code = 200
        response.data = {
            'ret_data': tag_data,
            'data_count': tag_list.count(),
        }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


