#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com


from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import json
import hashlib
import os
from django.views.decorators.csrf import csrf_exempt
import time

import xml.dom.minidom
from publicFunc.Response import ResponseObj
from publicFunc.account import get_token

import datetime
from publicFunc.gongzhonghao_weixin import WeChatPublicSendMsg

from zhugedanao import models


def checkSignature(timestamp, nonce, token, signature):

    tmp_str = "".join(sorted([timestamp, nonce, token]))
    hash_obj = hashlib.sha1()
    hash_obj.update(tmp_str.encode('utf-8'))
    if hash_obj.hexdigest() == signature:
        return True
    else:
        return False


@csrf_exempt
def index(request):
    signature = request.GET.get("signature")
    timestamp = request.GET.get("timestamp")
    nonce = request.GET.get("nonce")
    echostr = request.GET.get("echostr")

    token = 'hfdjsahjklfdhjklhfdkljsa'
    EncodingAESKey = 'LFYzOBp42g5kwgSUWhGC9uRugSmpyetKfAsJa5FdFHX'

    check_result = checkSignature(timestamp, nonce, token, signature)
    print('check_result -->', check_result)

    if check_result:
        we_chat_public_send_msg_obj = WeChatPublicSendMsg()
        if request.method == "GET":
            return HttpResponse(echostr)
        else:
            body_text = str(request.body, encoding="utf8")
            print('body_text -->', body_text)

            # 使用minidom解析器打开 XML 文档
            DOMTree = xml.dom.minidom.parseString(body_text)
            collection = DOMTree.documentElement
            print('collection -->', collection)

            # 事件类型
            event = collection.getElementsByTagName("Event")[0].childNodes[0].data
            print("event -->", event)

            # 用户的 openid
            openid = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data

            wechat_data_path = "webadmin/modules/wechat_data.json"
            # we_chat_public_send_msg_obj = WeChat.WeChatPublicSendMsg(wechat_data_path)

            # 扫描带参数的二维码
            if event in ["subscribe", "SCAN"]:
                # subscribe = 首次关注
                # SCAN = 已关注
                # 事件 Key 值
                event_key = collection.getElementsByTagName("EventKey")[0].childNodes[0].data
                if event == "subscribe":
                    event_key = event_key.split("qrscene_")[-1]
                event_key = json.loads(event_key)
                timestamp = event_key["timestamp"]
                print('event_key -->', event_key)

                # # 保证1个微信只能够关联1个账号
                user_objs = models.zhugedanao_userprofile.objects.filter(openid=openid)
                if user_objs:
                    obj = user_objs[0]
                    print(obj.username)
                    obj.timestamp = timestamp
                    obj.save()
                else:
                    ret_obj = we_chat_public_send_msg_obj.get_user_info(openid=openid)
                    print('ret_obj -->', ret_obj)

                    models.zhugedanao_userprofile.objects.create(
                        openid=openid,
                        token=get_token(timestamp),
                        timestamp=timestamp,
                        sex=ret_obj['sex'],
                        country=ret_obj['country'],
                        province=ret_obj['province'],
                        city=ret_obj['city'],
                        subscribe_time=ret_obj['subscribe_time'],
                        set_avator=ret_obj['headimgurl'],
                        username=ret_obj['nickname'],
                    )


            # 取消关注
            elif event == "unsubscribe":
                models.zhugedanao_userprofile.objects.filter(openid=openid).update(openid=None)

                # we_chat_public_send_msg_obj.sendTempMsg(post_data)

            return HttpResponse("")

    else:
        return HttpResponse(False)


@csrf_exempt
def wechat_login(request):
    response = ResponseObj()
    timestamp = request.POST.get('timestamp')
    user_objs = models.zhugedanao_userprofile.objects.select_related('level_name').filter(timestamp=timestamp)
    if user_objs:
        user_obj = user_objs[0]
        response.code = 200
        response.data = {
            'token': user_obj.token,
            'user_id': user_obj.id,
            'set_avator': user_obj.set_avator,
            'username': user_obj.username,
            'level_name': user_obj.level_name.name
        }
        response.msg = "登录成功"
    else:
        response.code = 405
        response.msg = '扫码登录异常，请重新扫描'

    return JsonResponse(response.__dict__)


# 获取用于登录的微信二维码
def generate_qrcode(request):
    response = ResponseObj()
    we_chat_public_send_msg_obj = WeChatPublicSendMsg()
    timestamp = str(int(time.time() * 1000))
    qc_code_url = we_chat_public_send_msg_obj.generate_qrcode({'timestamp': timestamp})
    print(qc_code_url)

    response.code = 200
    response.data = {
        'qc_code_url': qc_code_url,
        'timestamp': timestamp
    }

    return JsonResponse(response.__dict__)