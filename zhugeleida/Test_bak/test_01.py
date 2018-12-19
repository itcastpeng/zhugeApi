
import requests
import json

# get_user_data  = {'access_token': 'EBZrnGp0xSHhWcNoJM1pP1D1CvSomHkBuaAPonVeNtxWIMrXW1RQPJHWThfZxJfX9-dGfwDqInNd_4C8zlfUeiVoH4r7T7TZ0NBF4wD4I9ja-vPLiL2KSOuY7ssSGYTumjCwmbyYnUBmnoqgNfpq1rEqb00DCNAilA4iUCzr3LT2lzdOS1f8IPNKQHjbCvE5l2wgmB7US0pir2mpyC1sYg'}
# post_user_data  = {
#     'userid': '1528462413197',
#     'name': '张聪1',
#     # 'position': '开发',
#     'department': [1]
# }
# #
# add_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/create'
# print(json.dumps(post_user_data))
# #
# ret = requests.post(add_user_url, params=get_user_data, data=json.dumps(post_user_data))
# print('-----requests----->>',ret.text)

# get_user_data['department_id'] = 1
# get_user_data['fetch_child'] = 1
# get_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist'
# ret = requests.get(get_user_url, params=get_user_data)
# print(ret.text)

#
# def  conversion_seconds_hms(seconds):
#
#     m, s = divmod(seconds, 60)
#     h, m = divmod(m, 60)
#     time = 0
#     print('---h m s-->>',h,m,s)
#
#     if not h and not m and s:
#         print("%s秒" % (s))
#         time = "%s秒" % (s)
#     elif not h and m and s:
#         print("%s分%s秒" % (m, s))
#         time = "%s分%s秒" % (m, s)
#
#     elif not h and m and not s:
#         print("%s分钟" % (m))
#         time = "%s分钟" % (m)
#
#     elif h and m and s:
#         print("%s小时%s分%s秒" % (h, m, s))
#         time = "%s小时%s分%s秒" % (h, m, s)
#     elif h and m and not s:
#         print("%s小时%s分钟" % (h, m))
#         time = "%s小时%s分钟" % (h, m)
#
#     elif h and not  m and not s:
#         print("%s小时" % (h))
#         time = "%s小时" % (h)
#
#     return time
#
# print(conversion_seconds_hms(2400))

from urllib.parse import unquote

# 解析URl
share_url = '/zhugeleida/mycelery/user_send_action_log?timestamp=1545201763871&user_id=854&company_id=2&uid=135&action=14&rand_str=1c7c0939afe9ac1227aa03e160c9aa60&pid=1022&remark=%E6%AD%A3%E5%9C%A8%E6%9F%A5%E7%9C%8B%E6%96%87%E7%AB%A0%E3%80%8A%E6%B2%A1%E3%80%90%E7%95%99%E9%87%8F%E3%80%91%E6%AF%94%E6%B2%A1%E6%B5%81%E9%87%8F%E6%9B%B4%E5%8F%AF%E6%80%95%E2%80%94%E5%90%88%E4%BC%97%E5%BA%B7%E6%A1%A5%E3%80%8B%2C%E7%9C%8B%E6%9D%A5%E5%AF%B9%E6%82%A8%E7%9A%84%E6%96%87%E7%AB%A0%E6%84%9F%E5%85%B4%E8%B6%A3'


## 解码URl
redirect_url = unquote(share_url, 'utf-8')
print('-----------  文章分享之后, 客户打开让其跳转的 share_url是： -------->>', redirect_url)


application_data = {
    'leida': {
        'sToken': '5lokfwWTqHXnb58VCV',
        'sEncodingAESKey': 'ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt',
        'sCorpID': 'wx5d26a7a856b22bec',
    },
    'boss': {
        'sToken': '22LlaSyBP',
        'sEncodingAESKey': 'NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be',
        'sCorpID': 'wx36c67dd53366b6f0',
    },
    'address_book': {
        'sToken': '8sCAJ3YuU6EfYWxI',
        'sEncodingAESKey': '3gSz92t8espUQgbXembgcDk3e6Hrs9SpJf34zQ8lqEj',
        'sCorpID': 'wx1cbe3089128fda03',
    },
    'general_parm': {
        'sEncodingAESKey': 'HwX3RsMfMx9O4KBTqzwk9UMJ9pjNGbjE7PTyPaK7Gyxu4Z_G0ypv9iXT97A3EFDt',
        'sCorpID': 'wx81159f52aff62388',
    },
    'domain_urls': {
        'leida_http_url': 'http://zhugeleida.zhugeyingxiao.com'
    }
}

application_data1 = {
    'app_id' : 'wx67e2fde0f694111c',  # 小程序
    'app_secret' : '4a9690b43178a1287b2ef845158555ed',
    'token' :  'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg',
    'encodingAESKey' : 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143',
    # 'authorization_url': 'http://zhugeleida.zhugeyingxiao.com',
}

application_data2 = {
    'app_id' : 'wx6ba07e6ddcdc69b3',  # 公众号
    'app_secret' : '0bbed534062ceca2ec25133abe1eecba',
    'token' :'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg',
    'encodingAESKey' : 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143',
    'authorization_url' : 'http://zhugeleida.zhugeyingxiao.com',
    'api_url' : 'http://api.zhugeyingxiao.com'
}

token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
appid = 'wx6ba07e6ddcdc69b3'




# print(json.dumps(application_data))


