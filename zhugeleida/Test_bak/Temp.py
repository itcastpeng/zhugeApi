
import json
#
# jsonData = [{'name': 'ITY张某某', 'age': 30, 'sex': '男'}, {'name': '李某', 'age': 20, 'sex': '女'}]
#
# # 序列化，然后输出
# jsonStr = json.dumps(jsonData, ensure_ascii=False)
# print("序列化结果：")
# print(jsonStr)

import requests
app_id = 'wx67e2fde0f694111c'





#
# get_wx_info_data = {}
# post_wx_info_data = {}
# access_token = "13_H0YQkLqGN8KYZDT4mVhmuI96gIF2sDBPaGLHxo_Iivc5jajloUpby3yqCNFWU9nANuyuZVsVCfB0kpFCdiUEf4SbyAL2Hkwe8q8UfIjbCBZEMutVK8lFWnlrJ-FOgFCDBZrO7zBF7OSeh5tPSWZeABAHLO"
#
# post_wx_info_data['component_appid'] = app_id
# post_wx_info_data['authorizer_appid'] = 'wxd306d71b02c5075e'
# get_wx_info_data['component_access_token'] = access_token


# url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
# authorizer_info_ret = requests.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
#
# print('----------- 获取小程序授权方的authorizer_info信息 返回 ------------->', json.dumps(authorizer_info_ret.json()))
#
# gettemplate_list_url = 'https://api.weixin.qq.com/wxa/gettemplatelist'
# gettemplate_list_data = {
#     'access_token' : access_token
# }
#
# gettemplate_list_ret = requests.post(gettemplate_list_url, params=gettemplate_list_data)
#
# print('----------- 版库中的所有小程序代码模版 返回 ------------->', json.dumps(gettemplate_list_ret.json()))


# authorizer_access_token = "13_iIWzM88IS2bsJVG9guziHYRHfB4AUA2k8F3-XxbYmraDMI045etJ6474EoLeWw7VKXljIRof95H6CDUtz8mNdicQD5ripTUemLqz1qoZlVPw2taDA7kXokIK-AsHALk0lrCb99yFIE2bHytmBOBbAKDXKX"
# bind_tester_url = 'https://api.weixin.qq.com/wxa/bind_tester'
# get_bind_tester_data = {
#     'access_token': authorizer_access_token
# }
#
# for wechatid in ['Ju_do_it', 'ai6026325', 'crazy_acong', 'lihanjie5201314', 'wxid_6bom1qvrrjhv22']:
#     post_bind_tester_data = {
#         "wechatid": wechatid
#     }
#     domain_data_ret = requests.post(bind_tester_url, params=get_bind_tester_data,
#                                     data=json.dumps(post_bind_tester_data))
#     domain_data_ret = domain_data_ret.json()
#     print('----------绑定微信用户为小程序体验者------------>>', domain_data_ret)



################ 版本回退 @@@@@@@

# access_token = '13_R56rXwAjyGxvdJQu5XEGaXL1vLqwn2OD94-xVKVOhubjS17HclTf7ikdhdpPUPYvEbuhrXzi8ybYNhntstm-Nas-_vkHsxO76SPA3WOUtbbm7inpv-uqpmCDEWG_jYXvb0OId_H3sli7cip3VQJbAKDFAT'
#
# get_wx_info_data = {
#     'access_token' : access_token
#
# }
#
#
# url = 'https://api.weixin.qq.com/wxa/revertcoderelease'
#
# authorizer_info_ret = requests.get(url, params=get_wx_info_data)
#
# print('----------- 版库中的所有小程序代码模版 返回 ------------->', json.dumps(authorizer_info_ret.json()))



#
# def  create_authorizer_access_token():
#
#     app_id = 'wx67e2fde0f694111c'
#     get_auth_token_data = {
#         'component_access_token': "13_-0xJnm3FKROqkZb2GvNvqsRUV3RmL1Q_iDZpyaIqh5V92ShjxkduabLIWuQdsc-LQ_p46XaocIW_XBWfcdjvC3EGR7-Ca9AmBeV9btjNIHKHynyW_zV0OG5ipK0CXpvJOq4vzIEodBpHOkrYIQHdAHAPXO"
#     }
#
#     post_auth_token_data = {
#         'component_appid': app_id,
#         'authorizer_appid': 'wx1add8692a23b5976',
#         'authorizer_refresh_token': 'refreshtoken@@@09yY9swB2BonuG6Yk_Q80AaCGCuc5ftYTZiwVNS9Byw'
#     }
#
#     authorizer_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
#     authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data,
#                                         data=json.dumps(post_auth_token_data))
#     authorizer_info_ret = authorizer_info_ret.json()
#
#     print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)
#
#     authorizer_access_token = authorizer_info_ret.get('authorizer_access_token')
#     authorizer_refresh_token = authorizer_info_ret.get('authorizer_refresh_token')
#
#         # response.data = {
#         #     'authorizer_access_token' : authorizer_access_token
#         # }
#     print('------ 获取令牌（authorizer_access_token）成功------>>',authorizer_access_token)
#
#     get_wx_info_data = {
#         'access_token': authorizer_access_token
#
#     }
#     post_wx_info_data = {
#
#     }
#
#     #url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
#     # url = 'https://api.weixin.qq.com/cgi-bin/account/getaccountbasicinfo'
#     # url = 'https://api.weixin.qq.com/cgi-bin/wxopen/getcategory'
#     url = 'https://api.weixin.qq.com/wxa/getwxasearchstatus'
#     authorizer_info_ret = requests.get(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
#     authorizer_info_ret = authorizer_info_ret.json()
#
#     print('-->', json.dumps(authorizer_info_ret))
#
#
#
# create_authorizer_access_token()







# access_token = "13_pD2PP2-ElQpVkbt03YpmgLMw11-ProDxZBtX9bkxw98QGoir3jhEcc_ohI98T4VO0thagj53xgp8WRTOzBiFpwOxQBewfuBm_D4nv94EVvANa4gg6Vn4m4OtnVeLbEZJux4tH5tR4KZXOPoNMYQgAMDIUM"


# # url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
# # url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_create_user_to_customer_qrCode_poster'
#
# get_data = {
#     'data': json.dumps({"user_id": 60, "customer_id": 1})
# }
#
# # print(get_data)
#
# s = requests.session()
# s.keep_alive = False  # 关闭多余连接
# ret = s.get(url, params=get_data)
#
# # ret = requests.get(url, params=get_data)
#
#
# print(json.dumps(ret.json()))


authorizer_access_token = '15_4_FaXBldHX02B5fT-HH7p-HmiXIjYhbuUg0Mdl5PNCh_WqhvGrlcZdCxpyCDUub5svyQKYluuemJy5oCx30YeEGkrY8ymEvsSKUAvERdWmuA8N4WYwxdm1OqdbK6ldTuJyfhiyC-v1TZ_FQ5VBLhAEDQWG'
get_domin_data = {
    'access_token': authorizer_access_token
}
post_domain_data = {
    'action': 'set',
    'requestdomain': ['https://api.zhugeyingxiao.com'],
    'wsrequestdomain': ['wss://api.zhugeyingxiao.com'],
    'uploaddomain': ['https://statics.api.zhugeyingxiao.com'],    #https://statics.api.zhugeyingxiao.com
    'downloaddomain': ['https://api.zhugeyingxiao.com','https://statics.api.zhugeyingxiao.com']
}
#

post_domain_url = 'https://api.weixin.qq.com/wxa/modify_domain'
domain_data_ret = requests.post(post_domain_url, params=get_domin_data, data=json.dumps(post_domain_data))
domain_data_ret = domain_data_ret.json()
print('--------- 修改小程序服务器 接口返回---------->>', json.dumps(domain_data_ret))


post_domain_data = {
    'action': 'get'

}
domain_data_ret = requests.post(post_domain_url, params=get_domin_data, data=json.dumps(post_domain_data))
domain_data_ret = domain_data_ret.json()
print('--------- 修改小程序服务器 接口返回---------->>', json.dumps(domain_data_ret))







