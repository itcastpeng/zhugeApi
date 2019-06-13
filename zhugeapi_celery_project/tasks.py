#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import psutil
import requests
import datetime,time
import psutil
import os
import signal
import json
from zhugeleida.views_dir.public.qiniu_oper import qiniu_get_token, requests_video_download


#  小程序访问动作日志的发送到企业微信
@app.task
def user_send_action_log(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_action_log'
    get_data = data
    print('----------小程序|公招号->访问动作日志的发送应用消息 requests调用 get_data数据 ------------>',json.dumps(get_data))

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)


# 关注发送红包
@app.task
def user_forward_send_activity_redPacket(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_forward_send_activity_redPacket'
    get_data = data
    print('----------[公众号]转发文章后得红包 -->requests调用 get_data数据 ------------>',get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)



# 转发发送红包
@app.task
def user_focus_send_activity_redPacket(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_focus_send_activity_redPacket'
    get_data = data
    print('----------[公众号]关注文章后得红包 -->requests调用 get_data数据 ------------>',get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)


# 公众号第三方平台拉取用户的信息
@app.task
def get_customer_gongzhonghao_userinfo(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/get_customer_gongzhonghao_userinfo'
    get_data = data
    print('----------[公众号] 公众号第三方平台拉取用户的信息 -->requests调用 get_data数据 ------------>', get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)


## 绑定客户和文章的关系
@app.task
def binding_article_customer_relate(data):

    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/binding_article_customer_relate'
    get_data = data
    print('----------[公众号] 绑定客户和文章的关系 -->requests调用 get_data数据 ------------>', get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)
    # requests.get(url, params=get_data)



# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@app.task
def create_user_or_customer_small_program_qr_code(data):
    """
    :param data:    { 'user_id': '', 'customer_id':'' }         user_id 为用户ID    customer_id 为 客户ID
    :return:
    """
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
    get_data = {
        'data': data
    }
    print(get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)



# 企业用户生成小程序海报
@app.task
def create_user_or_customer_small_program_poster(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
    get_data = {
        'data': data
    }
    print(get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)


# 发送模板消息给客户提示。
@app.task
def user_send_template_msg_to_customer(data):
    print("2019-05-15 ------>user_send_template_msg_to_customer ------>", data)
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_template_msg'
    get_data = {
        'data': data
    }
    print('get_data-----------------------------celery AI用户 给小程序客户发送消息-----------------------------')

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)


# 补发活动红包。
@app.task
def bufa_send_activity_redPacket():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bufa_send_activity_redPacket'
    get_data = {

    }

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)



# 发送公众号-模板消息。
@app.task
def user_send_gongzhonghao_template_msg(data):
    print('--- 【公众号发送模板消息】 user_send_gongzhonghao_template_msg --->', data)
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_gongzhonghao_template_msg'
    get_data = data
    print('-----发送公众号-模板消息---->>',get_data)

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)


## 企业微信获取三方通讯录的人员信息
@app.task
def qiyeweixin_user_get_userinfo(data):
    print('--- 【企业微信-获取三方通讯录的人员信息】 --->', data)
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/qiyeweixin_user_get_userinfo'
    get_data = data


    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)


## 定时器杀死phantomjs进程
@app.task
def kill_phantomjs_process():
    pids = psutil.pids()

    for pid in pids:
        # print(pid)
        p = psutil.Process(pid)
        # print(p.name)
        if p.name() == 'phantomjs':
            print(pid)

            start_time  =  p.create_time()
            start_time = int(start_time)
            create_time_minute = time.localtime(start_time).tm_min

            # process_name = p.name()
            now_time = int(time.time())
            now_time_minute = time.localtime(now_time).tm_min
            if now_time_minute == create_time_minute:
                print('------ Lived process_name---->>', p.name(), '|', pid)
                continue
            else:
                print('------ kill process_name---->>',p.name(),'|',pid)
                try:
                    # cmd_name = 'kill -9  %s' % (pid)
                    # os.system(cmd_name)
                    process_ret = os.kill(pid, signal.SIGKILL)
                    print ('---- 已杀死%s pid为%s的进程, 返回值%s----->>' % (p.name(),pid,process_ret))

                except Exception as  e:
                    print ('----- Exception 没有如此进程!!!------>>')


# 【定时器刷新小程序审核状态】获取查询最新一次提交的审核状态并记录到数据库
@app.task
def get_latest_audit_status_and_release_code():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/get_latest_audit_status_and_release_code'
    get_data = {

    }

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url, params=get_data)

    # requests.get(url, params=get_data)

## 定时器生成小程序名片的二维码
@app.task
def crontab_create_user_to_customer_qrCode_poster():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_create_user_to_customer_qrCode_poster'
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.get(url)


## 批量获取图文素材
@app.task
def crontab_batchget_article_material():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_batchget_article_material'
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    s.post(url)

# 关联。
# @app.task
# def celery_addSmallProgram(xiaochengxuid): # 商城基础设置 添加小程序ID
#     if xiaochengxuid:
#         url = 'http://api.zhugeyingxiao.com/zhugeleida/admin/addSmallProgram?xiaochengxuid={}'.format(xiaochengxuid)
#         requests.get(url)


# 商城订单 定时刷新 十分钟未付款自动改状态
@app.task
def mallOrderTimeToRefresh():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/timeToRefresh'
    requests.get(url)

## 关注公众号可获取-重要通知
@app.task
def monitor_send_gzh_template_msg(data):
    print('--- 【公众号-监控发送模板消息数据】 --->', data)
    get_data = data

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/common_send_gzh_template_msg'  # 分页 聊天信息记录
    s.get(url, params=get_data)

# 缓存数据 (redis缓存 雷达AI 消息)
@app.task
def celery_statistical_content():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/celery_statistical_content/leida_redis_contact'
    print('-------------------------------------------雷达celery_____记录雷达AI消息缓存')
    requests.get(url)


# 缓存数据 (redis缓存 后台数据统计 缓存)
@app.task
def celery_data_statistics():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/celery_statistical_content/data_statistics'
    print('-------------------------------------------雷达celery_____记录数据统计缓存')
    requests.get(url)

# 异步下载视频
# @app.task
# def qiniu_celery_upload_video(url, video_path):
#     url = requests_video_download(url)  # 下载到本地
#     print('-----------------------------celery--------------------下载视频=-----------> ', datetime.datetime.today(), url)
#     qiniu_get_token(url, video_path)


# boos 雷达数据统计
@app.task
def data_overview_statistics():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/data_overview_statistics'
    print('-----------------------------------------------boos雷达统计----------------------------> ', datetime.datetime.today())
    requests.post(url)

# 更新文章
@app.task
def celery_regularly_update_articles():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/celery_regularly_update_articles'
    print('------------------------------更新文章-----------------------------> ', datetime.datetime.today())
    requests.get(url)











