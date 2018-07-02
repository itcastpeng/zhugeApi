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
        customer_id = request.GET.get('user_id')
        forms_obj = SmallProgramAddForm(request.GET)

        if forms_obj.is_valid():

            js_code = forms_obj.cleaned_data.get('code')
            user_type = forms_obj.cleaned_data.get('user_type')

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
                    user_type=user_type,   #  (1 代表'微信公众号'),  (2 代表'微信小程序'),
                    # superior=customer_id,  #上级人。
                )

                #models.zgld_information.objects.filter(customer_id=obj.id,source=source)
                # models.zgld_user_customer_belonger.objects.create(customer_id=obj.id,user_id=user_id,source=source)
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

@csrf_exempt
@account.is_token(models.zgld_customer)
def login_oper(request,oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        if oper_type == 'binding':
            print('request.GET -->', request.GET)

            forms_obj = LoginBindingForm(request.GET)
            if forms_obj.is_valid():

                # user_type = forms_obj.cleaned_data.get('user_type')
                source = forms_obj.cleaned_data.get('source')
                user_id = forms_obj.cleaned_data.get('uid')
                customer_id = forms_obj.cleaned_data.get('user_id')
                parent_id = forms_obj.cleaned_data.get('pid')

                # get_token_data = {
                #     'appid': Conf['appid'],
                #     'secret': Conf['appsecret'],
                #     'grant_type': 'authorization_code',
                # }
                #
                # ret_data = get_openid_info(get_token_data)
                # openid = ret_data['openid']
                # session_key = ret_data['session_key']
                # unionid = ret_data['unionid']

                # customer_objs = models.zgld_customer.objects.filter(
                #     openid=openid,
                #     user_type=user_type,
                # )
                # 如果openid存在一条数据

                user_customer_belonger_obj = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,user_id=user_id)

                if user_customer_belonger_obj:
                    response.code = 302
                    response.msg = "关系存在"

                else:

                    # obj = models.zgld_customer.objects.create(
                    #     customer_id=customer_id
                    #     # user_type=user_type,  #  (1 代表'微信公众号'),  (2 代表'微信小程序'),
                    #     # superior=customer_id,  #上级人。
                    # )
                    # user_customer_belonger_obj.user_type = user_type     #  (1 代表'微信公众号'),  (2 代表'微信小程序'),
                    user_customer_belonger_obj.superior = parent_id      #上级人。

                    #models.zgld_information.objects.filter(customer_id=obj.id,source=source)
                    models.zgld_user_customer_belonger.objects.create(customer_id=customer_id,user_id=user_id,source=source)

                    print('---------- crete successful ---->')

                # ret_data = {
                #     'cid': client_id,
                #     'token': token
                # }
                    response.code = 200
                    response.msg = "绑定关系成功"
                # response.data = ret_data

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        if oper_type == 'send_user_info':
            customer_id = request.GET.get('user_id')
            headimgurl = request.POST.get('avatarUrl')
            city = request.POST.get('city')
            country = request.POST.get('country')
            province = request.POST.get('province')

            gender = request.POST.get('gender')  #1代表男
            language = request.POST.get('language')
            username =  request.POST.get('nickName')

            objs = models.zgld_customer.objects.filter(
                id = customer_id,
            )
            if objs:
                objs.update( username = username,
                             headimgurl=headimgurl,
                             city =city,
                             country=country,
                             province = province,
                             language = language,
                )
                models.zgld_information.objects.create(sex=gender,customer_id=objs[0].id)
                response.code = 200
                response.msg = "保存成功"
            else:
                response.code = 301
                response.msg = "用户不存在"


            # else:
            #     response.code = 301
            #     response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)