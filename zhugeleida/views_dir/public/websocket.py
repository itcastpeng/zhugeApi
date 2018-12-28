import json
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from django.http import JsonResponse, HttpResponse
from publicFunc import deal_time
import time
import datetime
from zhugeapi_celery_project import tasks
from django.db.models import F
import json
import json
from zhugeleida import models
import base64
from zhugeleida.public.common import action_record
from zhugeleida.forms.xiaochengxu.chat_verify import ChatGetForm as xiaochengxu_ChatGetForm, \
    ChatPostForm as xiaochengxu_ChatPostForm
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc import account
from zhugeleida.forms.chat_verify import LeidaQueryChatPostForm , ChatPostForm as leida_ChatPostForm
try:
    import uwsgi
except ImportError as e:
    pass

import redis


def leida_websocket(request, oper_type):

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    # 雷达聊天
    if oper_type == 'leida_chat':

        redis_user_id_key = ''
        redis_customer_id_key = ''
        redis_user_query_info_key = ''
        user_id = ''
        customer_id = ''
        uwsgi.websocket_handshake()

        while True:

            redis_user_id_key_flag = rc.get(redis_user_id_key)
            redis_customer_id_flag = rc.get(redis_customer_id_key) # 判断 小程序是否已读了
            if user_id:
                rc.set(redis_user_query_info_key, False)

            print('---- 雷达 Flag 循环  uid: %s | customer_id: %s --->>',user_id,customer_id)
            if redis_user_id_key_flag == 'True' and user_id and customer_id:
                print('---- 雷达 Flag 为真 --->>', redis_user_id_key_flag)
                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    is_user_new_msg=True
                ).order_by('-create_date')

                ret_data_list = []
                count = objs.count()
                if objs:

                    for obj in objs:

                        customer_id = obj.customer_id
                        customer_username = obj.customer.username
                        customer_name = conversion_base64_customer_username_base64(customer_username, customer_id)
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
                        'data': {
                            'ret_data': ret_data_list,
                            'count': count
                        },
                        'msg': '实时推送雷达-最新聊天信息成功',
                        'code': 200
                    }

                    print('------ 有新消息, 实时推送给【雷达用户】 的数据：---->', response_data)
                    uwsgi.websocket_send(json.dumps(response_data))

                    ## 发送成功 修改 数据库状态值
                    objs.update(
                        is_user_new_msg=False
                    )
                    rc.set(redis_user_id_key, False)

            if redis_customer_id_flag == 'False' and user_id and customer_id:

                response_data = {
                    'data': {
                        'is_customer_already_read' : 1  # 1已读  0未读
                    },
                    'msg': '实时通知小程序新消息-已读通知',
                    'code': 202
                }
                print('------ 小程序新消息-已读, 实时推送给【雷达用户】 flag：---->', response_data)
                uwsgi.websocket_send(json.dumps(response_data))

                rc.set(redis_customer_id_key, 'Stop')


            else:
                try:
                    # data = uwsgi.websocket_recv()
                    data = uwsgi.websocket_recv_nb()
                    # print('------[雷达用户-非阻塞] websocket_recv_nb ----->>',data)

                    if not data:
                        time.sleep(0.2)
                        continue

                    _data = json.loads(data.decode('utf-8'))
                    print('--- 【雷达用户】发送过来的 数据: --->>', _data)

                    login_flag = account.socket_is_token(models.zgld_userprofile,_data)

                    if login_flag: #验证登录成功
                        type = _data.get('type')
                        user_id = _data.get('user_id')
                        customer_id = _data.get('customer_id')
                        Content = _data.get('content')

                        redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                        redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)
                        # redis_customer_query_info_key = 'message_customer_id_{cid}_info_num'.format(cid=customer_id)
                        redis_user_query_info_key = 'message_user_id_{uid}_info_num'.format(uid=user_id)

                        if type == 'register':
                            continue

                        elif type == 'closed':

                            ret_data = {
                                'code': 200,
                                'msg': '确认关闭 uid:%s | customer_id: %s' %(user_id,customer_id)
                            }
                            # uwsgi.websocket_send(json.dumps(ret_data))
                            return JsonResponse(ret_data)

                        forms_obj = leida_ChatPostForm(_data)
                        if not forms_obj.is_valid():

                            ret_data = {
                                'code': 401,
                                'msg': 'user_id和uid不能为空,终止连接'
                            }
                            # uwsgi.websocket_send(json.dumps(ret_data))
                            uwsgi.websocket_send(json.dumps(ret_data))
                            # return HttpResponse('user_id和uid不能为空,终止连接')
                            return JsonResponse(ret_data)

                    else:
                        ret_data = {
                            'code': 400,
                            'msg': '雷达token验证未通过'
                        }
                        print('----  【雷达验证未通过】 终止连接 uid  | customer_id --->>', user_id, customer_id,_data)
                        uwsgi.websocket_send(json.dumps(ret_data))
                        break


                except Exception as  e:
                    ret_data = {
                        'code': 400,
                        'msg': '报错:%s 终止连接' % (e)
                    }

                    print('----  报错:%s [雷达] 终止连接 uid  | customer_id --->>' % e,user_id, customer_id)
                    uwsgi.websocket_send(json.dumps(ret_data))
                    break
                    # return JsonResponse(ret_data)

    # 雷达获取消息未读数量
    elif oper_type == 'leida_query_info_num':
        redis_user_query_info_key = ''
        user_id = ''
        # customer_id = ''

        uwsgi.websocket_handshake()
        while True:

            redis_user_query_info_key_flag = rc.get(redis_user_query_info_key)
            print('---- 雷达【消息数量】 循环 | uid: %s --->>' % str(user_id))
            if redis_user_query_info_key_flag == 'True':
                print('---- 雷达【消息数量】 Flag 为 True  --->>', redis_user_query_info_key_flag)

                contact_data = {
                    'user_id' : user_id
                }
                chatinfo_count = query_info_num_list(contact_data)

                response_data = {
                    'data': {
                        'unread_msg_num': chatinfo_count,
                    },
                    'code': 200,
                    'msg': '实时获取雷达【消息数量】成功',
                }

                print('------ 有新消息, 实时推送给【雷达】 的数据：---->', response_data)
                uwsgi.websocket_send(json.dumps(response_data))
                rc.set(redis_user_query_info_key, False)

            else:
                try:
                    # data = uwsgi.websocket_recv()
                    data = uwsgi.websocket_recv_nb()

                    print('------[雷达【消息数量】-非阻塞] websocket_recv_nb ----->>', data)
                    if not data:
                        time.sleep(1)
                        continue

                    _data = json.loads(data.decode("utf-8"))
                    print('------ 【雷达-【消息数量】】发送过来的 数据:  ----->>', _data)

                    login_flag = account.socket_is_token(models.zgld_userprofile,_data)

                    if login_flag:
                        type = _data.get('type')
                        user_id = _data.get('user_id')
                        # customer_id = _data.get('customer_i、d')


                        forms_obj = LeidaQueryChatPostForm(_data)
                        if  forms_obj.is_valid():
                            # redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                            redis_user_query_info_key = 'message_user_id_{uid}_info_num'.format(uid=user_id)

                            if type  == 'register':

                                chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, send_type=2,
                                                                                     is_user_new_msg=True).count()

                                response_data = {
                                    'data': {
                                        # 'data_count' : contact_num,
                                        'unread_msg_num': chatinfo_count
                                    },
                                    'code': 200,
                                    'msg': '注册成功返回【消息数量】成功',
                                }
                                print('------ 注册成功返回【消息数量】成功---->', response_data)
                                uwsgi.websocket_send(json.dumps(response_data))

                            elif  type == 'query_num':

                                contact_data = {
                                    'user_id': user_id
                                }
                                chatinfo_count = query_info_num_list(contact_data)

                                response_data = {
                                    'data': {
                                        'unread_msg_num': chatinfo_count,
                                    },
                                    'code': 200,
                                    'msg': '实时获取雷达【消息数量】成功',
                                }
                                print('------ 分页获取获取雷达【消息数量】成功---->', response_data)
                                uwsgi.websocket_send(json.dumps(response_data))

                            elif type == 'closed':
                                msg = '确认关闭  customer_id | uid | ' + "|" + str(user_id)
                                ret_data = {
                                    'code': 200,
                                    'msg': msg
                                }
                                # uwsgi.websocket_send(json.dumps(ret_data))
                                return JsonResponse(ret_data)


                        else:
                            if not user_id:
                                ret_data = {
                                    'code': 401,
                                    'msg': 'user_id和uid不能为空,终止连接'
                                }
                                uwsgi.websocket_send(json.dumps(ret_data))
                                return JsonResponse(ret_data)

                    else:
                        ret_data = {
                            'code': 400,
                            'msg': '雷达token验证未通过'
                        }

                        print('----  【雷达验证未通过】 终止连接 uid  | customer_id --->>', user_id,_data)
                        uwsgi.websocket_send(json.dumps(ret_data))

                        return JsonResponse(ret_data)

                except Exception as  e:
                    ret_data = {
                        'code': 400,
                        'msg': '报错:%s 终止连接' % (e)
                    }
                    print('----  报错:%s [雷达] 终止连接 customer_id | user_id --->>' % e , str(user_id))

                    return JsonResponse(ret_data)

    # 雷达获取消息列表
    elif oper_type == 'leida_query_contact_list':
        redis_user_query_contact_key = ''
        user_id = ''

        uwsgi.websocket_handshake()
        while True:

            redis_user_query_contact_key_flag = rc.get(redis_user_query_contact_key)
            print('---- 雷达【消息列表】 循环 | uid: %s --->>' % str(user_id))
            if redis_user_query_contact_key_flag == 'True':
                print('---- 雷达【消息列表】 Flag 为 True  --->>', redis_user_query_contact_key_flag)

                contact_data = {
                    'current_page': 1,
                    'length': 10,
                    'user_id': user_id
                }
                ret_data_list, chatinfo_count = query_contact_list(contact_data)

                response_data = {
                    'data': {
                        'ret_data': ret_data_list,
                        'unread_msg_num': chatinfo_count,
                    },
                    'code': 200,
                    'msg': '实时获取雷达【消息数量】成功',
                }


                print('------ 有新消息, 实时推送给【雷达 消息列表】 的数据：---->', response_data)
                uwsgi.websocket_send(json.dumps(response_data))
                rc.set(redis_user_query_contact_key, False)

            else:
                try:
                    # data = uwsgi.websocket_recv()
                    data = uwsgi.websocket_recv_nb()

                    print('------[雷达【消息列表】-非阻塞] websocket_recv_nb ----->>', data)
                    if not data:
                        time.sleep(1)
                        continue

                    _data = json.loads(data.decode("utf-8"))
                    print('------ 【雷达-【消息列表】】发送过来的 数据:  ----->>', _data)

                    login_flag = account.socket_is_token(models.zgld_userprofile, _data)

                    if login_flag:

                        type = _data.get('type')
                        user_id = _data.get('user_id')

                        forms_obj = LeidaQueryChatPostForm(_data)
                        if forms_obj.is_valid():
                            # redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                            redis_user_query_contact_key = 'message_user_id_{uid}_contact_list'.format(uid=user_id)

                            if type == 'register':

                                chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, send_type=2,
                                                                                     is_user_new_msg=True).count()

                                response_data = {
                                    'data': {
                                        # 'data_count' : contact_num,
                                        'unread_msg_num': chatinfo_count
                                    },
                                    'code': 200,
                                    'msg': '注册成功返回【消息数量】成功',
                                }
                                print('------ 注册成功返回【消息数量】成功---->', response_data)
                                uwsgi.websocket_send(json.dumps(response_data))

                            elif type == 'query_num':
                                current_page = forms_obj.cleaned_data['current_page']
                                length = forms_obj.cleaned_data['length']

                                contact_data = {
                                    'current_page': current_page,
                                    'length': length,
                                    'user_id': user_id
                                }
                                print('----- 数据 contact_data---->>', contact_data)
                                ret_data_list, chatinfo_count = query_contact_list(contact_data)

                                response_data = {
                                    'data': {
                                        # 'data_count' : contact_num,
                                        'ret_data': ret_data_list,
                                        'unread_msg_num': chatinfo_count,
                                    },
                                    'code': 200,
                                    'msg': '实时获取雷达【消息数量】成功',
                                }
                                print('------ 分页获取获取雷达【消息数量】成功---->', response_data)
                                uwsgi.websocket_send(json.dumps(response_data))

                            elif type == 'closed':
                                msg = '确认关闭  customer_id | uid | ' + "|" + str(user_id)
                                ret_data = {
                                    'code': 200,
                                    'msg': msg
                                }
                                # uwsgi.websocket_send(json.dumps(ret_data))
                                return JsonResponse(ret_data)


                        else:
                            if not user_id:
                                ret_data = {
                                    'code': 401,
                                    'msg': 'user_id和uid不能为空,终止连接'
                                }
                                uwsgi.websocket_send(json.dumps(ret_data))
                                return JsonResponse(ret_data)

                    else:
                        ret_data = {
                            'code': 400,
                            'msg': '雷达token验证未通过'
                        }

                        print('----  【雷达验证未通过】 终止连接 uid  | customer_id --->>', user_id)
                        uwsgi.websocket_send(json.dumps(ret_data))

                        return JsonResponse(ret_data)


                except Exception as  e:
                    ret_data = {
                        'code': 400,
                        'msg': '报错:%s 终止连接' % (e)
                    }
                    print('----  报错:%s [小程序] 终止连接 customer_id | user_id --->>' % e, str(user_id))
                    uwsgi.websocket_send(json.dumps(ret_data))

                    return JsonResponse(ret_data)




# @csrf_exempt
# @account.is_token(models.zgld_customer)
def xiaochengxu_websocket(request, oper_type):

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    # 小程序 实时聊天
    if oper_type == 'xiaochengxu_chat':

        redis_customer_id_key = ''
        customer_id_position_key = ''
        user_id = ''
        customer_id = ''
        phone_flag = 0
        uwsgi.websocket_handshake()
        while True:

            redis_customer_id_key_flag = rc.get(redis_customer_id_key)
            print('---- 小程序 循环 customer_id: %s | uid: %s --->>' % (str(customer_id), str(user_id)),redis_customer_id_key_flag)
            if redis_customer_id_key_flag == 'True' and user_id and customer_id:
                print('---- 小程序 Flag 为 True  --->>', redis_customer_id_key_flag)
                print('---- 【小程序】 user_id | customer_id ------>>',customer_id,user_id)


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


                        customer_id = obj.customer_id
                        customer_username =obj.customer.username
                        print('----- Socket 客户姓名：---->>>',customer_username,"|",customer_id)
                        customer_name = conversion_base64_customer_username_base64(customer_username, customer_id)

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

                    customer_id_position_key_flag = rc.get(customer_id_position_key)


                    chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id,
                                                                         customer_id=customer_id, send_type=1,
                                                                         is_customer_new_msg=True).count()


                    response_data = {
                        'data': {
                            'ret_data': ret_data_list,
                            'count': count,
                            'unread_msg_num': chatinfo_count # 未读消息
                        },
                        'code': 200,
                        'msg': '实时推送小程序-最新聊天信息成功',
                    }


                    print('------ 有新消息, 实时推送给【小程序】 的数据：---->', response_data)
                    uwsgi.websocket_send(json.dumps(response_data))

                    print('--- list(msg_obj) -->>', ret_data_list)
                    if customer_id_position_key_flag == 'input':
                        objs.update(
                            is_customer_new_msg=False
                        )
                    rc.set(redis_customer_id_key, False)

            else:
                try:
                    # data = uwsgi.websocket_recv()
                    data = uwsgi.websocket_recv_nb()

                    print('------[小程序-非阻塞] websocket_recv_nb ----->>', data)
                    if not data:
                        time.sleep(0.2)
                        continue

                    _data = json.loads(data.decode("utf-8"))
                    print('------ 【小程序】发送过来的 数据:  ----->>', _data)

                    login_flag = account.socket_is_token(models.zgld_customer, _data)

                    if login_flag:

                        type = _data.get('type')
                        customer_id = _data.get('user_id')
                        user_id = _data.get('u_id')
                        Content = _data.get('content')

                        forms_obj = xiaochengxu_ChatPostForm(_data)
                        if forms_obj.is_valid():


                            redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)
                            customer_id_position_key = 'customer_id_{cid}_position'.format(cid=customer_id)  # 小程序 在聊天还是聊天页外面

                            if  type == 'query_num':

                                phone = ''
                                if phone_flag < 3:
                                    _customer_objs = models.zgld_customer.objects.filter(id=customer_id)
                                    if _customer_objs:
                                        phone =  _customer_objs[0].phone
                                        phone_flag = phone_flag + 1

                                chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id,
                                                                                     customer_id=customer_id, send_type=1,
                                                                                     is_customer_new_msg=True).count()

                                response_data = {

                                    'data': {
                                        'unread_msg_num': chatinfo_count  # 未读消息
                                    },
                                    'phone': phone,
                                    'code': 200,
                                    'msg': '查询成功-获取聊天数量',
                                }

                                uwsgi.websocket_send(json.dumps(response_data))
                                rc.set(customer_id_position_key, 'output')
                                continue

                            elif type == 'lived':
                                response_data = {
                                    'code': 270,
                                    'msg': '为了新中国的胜利向我开炮',
                                }
                                print('------ 注册成功返回【消息数量】成功---->', response_data)
                                uwsgi.websocket_send(json.dumps(response_data))
                                continue

                            elif  type == 'register': # 当进入聊天页面时

                                response_data = {
                                    'code': 200,
                                    'msg': '注册成功',
                                }
                                print('------ 注册成功返回【消息数量】成功---->', response_data)
                                uwsgi.websocket_send(json.dumps(response_data))
                                rc.set(customer_id_position_key, 'input')
                                continue

                            elif type == 'closed':
                                msg = '确认关闭  customer_id | uid | ' + str(customer_id) + "|" + str(user_id)
                                ret_data = {
                                    'code': 200,
                                    'msg': msg
                                }

                                return JsonResponse(ret_data)


                            # redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                            # redis_user_query_info_key = 'message_user_id_{uid}_info_num'.format(uid=user_id) # 小程序发过去消息,雷达用户的key 消息数量发生变化
                            # redis_user_query_contact_key = 'message_user_id_{uid}_contact_list'.format(uid=user_id)  # 小程序发过去消息,雷达用户的key 消息列表发生变化
                            # uwsgi.websocket_send(json.dumps({'code': 200, 'msg': "小程序消息-发送成功"}))
                            #
                            # models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                            #                                     is_last_msg=True).update(
                            #     is_last_msg=False)  # 把所有的重置为不是最后一条
                            #
                            # _content = json.loads(Content)
                            # info_type = _content.get('info_type')
                            # _msg = ''
                            # content = ''
                            #
                            # if info_type:
                            #     info_type = int(info_type)
                            #
                            #     if info_type == 1:
                            #         _msg = _content.get('msg')
                            #         encodestr = base64.b64encode(_msg.encode('utf-8'))
                            #         msg = str(encodestr, 'utf-8')
                            #         _content['msg'] = msg
                            #         content = json.dumps(_content)
                            #
                            # models.zgld_chatinfo.objects.create(
                            #     content=content,
                            #     userprofile_id=user_id,
                            #     customer_id=customer_id,
                            #     send_type=2
                            # )
                            #
                            # flow_up_objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id,
                            #                                                                  customer_id=customer_id)
                            # if flow_up_objs:  # 用戶發消息給客戶，修改最後跟進-時間
                            #     flow_up_objs.update(
                            #         is_customer_msg_num=F('is_customer_msg_num') + 1,
                            #         last_activity_time=datetime.datetime.now()
                            #     )
                            #
                            # if info_type == 1:  # 发送的图文消息
                            #     remark = ':%s' % (_msg)
                            #     _data['action'] = 0  # 代表用客户咨询产品或者发送聊天信息,不记录到日志中。只进行雷达提示
                            #     _data['uid'] = user_id
                            #     action_record(_data, remark)
                            #
                            # rc.set(redis_user_id_key, True)
                            # rc.set(redis_customer_id_key, True)
                            # rc.set(redis_user_query_info_key, True)     # 代表 雷达用户 消息数量发生了变化
                            # rc.set(redis_user_query_contact_key, True)  # 代表 雷达用户 消息列表的数量发生了变化


                        else:

                            if not user_id or not customer_id:
                                ret_data = {
                                    'code': 401,
                                    'msg': 'user_id和uid不能为空,终止连接'
                                }
                                uwsgi.websocket_send(json.dumps(ret_data))

                                return JsonResponse(ret_data)

                    else:
                        ret_data = {
                            'code': 400,
                            'msg': '小程序token验证未通过'
                        }

                        print('----  【小程序验证未通过】 终止连接 uid  | customer_id --->>', user_id, customer_id, _data)
                        uwsgi.websocket_send(json.dumps(ret_data))

                        return JsonResponse(ret_data)



                except Exception as  e:
                    ret_data = {
                        'code': 400,
                        'msg': '报错:%s 终止连接' % (e)
                    }
                    print('----  报错:%s [小程序] 终止连接 customer_id | user_id --->>' % e,str(customer_id), str(user_id))
                    uwsgi.websocket_send(json.dumps(ret_data))

                    return JsonResponse(ret_data)

    # 暂时废弃.等等再删
    elif oper_type == 'xiaochengxu_query_info_num':

        redis_customer_query_info_key = ''
        user_id = ''
        customer_id = ''

        uwsgi.websocket_handshake()
        while True:
            try:
                redis_customer_query_info_key_flag = rc.get(redis_customer_query_info_key)
                print('---- 小程序【消息数量】 循环 customer_id: %s | uid: %s --->>' % (str(customer_id), str(user_id)))
                if redis_customer_query_info_key_flag == 'True':
                    print('---- 小程序【消息数量】 Flag 为 True  --->>', redis_customer_query_info_key_flag)
                    chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,send_type=1, is_customer_new_msg=True).count()

                    response_data = {
                        'msg_data': {
                             'chatinfo_count': chatinfo_count,
                        },
                        'code': 200,
                        'msg': '实时获取小程序【消息数量】成功',
                    }

                    print('------ 有新消息, 实时推送给【小程序】 的数据：---->', response_data)
                    uwsgi.websocket_send(json.dumps(response_data))
                    rc.set(redis_customer_query_info_key, False)


                else:
                    try:
                        # data = uwsgi.websocket_recv()
                        data = uwsgi.websocket_recv_nb()

                        print('------[小程序【消息数量】-非阻塞] websocket_recv_nb ----->>', data)
                        if not data:
                            time.sleep(2)
                            continue

                        _data = json.loads(data.decode("utf-8"))
                        print('------ 【小程序-【消息数量】】发送过来的 数据:  ----->>', _data)

                        type = _data.get('type')
                        customer_id = _data.get('user_id')
                        user_id = _data.get('u_id')


                        # redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)

                        forms_obj = xiaochengxu_ChatPostForm(_data)
                        if  forms_obj.is_valid():
                            redis_customer_query_info_key = 'message_customer_id_{cid}_info_num'.format(cid=customer_id)

                            chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id,
                                                                                 customer_id=customer_id, send_type=1,
                                                                                 is_customer_new_msg=True).count()


                            if  type == 'query_num':
                                response_data = {
                                    'msg_data': {
                                        'chatinfo_count': chatinfo_count,
                                    },
                                    'code': 200,
                                    'msg': '获取成功',
                                }
                                uwsgi.websocket_send(json.dumps(response_data))

                            elif type == 'closed':
                                msg = '确认关闭  customer_id | uid | ' + str(customer_id) + "|" + str(user_id)
                                ret_data = {
                                    'code': 200,
                                    'msg': msg
                                }
                                # uwsgi.websocket_send(json.dumps(ret_data))
                                return JsonResponse(ret_data)


                        else:

                            if not user_id or not customer_id:
                                ret_data = {
                                    'code': 401,
                                    'msg': 'user_id和uid不能为空,终止连接'
                                }
                                uwsgi.websocket_send(json.dumps(ret_data))

                                return JsonResponse(ret_data)

                    except Exception as  e:
                        ret_data = {
                            'code': 400,
                            'msg': '报错:%s 终止连接' % (e)
                        }
                        print('----  报错:%s [小程序] 终止连接 customer_id | user_id --->>' % e,str(customer_id), str(user_id))
                        # uwsgi.websocket_send(json.dumps(ret_data))

                        return JsonResponse(ret_data)


            except Exception as  e:
                ret_data = {
                    'code': 400,
                    'msg': '报错:%s 终止连接' % (e)
                }
                print('----  报错:%s 终止连接 --->>' % e)
                # uwsgi.websocket_send(json.dumps(ret_data))

                return JsonResponse(ret_data)




# @csrf_exempt
def public_websocket(request, oper_type):
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    # 后台雷达用户 扫码登录
    if oper_type == 'scan_code_web_login':

        uwsgi.websocket_handshake()
        i = 0
        while True:

            try:
                data = uwsgi.websocket_recv()
                # data = uwsgi.websocket_recv_nb()
                print('------[扫码登录验证[auth_code]-非阻塞] websocket_recv_nb ----->>', data)
                if not data:
                    time.sleep(30)
                    response_data = {
                        'code': 504,
                        'msg': '链接超时,关闭长连接',
                    }
                    uwsgi.websocket_send(json.dumps(response_data))
                    return JsonResponse(response_data)

                _data = json.loads(data.decode("utf-8"))
                print('------ [扫码登录验证[auth_code] 发送过来的 数据:  ----->>', _data)

                type = _data.get('type')
                auth_code = _data.get('auth_code')

                if auth_code and  type == 'query_login_status':
                    auth_code_flag = rc.get(auth_code)
                    if auth_code_flag == 'True':

                        objs = models.zgld_userprofile.objects.filter(password=auth_code)
                        if objs:
                            obj = objs[0]
                            name = obj.username
                            avatar = obj.avatar
                            last_login_date_obj = obj.last_login_date
                            last_login_date = last_login_date_obj.strftime(
                                '%Y-%m-%d %H:%M:%S') if last_login_date_obj else ''


                            response_data = {
                                    'data' :  {
                                    'user_id': obj.id,
                                    'token': obj.token,
                                    'role_id': 1,
                                    'username': name,
                                    'avatar':   avatar,

                                    'company_name': obj.company.name,
                                    'company_id': obj.company_id,

                                    'weChatQrCode': obj.company.weChatQrCode,
                                    'state': 'scan_code_web_login',
                                    'last_login_date': last_login_date,

                                },
                                'code': 200,
                                'msg': '登录成功',
                            }

                            rc.delete(auth_code)
                            objs.update(
                                password = ''
                            )


                            print('----- 登录成功 --->>',auth_code,'|','True')
                            uwsgi.websocket_send(json.dumps(response_data))
                            return JsonResponse(response_data)

                        else:
                            response_data = {
                                'code': 301,
                                'msg': '登录失败',
                            }
                            print('----- 登录失败 --->>',auth_code,'|','True')
                            uwsgi.websocket_send(json.dumps(response_data))
                            return JsonResponse(response_data)

                    elif auth_code_flag == 'False':
                        response_data = {
                            'code': 201,
                            'msg': '等待验证中',
                        }
                        print('----- 等待验证中 --->>',auth_code,'|', 'False')
                        uwsgi.websocket_send(json.dumps(response_data))

                    else:
                        response_data = {
                            'code': 303,
                            'msg': 'Auth code已经失效',
                        }
                        rc.delete(auth_code)
                        print('----- Auth code已经失效 --->>',auth_code)
                        uwsgi.websocket_send(json.dumps(response_data))
                        return JsonResponse(response_data)


                    i = i + 1
                    if i > 115:

                        ret_data = {
                            'code': 504,
                            'msg': '等待超时,关闭长连接'
                        }
                        rc.delete(auth_code)
                        uwsgi.websocket_send(json.dumps(ret_data))
                        return JsonResponse(ret_data)


                elif type == 'closed':
                    msg = '确认关闭'
                    ret_data = {
                        'code': 200,
                        'msg': msg
                    }
                    # uwsgi.websocket_send(json.dumps(ret_data))
                    return JsonResponse(ret_data)

                elif type == 'register':

                    response_data = {
                        'code': 200,
                        'msg': '注册成功',
                    }

                    uwsgi.websocket_send(json.dumps(response_data))

            except Exception as  e:
                ret_data = {
                    'code': 400,
                    'msg': '报错:%s 终止连接' % (e)
                }
                print('----  报错:%s 终止连接 --->>' % e)
                # uwsgi.websocket_send(json.dumps(ret_data))

                return JsonResponse(ret_data)

    # 测试使用接口
    if oper_type == 'chat':

        """接受websocket传递过来的信息"""
        uwsgi.websocket_handshake()
        uwsgi.websocket_send("你还，很高心为你服务")

        while True:
            # msg = uwsgi.websocket_recv()
            try:
                msg = uwsgi.websocket_recv_nb()
                print('------[--》測試-非阻塞測試] websocket_recv_nb ----->>', msg)
                if not msg:
                    time.sleep(1)
                    continue

                msg = msg.decode()
                data = json.loads(msg)

                data_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                print('----- websocket_recv ---->>>', data)

                uwsgi.websocket_send(data["text"])


            except Exception as  e:
                ret_data = {
                    'code': 400,
                    'msg': '报错:%s 终止连接' % (e)
                }
                print('----  报错:%s 终止连接 --->>' % e)
                # uwsgi.websocket_send(json.dumps(ret_data))

                return JsonResponse(ret_data)


# 查询雷达消息未读的数量
def query_info_num_list(data):
    user_id = data.get('user_id')

    chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, send_type=2,
                                                         is_user_new_msg=True).count()

    return chatinfo_count

# 查询雷达通讯录列表的数量的数量
def query_contact_list(data):
    user_id = data.get('user_id')
    current_page = data.get('current_page')
    length = data.get('length')

    chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, send_type=2,
                                                         is_user_new_msg=True).count()


    chat_info_objs = models.zgld_chatinfo.objects.select_related(
        'userprofile',
        'customer'
    ).filter(
        userprofile_id=user_id,
        is_last_msg=True
    ).order_by('-create_date')

    # contact_num = chat_info_objs.count()

    if length != 0:
        start_line = (current_page - 1) * length
        stop_line = start_line + length
        chat_info_objs = chat_info_objs[start_line: stop_line]

    ret_data_list = []
    for obj in chat_info_objs:
        print('-------- obj.id -------->>', obj.id)

        # username = base64.b64decode(obj.customer.username)
        # customer_name = str(username, 'utf-8')

        try:
            customer_id = obj.customer_id
            if not customer_id:  # 没有customer_id
                continue

            _username = obj.customer.username

            username = base64.b64decode(_username)
            customer_name = str(username, 'utf-8')
            print('----- 解密b64decode username----->', customer_id, '|', username)
        except Exception as e:
            print('----- b64decode解密失败的 customer_id 是 | e ----->', obj.customer_id, "|", e)
            customer_name = '客户ID%s' % (obj.customer_id)

        content = obj.content

        if not content:
            continue

        _content = json.loads(content)
        info_type = _content.get('info_type')
        msg = ''
        if info_type:
            info_type = int(info_type)
            if info_type == 1:
                msg = _content.get('msg')
                msg = base64.b64decode(msg)
                msg = str(msg, 'utf-8')

            elif info_type == 2:
                msg = '向您咨询:' + _content.get('product_name')

            elif info_type == 3:
                msg = _content.get('msg')

        _objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
            userprofile_id=obj.userprofile_id,
            customer_id=obj.customer_id,
            is_user_new_msg=True,
            send_type=2
        )
        _count = _objs.count()

        base_info_dict = {
            'customer_id': obj.customer_id,
            'customer_source': obj.customer.user_type or '',
            'customer_source_text': obj.customer.get_user_type_display(),
            'is_subscribe': obj.customer.is_subscribe,
            'is_subscribe_text': obj.customer.get_is_subscribe_display(),
            'src': obj.customer.headimgurl,
            'name': customer_name,
            'dateTime': deal_time.deal_time(obj.create_date),
            'msg': msg,
            'count': _count
        }

        ret_data_list.append(base_info_dict)
    return  ret_data_list,chatinfo_count