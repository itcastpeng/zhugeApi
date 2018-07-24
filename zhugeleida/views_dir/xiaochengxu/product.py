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
from django.db.models import Q
from django.db.models import F
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
                    for obj in objs:
                        cover_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                        picture_type=1).order_by(
                            'create_date').values('id', 'picture_url')

                        product_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                          picture_type=2).values('id',
                                                                                                                 'order',
                                                                                                                 'picture_url')

                        article_data = models.zgld_product_article.objects.filter(product_id=obj.id).values('id', 'order',
                                                                                                            'content',
                                                                                                            'title')

                        article_picture_list = []
                        article_picture_list.extend(product_picture_data)
                        article_picture_list.extend(article_data)

                        print('---article_picture_list-->>', article_picture_list)

                        # article_content_data = models.zgld_product_article.objects.filter(type=2).values_list('id','order','content')
                        ret_data_list = sort_article_data(list(article_picture_list))
                        user_obj = models.zgld_userprofile.objects.get(id=user_id)
                        user_avatar = user_obj.avatar
                        username = user_obj.username
                        position = user_obj.position

                        ret_data.append({
                            'id': obj.id,
                            'publisher_date': obj.create_date,  # 发布日期。
                            'cover_picture': list(cover_picture_data) or '',  # 封面地址的URL
                            'name': obj.name,  # 产品名称
                            'price': obj.price,  # 价格
                            'user_avatar': user_avatar,
                            'username': username,
                            'position': position,
                            'reason': obj.reason,  # 推荐理由
                            'article_data': ret_data_list,
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
                                response = action_record(data, remark)

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
                order = request.GET.get('order', '-create_date')


                company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id

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

                objs = models.zgld_product.objects.select_related('user', 'company').filter(con).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                chatinfo_count = 0
                if customer_id:
                    chatinfo_count = models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                                         send_type=1, is_customer_new_msg=True).count()

                if objs:
                    for obj in objs:
                        product_id = obj.id

                        picture_obj = models.zgld_product_picture.objects.filter(
                                    product_id=product_id, picture_type=1
                        ).order_by('create_date')
                        picture_url = ''
                        if picture_obj:
                            picture_url = picture_obj[0].picture_url

                        user_avatar = models.zgld_userprofile.objects.get(id=user_id).avatar

                        ret_data.append({
                            'id': product_id,
                            'name': obj.name ,# 标题
                            'price': obj.price,  # 价格
                            'user_avatar': user_avatar, #用户头像
                            'reason': obj.reason,       # 推荐理由
                            'publisher_date': obj.create_date,  # 发布日期。
                            'cover_picture': picture_url,  # 封面地址的URL

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
                            response = action_record(data, remark)

                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'chatinfo_count': chatinfo_count,  # 留言个数
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


                picture_obj = models.zgld_product_picture.objects.filter(product_id=product_id,picture_type=1)[:1]
                product_cover_url = picture_obj[0].picture_url # 产品封面URL
                product_price = picture_obj[0].product.price   # 产品价格
                product_name =  picture_obj[0].product.name    #产品民称

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
                obj = models.zgld_chatinfo.objects.create(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=2,  # 代表客户发送给用户
                    info_type=2,  # (2,'product_info')   #客户和用户之间的产品咨询
                    product_name=product_name,
                    product_price=product_price,
                    product_cover_url=static_product_cover_url,
                    )


                remark = '向您咨询产品'
                data = request.GET.copy()
                data['action'] = 2  # 咨询产品
                response = action_record(data, remark)
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
            response = action_record(data, remark)
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
