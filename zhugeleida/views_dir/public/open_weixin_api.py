import requests
import json


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
