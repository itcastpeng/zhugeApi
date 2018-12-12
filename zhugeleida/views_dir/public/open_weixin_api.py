import requests
import json
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc import Response
import redis
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
import json
import redis


from zhugeleida.views_dir.admin.dai_xcx import create_authorizer_access_token as xiaochengxu_create_authorizer_access_token

# 获取（刷新）授权公众号或小程序的接口调用凭据（令牌）
def api_authorizer_token(component_access_token, component_appid, authorizer_appid, authorizer_refresh_token):
    url = "https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token?component_access_token={component_access_token}".format(
        component_access_token=component_access_token
    )

    print('url -->', url)
    post_data = {
        "component_appid": component_appid,
        "authorizer_appid": authorizer_appid,
        "authorizer_refresh_token": authorizer_refresh_token,
    }
    print('post_data -->', post_data)
    ret = requests.post(url, data=json.dumps(post_data))

    authorizer_access_token = ret.json().get('authorizer_access_token')

    print('获取（刷新）授权公众号或小程序的接口调用凭据（令牌） -->', ret.json())
    return authorizer_access_token


# 获取小程序设置的类目信息
def getcategory(access_token):
    # url = 'https://api.weixin.qq.com/cgi-bin/wxopen/getcategory?access_token={access_token}'.format(
    #     access_token=access_token
    # )

    "https://api.weixin.qq.com/cgi-bin/wxopen/getcategory?access_token=13_RuzOk-5g-ytAoTTCFqkTAGdmtl2WnjwEOszlZn16Oi5ATiOT1TyWhJRa9P_16kMDZ8hy9fBUlbLuJ263ve3gFM-p-3VeFMe3xXT3HeKpGB20Js6EduT27IfBTFRUuvMDk_NE6S3dc6noId56JFLfAIDAWC"

    url = "https://api.weixin.qq.com/cgi-bin/wxopen/getallcategories?access_token={access_token}".format(
        access_token=access_token
    )

    print('url -->', url)

    ret = requests.get(url)

    print('获取小程序设置的类目信息 -->', ret.json())


@csrf_exempt
def crate_token(request, oper_type):
    response = Response.ResponseObj()
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    if request.method == 'POST':

        if oper_type == 'xiaochengxu_authorizer_token':
            print('----- request.POST ----->>',request.POST)
            authorization_appid = request.POST.get('authorization_appid')
            key_name = '%s_authorizer_access_token' % (authorization_appid)
            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

            objs = models.zgld_xiaochengxu_app.objects.filter(authorization_appid=authorization_appid)
            if objs:

                obj = objs[0]
                authorizer_refresh_token = obj.authorizer_refresh_token
                name = obj.name
                authorizer_appid = obj.authorization_appid

                if not authorizer_access_token:

                    data = {
                        'key_name': key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid
                    }
                    authorizer_access_token_result = xiaochengxu_create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = authorizer_access_token_result.data
                        # ret_data = {  'name' : name, 'appid': authorizer_appid, 'authorizer_access_token' : authorizer_access_token }
                    else:

                        return JsonResponse(authorizer_access_token_result.__dict__)

                ret_data = {'name': name, 'appid': authorizer_appid,
                                'authorizer_access_token': authorizer_access_token}

                print('-- ret_data -->>',ret_data)
                response.data = ret_data
                response.code = 200
                response.msg = '查询成功'

            else:
                response.code = 301
                response.msg = 'Authorizer_appid: %s 不存在于数据库' % authorization_appid

    return JsonResponse(response.__dict__)