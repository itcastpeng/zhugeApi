

import sys
from zhugeleida.public.crypto_.WXBizMsgCrypt_qiyeweixin import WXBizMsgCrypt
# from  zhugeleida.views_dir.admin import WXBizMsgCrypt

import xml.etree.cElementTree as ET
import requests

suite_access_token = 'Eh7KjCiXH4ptc2Guifa1Mgj1wO4vxAcJatxBUTpVw6E | FTo7YPixgYQmjZ6LASgC56dYZressEouz7-0Pc8D66DZjJtmldvIK4--f1WRhNN6Dy1N524W840twPG8u2i1D-Tx6CS43K2o0jjbdBQq3RCX5POXI8PdjTwDbhBoAd0S'

get_url = 'https://qyapi.weixin.qq.com/cgi-bin/agent/get'


get_permanent_code_url_data = {
    'access_token': suite_access_token,
    'agentid': 1000007,
}
# post_permanent_code_url_data = {
#     'AuthCode': AuthCode
# }

get_permanent_code_info_ret = requests.get(get_url, params=get_permanent_code_url_data,
                                            )
import json
print(json.dumps(get_permanent_code_info_ret.json()))
