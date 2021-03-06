from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc import deal_time
from zhugeleida.forms.contact_verify import ContactSelectForm
from publicFunc.base64 import b64decode
from zhugeleida import models
import json, base64, time, redis

# 获取用户聊天的信息列表
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def contact(request):
    response = Response.ResponseObj()
    if request.method == 'GET':
        forms_obj = ContactSelectForm(request.GET)
        if forms_obj.is_valid():

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            chatinfo_count = models.zgld_chatinfo.objects.filter(
                userprofile_id=user_id,
                send_type=2,
                is_user_new_msg=True
            ).count() # 未读消息数量

            data_list = rc.hget('leida_redis_contact', 'leida_redis_contact_{}'.format(user_id))
            if data_list:
                data_list = eval(data_list)
                count = len(data_list)
                response.code = 200
                response.data = {
                    'ret_data': data_list,  # 数据列表
                    'data_count': count,  # 数据总数
                }
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    data_list = data_list[start_line: stop_line]
            else:
                data_list = []
                count = 0

            response.code = 200
            response.data = {
                'ret_data': data_list,          # 数据列表
                'data_count': count,                # 数据总数
                'unread_msg_num': chatinfo_count,   # 未读消息数量
            }

            response.note = {
                'customer_id': '客户ID',
                'name': '客户姓名',
                'customer_source': '客户访问类型ID(微信公众号 微信小程序)',
                'customer_source_text': '客户访问类型',
                'src': '客户头像',
                'is_subscribe': '该客户是否订阅该公众号ID',
                'is_subscribe_text': '该客户是否订阅该公众号 文本',
                'dateTime': '消息发送时间',
                'msg': '发送的消息',
                'count': '该客户发送消息的数量',
                'tags_list': '标签列表',
                'unread_msg_num': '未读消息总数',
            }


            #
            # chat_info_objs = models.zgld_chatinfo.objects.select_related(
            #     'userprofile',
            #     'customer'
            # ).filter(
            #     userprofile_id=user_id,
            #     is_last_msg=True
            # ).order_by('-create_date')
            #
            # ret_data_list = []
            # customer_id_list = []
            # for obj in chat_info_objs:
            #     customer_id = obj.customer_id
            #     if customer_id in customer_id_list:
            #         continue
            #     customer_id_list.append(customer_id)
            #
            #     info_objs = models.zgld_chatinfo.objects.filter(
            #         userprofile_id=user_id,
            #         customer_id=customer_id,
            #         is_last_msg=True
            #     ).order_by('-create_date')
            #     if info_objs:
            #         info_objs = info_objs[0]
            #     customer_name = ''
            #     if info_objs.customer.username:
            #         customer_name = b64decode(info_objs.customer.username)
            #
            #     content = info_objs.content
            #
            #     msg = ''
            #     if  content:
            #         _content = json.loads(content)
            #         info_type = _content.get('info_type')
            #
            #         if info_type:
            #             info_type = int(info_type)
            #             if info_type == 1:
            #                 msg = b64decode(_content.get('msg'))
            #
            #             elif info_type == 2:
            #                 msg ='向您咨询:' +  _content.get('product_name')
            #
            #             elif info_type == 3:
            #                 msg = _content.get('msg')
            #
            #     _count = models.zgld_chatinfo.objects.select_related(
            #         'userprofile',
            #         'customer'
            #     ).filter(
            #         userprofile_id=user_id,
            #         customer_id=customer_id,
            #         is_user_new_msg=True,
            #         send_type=2
            #     ).count()
            #
            #     tags_list = []
            #     if info_objs.customer.user_type == 1:
            #         tags_list =  list(info_objs.customer.zgld_tag_set.filter(tag_type=1,user_id=user_id).order_by('-create_date').values_list('name', flat=True))
            #
            #     elif info_objs.customer.user_type == 2:
            #         tags_list = list(info_objs.customer.zgld_tag_set.filter(tag_type=2,user_id=user_id).order_by('-create_date').values_list('name', flat=True))

                # base_info_dict = {
                #     'customer_id': customer_id,
                #     'customer_source' : info_objs.customer.user_type or '',
                #     'customer_source_text' : info_objs.customer.get_user_type_display(),
                #     'src': info_objs.customer.headimgurl,
                #     'is_subscribe': info_objs.customer.is_subscribe,
                #     'is_subscribe_text': info_objs.customer.get_is_subscribe_display(),
                #     'name': customer_name,
                #     'dateTime': deal_time.deal_time(info_objs.create_date),
                #     'msg': msg,
                #     'count' :_count,
                #     'tags_list' : tags_list,
                #     'crea_date' : time.mktime(info_objs.create_date.timetuple()) #  前端无需引用 时间戳排序用
                # }
                #
                # ret_data_list.append(base_info_dict)


            # count = len(ret_data_list)
            # print('ret_data_list-> ', json.dumps(ret_data_list))
            # ret_data_list = sorted(ret_data_list, key=lambda x: x['crea_date'], reverse=True)


    return JsonResponse(response.__dict__)


# 聊天信息操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def contact_oper(request,oper_type):
    response = Response.ResponseObj()
    if request.method == 'GET':

        # 底部导航消息功能显示的未读数
        if oper_type == 'query_num':

            response = Response.ResponseObj()
            user_id = request.GET.get('user_id')
            company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
            chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id,send_type=2, is_user_new_msg=True).count()

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'chatinfo_count': chatinfo_count,
                'company_id' : company_id
            }

        else:
            response.code = 302
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)