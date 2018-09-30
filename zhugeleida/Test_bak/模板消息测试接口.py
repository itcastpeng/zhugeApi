
import json,requests
import time


def create_component_access_token():
    component_verify_ticket = "ticket@@@tF28I_BTl2gJLnkJQhFx5VgjbGXHf41FQwoz45udw90931DwhC7x46XVgVImTvAlbtDLE-39NU0A609UQlyniw"

    app_id =  'wx6ba07e6ddcdc69b3',                     # 查看诸葛雷达_公众号的 appid
    app_secret =  '0bbed534062ceca2ec25133abe1eecba'    # 查看诸葛雷达_公众号的AppSecret

    post_component_data = {
        'component_appid': app_id,
        'component_appsecret': app_secret,
        'component_verify_ticket': component_verify_ticket
    }


    post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
    component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
    print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
    component_token_ret = component_token_ret.json()
    access_token = component_token_ret.get('component_access_token')

    return access_token




def  create_authorizer_access_token():
    # component_access_token = create_component_access_token()
    component_access_token = "14_k62dPPwCP_G7ckDcroFVdiP8Un1ROfWUYRLi9v150pCAYPHMsntj0xSLinq7TWrOVJgRTuW44ZrOcSVHPmZYqsdomiyT9F529FvBAeqU3n35c6g4SUF5k_iqTHyVxYZhQ17nDhd3NaXh3WamYSRfAEAPJI"

    # app_id = 'wx67e2fde0f694111c' # 小程序三方平台ID
    app_id = 'wx6ba07e6ddcdc69b3'   # 公众号三方平台ID

    get_auth_token_data = {
        'component_access_token': component_access_token
    }

    post_auth_token_data = {
        'component_appid': app_id,
        'authorizer_appid': 'wxf1a6faa38d214b2d',
        'authorizer_refresh_token': 'refreshtoken@@@6WssLAxbrK_GG81Nkz0kIvL_t5WymTwXxaUpeGHNAVo'
    }

    authorizer_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
    authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data, data=json.dumps(post_auth_token_data))
    authorizer_info_ret = authorizer_info_ret.json()

    # print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)

    authorizer_access_token = authorizer_info_ret.get('authorizer_access_token')
    authorizer_refresh_token = authorizer_info_ret.get('authorizer_refresh_token')

        # response.data = {
        #     'authorizer_access_token' : authorizer_access_token
        # }
    print('------ 获取令牌（authorizer_access_token）成功------>>',authorizer_access_token)

    return authorizer_access_token





# token = create_authorizer_access_token()

token = "14_kSx4ahPdEtq5JWcOrJBzf2wdPWEanQd7kc8brpOEgxqQzWYGKrKBRkXln75TjspQHpLwVlTUtPkHn4rbkF41I6AaishKMnSn4x7509MLhAZQ9VdsknWNk7QpxN2lQlsP2yaW4_9g-ZBa4bRCXQHeAJDGZQ"

# get_user_data  = {'access_token': token }

# post_data = {
# 	"offset": 0,
# 	"count": 1
# }

# list_url =  'https://api.weixin.qq.com/cgi-bin/wxopen/template/list'
# keyword_url = 'https://api.weixin.qq.com/cgi-bin/wxopen/template/library/get'
# keyword_post_data = {
#    'id': 'AT0782',
#    'access_token': token
# }
# ret = requests.post(keyword_url, params=get_user_data,data=json.dumps(keyword_post_data))
# print(json.dumps(ret.json()))




# template_list_url = 'https://api.weixin.qq.com/cgi-bin/wxopen/template/list'
# post_template_data = {
# 	"offset": 0,
# 	"count": 10
# }
#
# template_list_ret = requests.post(template_list_url, params=get_user_data,data=json.dumps(post_template_data))
# print('---- 前 ---->',json.dumps(template_list_ret.json()))



# template_add_url  = 'https://api.weixin.qq.com/cgi-bin/wxopen/template/add'
# post_template_add_data = {
#     'id': 'AT0782',
#     "keyword_id_list":[25,22,11]
# }
#
# add_ret = requests.post(template_add_url, params=get_user_data,data=json.dumps(post_template_add_data))
# print('----- 加 -->',json.dumps(add_ret.json()))
# time.sleep(3)
#
# template_list_ret = requests.post(template_list_url, params=get_user_data,data=json.dumps(post_template_data))
# print('---- 后 ---->',json.dumps(template_list_ret.json()))



###### 公众号 设置所属行业 #########

# api_set_industry_url  = 'https://api.weixin.qq.com/cgi-bin/template/api_set_industry'
# post_industry_data = {
#     "industry_id1": "1",
#     "industry_id2": "2"
# }
# template_list_ret = requests.post(api_set_industry_url, params=get_user_data,data=json.dumps(post_industry_data))
# print('---- 前 ---->',json.dumps(template_list_ret.json()))
# {"errcode": 0, "errmsg": "ok"}

##### 获得模板ID ############

# api_add_template_url = 'https://api.weixin.qq.com/cgi-bin/template/api_add_template'
#
# post_add_template_data = {
#     "template_id_short": "OPENTM202109783"
# }
#
# ret = requests.post(api_add_template_url, params=get_user_data,data=json.dumps(post_add_template_data))
# print('---- 添加后 ---->',json.dumps(ret.json()))




get_user_data = {
    'access_token': 'E-psUgPy8Jvhs-DwRk_lWg8cbLbFcfB9vFcDQV8REYu8m009j8dErf63klIcy3UQJXhoGPmmHHH-tyoO7cpPjaH1_ZdclKMTwng9MpQqQeoBkNtMjU6i6n6GDn3NPcLdfARg4HKpkF0XE-xx-m1ZyZct_wLn1P143x6HUBg5ObwEfjO8cwrhZYt7JtH5T1uecaaOBMz18eA20FivV94C7A'
}

update_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/update'
post_user_data = {"name": "\u5c0f\u660e", "position": "\u6d4b\u8bd5", "department": "[9]", "mobile": "15601096637", "userid": "1531993938983"}
post_user_data = {"name": "\u5c0f\u660e", "position": "\u6d4b\u8bd5", "department": [9], "mobile": "15601096637", "userid": "1531993938983"}

ret = requests.post(update_url, params=get_user_data, data=json.dumps(post_user_data))

weixin_ret = ret.json()
print('---- 添加后 ---->',json.dumps(weixin_ret))










