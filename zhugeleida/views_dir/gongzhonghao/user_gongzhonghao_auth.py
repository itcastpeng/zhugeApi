from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.smallprogram_verify import SmallProgramAddForm,LoginBindingForm

import time
import datetime

import requests
from publicFunc.condition_com import conditionCom
from ..conf import *
from zhugeapi_celery_project import tasks
from zhugeleida.public.common import action_record
import base64
import json

from collections import OrderedDict
import logging.handlers
import redis

# 从微信公众号接口中获取openid等信息
def get_openid_info(get_token_data):
    oauth_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    # rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    ret = requests.get(oauth_url, params=get_token_data)
    ret_json = ret.json()
    print('---ret_json-->>', ret_json)
    openid = ret_json['openid']  # 用户唯一标识
    session_key = ret_json['session_key']  # 会话密钥
    access_token = ret_json['access_token']  # 会话密钥

    ret_data = {
        'openid': openid,
        'session_key': session_key,
        'access_token' : access_token
    }

    return ret_data


@csrf_exempt
def user_gongzhonghao_auth(request,company_id):
    response = Response.ResponseObj()

    if request.method == "GET":
        print('request.GET -->', request.GET)
        customer_id = request.GET.get('user_id')
        company_id = company_id
        forms_obj = SmallProgramAddForm(request.GET)

        if forms_obj.is_valid():

            js_code = forms_obj.cleaned_data.get('code')
            user_type = forms_obj.cleaned_data.get('user_type')
            gongzhonghao_app_obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)

            authorization_appid = ''
            authorization_secret = ''
            if gongzhonghao_app_obj:
                authorization_appid = gongzhonghao_app_obj.authorization_appid
                authorization_secret = gongzhonghao_app_obj.authorization_secret
            appid = authorization_appid    #公众号的唯一标识
            secret = authorization_secret  #公众号的appsecret

            get_token_data = {
                'appid': appid ,
                'secret': secret,
                'code': js_code,
                'grant_type': 'authorization_code',
            }

            ret_data = get_openid_info(get_token_data)
            openid = ret_data['openid']
            access_token = ret_data['access_token']
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

                client_id = obj.id
                print('---------- 公众号-新用户创建成功 crete successful ---->')

                get_user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
                get_user_info_data = {
                    'access_token': access_token,
                    'openid': openid,
                    'lang': 'zh_CN',
                }

                ret = requests.get(get_user_info_url, params=get_user_info_data)
                ret_json = ret.json()
                print('------- 拉取用户信息 接口返回----->>', ret_json)


                if 'errcode' not  in  ret_json:

                    openid = ret_json['openid']  # 用户唯一标识
                    nickname = ret_json['nickname']  # 会话密钥
                    sex = ret_json['sex']  #
                    province = ret_json['province']  #
                    city = ret_json['city']  #
                    country = ret_json['country']    #
                    headimgurl = ret_json['headimgurl']  #
                    obj.openid = openid
                    obj.nickname = nickname
                    obj.sex = sex
                    obj.openid = openid


                else:
                    errcode = ret_json.get('errcode')
                    errmsg = ret_json.get('errmsg')




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