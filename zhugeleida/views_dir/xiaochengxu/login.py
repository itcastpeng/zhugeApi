from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.smallprogram_verify import SmallProgramAddForm
import time
import datetime
import json
import requests
from publicFunc.condition_com import conditionCom
from ..conf import *


# 从微信小程序接口中获取openid等信息
def get_openid_info(get_token_data):
    ret = requests.get(Conf['appurl'], params=get_token_data)
    ret_json = ret.json()
    print('---ret_json-->>', ret_json)
    openid = ret_json['openid']  # 用户唯一标识
    session_key = ret_json['session_key']  # 会话密钥

    unionid = ''
    if 'unionid' in ret_json:
        unionid = ret_json['unionid']  # 用户在开放平台的唯一标识符

    ret_data = {
        'openid': openid,
        'session_key': session_key,
        'unionid': unionid
    }

    return ret_data


@csrf_exempt
def login(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        print('request.GET -->', request.GET)

        forms_obj = SmallProgramAddForm(request.GET)
        if forms_obj.is_valid():

            js_code = forms_obj.cleaned_data.get('code')
            user_type = forms_obj.cleaned_data.get('user_type')
            source = forms_obj.cleaned_data.get('source')

            get_token_data = {
                'appid': Conf['appid'],
                'secret': Conf['appsecret'],
                'js_code': js_code,
                'grant_type': 'authorization_code',
            }

            ret_data = get_openid_info(get_token_data)
            openid = ret_data['openid']
            # session_key = ret_data['session_key']
            # unionid = ret_data['unionid']

            customer_objs = models.zgld_customer.objects.filter(
                openid=openid,
                user_type=user_type,

            )
            # 如果openid存在一条数据
            if customer_objs:
                token = customer_objs[0].token
                client_id = customer_objs[0].id

            else:
                token = account.get_token(account.str_encrypt(openid))

                obj = models.zgld_customer.objects.create(
                    token=token,
                    openid=openid,
                    user_type=user_type,
                )
                
                #models.zgld_information.objects.filter(customer_id=obj.id,source=source)

                client_id = obj.id
                print('---------- crete successful ---->')

            ret_data = {
                'cid': client_id,
                'token': token
            }
            response.code = 200
            response.msg = "返回成功"
            response.data = ret_data

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求方式异常"

    return  JsonResponse(response.__dict__)