from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom, action_record
from zhugeleida.forms.xiaochengxu.product_verify  import ProductSelectForm,ProductGetForm
import json
from django.db.models import Q
from django.db.models import F


@csrf_exempt
@account.is_token(models.zgld_customer)
def product(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        if oper_type == 'product_single':

            forms_obj = ProductGetForm(request.GET)
            if forms_obj.is_valid():

                customer_id = request.GET.get('user_id')
                user_id = request.GET.get('uid')
                product_id = request.GET.get('product_id')

                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                q.add(Q(**{'id': product_id}), Q.AND)


                objs = models.zgld_product.objects.select_related('user', 'company').filter(q)
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
                        user_avatar = models.zgld_userprofile.objects.get(id=user_id).avatar

                        ret_data.append({
                            'id': obj.id,
                            'publisher_date': obj.create_date,  # 发布日期。
                            'cover_picture': list(cover_picture_data) or '',  # 封面地址的URL
                            'name': obj.name,  # 产品名称
                            'price': obj.price,  # 价格
                            'user_avatar': user_avatar,

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
                q1.children.append(('user_id', user_id))
                q1.children.append(('company_id', company_id))
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

                if objs:
                    for obj in objs:
                        product_id = obj.id

                        picture_url = models.zgld_product_picture.objects.filter(
                                    product_id=product_id, picture_type=1
                        ).order_by('create_date')[0].picture_url
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
                            'status_code': obj.status  # 产品的动态。

                        })

                        remark = '正在查看您发布的产品,尽快把握商机'
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
                    response.msg = '产品列表无数据'


            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

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