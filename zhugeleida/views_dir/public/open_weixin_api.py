import requests


# 获取（刷新）授权公众号或小程序的接口调用凭据（令牌）
def api_authorizer_token(component_access_token, component_appid, authorizer_appid, authorizer_refresh_token):
    url = "https://api.weixin.qq.com /cgi-bin/component/api_authorizer_token?component_access_token={component_access_token}".format(
        component_access_token=component_access_token
    )
    post_data = {
        "component_appid": component_appid,
        "authorizer_appid": authorizer_appid,
        "authorizer_refresh_token": authorizer_refresh_token,
    }
    ret = requests.post(url, data=post_data)

    print('获取（刷新）授权公众号或小程序的接口调用凭据（令牌） -->', ret.json())


# 获取小程序设置的类目信息
def getcategory(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/wxopen/getcategory?access_token={access_token}'.format(
        access_token=access_token
    )

    ret = requests.get(url)

    print('获取小程序设置的类目信息 -->', ret.json())
