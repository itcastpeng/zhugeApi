# import redis
# rc = redis.StrictRedis(host='redis_host', port=6379,db=8, decode_responses=True)
#
# # rc.set('xxx', 'ddd', 10)
# ret = rc.get('xxx')
# print(ret)
import requests

import json

code = 'vq6XRbGxe60eJJzitVXSRHN3IaPfujZkNgQJRi6H3KQ'

# access_token=''

# get_code_data['code'] = code
# get_code_data['access_token'] = access_token
# code_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
# code_ret = requests.get(code_url, params=get_code_data)
#
# code_ret_json = code_ret.json()
# print('===========【企业微信】 获取 user_ticket 返回:==========>', json.dumps(code_ret_json))


# gettoken_url =  'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
# get_token_data = {
#     'corpid' : 'ww1960d3c6176cbd76' ,
#     'corpsecret':    'iT4riv1UONesI5iSCj_YcTjvAaWAiNV8y9mFYi2eO2o',
# }
#
# get_token_data_ret = requests.get(gettoken_url, params=get_token_data)
#
#
# get_token_data_ret = get_token_data_ret.json()
# print('===========【企业微信】 获取 token 返回:==========>\n', json.dumps(get_token_data_ret))
#
# access_token = get_token_data_ret.get('access_token')
#
# agent_url = 'https://qyapi.weixin.qq.com/cgi-bin/agent/get'
# get_code_data['agentid'] = 1000002
# get_code_data['access_token'] = access_token
#
# code_ret = requests.get(agent_url, params=get_code_data)
# code_ret_json = code_ret.json()
# print('===========【企业微信】 获取 user_ticket 返回:==========>\n', json.dumps(code_ret_json))


# agent_set_url = 'https://qyapi.weixin.qq.com/cgi-bin/agent/set'
#
# home_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?redirect_uri=http://zhugeleida.zhugeyingxiao.com/zhugeleida/qiyeweixin/work_weixin_auth/5&appid=ww407b59110fea55c2&agentid=1000002&scope=snsapi_userinfo&response_type=code#wechat_redirect'
# get_code_data['access_token'] = access_token
# post_data = {
#     'agentid': 1000002,
#     'access_token': access_token,
#     'home_url': home_url,
#
# }
# code_ret = requests.post(agent_set_url, params=get_code_data,data=json.dumps(post_data))
#
# code_ret = code_ret.json()
# print(code_ret)


post_data = {
    "access_token"  : "RWjRc3L6ymjnZ6d7IXtbJizEfrRklrdqe07DuorGdxBKWUqs-1s10Isk_ihzGnRzTQBAeQx5UZ2fxJmq4nddMwaNw6PJJxuyaroEw5c7-zeZicGvrt9xTkqFBNcKqrN-d2ohj1nZjzkqcqbrIl7kPDXKedugTXFxC4RDFjKwGAdPWwAOGn24VfvgI9SFwwCN9vzq7NFWcu4FP-51efyQ_A"
}



access_token = 'VSM-cq9Yki7W1eMGJ7fX1KjYUppbPpg3NzdIYJRb7A3biYj3PdVZCo_ORibgXXxHgqX3YdfQDEXelHkIFwihPy7IxSDM747inr_O6AkzAz3pRS9CAjLmwjmoTXdBB8_-AyWDhdS0d5Xa48rzW4Yu0N7zs8n0ptq9CmF2GDw8YQMObBLs2FFHXkpVH7r04LFIwGAHYUrRTuYn1u5R3_tmdA'

get_code_data = {
    'access_token' : access_token,
    'userid': 'ZhangJu'
}
code_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
code_ret = requests.get(code_url, params=get_code_data)

code_ret_json = code_ret.json()
print('===========【企业微信】 获取 user_ticket 返回:==========>', json.dumps(code_ret_json))
