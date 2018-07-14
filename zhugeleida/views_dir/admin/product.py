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
from zhugeleida.forms.admin.product_verify import ProductSelectForm, ProductGetForm,ProductAddForm

import json
from django.db.models import Q
from django.db.models import F
import uuid
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == 'product_edit':
            product_type = int(request.GET.get('product_type')) if request.GET.get('product_type') else ''

            if int(product_type) == 1:     #单个官网产品展示
                user_id = request.GET.get('user_id')
                product_id = request.GET.get('product_id')
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id
                q.add(Q(**{'company_id': company_id}), Q.AND)
                q.add(Q(**{'id': product_id}), Q.AND)
                q.add(Q(**{'user_id__isnull': True }), Q.AND)


                objs = models.zgld_product.objects.select_related('user', 'company').filter(q)
                count = objs.count()

                if objs:
                    ret_data = []
                    for obj in objs:
                        if obj.user_id:
                            if int(obj.user_id) == int(user_id):
                                publisher = '我添加的'
                            else:
                                publisher = obj.user.username + '添加的'
                        else:
                            publisher = '企业发布'

                        cover_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                        picture_type=1).order_by(
                            'create_date').values('id', 'picture_url')

                        product_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                          picture_type=2).order_by(
                            'create_date').values('id',
                                                  'order',
                                                  'picture_url')

                        ret_data.append({
                            'id': obj.id,

                            'publisher': publisher,  # 发布者
                            'publisher_date': obj.create_date,  # 发布日期。
                            'cover_picture': list(cover_picture_data) or '',  # 封面地址的URL
                            'name': obj.name,  # 产品名称  必填
                            'price': obj.price,  # 价格     必填
                            'reason': obj.reason,  # 推荐理由

                            # 'article_data': ret_data_list,
                            'product_picture_list': list(product_picture_data),  # 产品的列表
                            'create_date': obj.create_date.strftime("%Y-%m-%d"),  # 发布的日期
                            'status': obj.get_status_display(),  # 产品的动态
                            'status_code': obj.status  # 产品的动态值。

                        })
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

            elif product_type == 2:  # 单个个人产品展示
                user_id = request.GET.get('user_id')
                product_id = request.GET.get('product_id')
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id
                q.add(Q(**{'company_id': company_id}), Q.AND)
                q.add(Q(**{'id': product_id}), Q.AND)
                q.add(Q(**{'user_id': user_id }), Q.AND)

                objs = models.zgld_product.objects.select_related('user', 'company').filter(q)
                count = objs.count()

                if objs:
                    ret_data = []
                    for obj in objs:
                        if obj.user_id:
                            publisher = obj.user.username + '添加的'
                        else:
                            publisher = '企业发布'

                        cover_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                        picture_type=1).order_by(
                            'create_date').values('id', 'picture_url')

                        product_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                          picture_type=2).values('id',
                                                                                                                 'order',
                                                                                                                 'picture_url')

                        article_data = models.zgld_product_article.objects.filter(product_id=obj.id).values('id',
                                                                                                            'order',
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

                            'publisher': publisher,  # 发布者
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


        elif oper_type == 'product_list':

            forms_obj = ProductSelectForm(request.GET)
            if forms_obj.is_valid():
                product_type = forms_obj.cleaned_data.get('product_type')

                # 如果为1 代表是公司的官网
                if product_type == 1:

                    user_id = request.GET.get('user_id')
                    current_page = forms_obj.cleaned_data['current_page']
                    length = forms_obj.cleaned_data['length']
                    order = request.GET.get('order', '-create_date')

                    q1 = Q()
                    q1.connector = 'and'
                    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
                    company_id = user_obj.company_id
                    role_id = user_obj.role_id
                    q1.children.append(('user_id__isnull', True))

                    if role_id == 1:  # 为管理员 展示出所有公司的产品
                        search_company_id = request.GET.get('company_id')  # 当有搜索条件,如 公司搜索
                        if search_company_id:
                            q1.children.append(('company_id', search_company_id))

                    elif role_id == 2:  # 为普通用户 展示出自己所属公司的产品
                        q1.children.append(('company_id', company_id))

                    search_product_name = request.GET.get('product_name')  # 当有搜索条件 如 搜索产品名称
                    if search_product_name:
                        q1.children.append(('name__contains', search_product_name))

                    search_product_status = request.GET.get('status')  # 当有搜索条件 如 搜索上架或者不上架的
                    if not search_product_status:
                        q1.children.append(('status__in', [1, 3]))  # 默认是显示出所有的上架的产品
                    else:
                        if int(search_product_status) == 1:
                            q1.children.append(('status__in', [1, 3]))  # (1,'已上架')

                        elif int(search_product_status) == 2:
                            q1.children.append(('status__in', [2]))  # (2,'已下架')

                    objs = models.zgld_product.objects.select_related('user', 'company').filter(q1).order_by(order)
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

                            ret_data.append({
                                'product_id': product_id,
                                'cover_picture': picture_url,  # 封面地址的URL
                                'name': obj.name,  # 产品名称
                                'price': obj.price,  # 价格
                                'publisher_date': obj.create_date.strftime("%Y-%m-%d %H:%M:%S"),  # 发布日期。
                                'publisher': obj.company.name,  # 发布者
                                'status': obj.get_status_display(),
                                'status_code': obj.status  # 产品的动态。
                            })

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

                # 如果为2 代表个人产品列表
                elif product_type == 2:

                    user_id = request.GET.get('user_id')
                    current_page = forms_obj.cleaned_data['current_page']
                    length = forms_obj.cleaned_data['length']
                    order = request.GET.get('order', '-create_date')

                    q1 = Q()
                    q1.connector = 'and'
                    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
                    company_id = user_obj.company_id
                    role_id = user_obj.role_id
                    q1.children.append(('user_id__isnull', False))

                    if role_id == 1:  # 为管理员 展示出所有公司的产品
                        search_company_id = request.GET.get('company_id')  # 当有搜索条件,如 公司搜索
                        if search_company_id:
                            q1.children.append(('company_id', search_company_id))

                    elif role_id == 2:  # 为普通用户 展示出自己所属公司的产品
                        q1.children.append(('company_id', company_id))

                    search_product_name = request.GET.get('product_name')  # 当有搜索条件 如 搜索产品名称
                    if search_product_name:
                        q1.children.append(('name__contains', search_product_name))

                    search_product_status = request.GET.get('status')  # 当有搜索条件 如 搜索上架或者不上架的
                    if not search_product_status:
                        q1.children.append(('status__in', [1, 3]))  # 默认是显示出所有的上架的产品
                    else:
                        if int(search_product_status) == 1:
                            q1.children.append(('status__in', [1, 3]))  # (1,'已上架')

                        elif int(search_product_status) == 2:
                            q1.children.append(('status__in', [2]))  # (2,'已下架')

                    objs = models.zgld_product.objects.select_related('user', 'company').filter(q1).order_by(order)
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

                            ret_data.append({
                                'product_id': product_id,
                                'cover_picture': picture_url,  # 封面地址的URL
                                'name': obj.name,  # 产品名称
                                'price': obj.price,  # 价格
                                'publisher_date': obj.create_date.strftime("%Y-%m-%d %H:%M:%S"),  # 发布日期。
                                'publisher': obj.user.username,  # 发布者
                                'status': obj.get_status_display(),
                                'status_code': obj.status  # 产品的动态。
                            })

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

    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 删除-个人产品
        if oper_type == "delete":
            user_id = request.GET.get('user_id')
            user_obj =  models.zgld_userprofile.objects.filter(id=user_id)
            role_id = user_obj[0].role_id
            company_id = user_obj[0].company_id
            product_picture_objs = models.zgld_product_picture.objects.filter(product_id=o_id)
            product_article_objs = models.zgld_product_article.objects.filter(product_id=o_id)

            if role_id == 1:  # 管理员 ，能删除官网的产品和个人的所有的产品。
                product_objs = models.zgld_product.objects.filter(id=o_id)
                if product_objs:
                    product_objs.delete()
                    product_picture_objs.delete()
                    product_article_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"

            elif role_id == 2:  # 普通用户只能删除自己的公司的个人产品。
                product_objs = models.zgld_product.objects.filter(id=o_id, user_id__isnull=False, company_id=company_id,)

                if product_objs:
                    product_objs.delete()
                    product_picture_objs.delete()
                    product_article_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '产品不存在'

        # 添加-公司产品。不能添加个人产品
        elif oper_type == "add":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格     必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                # 'title': request.POST.get('title'),    # 标题    非必须
                # 'content': request.POST.get('content'),  # 内容    非必须
            }

            forms_obj = ProductAddForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                article_data_list = json.loads(request.POST.get('article_data'))
                cover_picture_list = json.loads(request.POST.get('cover_picture_id'))

                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                product_obj = models.zgld_product.objects.create(
                    user_id=user_id,
                    company_id=company_id,
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )


                #封面图片绑定到产品。
                product_id = product_obj.id
                picture_objs = models.zgld_product_picture.objects.filter(id__in=cover_picture_list)
                picture_objs.update(product_id=product_id)

                if article_data_list:
                    for article_data in article_data_list:
                        print('article_data_list 2 ------>>', article_data, type(article_data))

                        if  'picture_id' in article_data:
                            picture_id = article_data.get('picture_id')
                            picture_obj = models.zgld_product_picture.objects.filter(id=picture_id)
                            picture_obj.update(product_id=product_id, order=article_data.get('order'))

                    response.code = 200
                    response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())








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

