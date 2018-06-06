
from django.shortcuts import render,redirect
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

@csrf_exempt
def work_weixin_auth(request, company_id):
    response = Response.ResponseObj()

    if request.method == "GET":
            code = request.GET.get('code')
            get_code_data = {}
            get_token_data = {}
            post_userlist_data = {}
            get_userlist_data = {}

            get_token_data['corpid'] = Conf['corpid']
            get_token_data['corpsecret'] = Conf['corpsecret']
            # get 传参 corpid = ID & corpsecret = SECRECT
            ret = requests.get(Conf['token_url'],params=get_token_data)
            ret_json = ret.json()
            access_token = ret_json['access_token']


            print('===========>token_ret',ret_json)

            get_code_data['code'] = code
            get_code_data['access_token'] = access_token
            code_ret = requests.get(Conf['code_url'], params=get_code_data)
            print('===========>code_ret', code_ret.json())

            code_ret_json = code_ret.json()
            user_ticket = code_ret_json['user_ticket']

            # ?access_token = ACCESS_TOKEN
            post_userlist_data['user_ticket'] = user_ticket
            get_userlist_data['access_token'] = access_token
            print('======>>>>>',post_userlist_data,get_userlist_data)
            user_list_ret =  requests.post(Conf['userlist_url'], params=get_userlist_data, data=json.dumps(post_userlist_data))
            # print('user_list_ret_url -->', user_list_ret.url)

            #
            # response.code = 200
            # response.data = {
            #     'ret_data': user_list_ret.json(),
            #
            # }

            user_list_ret_json = user_list_ret.json()
            userid = user_list_ret_json['userid']
            name = user_list_ret_json['name']
            avatar = user_list_ret_json['avatar']
            gender = user_list_ret_json['gender']


            print('----------user_list_ret_json---->',user_list_ret_json)
            user_profile_objs = models.zgld_userprofile.objects.filter(
                userid=userid,
                company_id=company_id
            )
            # 如果用户存在
            if user_profile_objs:
                user_profile_obj = user_profile_objs[0]
                if user_profile_obj.status == 1:
                    redirect_url = 'http://zhugeleida.zhugeyingxiao.com?token=' + user_profile_obj.token + '&' + 'id=' + str(user_profile_obj.id) + '&' + 'avatar=' + avatar
                    return  redirect(redirect_url)



            else:
                token = account.get_token(account.str_encrypt(str(int(time.time() * 1000)) + userid))
                user_data_dict = {
                    'userid': userid,
                    'name': name,
                    'avatar': avatar,
                    'gender': gender,
                    'role_id': 1,
                    'company_id': company_id,
                    'token': token
                }
                models.zgld_userprofile.objects.create(**user_data_dict)
                print('---------- crete successful ---->')

            return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')


    else:
        response.code = 402
        response.msg = "请求方式异常"
