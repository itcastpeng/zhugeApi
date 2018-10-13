

import sys
from zhugeleida.public.crypto_.WXBizMsgCrypt_qiyeweixin import WXBizMsgCrypt
# from  zhugeleida.views_dir.admin import WXBizMsgCrypt

import xml.etree.cElementTree as ET
import requests

suite_access_token = 'ZxoeGH2TnCQpONXYVVHKBb151LTRc5lle3j1p--aSD4sjjynZHy84FeRWR8JESnHQ4bdX-9jSL4kzQRxrO23wmS6uprpESeXMmORA-utp9Wzdi4u4Svv_LZPu8VOT_wK'

# get_url = 'https://qyapi.weixin.qq.com/cgi-bin/agent/get'
#
#
# get_permanent_code_url_data = {
#     'access_token': suite_access_token,
#     'agentid': 1000007,
# }
# # post_permanent_code_url_data = {
# #     'AuthCode': AuthCode
# # }
#
# get_permanent_code_info_ret = requests.get(get_url, params=get_permanent_code_url_data,
#                                             )
import json
# print(json.dumps(get_permanent_code_info_ret.json()))

get_permanent_code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code'
AuthCode = 'eHdVUhDfAduRYjOY4IIyVvoSS5eU9BfNICf4lFpk3i1UD2ZGsKKtOfmJ7PSLSUQbFmoJsrFmYm2qzI6C-Vx9XtwqPVWaQEes3m2GSd5Xtzc'
get_permanent_code_url_data = {
    'suite_access_token': suite_access_token
}
post_permanent_code_url_data = {
    'auth_code': AuthCode
}

get_permanent_code_info_ret = requests.post(get_permanent_code_url, params=get_permanent_code_url_data,
                                            data=json.dumps(post_permanent_code_url_data))

print(json.dumps(get_permanent_code_info_ret.json()))



