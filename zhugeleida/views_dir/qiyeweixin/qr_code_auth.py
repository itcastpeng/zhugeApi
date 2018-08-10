from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

import json
import requests

from ..conf import *
import os

#后台点击按钮生成了企业有用户的二维码。
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def  create_qr_code(request):
    response = Response.ResponseObj()

    if request.method == "GET":
       user_id = request.GET.get('user_id')
       customer_id = request.GET.get('customer_id')

       data_dict = {'user_id': user_id,'customer_id': customer_id}
       response = create_small_program_qr_code(data_dict)  #

       return JsonResponse(response.__dict__)


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)

#有上面的URl调用的
def create_small_program_qr_code(data):
    response = Response.ResponseObj()
    user_id = data.get('user_id')
    customer_id = data.get('customer_id','')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    get_token_data = {}

    if not  customer_id:
       path = '/pages/mingpian/index?uid=%s&source=1&' % (user_id)
       user_qr_code = '/%s_qrcode.jpg' % (user_id)

    else:
       path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
       user_qr_code = '/%s_%s_qrcode.jpg' % (user_id,customer_id)

    get_qr_data = {}

    get_token_data['appid'] = Conf['appid']
    get_token_data['secret'] = Conf['appsecret']
    get_token_data['grant_type'] = 'client_credential'

    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
    key_name = "company_%s_xiaochengxu_token" % (company_id)
    token_ret = rc.get(key_name)

    print('---token_ret---->>', token_ret)

    if not token_ret:
        # {"errcode": 0, "errmsg": "created"}
        token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
        token_ret_json = token_ret.json()
        print('-----token_ret_json------>',token_ret_json)
        if not token_ret_json.get('access_token'):
            response.code = token_ret_json['errcode']
            response.msg = "生成小程序二维码未验证通过"
            return response


        access_token = token_ret_json['access_token']
        print('---- access_token --->>', token_ret_json)
        get_qr_data['access_token'] = access_token

        rc.set(key_name, access_token, 7000)

    else:

        get_qr_data['access_token'] = token_ret

    post_qr_data = {'path': path, 'width': 430}
    qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

    if not qr_ret.content:

        response.msg = "生成小程序二维码未验证通过"
        return response

    # print('-------qr_ret---->', qr_ret.text)

    IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida','imgs','xiaochengxu','qr_code') + user_qr_code
    with open('%s' % (IMG_PATH), 'wb') as f:
        f.write(qr_ret.content)

    user_obj = models.zgld_userprofile.objects.get(id=user_id)
    user_obj.qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
    user_obj.save()

    response.code = 200
    response.msg = "生成小程序二维码成功"


    return response

