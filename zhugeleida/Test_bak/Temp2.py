import requests,json


# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_create_user_to_customer_qrCode_poster'
#
# get_data = {
#     'data': json.dumps({"user_id": 87, "customer_id": 1090})
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
import datetime
import os

# ## 下载图片链接
# qrcode_url = 'http://wx.qlogo.cn/mmopen/Oic0uTcibguuSMlpaHLGsQbFib0DAUicZBIpibFVIEBBRRgWphYGeWibQaAF1jkgtBYAgcgsNibaU4olEQddHMr5ibZv5gjEibib9EWWah/0'
#
#
# s = requests.session()
# s.keep_alive = False  # 关闭多余连接
# html = s.get(qrcode_url)
#
# # html = requests.get(qrcode_url)
#
# now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
# filename = "/%s_%s.jpg" % ('YYYYY', now_time)
# file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'qr_code') + filename
# with open(file_dir, 'wb') as file:
#     file.write(html.content)


authorizer_access_token = '16_sROo5f00GWhzT0_4tEuJTYM2YuTwXCpsB1b3WTgNiEXeeLs-QBne7L0QVZm14FDYIDKiX_CdJ5s-u8rfCiEDytAok2uk2K4u0GPOYMcN0CNemn1SfX2douBuN6gKZZvPlOwe4wCBQt9JlVG_PQPbAHDZAZ'

url = 'https://api.weixin.qq.com/cgi-bin/wxopen/wxamplink'
get_wx_info_data = {
    'access_token': authorizer_access_token
}
post_wx_info_data = {
    "appid": 'wxd306d71b02c5075e',  # 小程序appID
    "notify_users": 1,
    "show_profile": 1,
}

s = requests.session()
s.keep_alive = False  # 关闭多余连接
authorizer_info_ret = s.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))

authorizer_info_ret = authorizer_info_ret.json()
print('---------- 公众号 关联小程序 接口返回 ----------------->', json.dumps(authorizer_info_ret))
















