
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
share_url = '/zhugeleida/mycelery/user_send_action_log?action=2&remark=%E6%AD%A3%E5%9C%A8%E6%9F%A5%E7%9C%8B%E7%A5%9B%E7%97%98%E5%A5%97%E9%A4%90A%2C%E5%B0%BD%E5%BF%AB%E6%8A%8A%E6%8F%A1%E5%95%86%E6%9C%BA&user_id=1230&timestamp=1543309333073&product_id=60&uid=60&rand_str=b530e68f2d0e4919f8b6fb2aab8ecad7'


redirect_url = unquote(share_url, 'utf-8')
print('-----------  文章分享之后, 客户打开让其跳转的 share_url是： -------->>', redirect_url)


