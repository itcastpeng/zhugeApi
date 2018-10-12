
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


def  conversion_seconds_hms(seconds):

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time = 0
    print('---h m s-->>',h,m,s)

    if not h and not m and s:
        print("%s秒" % (s))
        time = "%s秒" % (s)
    elif not h and m and s:
        print("%s分%s秒" % (m, s))
        time = "%s分%s秒" % (m, s)

    elif not h and m and not s:
        print("%s分钟" % (m))
        time = "%s分钟" % (m)

    elif h and m and s:
        print("%s小时%s分%s秒" % (h, m, s))
        time = "%s小时%s分%s秒" % (h, m, s)
    elif h and m and not s:
        print("%s小时%s分钟" % (h, m))
        time = "%s小时%s分钟" % (h, m)

    elif h and not  m and not s:
        print("%s小时" % (h))
        time = "%s小时" % (h)

    return time

print(conversion_seconds_hms(2400))
