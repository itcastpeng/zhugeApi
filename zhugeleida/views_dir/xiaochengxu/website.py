from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.website_verify import WebsiteAddForm, DepartmentUpdateForm, DepartmentSelectForm
import json
from publicFunc.condition_com import conditionCom
import requests
from ..conf import *
from django.db.models import Q
from zhugeleida.public.common import action_record

@csrf_exempt
# @account.is_token(models.zgld_customer)
def website(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        user_id = request.GET.get('uid')
        customer_id = request.GET.get('user_id')
        website_content = models.zgld_userprofile.objects.get(id=user_id).company.website_content

        if customer_id and user_id:
            customer_obj = models.zgld_customer.objects.filter(id=customer_id)
            if customer_obj and customer_obj[0].username:  # 说明客户访问时候经过认证的
                remark = '查看了您公司的官网,看来TA对您公司感兴趣'
                data = request.GET.copy()
                data['action'] = 4
                action_record(data, remark)

        response.code = 200
        response.data = {
            'ret_data': json.loads(website_content),
            'data_count': 6,
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"

