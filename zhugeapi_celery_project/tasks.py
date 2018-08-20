#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import psutil
import requests
import json


#  小程序访问动作日志的发送到企业微信
@app.task
def user_send_action_log(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_action_log'
    # url = 'http://127.0.0.1:8000/zhugeleida/mycelery/user_send_action_log'
    post_data = {
        'data': data
    }
    print(post_data)
    requests.post(url, data=post_data)


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@app.task
def create_user_or_customer_small_program_qr_code(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
    get_data = {
        'data': data
    }
    print(get_data)

    requests.get(url, params=get_data)

# 发送模板消息。
@app.task
def user_send_template_msg_to_customer(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_template_msg'
    get_data = {
        'data': data
    }
    print(get_data)
    requests.get(url, params=get_data)


@app.task
def kill_phantomjs_process():
    process_name = 'phantomjs'
    pids = psutil.pids()
    for pid in pids:
        # print(pid)
        p = psutil.Process(pid)
        # print(p.name)
        if p.name() == process_name:
            print(pid)
            p.name()




# import datetime
# import psutil
# def kill_phantomjs_process():
#     pids = psutil.pids()
#     for pid in pids:
#         # print(pid)
#         p = psutil.Process(pid)
#         # print(p.name)
#         if p.name() == 'phantomjs':
#             print(pid)
#             import math
#             # from jb51.net
#
#             start_time  =  p.create_time()
#             start_time = str((int(start_time)))
#             create_time_minute = start_time.strftime(start_time)
#
#             # process_name = p.name()
#             now_time_minute = datetime.datetime.strptime("%M", datetime.datetime.now())
#             if now_time_minute == create_time_minute:
#                 continue
#             else:
#                 print('------ kill process_name---->>',p.name(),'|',pid)
#
#
# kill_phantomjs_process()


