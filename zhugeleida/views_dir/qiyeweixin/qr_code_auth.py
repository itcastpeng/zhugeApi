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

@csrf_exempt
@account.is_token(models.zgld_userprofile)
def qr_code_auth(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    get_token_data = {}
    path = '/pages/mingpian/index?user_id=%s&source=1' % (user_id)   #来源 1代表扫码 2 代表转发

    post_qr_data = {'path': '/?uid=%s', 'width': 430}
    get_qr_data = {}

    get_token_data['appid'] = Conf['appid']
    get_token_data['secret'] = Conf['appsecret']
    get_token_data['grant_type'] = 'client_credential'

    # get 传参 corpid = ID & corpsecret = SECRECT
    token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
    token_ret_json = token_ret.json()
    access_token = token_ret_json['access_token']
    print('---- access_token --->>', token_ret_json)

    get_qr_data['access_token'] = access_token
    qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))
    # print('-------qr_ret---->', qr_ret.text)
    user_qr_code = '/%s_qrcode.jpg' %  user_id
    IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida') + user_qr_code
    with open('%s' % (IMG_PATH), 'wb') as f:
        f.write(qr_ret.content)
    user_obj = models.zgld_userprofile.objects.get(id=user_id)
    user_obj.qr_code = IMG_PATH
    user_obj.save()

    response.code = 200
    response.msg = "生成二维码成功"


    return JsonResponse(response.__dict__)

