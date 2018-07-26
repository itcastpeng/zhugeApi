from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.chat_verify import ChatSelectForm,ChatGetForm,ChatPostForm
from zhugeapi_celery_project import tasks

import json
from zhugeleida import models
import base64
from zhugeleida.public.common import action_record

@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat(request):
    '''
    【分页获取】- 所有的聊天信息
    :param request:
    :return:
    '''
    if request.method == 'GET':
        forms_obj = ChatSelectForm(request.GET)
        if forms_obj.is_valid():
            response = Response.ResponseObj()
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')
            # send_type = request.GET.get('send_type')

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']


            objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                userprofile_id=user_id,
                customer_id=customer_id,
            ).order_by('-create_date')
            objs.update(
                is_user_new_msg=False
            )
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]


            ret_data_list = []
            for obj in objs:

                customer_name = base64.b64decode(obj.customer.username)
                customer_name = str(customer_name, 'utf-8')


                if  obj.info_type == 1:  # 如果为聊信息。
                    ret_data_list.append({
                         'customer_id': obj.customer.id,
                         'customer_avatar': obj.customer.headimgurl,
                         'user_id': obj.userprofile.id,
                         'src': obj.customer.headimgurl,
                         'name': customer_name,
                         'dateTime': obj.create_date,
                         'msg': obj.msg,
                         'send_type': obj.send_type,
                         'info_type': obj.info_type,  # (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                    })
                elif obj.info_type == 2:  # 如果为产品咨询。
                    ret_data_list.append({
                         'customer_id': obj.customer.id,
                         'customer_avatar': obj.customer.headimgurl,
                         'user_id': obj.userprofile.id,
                         'src': obj.customer.headimgurl,
                         'name': customer_name,
                         'dateTime': obj.create_date,

                         'product_cover_url': obj.product_cover_url,
                         'product_name': obj.product_name,
                         'product_price': obj.product_price,
                         'info_type': obj.info_type,      # (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                         'send_type': obj.send_type,
                    })

            ret_data_list.reverse()
            response.code = 200
            response.msg = '分页获取-全部聊天消息成功'
            response.data = {
                'ret_data':  ret_data_list,
                'data_count': count,
            }

            if not ret_data_list:
                # 没有新消息
                response.msg = 'No new data'

            return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "GET":
        if oper_type == 'getmsg':

            forms_obj = ChatGetForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('user_id')
                customer_id = request.GET.get('customer_id')

                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    is_user_new_msg=True

                ).order_by('-create_date')

                ret_data_list = []
                count = objs.count()
                for obj in objs:

                    customer_name = base64.b64decode(obj.customer.username)
                    customer_name = str(customer_name, 'utf-8')

                    if obj.info_type == 1:  # 如果为聊信息。
                        ret_data_list.append({
                            'customer_id': obj.customer.id,
                            'customer_avatar': obj.customer.headimgurl,
                            'user_id': obj.userprofile.id,
                            'src': obj.customer.headimgurl,
                            'name': customer_name,
                            'dateTime': obj.create_date,
                            'msg': obj.msg,
                            'send_type': obj.send_type,
                            'info_type': obj.info_type,  # (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                        })
                    elif obj.info_type == 2:  # 如果为产品咨询。
                        ret_data_list.append({
                            'customer_id': obj.customer.id,
                            'customer_avatar': obj.customer.headimgurl,
                            'user_id': obj.userprofile.id,
                            'src': obj.customer.headimgurl,
                            'name': customer_name,
                            'dateTime': obj.create_date,

                            'product_cover_url': obj.product_cover_url,
                            'product_name': obj.product_name,
                            'product_price': obj.product_price,
                            'info_type': obj.info_type,  # (1, #客户和用户之间的聊天信息 (2,#客户和用户之间的产品咨询
                            'send_type': obj.send_type,
                        })

                response.code = 200
                response.msg = '实时获取-最新聊天信息成功'
                print('--- list(msg_obj) -->>', ret_data_list)
                ret_data_list.reverse()
                response.data = {
                    'ret_data': ret_data_list,
                    'data_count': count,
                }

                objs.update(
                    is_user_new_msg=False
                )

                if not ret_data_list:
                    # 没有新消息
                    response.msg = '没有得到实时聊天信息'
                return JsonResponse(response.__dict__)

    elif request.method == 'POST':
        # 用户推送消息到server端,然后入库
        if  oper_type == 'send_msg':
            print('----send_msg--->>',request.POST)
            forms_obj = ChatPostForm(request.POST)

            if forms_obj.is_valid():
                data = request.POST
                user_id = int(data.get('user_id'))
                customer_id = int(data.get('customer_id'))
                msg = data.get('msg')
                send_type = int(data.get('send_type'))

                flow_up_obj = models.zgld_user_customer_flowup.objects.get(user_id=user_id, customer_id=customer_id)
                if send_type == 1: # 用戶發消息給客戶，修改最後跟進-時間
                    flow_up_obj.last_follow_time=datetime.datetime.now()
                    flow_up_obj.save()

                elif send_type == 2: # 客戶發消息給用戶，修改最後活動-時間
                    flow_up_obj.last_activity_time = datetime.datetime.now()
                    flow_up_obj.save()

                models.zgld_chatinfo.objects.filter(userprofile_id=user_id,customer_id=customer_id,is_last_msg=True).update(is_last_msg=False)
                models.zgld_chatinfo.objects.create(
                        msg=msg,
                        userprofile_id=user_id,
                        customer_id=customer_id,
                        send_type=send_type,

                )

                # remark = ':%s' % (msg)
                # data = request.GET.copy()
                # data['action'] = 0
                # data['uid'] = user_id
                # response = action_record(data, remark)

                data['customer_id'] = customer_id
                data['user_id'] = user_id
                tasks.user_send_template_msg_to_customer.delay(json.dumps(data))

                response.code = 200
                response.msg = 'send msg successful'
                return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)