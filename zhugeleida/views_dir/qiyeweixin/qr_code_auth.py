from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

import json
import requests
import redis
from ..conf import *
import os
from zhugeleida.views_dir.admin.dai_xcx  import create_authorizer_access_token

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

    if not  customer_id:
       path = '/pages/mingpian/index?uid=%s&source=1&' % (user_id)
       user_qr_code = '/%s_qrcode.jpg' % (user_id)

    else:
       path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
       user_qr_code = '/%s_%s_qrcode.jpg' % (user_id,customer_id)

    get_qr_data = {}
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
    company_id = userprofile_obj.company_id
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid

    # component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
    key_name = '%s_authorizer_access_token' % (authorizer_appid)

    authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

    if not authorizer_access_token:
        data = {
            'key_name': key_name,
            'authorizer_refresh_token': authorizer_refresh_token,
            'authorizer_appid': authorizer_appid,

        }
        authorizer_access_token = create_authorizer_access_token(data)  # 调用生成 authorizer_access_token 授权方接口调用凭据, 也简称为令牌。

    get_qr_data['access_token'] = authorizer_access_token
    post_qr_data = {'path': path, 'width': 430}

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    qr_ret = s.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

    # qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

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

