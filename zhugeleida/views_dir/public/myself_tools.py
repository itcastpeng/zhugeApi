


from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.smallprogram_verify import SmallProgramAddForm,LoginBindingForm

import time
import datetime
import json
import requests
from publicFunc.condition_com import conditionCom
from ..conf import *
import base64
from zhugeleida.public.WorkWeixinOper import WorkWeixinOper
from zhugeapi_celery_project import tasks

@csrf_exempt
# @account.is_token(models.zgld_customer)
def tools_oper(request,oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        ## 生成小程序 authrizition token
        if  oper_type == 'send_formid_html':

            return render(request, 'test_send_formid.html', locals())

        ## 批准审核用户入库
        elif oper_type == 'approval_audit':

            return render(request, 'approval_audit.html', locals())

        ## 监控发送模板消息数据
        elif oper_type == 'monitor_send_gzh_template_msg':

            title = request.GET.get('title')
            content = request.GET.get('content')
            remark = request.GET.get('remark')

            objs = models.zgld_customer.objects.filter(session_key='notifier',company_id__in=[1])

            for obj in objs:

                data_dict = {
                    'company_id' : obj.company_id,
                    'customer_id' : obj.id,
                    'type' : 'gongzhonghao_template_tishi',
                    'title' :  title,
                    'content' : content,
                    'remark' :  remark
                }
                tasks.monitor_send_gzh_template_msg.delay(json.dumps(data_dict))



