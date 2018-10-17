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
from django.db.models import  Sum
from zhugeleida import models
import json
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import create_authorizer_access_token
from django.db.models import Q
from publicFunc import Response

#  小程序访问动作日志的发送到企业微信
@app.task
def user_send_action_log(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_action_log'
    # url = 'http://127.0.0.1:8000/zhugeleida/mycelery/user_send_action_log'
    post_data = {
        'data': data
    }
    print('----------小程序|公招号->访问动作日志的发送应用消息 requests调用 post_data数据 ------------>',post_data)
    requests.post(url, data=post_data)


# 转发发送红包
@app.task
def user_forward_send_activity_redPacket(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_forward_send_activity_redPacket'
    get_data = data
    print('----------[公众号]转发文章后得红包 -->requests调用 get_data数据 ------------>',get_data)
    requests.get(url, data=get_data)


# 转发发送红包
@app.task
def user_focus_send_activity_redPacket(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_focus_send_activity_redPacket'
    get_data = data
    print('----------[公众号]关注文章后得红包 -->requests调用 get_data数据 ------------>',get_data)
    requests.get(url, data=get_data)



# 公众号第三方平台拉取用户的信息
@app.task
def get_customer_gongzhonghao_userinfo(data):
    authorizer_appid = data.get('authorizer_appid')
    openid = data.get('openid')

    objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=authorizer_appid)
    authorizer_refresh_token = ''
    if objs:
        authorizer_refresh_token = objs[0].authorizer_refresh_token
    key_name = 'authorizer_access_token_%s' % (authorizer_appid)
    _data = {
        'authorizer_appid': authorizer_appid,
        'authorizer_refresh_token': authorizer_refresh_token,
        'key_name': key_name,
        'app_id': 'wx6ba07e6ddcdc69b3',                   # 查看诸葛雷达_公众号的 appid
        'app_secret': '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
    }

    authorizer_access_token_ret = create_authorizer_access_token(_data)
    authorizer_access_token = authorizer_access_token_ret.data

    # access_token = "14_8p_bIh8kVgaZpnn_8IQ3y77mhJcSLoLuxnqtrE-mKYuOfXFPnNYhZAOWk8AZ-NeK6-AthHxolrSOJr1HvlV-gSlspaO0YFYbkPrsjJzKxalWQtlBxX4n-v11mqJElbT0gn3WVo9UO5zQpQMmTDGjAEDZJM"
    # openid = 'ob5mL1Q4faFlL2Hv2S43XYKbNO-k'

    get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
    get_user_info_data = {
        'access_token': authorizer_access_token,
        'openid': openid,
        'lang': 'zh_CN',
    }

    ret = requests.get(get_user_info_url, params=get_user_info_data)
    ret.encoding = 'utf-8'
    ret_json = ret.json()
    print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', json.dumps(ret_json))

    if 'errcode' not in ret_json:
        openid = ret_json['openid']  # 用户唯一标
        subscribe = ret_json['subscribe']  # 值为0时，代表此用户没有关注该公众号

        objs = models.zgld_customer.objects.filter(openid=openid)
        objs.update(
            is_subscribe=subscribe
        )
        print('---------- 公众号-用户创建成功 crete successful openid | subscribe ---->',openid,"|",subscribe)





## 绑定客户和文章的关系
@app.task
def binding_article_customer_relate(data):

    response = Response.ResponseObj()

    article_id = data.get('article_id')    # 公众号文章ID
    customer_id = data.get('customer_id')  # 公众号客户ID
    user_id = data.get('user_id')  # 由哪个雷达用户转发出来,Ta的用户的ID
    level = data.get('level')      # 公众号层级
    parent_id = data.get('pid')    # 所属的父级的客户ID。为空代表第一级。
    company_id = data.get('company_id')    # 所属的父级的客户ID。为空代表第一级。

    q = Q()
    q.add(Q(**{'article_id': article_id}), Q.AND)
    q.add(Q(**{'customer_id': customer_id}), Q.AND)
    q.add(Q(**{'user_id': user_id}), Q.AND)
    q.add(Q(**{'level': level}), Q.AND)

    if parent_id:
        q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
    else:
        q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

    print('------ 绑定文章客户关系 json.dumps(data) ------>>',json.dumps(data))

    article_to_customer_belonger_obj = models.zgld_article_to_customer_belonger.objects.filter(q)

    if article_to_customer_belonger_obj:
        print('------ 文章和客户\雷达用户-关系存在 [zgld_article_to_customer_belonger] ------>>')
        response.code = 302
        response.msg = "文章和客户\雷达用户-关系存在"

    else:
        print('------ [创建]文章和客户\雷达用户关系 ------>')
        models.zgld_article_to_customer_belonger.objects.create(
            article_id=article_id,
            customer_id=customer_id,
            user_id=user_id,
            customer_parent_id=parent_id,
            level=level,
        )

    user_customer_belonger_obj = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,user_id=user_id)
    if user_customer_belonger_obj:
        print('------- [通讯录]关系存在 [zgld_user_customer_belonger]:customer_id|user_id  ------>>',customer_id,"|",user_id)
        response.code = 302
        response.msg = "关系存在"

    else:
        print('------- 创建[通讯录]关系 [zgld_user_customer_belonger]:customer_id|user_id  ------>>', customer_id, "|",
              user_id)
        models.zgld_user_customer_belonger.objects.create(customer_id=customer_id, user_id=user_id,source=4)

    activity_objs = models.zgld_article_activity.objects.filter(article_id=article_id, status=2)
    if activity_objs:
        activity_id = activity_objs[0].id
        print('------ 此文章有活动 article_id：----->',article_id)
        redPacket_objs = models.zgld_activity_redPacket.objects.filter(article_id=article_id,activity_id=activity_id,customer_id=customer_id)

        if redPacket_objs:
            print('----- 活动发红包表数据【存在】 article_id:%s | activity_id:%s | customer_id: %s ----->>' % (article_id,activity_id,customer_id) )
            response.code = 302
            response.msg = "关系存在"

        else:
            print('----- 活动发红包表数据【不存在并创建】 article_id:%s | activity_id:%s | customer_id: %s | company_id: %s ----->>' % (
            article_id, activity_id, customer_id,company_id))

            models.zgld_activity_redPacket.objects.create(article_id=article_id,
                                                          activity_id=activity_id,
                                                          customer_id=customer_id,
                                                          company_id=company_id,
                                                         )
            response.code = 200
            response.msg = "绑定成功"

    return response





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

    requests.get(url, params=get_data)


# 企业用户生成小程序海报
@app.task
def create_user_or_customer_small_program_poster(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
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


# 发送公众号-模板消息。
@app.task
def user_send_gongzhonghao_template_msg(data):
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/user_send_gongzhonghao_template_msg'
    get_data = {
        'data': data
    }
    print('-----发送公众号-模板消息---->>',get_data)
    requests.get(url, params=get_data)





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


# 获取查询最新一次提交的审核状态并记录到数据库
@app.task
def get_latest_audit_status_and_release_code():
    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/get_latest_audit_status_and_release_code'
    get_data = {

    }
    requests.get(url, params=get_data)
@app.task
def celery_addSmallProgram(xiaochengxuid): # 商城基础设置 添加小程序ID
    if xiaochengxuid:
        url = 'http://api.zhugeyingxiao.com/zhugeleida/admin/addSmallProgram?xiaochengxuid={}'.format(xiaochengxuid)
        requests.get(url)
