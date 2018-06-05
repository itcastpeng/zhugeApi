from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.chat_verify import ChatSelectForm

import json
from zhugeleida import models


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat(request):
    '''
     实时获取聊天信息
    :param request:
    :return:
    '''
    if request.method == 'GET':

        forms_obj = ChatSelectForm(request.GET)
        if forms_obj.is_valid():
            response = Response.ResponseObj()
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')
            send_type = request.GET.get('send_type')

            msg_obj = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                userprofile_id=user_id,customer_id=customer_id, send_type=send_type, is_new_msg=True).values('id', 'userprofile_id',
                                                                                     'userprofile__username',
                                                                                     'customer_id', 'customer__username',
                                                                                     'send_type',
                                                                                     'msg', 'create_date', ).order_by('-create_date')
            response.code = 200
            response.msg = 'get new msg successful'
            print('--- list(msg_obj) -->>', list(msg_obj))

            response.data = list(msg_obj)
            msg_obj.update(
                is_new_msg=False
            )


            if not msg_obj:
                # 没有新消息
                response.msg = 'No new data'

            return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "GET":
        pass

    elif request.method == 'POST':
        # 用户推送消息到server端,然后入库
        if  oper_type == 'send_msg':
            print('----send_msg--->>',request.POST)
            forms_obj = ChatSelectForm(request.POST)

            if forms_obj.is_valid():
                userprofile_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                data = request.POST
                user_id = int(data.get('user_id'))
                customer_id = int(data.get('customer_id'))
                msg = data.get('msg')
                send_type = int(data.get('send_type'))

                print('---msg----->>', msg)

                info_chat_create_obj = models.zgld_chatinfo.objects.create(msg=msg)
                info_chat_get_obj = models.zgld_chatinfo.objects.get(id=info_chat_create_obj.id)
                info_chat_get_obj.userprofile_id = user_id
                info_chat_get_obj.customer_id = customer_id
                info_chat_get_obj.send_type = send_type
                info_chat_get_obj.is_new_msg = True
                info_chat_get_obj.is_last_msg = True
                info_chat_create_obj.save()
                info_chat_get_obj.save()

                exclude_chatinfo_obj = models.zgld_chatinfo.objects.all().exclude(id=info_chat_create_obj.id)
                exclude_chatinfo_obj.update(is_last_msg=False)
                response.code = 200
                response.msg = 'send msg successful'
                return JsonResponse(response.__dict__)



    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)