from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc import deal_time
from zhugeleida.forms.contact_verify import ContactSelectForm
import base64
from zhugeleida import models
import json

# 获取用户聊天的信息列表
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def contact(request):
    response = Response.ResponseObj()
    if request.method == 'GET':

        forms_obj = ContactSelectForm(request.GET)
        if forms_obj.is_valid():
            print(request.GET)

            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            chat_info_objs = models.zgld_chatinfo.objects.select_related(
                'userprofile',
                'customer'
            ).filter(
                userprofile_id=user_id,
                is_last_msg=True
            ).order_by('-create_date')

            count = chat_info_objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                chat_info_objs = chat_info_objs[start_line: stop_line]

            ret_data_list = []

            for obj in chat_info_objs:
                print('--------chat_info_objs-------->>', obj.create_date)

                # username = base64.b64decode(obj.customer.username)
                # customer_name = str(username, 'utf-8')

                try:
                    username = base64.b64decode(obj.customer.username)
                    customer_name = str(username, 'utf-8')
                    print('----- 解密b64decode username----->', username)
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
                    if info_type == 1 or info_type == 3:
                        msg = _content.get('msg')
                        msg = base64.b64decode(msg)
                        msg = str(msg, 'utf-8')

                    elif info_type == 2:
                        msg ='向您咨询:' +  _content.get('product_name')

               

                base_info_dict = {
                    'customer_id': obj.customer_id,
                    'customer_source' : obj.customer.user_type,
                    'customer_source_text' : obj.customer.get_user_type_display(),
                    'src': obj.customer.headimgurl,
                    'name': customer_name,
                    'dateTime': deal_time.deal_time(obj.create_date),
                    'msg': msg,
                }

                ret_data_list.append(base_info_dict)


            response.code = 200
            response.data = {
                'ret_data': ret_data_list,
                'data_count': count,
            }

    return JsonResponse(response.__dict__)
