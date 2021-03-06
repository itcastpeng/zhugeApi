from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.public.common import action_record
from zhugeleida.forms.xiaochengxu.product_verify  import ProductSelectForm,ProductGetForm
import json
from django.db.models import Q,F

import uuid
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

@csrf_exempt
# @account.is_token(models.zgld_customer)
def product(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        if oper_type == 'product_single':

            forms_obj = ProductGetForm(request.GET)
            if forms_obj.is_valid():
                user_id = request.GET.get('uid')
                customer_id = request.GET.get('user_id')
                product_id = request.GET.get('product_id')


                # company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id
                con = Q()

                q1 = Q()
                q1.connector = 'and'
                # q1.children.append(('company_id', company_id))
                q1.children.append(('id', product_id))
                q1.children.append(('user_id__isnull', False))

                q2 = Q()
                q2.connector = 'and'
                # q2.children.append(('company_id', company_id))
                q2.children.append(('id', product_id))
                q2.children.append(('user_id__isnull', True))

                con.add(q1, 'OR')
                con.add(q2, 'OR')


                objs = models.zgld_product.objects.select_related('user', 'company').filter(con)
                count = objs.count()

                if objs:
                    ret_data = []
                    user_obj = models.zgld_userprofile.objects.get(id=user_id)
                    username = user_obj.username
                    position = user_obj.position

                    for obj in objs:
                        user_photo_obj = models.zgld_user_photo.objects.filter(user_id=user_id, photo_type=2).order_by(
                            '-create_date')

                        if user_photo_obj:
                            user_avatar = user_photo_obj[0].photo_url

                        else:
                            # if obj.avatar.startswith("http"):
                            #     user_avatar = obj.avatar
                            # else:
                            user_avatar = user_obj.avatar


                        ret_data.append({
                            'id': obj.id,
                            'publisher_date': obj.create_date,  # 发布日期。
                            'content': json.loads(obj.content),
                            'name': obj.name,  # 产品名称
                            'price': obj.price,  # 价格
                            'user_avatar': user_avatar,
                            'username': username,
                            'position': position,
                            'reason': obj.reason,  # 推荐理由

                            'create_date': obj.create_date.strftime("%Y-%m-%d"),  # 发布的日期
                            'status': obj.get_status_display(),  # 产品的动态
                            'status_code': obj.status  # 产品的动态值。
                        })

                        # if len(('正在查看' + obj.name)) > 20:
                        #     remark = '%s...,尽快把握商机' % (('正在查看'+obj.name)[:20])
                        # else:
                        #     remark = '%s,尽快把握商机' % (('正在查看' + obj.name))
                        if customer_id:
                            customer_obj = models.zgld_customer.objects.filter(id=customer_id)
                            if customer_obj and  customer_obj[0].username : # 说明客户访问时候经过认证的
                                remark = '%s,尽快把握商机' % (('正在查看' + obj.name))
                                data = request.GET.copy()
                                data['action'] = 2
                                action_record(data, remark)

                        #  查询成功 返回200 状态码
                        response.code = 200
                        response.msg = '查询成功'
                        response.data = {
                            'ret_data': ret_data,
                            'data_count': count,
                        }

                else:
                    response.code = 302
                    response.msg = "产品不存在"
            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'product_list':

            forms_obj = ProductSelectForm(request.GET)
            if forms_obj.is_valid():
                customer_id = request.GET.get('user_id')
                user_id = forms_obj.data['uid']

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-recommend_index')


                company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id

                # con = Q(Q('company_id', company_id) & Q(Q('user_id', user_id) | Q('user_id__isnull', True)))
                # print('con -->', con)

                con = Q()
                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))
                q1.children.append(('user_id', user_id))

                q2 = Q()
                q2.connector = 'and'
                q2.children.append(('company_id', company_id))
                q2.children.append(('user_id__isnull', True))

                con.add(q1, 'OR')
                con.add(q2, 'OR')
                print('-----con----->',con)

                objs = models.zgld_product.objects.select_related('user', 'company').filter(con).exclude(status=2).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []

                if objs:
                    for obj in objs:
                        product_id = obj.id

                        user_avatar = models.zgld_userprofile.objects.get(id=user_id).avatar
                        content = {
                            'cover_data': json.loads(obj.content).get('cover_data')

                        }

                        ret_data.append({
                            'id': product_id,
                            'name': obj.name ,# 标题
                            'price': obj.price,  # 价格
                            'user_avatar': user_avatar, #用户头像
                            'reason': obj.reason,       # 推荐理由
                            'publisher_date': obj.create_date,  # 发布日期。
                            'content': content,

                            'create_date': obj.create_date.strftime("%Y-%m-%d"),  # 发布的日期
                            'status': obj.get_status_display(),
                            'status_code': obj.status,  # 产品的动态。
                        })


                    if customer_id:
                        customer_obj = models.zgld_customer.objects.filter(id=customer_id)
                        if customer_obj and  customer_obj[0].username : # 说明客户访问时候经过认证的
                            remark = '正在查看您发布的产品,尽快把握商机'
                            data = request.GET.copy()
                            data['action'] = 2
                            action_record(data, remark)

                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        # 'chatinfo_count': chatinfo_count,  # 留言个数
                        'data_count': count,
                    }

                else:
                    response.code = 302
                    response.msg = '产品列表无数据'


            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'consult_product':
            forms_obj = ProductGetForm(request.GET)
            if forms_obj.is_valid():
                customer_id = request.GET.get('user_id')
                user_id = request.GET.get('uid')
                product_id = request.GET.get('product_id')


                picture_obj = models.zgld_product.objects.get(id=product_id)
                product_cover_url = json.loads(picture_obj.content).get('cover_data')[0]['data'][0]   # 产品价格
                product_price = picture_obj.price   # 产品价格
                product_name =  picture_obj.name    #产品民称
                product_id =  picture_obj.id    #产品民称

                new_product_cover_filename = str(uuid.uuid1())
                exit_product_cover_path = BASE_DIR + '/' +  product_cover_url
                file_type = exit_product_cover_path.split('.')[-1]

                new_filename = new_product_cover_filename + '.' + file_type

                new_product_cover_path =  "/".join((BASE_DIR, 'statics', 'zhugeleida', 'imgs','chat' ,new_filename))
                print('------new_product_cover_path------->>',new_product_cover_path)
                with open(exit_product_cover_path,'rb') as read_file:
                    with open(new_product_cover_path, 'wb') as new_file:
                      new_file.write(read_file.read())

                static_product_cover_url =  "/".join(( 'statics', 'zhugeleida', 'imgs', 'chat', new_filename))
                print('------static_product_cover_url---->>',static_product_cover_url)

                models.zgld_chatinfo.objects.filter(userprofile_id=user_id,customer_id=customer_id).update(is_last_msg=False)

                _content =  {
                    'info_type' : 2,  # (2,'product_info')   #客户和用户之间的产品咨询
                    'product_name' : product_name,
                    'product_price' : product_price,
                    'product_cover_url' : static_product_cover_url,
                    'product_id' : product_id
                }
                content = json.dumps(_content)

                obj = models.zgld_chatinfo.objects.create(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=2,  # 代表客户发送给用户
                    content=content
                    # info_type=2,  # (2,'product_info')   #客户和用户之间的产品咨询
                    # product_name=product_name,
                    # product_price=product_price,
                    # product_cover_url=static_product_cover_url,
                    )

                ## 记录客户咨询产品
                flow_up_objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id, customer_id=customer_id)
                # update(read_count=F('read_count') + 1)

                if flow_up_objs:  # 用戶發消息給客戶，修改最後跟進-時間
                    flow_up_objs.update(
                        is_customer_msg_num=F('is_customer_msg_num') + 1,
                        last_activity_time=datetime.datetime.now()
                    )

                remark = '向您咨询产品'
                data = request.GET.copy()
                data['action'] = 7 # 咨询产品
                action_record(data, remark)
                response.code = 200
                response.msg = "咨询产品返回成功"

        elif oper_type == 'forward_product':

            product_id = request.GET.get('product_id')
            objs = models.zgld_product.objects.filter(id=product_id)

            # if len(('转发了' + objs[0].name)) > 23:
            #     remark = '%s...' % (('转发了' + objs[0].name)[:23])
            # else:
            #     remark = '%s' % (('转发了' + objs[0].name))

            remark = '%s' % (('转发了' + objs[0].name))
            data = request.GET.copy()
            data['action'] = 2
            action_record(data, remark)
            response.code = 200
            response.msg = "记录转发产品成功"


    return JsonResponse(response.__dict__)


def sort_article_data(data):
    ret_list = []
    for obj in data:
        if not ret_list:
            # tmp_dict[obj['order']] = obj
            ret_list.append(obj)

        else:
            for index, data in enumerate(ret_list):
                if obj['order'] < data['order']:
                    ret_list.insert(index, obj)
                    break
            else:
                ret_list.append(obj)
    return ret_list













# # 展示单个的名片信息
# @csrf_exempt
# @account.is_token(models.zgld_customer)
# def product(request):
#     remark = '正在查看你发布的产品,尽快把握商机'
#     response = action_record(request, remark)
#
#
#     return JsonResponse(response.__dict__)
#
#
# # 展示全部的名片、记录各种动作到日志中
# @csrf_exempt
# @account.is_token(models.zgld_customer)
# def product_oper(request, oper_type):
#     response = Response.ResponseObj()
#     if request.method == 'GET':
#         if oper_type == '竞价排名':
#
#
#
#
#
#             remark = '正在查看你发布的产品,尽快把握商机'
#             response = action_record(request, remark)
#
#
#
#
#
#         elif oper_type == '转发':
#             remark = '转发了竞价排名。'
#             response = action_record(request, remark)
#
#
#     else:
#         response.code = 402
#         response.msg = "请求异常"
#
#     return JsonResponse(response.__dict__)
