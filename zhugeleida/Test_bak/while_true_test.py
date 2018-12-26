
import requests,json

component_access_token = '17_vV9M5ufSorXhvYAHbPDpAhqyoCzP0zFvFvj-iqWZFI2X1x6K6u3dizRi2eWul-mI-aPovkC-PDAZBKpgLMnr1fdz3fV5jRmLjzO0Y2pqqWwZtrQXyirN-mrsUhzEq19UVSYd3qkdQjsYN6LXEHJbADDWZB'

get_user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
# get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
get_user_info_data = {
    'access_token': component_access_token,
    'openid': 'ob8Vy537Y0L0fHztITCKVjP9vf58',
    'lang': 'zh_CN',
}
print('数据get_user_info_data --->>' ,json.dumps(get_user_info_data))


s = requests.session()
s.keep_alive = False  # 关闭多余连接
ret = s.get(get_user_info_url, params=get_user_info_data)

print(ret.json())

get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
get_user_info_data = {
    'access_token': component_access_token,
    'openid': 'ob8Vy537Y0L0fHztITCKVjP9vf58',
    'lang': 'zh_CN',
}

s = requests.session()
s.keep_alive = False  # 关闭多余连接
ret = s.get(get_user_info_url, params=get_user_info_data)
# ret = requests.get(get_user_info_url, params=get_user_info_data)

ret.encoding = 'utf-8'
ret_json = ret.json()
print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', json.dumps(ret_json))