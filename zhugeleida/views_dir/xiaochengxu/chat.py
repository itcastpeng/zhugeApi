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

import json
from zhugeleida import models


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
            ).order_by('-create_date')

            objs.update(
                is_customer_new_msg=False
            )
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]


            ret_data_list = []
            for obj in objs:
                ret_data_list.append({
                     'customer_id': obj.customer.id,
                     'user_id': obj.userprofile.id,
                     'customer': obj.customer.username,
                     'customer_headimgurl': obj.customer.headimgurl,
                     'dateTime': obj.create_date,
                     'msg': obj.msg,
                     'send_type': obj.send_type,
                })

            ret_data_list.reverse()
            response.code = 200
            response.msg = '分页获取-全部聊天消息成功'
            response.data = {
                'ret_data': ret_data_list,
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
                    ret_data_list.append({
                        'customer_id': obj.customer.id,
                        'user_id': obj.userprofile.id,
                        'customer_headimgurl':  obj.customer.headimgurl,
                        'customer': obj.customer.username,
                        'dateTime': obj.create_date,
                        'send_type': obj.send_type,
                        'msg':       obj.msg,
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
                                                    is_last_msg=True).update(is_last_msg=False)
                models.zgld_chatinfo.objects.create(
                    msg=msg,
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=send_type,
                )

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