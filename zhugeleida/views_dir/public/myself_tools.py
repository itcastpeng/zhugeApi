


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

