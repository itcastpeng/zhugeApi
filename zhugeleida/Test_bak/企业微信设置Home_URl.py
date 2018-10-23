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
    "access_token"  : "oZYz-dDr76AnEQQLHiDwLG29eAYQfJqfpa2EjnOkQ8zTXi7rvaY-mPfKUnqC0gZqdDm-wJ-6u-b1E91Y-1a7bB-wFqNg3gqa81BmFwbJXtiyTnQnV7sylItoVmgcrvGLiUMSuWf2tStqUAJRhLvGqX80la_776VkptqaER5ZStVEwWwOC8IYx5Jg36WrI5dgPoiNyoSdp0T8ExOkMThkLg"

}



access_token = "oZYz-dDr76AnEQQLHiDwLG29eAYQfJqfpa2EjnOkQ8zTXi7rvaY-mPfKUnqC0gZqdDm-wJ-6u-b1E91Y-1a7bB-wFqNg3gqa81BmFwbJXtiyTnQnV7sylItoVmgcrvGLiUMSuWf2tStqUAJRhLvGqX80la_776VkptqaER5ZStVEwWwOC8IYx5Jg36WrI5dgPoiNyoSdp0T8ExOkMThkLg"

get_code_data = {
    'access_token' : access_token,
    'userid': '1539586048417872'
}
code_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
code_ret = requests.get(code_url, params=get_code_data)

code_ret_json = code_ret.json()
print('===========【企业微信】 获取 user_ticket 返回:==========>', json.dumps(code_ret_json))





# _data = {
#     'SuiteId': SuiteId
# }
# create_pre_auth_code_ret = common.create_pre_auth_code(_data)
# suite_access_token = create_pre_auth_code_ret.data.get('suite_access_token')

# get_permanent_code_url_data = {
#     'suite_access_token': 'UaUErizLfeXLVMx2Hy9ZQNfsj4RMvO7x9vrnkXBO8F45XSiz8YFdoCsVAWkjNrjcSJhfExfv5u1uWb2TVM4aYuJERHklh26AwzJFwncREMPC_HYAvR9NQD2Q8UllLrrF'
# }
# post_permanent_code_url_data = {
#     'auth_code': 'eHdVUhDfAduRYjOY4IIyViu06uTVRuuJTLo4vWL1rbOVt8f9-wdEXgetkxd1Xm03YJKErTrVyjs9pIOvBxtE0r5wyi8RcLDaNKwlBs8q_WE'
# }
#
# get_permanent_code_info_ret = requests.post(get_permanent_code_url, params=get_permanent_code_url_data,
#                                             data=json.dumps(post_permanent_code_url_data))
#
# get_permanent_code_info = get_permanent_code_info_ret.json()
# print('-------[企业微信-通讯录] 获取企业永久授权码 返回------->>', json.dumps(get_permanent_code_info))
