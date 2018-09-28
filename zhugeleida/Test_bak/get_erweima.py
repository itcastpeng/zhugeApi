
from publicFunc import Response

import requests
import json
from zhugeleida.views_dir.conf import *
import os

#
# def qr_code_auth():
#
#         get_token_data = {}
#         post_qr_data = {'path': '/', 'width': 430}
#         get_qr_data = {}
#
#         get_token_data['appid'] = Conf['appid']
#         get_token_data['secret'] = Conf['appsecret']
#         get_token_data['grant_type'] = 'client_credential'
#
#         # get 传参 corpid = ID & corpsecret = SECRECT
#         token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
#         token_ret_json = token_ret.json()
#         access_token = token_ret_json['access_token']
#         print('---- access_token --->>',token_ret_json)
#
#         get_qr_data['access_token'] = access_token
#         qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data,data=json.dumps(post_qr_data))
#         print('-------qr_ret---->',qr_ret.text)
#         with open('ewm.jpg', 'wb') as f:
#             f.write(qr_ret.content)
#
#
#
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)
# print ( os.path.join(BASE_DIR, 'statics','zhugeleida') + '\sewm.jpg')
#
#


import datetime


# input datetime1, and an month offset
# return the result datetime

def datetime_offset_by_month(datetime1, n=1):
        # create a shortcut object for one day
        one_day = datetime.timedelta(days=1)

        # first use div and mod to determine year cycle
        q, r = divmod(datetime1.month + n, 12)

        # create a datetime2
        # to be the last day of the target month
        datetime2 = datetime.datetime(
                datetime1.year + q, r + 1, 1) - one_day

        if datetime1.month != (datetime1 + one_day).month:
                return datetime2

        if datetime1.day >= datetime2.day:
                return datetime2


        return datetime2.replace(day=datetime1.day)


d1 = datetime.datetime(2018, 9,7)
d2 = datetime_offset_by_month(d1, 3)

print('----d2------>>',d2)







