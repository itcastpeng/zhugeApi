from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.contact_verify import  ContactSelectForm

from zhugeleida import models

@csrf_exempt
@account.is_token(models.zgld_userprofile)
def contact(request):
    '''
    获取用户的聊天表
    :param request:
    :return:
    '''
    response = Response.ResponseObj()
    if request.method == 'GET':

            forms_obj = ContactSelectForm(request.GET)
            if forms_obj.is_valid():
                print(request.GET)

                userprofile_id = int(request.GET.get('user_id'))
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                chat_info_objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=userprofile_id,is_last_msg=True).values('id', 'userprofile_id', 'userprofile__username', 'customer_id',
                                                                                   'customer__username', 'send_type',
                                                                                     'msg', 'create_date', ).order_by('create_date')

                count = chat_info_objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    chat_info_objs = chat_info_objs[start_line: stop_line]

                    response.code = 200
                    response.data = {
                        'ret_data': list(chat_info_objs),
                        'now_data_count': chat_info_objs.count(),
                        'data_count': count,
                    }

            return JsonResponse(response.__dict__)

