from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.gongzhonghao.chat_verify import ChatSelectForm,ChatGetForm,ChatPostForm,EncryptedPhoneNumberForm
import base64
from django.db.models import F
import json
from django.db.models import Q
from zhugeleida.public.WXBizDataCrypt import WXBizDataCrypt

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

            phone = ''
            wechat = ''
            ret_data_list = []
            if objs:
                phone = objs[0].userprofile.mingpian_phone if objs[0].userprofile.mingpian_phone else objs[0].userprofile.wechat_phone
                wechat = objs[0].userprofile.wechat if objs[0].userprofile.wechat else objs[0].userprofile.wechat_phone

                for obj in objs:

                    mingpian_avatar_obj = models.zgld_user_photo.objects.filter(user_id=user_id, photo_type=2).order_by('-create_date')
                    mingpian_avatar = ''
                    if mingpian_avatar_obj:
                        mingpian_avatar = mingpian_avatar_obj[0].photo_url
                    else:

                        mingpian_avatar =  obj.userprofile.avatar

                    customer_name = base64.b64decode(obj.customer.username)
                    customer_name = str(customer_name, 'utf-8')


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
                        # 'from_user_name': customer_name,
                        'user_id': obj.userprofile.id,
                        'customer': customer_name,
                        'user_avatar': mingpian_avatar,
                        'customer_headimgurl': obj.customer.headimgurl,
                        'dateTime': obj.create_date,

                        'send_type': obj.send_type,
                        'is_first_info': is_first_info,       #是否为第一条的信息
                    }

                    base_info_dict.update(_content)

                    ret_data_list.append(base_info_dict)


                ret_data_list.reverse()
                response.code = 200
                response.msg = '分页获取-全部聊天消息成功'
                response.data = {
                    'ret_data': ret_data_list,
                    'mingpian_phone': phone,
                    'wechat': wechat,
                    'data_count': count,
                }

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
                send_type = 2
                models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                    is_last_msg=True).update(is_last_msg=False)  # 把所有的重置为不是最后一条


                _content = json.loads(content)
                info_type = _content.get('info_type')
                _msg = ''
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


                if info_type == 1:  # 发送的文字消息
                    remark = ':%s' % (_msg)
                    data = request.GET.copy()
                    data['action'] = 0  # 代表发送客户聊天信息
                    data['uid'] = user_id
                    response = action_record(data, remark)

                response.code = 200
                response.msg = 'send msg successful'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 解密接收手机发送的手机号
        elif oper_type == 'encrypted_phone_number':

            forms_obj = EncryptedPhoneNumberForm(request.POST)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                customer_id = request.GET.get('user_id')

                print('---- request.POST --->>',json.dumps(request.POST))

                user_id = request.POST.get('u_id')
                encryptedData = request.POST.get('encryptedData')
                iv = request.POST.get('iv')

                objs =  models.zgld_userprofile.objects.filter(id=user_id)
                if objs:
                    obj =objs[0]
                    customer_obj = models.zgld_customer.objects.get(id=customer_id)
                    session_key = customer_obj.session_key
                    company_id = obj.company_id
                    xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)
                    authorization_appid = ''
                    if xiaochengxu_app_objs:
                        authorization_appid = xiaochengxu_app_objs[0].authorization_appid

                    print('----- authorization_appid ----->>',authorization_appid,session_key,'\n',encryptedData,iv)
                    pc = WXBizDataCrypt(authorization_appid, session_key)
                    ret =  pc.decrypt(encryptedData, iv)
                    print('------ pc.decrypt(encryptedData) ------->>', ret)

                    phoneNumber = ret.get('phoneNumber')


                    # { 'phoneNumber': '17326681685',
                    #   'purePhoneNumber': '17326681685', 'countryCode': '86',
                    #   'watermark': {'timestamp': 1537415579, 'appid': 'wx1add8692a23b5976'}}


                    if phoneNumber:
                        _msg = '我的手机号是: %s' % (phoneNumber)

                        encodestr = base64.b64encode(_msg.encode('utf-8'))
                        msg = str(encodestr, 'utf-8')
                        _content =  {
                           'info_type' : 1,
                           'msg' : msg
                        }
                        content = json.dumps(_content)

                        models.zgld_chatinfo.objects.create(
                            content=content,
                            userprofile_id=user_id,
                            customer_id=customer_id,
                            send_type=2
                        )
                        customer_obj.phone = phoneNumber
                        customer_obj.save()

                        response.code = 200
                        response.msg = '获取成功'
                        response.data = {
                             'phoneNumber': phoneNumber,
                         }
                    else:
                        response.code = 200
                        response.msg = '获取失败'


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)