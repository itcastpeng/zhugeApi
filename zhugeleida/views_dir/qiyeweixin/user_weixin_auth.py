from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.role_verify import RoleAddForm, RoleUpdateForm, RoleSelectForm
import time
import datetime
import json
import requests
from publicFunc.condition_com import conditionCom
from ..conf import *
import os
import redis
from django.http import HttpResponse


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
        token_ret = rc.get('leida_app_token')
        print('---token_ret---->>', token_ret)

        if not token_ret:

            company_obj = models.zgld_company.objects.get(id=company_id)
            corpid = company_obj.corp_id
            corpsecret = company_obj.zgld_app_set.get(company_id=company_id,name='AI雷达').app_secret

            get_token_data['corpid'] = corpid
            get_token_data['corpsecret'] = corpsecret

            ret = requests.get(Conf['token_url'], params=get_token_data)
            ret_json = ret.json()
            print('===========access_token==========>', ret_json)
            access_token = ret_json.get('access_token')
            rc.set('leida_app_token', access_token, 7000)

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
        user_list_ret = requests.post(Conf['userlist_url'], params=get_userlist_data,
                                      data=json.dumps(post_userlist_data))

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
