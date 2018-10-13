

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

# get_permanent_code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code'
# AuthCode = 'eHdVUhDfAduRYjOY4IIyVvoSS5eU9BfNICf4lFpk3i1UD2ZGsKKtOfmJ7PSLSUQbFmoJsrFmYm2qzI6C-Vx9XtwqPVWaQEes3m2GSd5Xtzc'
# get_permanent_code_url_data = {
#     'suite_access_token': suite_access_token
# }
# post_permanent_code_url_data = {
#     'auth_code': AuthCode
# }
#
# get_permanent_code_info_ret = requests.post(get_permanent_code_url, params=get_permanent_code_url_data,
#                                             data=json.dumps(post_permanent_code_url_data))
#
# print(json.dumps(get_permanent_code_info_ret.json()))


msg = {'auth_user_info': {'userid': 'ZhangJu', 'avatar': 'http://p.qlogo.cn/bizmail/Tj5TZc6xibicYIiaQm9mghQl5oE5712iaVIBYicEAM0C20zpn8FBZUnXKmQ/0', 'name': '张炬'}, 'expires_in': 7200, 'permanent_code': 'jKrkdJpPrl8MyNQ3WxaegnQGKpk1yI9qylIFP4ZsIoY', 'auth_info': {'agent': [{'square_logo_url': 'https://p.qlogo.cn/bizmail/ibibToKibqoRad1Ntts3b1nYibyIiclNe1k0DAERLqjtXhJx53Zy98KNC7g/0', 'privilege': {'extra_tag': [], 'allow_tag': [], 'level': 1, 'extra_party': [], 'allow_user': [], 'extra_user': [], 'allow_party': [1]}, 'agentid': 1000003, 'name': '雷达AI'}]}, 'access_token': 'G6tw0AYdRThjvOuvY81SPktgE4EikhDXYAS5AMmKndpFSRUWpB6UTk5WUx5KddyGRztGyZY2bLlIqCQpUVRTx3FOryK_WyCUqlBFNSYON9KRN0C7yrFffDp-gtad3kteKBxC__3M5lciFWG_xK0RLEvsKd2MebSdnZpB80D7AH93z0xyE6foP98EVdF67C1zuGXF71ONXhlOvV68sSWbhw', 'auth_corp_info': {'corp_agent_max': 0, 'corp_wxqrcode': 'http://p.qpic.cn/pic_wework/1692194587/0107d40d9a825c336b2246596229053d19d4f58bf3c3dc50/0', 'location': '', 'corp_scale': '201-500人', 'corpid': 'wwf358ba1c3f3560c5', 'corp_sub_industry': '计算机软件/硬件/信息服务', 'verified_end_time': 0, 'corp_name': '医美企业_雷达测试', 'corp_type': 'unverified', 'corp_user_max': 200, 'corp_square_logo_url': 'http://p.qlogo.cn/bizmail/rjFD5BcbWnicFeviaoqM8I96OX7P8QxhwISTNpUPcKpn8uqrN4aibRxeQ/0', 'corp_industry': 'IT服务', 'corp_full_name': '', 'corp_round_logo_url': 'http://p.qpic.cn/pic_wework/3777001839/4046834be7a5f2711feaaa3cc4e691e1bcb1e526cb4544b5/0', 'subject_type': 1}}

print(json.dumps(msg))

