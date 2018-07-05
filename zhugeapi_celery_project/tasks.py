#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app

import requests
import json


# 测试任务
@app.task
def user_send_action_log(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_action_log'
    # url = 'http://127.0.0.1:8000/zhugeleida/mycelery/user_send_action_log'
    post_data = {
        'data': data
    }
    print(post_data)
    requests.post(url, data=post_data)




@app.task
def create_user_or_customer_small_program_qr_code(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
    get_data = {
        'data': data
    }
    print(get_data)

    requests.get(url, params=get_data)
