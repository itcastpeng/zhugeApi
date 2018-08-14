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
                if obj.id == first_info[0].get('id'): # 判断第一条问候语数据

                    ret_data_list.append({
                        'customer_id': obj.customer.id,
                        'user_id': obj.userprofile.id,
                        'customer': customer_name,
                        'user_avatar': mingpian_avatar,
                        'customer_headimgurl': obj.customer.headimgurl,
                        'dateTime': obj.create_date,
                        'msg': obj.msg,
                        'send_type': obj.send_type,
                        'info_type': obj.info_type,  # (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                        'is_first_info': True,       # 是否为第一条的信息
                    })
                elif obj.info_type == 2: # 如果为产品咨询。
                    print('------first_info.get----->', first_info[0].get('id'))
                    ret_data_list.append({
                        'customer_id': obj.customer.id,
                        'from_user_name': customer_name,
                        'user_id': obj.userprofile.id,
                        'customer': customer_name,
                        'user_avatar': mingpian_avatar,
                        'customer_headimgurl': obj.customer.headimgurl,
                        'dateTime': obj.create_date,
                        'product_cover_url': obj.product_cover_url,
                        'product_name': obj.product_name,
                        'product_price': obj.product_price,
                        'info_type': obj.info_type,  #   (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                        'send_type': obj.send_type,
                        'is_first_info': False,  # 是否为第一条的信息

                    })

                else:

                    ret_data_list.append({
                        'customer_id': obj.customer.id,
                        'user_id': obj.userprofile.id,
                        'customer': customer_name,
                        'user_avatar': mingpian_avatar,
                        'customer_headimgurl': obj.customer.headimgurl,
                        'dateTime': obj.create_date,
                        'msg': obj.msg,
                        'info_type': obj.info_type,
                        'send_type': obj.send_type, # (1, 'user_to_customer'),  (2, 'customer_to_user')
                        'is_first_info': False,     # 是否为第一条的信息
                    })

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
                    is_customer_new_msg = True,
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

                        # if obj.userprofile.avatar.startswith("http"):
                        #     mingpian_avatar = obj.userprofile.avatar
                        # else:
                        mingpian_avatar =  obj.userprofile.avatar

                    customer_name = base64.b64decode(obj.customer.username)
                    customer_name = str(customer_name, 'utf-8')


                    ret_data_list.append({
                                'customer_id': obj.customer.id,
                                'user_id': obj.userprofile.id,
                                'user_avator' :  mingpian_avatar,
                                'customer_headimgurl':  obj.customer.headimgurl,
                                'customer': customer_name,
                                'dateTime': obj.create_date,
                                'msg':       obj.msg,
                                'send_type': obj.send_type,  # (1, 'user_to_customer'),  (2, 'customer_to_user')
                                'is_first_info': False,  # 是否为第一条的信息
                                'info_type': obj.info_type, # 消息的类型
                            })


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

        return JsonResponse(response.__dict__)

    elif request.method == 'POST':
        # 用户推送消息到server端,然后入库
        if  oper_type == 'send_msg':

            forms_obj = ChatPostForm(request.POST)

            if forms_obj.is_valid():

                print('----send_msg--->>',request.POST)
                customer_id = int(request.GET.get('user_id'))
                user_id =  request.POST.get('u_id')
                msg = request.POST.get('msg')
                send_type = request.POST.get('send_type')
                models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                    is_last_msg=True).update(is_last_msg=False)  # 把所有的重置为不是最后一条

                models.zgld_chatinfo.objects.create(
                    msg=msg,
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=send_type,
                )

                # user_new_msg_count = models.zgld_chatinfo.objects.filter(
                #         userprofile_id=user_id,
                #         customer_id=customer_id,
                #
                # ).count()
                # if user_new_msg_count > 0: # 说明有未读的消息

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


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)