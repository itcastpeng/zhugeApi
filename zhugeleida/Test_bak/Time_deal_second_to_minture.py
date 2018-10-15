

# seconds = 0
# m, s = divmod(seconds, 60)
# h, m = divmod(m, 60)
#
#
#
# if not h and not m and s:
#     print("%s秒" % (s))
# elif  not h  and  m and s:
#     print ("%s分%s秒" % (m, s))
#
# elif  h and m and s:
#     print ("%s时%s分%s秒" % (h, m, s))
import requests

from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import create_authorizer_access_token


_data = {
    'authorizer_appid': 'wxa77213c591897a13',
    'authorizer_refresh_token': 'refreshtoken@@@RAVUheyR510HyjAYrDxgSrX8MHDkbbb5ysHgGRWHeUc',
    'key_name': 'authorizer_access_token_wxa77213c591897a13',
    'app_id': 'wx6ba07e6ddcdc69b3',  # 查看诸葛雷达_公众号的 appid
    'app_secret': '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
}

authorizer_access_token_ret  = create_authorizer_access_token(_data)
authorizer_access_token = authorizer_access_token_ret.data

# access_token = "14_8p_bIh8kVgaZpnn_8IQ3y77mhJcSLoLuxnqtrE-mKYuOfXFPnNYhZAOWk8AZ-NeK6-AthHxolrSOJr1HvlV-gSlspaO0YFYbkPrsjJzKxalWQtlBxX4n-v11mqJElbT0gn3WVo9UO5zQpQMmTDGjAEDZJM"
openid = 'ob5mL1Q4faFlL2Hv2S43XYKbNO-k'

# get_user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
get_user_info_data = {
    'access_token': authorizer_access_token,
    'openid': openid,
    'lang': 'zh_CN',
}
import json
ret = requests.get(get_user_info_url, params=get_user_info_data)
ret.encoding = 'utf-8'
ret_json = ret.json()

print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', json.dumps(ret_json))
