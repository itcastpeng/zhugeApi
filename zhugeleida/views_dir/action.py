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
def action(request):
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

