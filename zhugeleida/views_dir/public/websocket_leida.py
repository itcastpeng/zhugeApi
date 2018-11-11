import json
from django.http.response import HttpResponse
from django.shortcuts import render
from dwebsocket import require_websocket, accept_websocket
from zhugeleida import models

from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from zhugeapi_celery_project import tasks
from django.db.models import F
import json
import json
from zhugeleida import models
import base64
from zhugeleida.public.common import action_record
from zhugeleida.forms.xiaochengxu.chat_verify import ChatGetForm as xiaochengxu_ChatGetForm,  ChatPostForm as xiaochengxu_ChatPostForm

from zhugeleida.forms.chat_verify import ChatGetForm as leida_ChatGetForm, ChatPostForm as leida_ChatPostForm
import uwsgi

# @accept_websocket  # 既能接受http也能接受websocket请求
def websocket(request, oper_type):
    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    # if not request.is_websocket():
    #     try:
    #         print('---- request.GET 数据：--->>', request.GET)
    #         message = request.GET['message']
    #         return HttpResponse(message)
    #
    #     except Exception as e:
    #         print('---- 报错: e--->>', e)
    #         return HttpResponse('链接-->')

    if oper_type == 'leida':

        redis_user_id_key = ''
        user_id = ''
        customer_id = ''
        uwsgi.websocket_handshake()

        while True:

            redis_user_id_key = rc.rpop(redis_user_id_key)
            if redis_user_id_key:
                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    is_user_new_msg=True
                ).order_by('-create_date')

                ret_data_list = []
                count = objs.count()
                if objs:
                    for obj in objs:

                        customer_name = base64.b64decode(obj.customer.username)
                        customer_name = str(customer_name, 'utf-8')
                        content = obj.content

                        if not content:
                            continue

                        is_customer_new_msg = obj.is_customer_new_msg
                        if is_customer_new_msg:  # 为True时
                            is_customer_already_read = 0  # 未读
                            is_customer_already_read_text = '未读'
                        else:
                            is_customer_already_read = 1  # 已读
                            is_customer_already_read_text = '已读'

                        _content = json.loads(content)
                        info_type = _content.get('info_type')
                        if info_type:
                            info_type = int(info_type)

                            if info_type == 1:
                                msg = _content.get('msg')
                                msg = base64.b64decode(msg)
                                msg = str(msg, 'utf-8')
                                _content['msg'] = msg

                        base_info_dict = {
                            'customer_id': obj.customer_id,
                            'customer_avatar': obj.customer.headimgurl,
                            'user_id': obj.userprofile_id,
                            'src': obj.customer.headimgurl,
                            'name': customer_name,
                            'dateTime': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'send_type': obj.send_type,
                            'is_customer_already_read': is_customer_already_read,
                            'is_customer_already_read_text': is_customer_already_read_text
                        }
                        base_info_dict.update(_content)
                        ret_data_list.append(base_info_dict)

                    print('--- list(msg_obj) -->>', ret_data_list)
                    ret_data_list.reverse()
                    response_data = {
                        'data' : {
                            'ret_data': ret_data_list,
                            'count': count
                        },
                        'msg' : '实时推送雷达-最新聊天信息成功',
                        'code': 200
                    }

                    objs.update(
                        is_user_new_msg=False
                    )

                    print('------ 有新消息, 实时推送给【雷达用户】 的数据：---->', response_data)
                    uwsgi.websocket_send(json.dumps(response_data))

            # if request.websocket.count_messages() > 0:
            #     for data in request.websocket:

                    # print('request.websocket._get_new_messages() -->', request.websocket._get_new_messages())
                    # if request.websocket.is_closed():
                    #     print('--- 雷达-连接关闭 --->')
                    #     return HttpResponse('--- 连接断开 ---->>')
                    #
                    # else:
            else:
                # data = uwsgi.websocket_recv()
                data = uwsgi.websocket_recv_nb()
                print('------[雷达用户-非阻塞] websocket_recv_nb ----->>',data)
                if not data:
                    continue

                _data = json.loads(data)
                print('--- 【雷达用户】发送过来的 数据: --->>', _data)

                user_id = _data.get('user_id')
                customer_id = _data.get('customer_id')
                Content = _data.get('content')

                redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)

                forms_obj = leida_ChatPostForm(_data)

                if forms_obj.is_valid():

                    # data = request.POST.copy()
                    # user_id = int(data.get('user_id'))
                    # customer_id = int(data.get('customer_id'))
                    # Content = data.get('content')
                    # send_type = int(data.get('send_type'))

                    flow_up_obj = models.zgld_user_customer_belonger.objects.select_related('user',
                                                                                            'customer').filter(
                        user_id=user_id, customer_id=customer_id)

                    if flow_up_obj:  # 用戶發消息給客戶，修改最後跟進-時間
                        flow_up_obj.update(
                            is_user_msg_num=F('is_user_msg_num') + 1,
                            last_follow_time=datetime.datetime.now()
                        )

                    _content = json.loads(Content)
                    info_type = _content.get('info_type')
                    content = ''
                    msg = ''
                    if info_type:
                        info_type = int(info_type)
                        if info_type == 1:
                            msg = _content.get('msg')
                            encodestr = base64.b64encode(msg.encode('utf-8'))
                            msg = str(encodestr, 'utf-8')
                            _content['msg'] = msg
                            content = json.dumps(_content)

                        elif info_type == 3:
                            msg = '您好,请问能否告诉我您的手机号?'
                            _content['msg'] = msg
                            content = json.dumps(_content)

                    models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                        is_last_msg=True).update(is_last_msg=False)
                    obj = models.zgld_chatinfo.objects.create(
                        content=content,
                        userprofile_id=user_id,
                        customer_id=customer_id,
                        send_type=1
                    )

                    user_type = obj.customer.user_type

                    if  user_type == 2 and customer_id and user_id:
                        _data['customer_id'] = customer_id
                        _data['user_id'] = user_id
                        tasks.user_send_template_msg_to_customer.delay(json.dumps(_data))  # 发送【小程序】模板消息

                    elif user_type == 1 and customer_id and user_id:
                        print('--- 【公众号发送模板消息】 user_send_gongzhonghao_template_msg --->')
                        _data['customer_id'] = customer_id
                        _data['user_id'] = user_id
                        # data['type'] = 'gongzhonghao_template_chat'
                        _data['type'] = 'gongzhonghao_send_kefu_msg'
                        _data['content'] = Content
                        tasks.user_send_gongzhonghao_template_msg.delay(data)  # 发送【公众号发送模板消息】

                    rc.lpush(redis_user_id_key, msg)
                    rc.lpush(redis_customer_id_key, msg)
                    # uwsgi.websocket_send( json.dumps({'code':200,'msg': "雷达消息-发送成功"}))
                    print('---- 雷达消息-发送成功 --->>', '雷达消息-发送成功')
                    uwsgi.websocket_send(json.dumps({'code':200,'msg': "雷达消息-发送成功"}))


                else:
                    if not  user_id or not customer_id:

                        ret_data = {
                            'code' : 401,
                            'msg' : 'user_id和uid不能为空,终止连接'
                        }
                        # uwsgi.websocket_send(json.dumps(ret_data))
                        uwsgi.websocket_send(json.dumps(ret_data))
                        return HttpResponse('user_id和uid不能为空,终止连接')
                    # elif not Content:
                    #     ret_data = {
                    #         'code': 402,
                    #         'msg': 'content字段内容不能为空'
                    #     }
                    #     uwsgi.websocket_send(json.dumps(ret_data))
                    # break

            # else:



    elif oper_type == 'xiaochengxu':

        redis_customer_id_key = ''
        user_id = ''
        customer_id = ''
        uwsgi.websocket_handshake()
        while True:

            redis_customer_id_key = rc.rpop(redis_customer_id_key)
            if redis_customer_id_key:

                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    is_customer_new_msg=True
                ).order_by('-create_date')

                ret_data_list = []
                count = objs.count()
                if objs:
                    for obj in objs:

                        mingpian_avatar_obj = models.zgld_user_photo.objects.filter(user_id=user_id,
                                                                                    photo_type=2).order_by(
                            '-create_date')

                        if mingpian_avatar_obj:
                            mingpian_avatar = mingpian_avatar_obj[0].photo_url
                        else:

                            mingpian_avatar = obj.userprofile.avatar

                        customer_name = base64.b64decode(obj.customer.username)
                        customer_name = str(customer_name, 'utf-8')

                        content = obj.content
                        if not content:
                            continue
                        _content = json.loads(content)
                        info_type = _content.get('info_type')
                        if info_type:
                            info_type = int(info_type)

                            if info_type == 1:
                                msg = _content.get('msg')
                                msg = base64.b64decode(msg)
                                msg = str(msg, 'utf-8')
                                _content['msg'] = msg

                        base_info_dict = {
                            'customer_id': obj.customer_id,
                            'user_id': obj.userprofile_id,
                            'user_avatar': mingpian_avatar,
                            'customer_headimgurl': obj.customer.headimgurl,
                            'customer': customer_name,
                            'dateTime': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'send_type': obj.send_type,  # (1, 'user_to_customer'),  (2, 'customer_to_user')
                            'is_first_info': False,  # 是否为第一条的信息
                            # 'info_type': obj.info_type, # 消息的类型
                        }

                        base_info_dict.update(_content)

                        ret_data_list.append(base_info_dict)

                    ret_data_list.reverse()
                    # response.code = 200
                    # response.msg = '实时获取-最新聊天信息成功'
                    print('--- list(msg_obj) -->>', ret_data_list)

                    response_data = {
                        'data': {
                            'ret_data': ret_data_list,
                            'data_count': count,
                        },
                        'code': 200,
                        'msg': '实时推送小程序-最新聊天信息成功',
                    }

                    objs.update(
                        is_customer_new_msg=False
                    )

                    print('------ 有新消息,实时推送给【小程序】 的数据：---->', response_data)
                    uwsgi.websocket_send(json.dumps(response_data))

            else:
                # data = uwsgi.websocket_recv()
                data = uwsgi.websocket_recv_nb()
                print('------[小程序-非阻塞] websocket_recv_nb ----->>', data)
                if not data:
                    continue


                _data = json.loads(data.decode())
                print('------ 【小程序】发送过来的 数据:  ----->>', _data)

                customer_id = _data.get('user_id')
                user_id = _data.get('u_id')
                Content = _data.get('content')


                redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)

                forms_obj = xiaochengxu_ChatPostForm(_data)
                if forms_obj.is_valid():

                    # customer_id = int(request.GET.get('user_id'))
                    # user_id = request.POST.get('u_id')
                    # content = request.POST.get('content')
                    # send_type = int(request.POST.get('send_type'))

                    models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                        is_last_msg=True).update(
                        is_last_msg=False)  # 把所有的重置为不是最后一条

                    _content = json.loads(Content)
                    info_type = _content.get('info_type')
                    _msg = ''
                    content = ''
                    msg = ''
                    if info_type:
                        info_type = int(info_type)

                        if info_type == 1:
                            _msg = _content.get('msg')
                            encodestr = base64.b64encode(_msg.encode('utf-8'))
                            msg = str(encodestr, 'utf-8')
                            _content['msg'] = msg
                            content = json.dumps(_content)

                    models.zgld_chatinfo.objects.create(
                        content=content,
                        userprofile_id=user_id,
                        customer_id=customer_id,
                        send_type=2
                    )

                    flow_up_objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id,
                                                                                     customer_id=customer_id)
                    if flow_up_objs:  # 用戶發消息給客戶，修改最後跟進-時間
                        flow_up_objs.update(
                            is_customer_msg_num=F('is_customer_msg_num') + 1,
                            last_activity_time=datetime.datetime.now()
                        )

                    if info_type == 1:  # 发送的图文消息
                        remark = ':%s' % (_msg)
                        _data['action'] = 0  # 代表用客户咨询产品
                        _data['uid'] = user_id
                        action_record(_data, remark)

                    rc.lpush(redis_user_id_key, msg)
                    rc.lpush(redis_customer_id_key, msg)
                    print('----- redis_customer_id_key --->',redis_customer_id_key)
                    uwsgi.websocket_send(json.dumps({'code': 200, 'msg': "小程序消息-发送成功"}))


                else:

                    if not user_id or not customer_id:
                        ret_data = {
                            'code': 401,
                            'msg': 'user_id和uid不能为空,终止连接'
                        }
                        uwsgi.websocket_send(json.dumps(ret_data))
                        # request.websocket.close()
                        return HttpResponse('user_id和uid不能为空,终止连接')


            # else:



    if  oper_type == 'chat':

            """接受websocket传递过来的信息"""
            uwsgi.websocket_handshake()
            uwsgi.websocket_send("你还，很高心为你服务")

            while True:
                msg = uwsgi.websocket_recv()
                msg = msg.decode()
                data = json.loads(msg)
                data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                print('----- websocket_recv ---->>>',data)


                uwsgi.websocket_send(data["text"])
