from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.role_verify import RoleAddForm, RoleUpdateForm, RoleSelectForm
import datetime
import json
import requests
from publicFunc.condition_com import conditionCom
from ..conf import *
import os
import redis
from django.http import HttpResponse

import random
import string
import time
from  publicFunc.account import str_sha_encrypt


@csrf_exempt
def work_weixin_auth(request, company_id):
    response = Response.ResponseObj()

    if request.method == "GET":
        code = request.GET.get('code')
        get_code_data = {}
        get_token_data = {}
        post_userlist_data = {}
        get_userlist_data = {}


        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
        key_name = "company_%s_leida_app_token" % (company_id)
        token_ret = rc.get(key_name)
        print('---token_ret---->>', token_ret)

        if not token_ret:

            company_obj = models.zgld_company.objects.get(id=company_id)
            corpid = company_obj.corp_id
            # corpsecret = company_obj.zgld_app_set.get(company_id=company_id,name='AI雷达').app_secret
            corpsecret = company_obj.zgld_app_set.get(company_id=company_id,app_type=1).app_secret

            get_token_data['corpid'] = corpid
            get_token_data['corpsecret'] = corpsecret

            ret = requests.get(Conf['token_url'], params=get_token_data)
            ret_json = ret.json()
            print('===========access_token==========>', ret_json)
            access_token = ret_json.get('access_token')

            key_name = "company_%s_leida_app_token" % (company_id)
            rc.set(key_name, access_token, 7000)

        else:
            access_token = token_ret


        get_code_data['code'] = code
        get_code_data['access_token'] = access_token
        code_ret = requests.get(Conf['code_url'], params=get_code_data)
        print('===========user_ticket==========>', code_ret.json())
        code_ret_json = code_ret.json()


        user_ticket = code_ret_json.get('user_ticket')
        if not user_ticket:
            return  HttpResponse('404')

        # ?access_token = ACCESS_TOKEN
        post_userlist_data['user_ticket'] = user_ticket
        get_userlist_data['access_token'] = access_token
        print('======>>>>>', post_userlist_data, get_userlist_data)
        user_list_ret = requests.post(Conf['userlist_url'], params=get_userlist_data,data=json.dumps(post_userlist_data))

        user_list_ret_json = user_list_ret.json()
        print('----------user_list_ret_json---->', user_list_ret_json)

        userid = user_list_ret_json['userid']
        name = user_list_ret_json['name']
        avatar = user_list_ret_json['avatar']    # 加上100 获取小图
        gender = user_list_ret_json['gender']
        # email = user_list_ret_json['email']

        # qr_code_auth()  # 生成二维码保存至数据库路径

        user_profile_objs = models.zgld_userprofile.objects.filter(
            userid=userid,
            company_id=company_id
        )
        # 如果用户存在
        if user_profile_objs:
            user_profile_obj = user_profile_objs[0]
            if user_profile_obj.status == 1:
                user_profile_obj.gender = gender
                # user_profile_obj.email = email
                user_profile_obj.avatar = avatar
                user_profile_obj.save()

                redirect_url = 'http://zhugeleida.zhugeyingxiao.com?token=' + user_profile_obj.token + '&' + 'id=' + str(
                    user_profile_obj.id) + '&' + 'avatar=' + avatar
                return redirect(redirect_url)

        return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')

    else:
        response.code = 402
        response.msg = "请求方式异常"





#生成JS-SDK使用权限签名算法
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def enterprise_weixin_sign(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        '''
        生成签名之前必须先了解一下jsapi_ticket，jsapi_ticket是H5应用调用企业微信JS接口的临时票据。
        正常情况下，jsapi_ticket的有效期为7200秒，通过access_token来获取
        '''
        get_ticket_data = {}
        get_token_data = {}
        user_id = request.GET.get('user_id')
        user_obj = models.zgld_userprofile.objects.get(id=user_id)
        company_id = user_obj.company_id
        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
        key_name = "company_%s_leida_app_token" % (company_id)
        token_ret = rc.get(key_name)
        print('---token_ret---->>', token_ret)
        company_obj = models.zgld_company.objects.get(id=company_id)
        corpid = company_obj.corp_id

        if not token_ret:

            # corpsecret = company_obj.zgld_app_set.get(company_id=company_id,name='AI雷达').app_secret
            corpsecret = company_obj.zgld_app_set.get(company_id=company_id,app_type=1).app_secret

            get_token_data['corpid'] = corpid
            get_token_data['corpsecret'] = corpsecret

            ret = requests.get(Conf['token_url'], params=get_token_data)
            ret_json = ret.json()
            print('===========access_token==========>', ret_json)
            access_token = ret_json.get('access_token')

            key_name = "company_%s_leida_app_token" % (company_id)
            rc.set(key_name, access_token, 7000)

        else:
            access_token = token_ret


        key_name = "company_%s_jsapi_ticket" % (company_id)
        ticket_ret = rc.get(key_name)
        print('--- 从redis里取出 %s : ---->>' % (key_name), ticket_ret)
        jsapi_ticket = ticket_ret

        if not ticket_ret:
            get_jsapi_ticket_url =  'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket'
            get_ticket_data  = {
                'access_token' : access_token
            }
            jsapi_ticket_ret = requests.get(get_jsapi_ticket_url, params=get_ticket_data)
            print('=========== 权限签名 jsapi_ticket_ret 接口返回 ==========>', jsapi_ticket_ret.json())
            jsapi_ticket_ret = jsapi_ticket_ret.json()
            ticket = jsapi_ticket_ret.get('ticket')
            errmsg = jsapi_ticket_ret.get('errmsg')
            if errmsg != "ok":
                response.code = 402
                response.msg = "没有生成生成签名所需的jsapi_ticket"
                print('-------- 生成签名所需的jsapi_ticket ----------->>')
                return JsonResponse(response.__dict__)
            else:
                rc.set(key_name, ticket, 7000)
                jsapi_ticket = ticket

        noncestr = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        timestamp = int(time.time())
        url = 'zhugeleida.zhugeyingxiao.com'
        sha_string = "jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s" % (jsapi_ticket,noncestr,timestamp,url)
        signature = str_sha_encrypt(sha_string.encode('utf-8'))

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'signature': signature,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'appId': corpid
        }



    else:
        response.code = 402
        response.msg = "请求方式异常"

    return JsonResponse(response.__dict__)



