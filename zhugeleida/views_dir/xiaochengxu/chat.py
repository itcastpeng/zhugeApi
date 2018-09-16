from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.xiaochengxu.chat_verify import ChatSelectForm,ChatGetForm,ChatPostForm
import base64
from django.db.models import F
import json
from django.db.models import Q

import json
from zhugeleida import models
from zhugeleida.public.common import action_record

@csrf_exempt
@account.is_token(models.zgld_customer)
def chat(request):
    '''
    【分页获取】- 所有的聊天信息
    :param request:
    :return:
    '''
    if request.method == 'GET':
        response = Response.ResponseObj()
        forms_obj = ChatSelectForm(request.GET)

        if forms_obj.is_valid():
            response = Response.ResponseObj()
            customer_id = request.GET.get('user_id')
            user_id = request.GET.get('u_id')
            # send_type = request.GET.get('send_type')

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']


            objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                userprofile_id=user_id,
                customer_id=customer_id,
            )

            # 第一条数据
            first_info = list(objs[:1].values('id'))
            print('---first_info->>', first_info)

            objs = objs.order_by('-create_date')
            objs.update(
                is_customer_new_msg=False
            )
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            global phone,wechat

            ret_data_list = []
            for obj in objs:

                mingpian_avatar_obj = models.zgld_user_photo.objects.filter(user_id=user_id, photo_type=2).order_by('-create_date')
                mingpian_avatar = ''
                if mingpian_avatar_obj:
                    mingpian_avatar = mingpian_avatar_obj[0].photo_url
                else:

                    # if obj.userprofile.avatar.startswith("http"):
                    #     mingpian_avatar = obj.userprofile.avatar
                    # else:
                    mingpian_avatar =  obj.userprofile.avatar

                customer_name = base64.b64decode(obj.customer.username)
                customer_name = str(customer_name, 'utf-8')
                phone = obj.userprofile.mingpian_phone  if obj.userprofile.mingpian_phone else obj.userprofile.wechat_phone
                wechat = obj.userprofile.wechat if obj.userprofile.wechat else obj.userprofile.wechat_phone

                is_first_info = False
                if obj.id == first_info[0].get('id'): # 判断第一条问候语数据
                    is_first_info =  True



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
                    'customer_id': obj.customer.id,
                    'from_user_name': customer_name,
                    'user_id': obj.userprofile.id,
                    'customer': customer_name,
                    'user_avatar': mingpian_avatar,
                    'customer_headimgurl': obj.customer.headimgurl,
                    'dateTime': obj.create_date,

                    'send_type': obj.send_type,
                    'is_first_info': is_first_info,     #是否为第一条的信息
                }

                base_info_dict.update(_content)

                ret_data_list.append(base_info_dict)


                # elif obj.info_type == 2: # 如果为产品咨询。
                #     print('------first_info.get----->', first_info[0].get('id'))
                #     ret_data_list.append({
                #         'customer_id': obj.customer.id,
                #         'from_user_name': customer_name,
                #         'user_id': obj.userprofile.id,
                #         'customer': customer_name,
                #         'user_avatar': mingpian_avatar,
                #         'customer_headimgurl': obj.customer.headimgurl,
                #         'dateTime': obj.create_date,
                #
                #         'product_cover_url': obj.product_cover_url,
                #         'product_name': obj.product_name,
                #         'product_price': obj.product_price,
                #
                #         'info_type': obj.info_type,  #   (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                #         'send_type': obj.send_type,
                #         'is_first_info': False,  # 是否为第一条的信息
                #     })
                #
                # else:
                #
                #     ret_data_list.append({
                #         'customer_id': obj.customer.id,
                #         'user_id': obj.userprofile.id,
                #         'customer': customer_name,
                #         'user_avatar': mingpian_avatar,
                #         'customer_headimgurl': obj.customer.headimgurl,
                #         'dateTime': obj.create_date,
                #
                #         'msg': obj.msg,
                #         'info_type': obj.info_type,
                #
                #         'send_type': obj.send_type, # (1, 'user_to_customer'),  (2, 'customer_to_user')
                #         'is_first_info': False,     # 是否为第一条的信息
                #     })

            ret_data_list.reverse()
            response.code = 200
            response.msg = '分页获取-全部聊天消息成功'
            response.data = {
                'ret_data': ret_data_list,
                'mingpian_phone': phone,
                'wechat': wechat,
                'data_count': count,
            }
            if not ret_data_list:
                # 没有新消息
                response.msg = 'No new data'
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

        return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_customer)
def chat_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "GET":
        if oper_type == 'getmsg':

            forms_obj = ChatGetForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                customer_id = request.GET.get('user_id')
                user_id = request.GET.get('u_id')

                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    is_customer_new_msg = True
                ).order_by('-create_date')


                ret_data_list = []
                count = objs.count()
                for obj in objs:

                    mingpian_avatar_obj = models.zgld_user_photo.objects.filter(user_id=user_id, photo_type=2).order_by(
                        '-create_date')

                    mingpian_avatar = ''
                    if mingpian_avatar_obj:
                        mingpian_avatar = mingpian_avatar_obj[0].photo_url
                    else:

                        mingpian_avatar =  obj.userprofile.avatar

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
                        'user_avator' :  mingpian_avatar,
                        'customer_headimgurl':  obj.customer.headimgurl,
                        'customer': customer_name,
                        'dateTime': obj.create_date,
                        # 'msg':       obj.msg,
                        'send_type': obj.send_type,  # (1, 'user_to_customer'),  (2, 'customer_to_user')
                        'is_first_info': False,      # 是否为第一条的信息
                        # 'info_type': obj.info_type, # 消息的类型

                    }

                    base_info_dict.update(_content)

                    ret_data_list.append(base_info_dict)

                    # ret_data_list.append({
                                # 'customer_id': obj.customer.id,
                                # 'user_id': obj.userprofile.id,
                                # 'user_avator' :  mingpian_avatar,
                                # 'customer_headimgurl':  obj.customer.headimgurl,
                                # 'customer': customer_name,
                                # 'dateTime': obj.create_date,
                                # 'msg':       obj.msg,
                                # 'send_type': obj.send_type,  # (1, 'user_to_customer'),  (2, 'customer_to_user')
                                # 'is_first_info': False,  # 是否为第一条的信息
                                # 'info_type': obj.info_type, # 消息的类型
                            # })


                ret_data_list.reverse()
                response.code = 200
                response.msg = '实时获取-最新聊天信息成功'
                print('--- list(msg_obj) -->>', ret_data_list)

                response.data = {
                    'ret_data': ret_data_list,
                    'data_count': count,
                }

                objs.update(
                    is_customer_new_msg=False
                )

                if not ret_data_list:
                    # 没有新消息
                    response.msg = '没有得到实时聊天信息'
            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        #查询聊天信息数量
        elif oper_type == 'query_num':
            forms_obj = ChatGetForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                customer_id = request.GET.get('user_id')
                user_id = request.GET.get('u_id')

                chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,send_type=1, is_customer_new_msg=True).count()

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'chatinfo_count': chatinfo_count,
                }

            else:
                response.code = 302
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'history_chatinfo_store_content':


            # models.zgld_chatinfo.objects.all().values('id','info_type','msg','product_cover_url','product_name','product_price')
            objs = models.zgld_chatinfo.objects.all()

            for obj in objs:
                chat_id = obj.id
                info_type = obj.info_type
                msg = obj.msg
                product_cover_url = obj.product_cover_url
                product_name = obj.product_name
                product_price = obj.product_price

                if info_type == 1:  # msg

                    if msg:
                        print('------ 【msg】 chat_id ------>>',chat_id)
                        encodestr = base64.b64encode(msg.encode('utf-8'))
                        msg = str(encodestr, 'utf-8')

                        _content = {
                            'info_type': 1,
                            'msg': msg
                        }
                        obj.content = json.dumps(_content)
                        obj.save()

                elif info_type == 2:

                    if product_name and product_cover_url:
                        print('------ 【product】 chat_id ------>>', chat_id)

                        _content = {
                            'info_type': 2,  # 2代表发送的产品咨询  3代表发送的电话号码  4代表发送的图片|截图  5、视频
                            'product_cover_url': product_cover_url ,
                            'product_name': product_name,
                            'product_price': product_price
                        }
                        obj.content = json.dumps(_content)
                        obj.save()


            response.code = 200
            response.msg = '成功'

        return JsonResponse(response.__dict__)

    elif request.method == 'POST':
        # 用户推送消息到server端,然后入库
        if  oper_type == 'send_msg':

            forms_obj = ChatPostForm(request.POST)

            if forms_obj.is_valid():

                print('----send_msg--->>',request.POST)
                customer_id = int(request.GET.get('user_id'))
                user_id =  request.POST.get('u_id')
                content = request.POST.get('content')
                send_type = int(request.POST.get('send_type'))
                models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                    is_last_msg=True).update(is_last_msg=False)  # 把所有的重置为不是最后一条


                _content = json.loads(content)
                info_type = _content.get('info_type')
                msg = ''
                if info_type:
                    info_type = int(info_type)

                    if info_type == 1:
                        msg = _content.get('msg')
                        encodestr = base64.b64encode(msg.encode('utf-8'))
                        msg = str(encodestr, 'utf-8')
                        _content['msg'] = msg
                        content = json.dumps(_content)

                models.zgld_chatinfo.objects.create(
                    content=content,
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=send_type
                )

                flow_up_objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id, customer_id=customer_id)
                if send_type == 2 and flow_up_objs: # 用戶發消息給客戶，修改最後跟進-時間
                    flow_up_objs.update(
                        is_customer_msg_num=F('is_customer_msg_num') + 1,
                        last_activity_time = datetime.datetime.now()
                    )

                if info_type == 1:  # 发送的图文消息
                    remark = ':%s' % (msg)
                    data = request.GET.copy()
                    data['action'] = 0  # 代表用客户咨询产品
                    data['uid'] = user_id
                    response = action_record(data, remark)

                response.code = 200
                response.msg = 'send msg successful'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 解密接收手机发送的手机号
        elif oper_type == '':
            pass


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)