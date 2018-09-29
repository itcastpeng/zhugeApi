
import requests
import json

get_user_data  = {'access_token': 'EBZrnGp0xSHhWcNoJM1pP1D1CvSomHkBuaAPonVeNtxWIMrXW1RQPJHWThfZxJfX9-dGfwDqInNd_4C8zlfUeiVoH4r7T7TZ0NBF4wD4I9ja-vPLiL2KSOuY7ssSGYTumjCwmbyYnUBmnoqgNfpq1rEqb00DCNAilA4iUCzr3LT2lzdOS1f8IPNKQHjbCvE5l2wgmB7US0pir2mpyC1sYg'}
post_user_data  = {
    'userid': '1528462413197',
    'name': '张聪1',
    # 'position': '开发',
    'department': [1]
}
#
add_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/create'
print(json.dumps(post_user_data))
#
ret = requests.post(add_user_url, params=get_user_data, data=json.dumps(post_user_data))
print('-----requests----->>',ret.text)

# get_user_data['department_id'] = 1
# get_user_data['fetch_child'] = 1
# get_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist'
# ret = requests.get(get_user_url, params=get_user_data)
# print(ret.text)
