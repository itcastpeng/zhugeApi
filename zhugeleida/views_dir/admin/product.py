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
from zhugeleida.forms.admin.product_verify import ProductSelectForm, ProductGetForm,ProductAddForm,imgMergeForm,imgUploadForm
from zhugeleida.forms.qiyeweixin.product_verify import  ProductUpdateForm
import json
from django.db.models import Q
from django.db.models import F
import uuid
import os
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BasePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == 'product_edit':
            product_type = int(request.GET.get('product_type')) if request.GET.get('product_type') else ''

            if product_type  == 1:     #单个官网产品展示
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
            print('request.GET----->', request.GET)
            forms_obj = ProductSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                product_type = forms_obj.cleaned_data.get('product_type')

                print('product_type----->',request.GET.get('product_type'),product_type)

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
                    print('-----q1---->>',q1)
                    objs = models.zgld_product.objects.select_related('user', 'company').filter(q1).order_by(order)
                    count = objs.count()
                    print('-----objs----->>',objs)

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
        elif oper_type == "add_temp":

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

                product_type = int(request.POST.get('product_type')) if request.POST.get('product_type') else ''

                if product_type == 1:  # 单个官网产品展示
                    user_id = request.GET.get('user_id')

                    cover_picture_list = json.loads(request.POST.get('cover_picture_data'))
                    article_data_list = json.loads(request.POST.get('article_data'))

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
                    cover_obj_list = []
                    for obj in cover_picture_list:
                        cover_obj = models.zgld_product_picture(
                            picture_url=obj.get('picture_url'),
                            picture_type = 1,
                            product_id=product_id,
                            order=obj.get('order')
                        )
                        cover_obj_list.append(cover_obj)
                    models.zgld_product_picture.objects.bulk_create(cover_obj_list)

                    #产品图片绑定到产品。

                    product_picture_list = []
                    for obj in article_data_list:
                        picture_obj = models.zgld_product_picture(
                            picture_url=obj.get('picture_url'),
                            picture_type =2,
                            product_id= product_id,
                            order=obj.get('order')
                        )
                        product_picture_list.append(picture_obj)
                    models.zgld_product_picture.objects.bulk_create(product_picture_list)

                    # if article_data_list:
                    #     for article_data in article_data_list:
                    #         print('article_data_list 2 ------>>', article_data, type(article_data))
                    #
                    #         if  'picture_id' in article_data:
                    #             picture_id = article_data.get('picture_id')
                    #             picture_obj = models.zgld_product_picture.objects.filter(id=picture_id)
                    #             picture_obj.update(product_id=product_id, order=article_data.get('order'))

                    response.code = 200
                    response.msg = "添加成功"



                elif product_type == 2:  #个人产品
                    user_id = request.GET.get('user_id')

                    cover_picture_list = json.loads(request.POST.get('cover_picture_data'))
                    article_data_list = json.loads(request.POST.get('article_data'))

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
                    cover_obj_list = []
                    for obj in cover_picture_list:
                        cover_obj = models.zgld_product_picture(
                            picture_url=obj.get('picture_url'),
                            picture_type = 1,
                            product_id=product_id,
                            order=obj.get('order')
                        )
                        cover_obj_list.append(cover_obj)
                    models.zgld_product_picture.objects.bulk_create(cover_obj_list)

                    #产品图片绑定到产品。

                    product_picture_list = []
                    for obj in article_data_list:
                        picture_obj = models.zgld_product_picture(
                            picture_url=obj.get('picture_url'),
                            picture_type =2,
                            product_id= product_id,
                            order=obj.get('order')
                        )
                        product_picture_list.append(picture_obj)
                    models.zgld_product_picture.objects.bulk_create(product_picture_list)




            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update_temp":
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

                product_type = int(request.POST.get('product_type')) if request.POST.get('product_type') else ''

                if product_type == 1:  # 单个官网产品修改

                    user_id = request.GET.get('user_id')
                    cover_picture_list = request.POST.get('cover_picture_data')
                    article_data_list = request.POST.get('article_data')

                    product_obj = models.zgld_product.objects.filter(id=o_id)
                    product_obj.update(
                        user_id=user_id,

                        name=forms_obj.data.get('name'),
                        price=forms_obj.data.get('price'),
                        reason=forms_obj.data.get('reason'),
                    )
                    product_obj.save()

                    # 封面图片数据绑定到产品。
                    product_id = product_obj.id
                    cover_objs = models.zgld_product_picture.objects.filter(id=product_id, picture_type=1, )
                    if cover_objs:
                        cover_objs.update(
                            picture_url=cover_picture_list
                        )

                    # 产品图片数据绑定到产品。
                    product_picture_objs = models.zgld_product_picture.objects.filter(id=product_id,picture_type=2,)
                    if product_picture_objs:
                        product_picture_objs.update(
                            picture_url = article_data_list
                        )
                    response.code = 200
                    response.msg = "添加成功"


                elif product_type == 2:  # 单个个人产品修改
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

                        cover_picture_list = json.loads(request.POST.get('cover_picture_data'))
                        article_data_list = json.loads(request.POST.get('article_data'))

                        company_id = models.zgld_userprofile.objects.get(id=user_id).company_id

                        product_obj = models.zgld_product.objects.filter(id=o_id)
                        product_obj.update(
                            user_id=user_id,
                            company_id=company_id,
                            name=forms_obj.data.get('name'),
                            price=forms_obj.data.get('price'),
                            reason=forms_obj.data.get('reason'),
                        )
                        product_obj.save()

                        # 封面图片数据绑定到产品。
                        product_id = product_obj.id
                        cover_objs = models.zgld_product_picture.objects.filter(id=product_id, picture_type=1, )
                        if cover_objs:
                            cover_objs.update(
                                picture_url=cover_picture_list
                            )

                        # 产品图片数据绑定到产品。
                        product_picture_objs = models.zgld_product_picture.objects.filter(id=product_id,
                                                                                          picture_type=2, )
                        if product_picture_objs:
                            product_picture_objs.update(
                                picture_url=article_data_list
                            )

                        response.code = 200
                        response.msg = "添加成功"


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "change_status":

            status = int(request.POST.get('status'))
            user_id = int(request.GET.get('user_id'))
            product_objs = models.zgld_product.objects.filter(id=o_id)
            print('product_objs--------->', product_objs)

            if product_objs:

                if not product_objs[0].user_id:  # 用户ID不存在，说明它是企业发布的产品，只能被推荐和取消推荐，不能被下架和上架。
                    product_objs.update(
                        status=status
                    )
                    response.code = 200
                    response.msg = "修改状态成功"
                    response.data = {
                        'product_id': product_objs[0].id,
                        'status': product_objs[0].get_status_display(),
                        'status_code': product_objs[0].status
                    }




            else:

                response.code = 302
                response.msg = '产品不存在'

        if oper_type == "update":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'product_id': o_id,  # 标题    非必须
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格    非必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                # 'article_id': request.POST.get('article_id'),  # 内容    非必须
            }
            product_type = int(request.POST.get('product_type')) if request.POST.get('product_type') else ''

            forms_obj = ProductUpdateForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                product_id = forms_obj.data.get('product_id')
                article_data_list = json.loads(request.POST.get('article_data'))
                cover_picture_list = json.loads(request.POST.get('cover_picture_id'))



                product_obj = models.zgld_product.objects.filter(id=product_id)

                product_obj.update(
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )
                exist_cover_picture_list = []
                picture_list = list(
                    models.zgld_product_picture.objects.filter(product_id=product_id, picture_type=1).values_list('id'))
                for p in picture_list:
                    exist_cover_picture_list.append(p[0])

                delete_cover_picture_list = list(set(exist_cover_picture_list).difference(set(cover_picture_list)))
                print('----delete_cover_picture_list-->>', delete_cover_picture_list)

                delete_cover_picture_objs = models.zgld_product_picture.objects.filter(id__in=delete_cover_picture_list)

                if delete_cover_picture_objs:  # 要删除的封面图片。
                    for delete_picture_obj in delete_cover_picture_objs:
                        IMG_PATH = BASE_DIR + '/' + delete_picture_obj.picture_url
                        if os.path.exists(IMG_PATH): os.remove(IMG_PATH)
                    delete_cover_picture_objs.delete()

                product_id = product_obj[0].id
                picture_objs = models.zgld_product_picture.objects.filter(
                    id__in=cover_picture_list)  # 更新前端传过来的封面ID绑定到数据库。
                picture_objs.update(product_id=product_id)

                now_picture_list = []
                now_article_list = []
                if article_data_list:

                    for article_data in article_data_list:
                        if 'picture_id' in article_data:
                            picture_id = article_data.get('picture_id')
                            now_picture_list.append(picture_id)

                    exist_product_picture_list = []
                    picture_list = list(
                        models.zgld_product_picture.objects.filter(product_id=product_id, picture_type=2).values_list(
                            'id'))
                    for p in picture_list:
                        exist_product_picture_list.append(p[0])

                    delete_product_picture_list = list(
                        set(exist_product_picture_list).difference(set(now_picture_list)))
                    print('----delete_product_picture_list-->>', delete_product_picture_list)

                    delete_product_picture_objs = models.zgld_product_picture.objects.filter(
                        id__in=delete_product_picture_list)

                    if delete_product_picture_objs:  # 要删除的产品图片。
                        for delete_picture_obj in delete_product_picture_objs:
                            IMG_PATH = BASE_DIR + '/' + delete_picture_obj.picture_url
                            if os.path.exists(IMG_PATH): os.remove(IMG_PATH)
                        delete_product_picture_objs.delete()

                    ## 比较新穿过来的文章列表和已经存在数据库的文章的ID的差级
                    for article_data in article_data_list:
                        if 'article_id' in article_data:
                            article_id = article_data.get('article_id')
                            now_article_list.append(article_id)

                    exist_article_list = []
                    article_list = models.zgld_product_article.objects.filter(product_id=product_id).values_list('id')
                    for a in article_list:
                        exist_article_list.append(a[0])

                    delete_article_list = list(set(exist_article_list).difference(set(now_article_list)))
                    print('--------delete_article_list------->>', delete_article_list)
                    delete_article_objs = models.zgld_product_article.objects.filter(id__in=delete_article_list)

                    if delete_article_objs:  # 要删除的文章内容的ID。
                        delete_article_objs.delete()

                    for article_data in article_data_list:
                        print('article_data_list 2 ------>>', article_data, type(article_data))
                        article_id = article_data.get('article_id')

                        if 'article_id' in article_data and 'title' in article_data:
                            obj = models.zgld_product_article.objects.filter(product_id=product_id, id=article_id)
                            obj.update(
                                title=article_data.get('title'),
                                type=1,
                                order=article_data.get('order')
                            )


                        elif 'article_id' in article_data and 'content' in article_data:
                            obj = models.zgld_product_article.objects.filter(product_id=product_id, id=article_id)
                            obj.update(
                                content=article_data.get('content'),
                                type=2,
                                order=article_data.get('order')
                            )


                        elif 'article_id' not in article_data and 'title' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                title=article_data.get('title'),
                                type=1,
                                order=article_data.get('order')
                            )

                        elif 'article_id' not in article_data and 'content' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                content=article_data.get('content'),
                                type=2,
                                order=article_data.get('order')
                            )
                        elif 'picture_id' in article_data:
                            picture_id = article_data.get('picture_id')
                            picture_obj = models.zgld_product_picture.objects.filter(id=picture_id)
                            picture_obj.update(product_id=product_id, order=article_data.get('order'))

                    response.code = 200
                    response.msg = "添加成功"
                else:
                    objs = models.zgld_product_article.objects.filter(product_id=product_id)
                    if objs:
                        objs.delete()

                    response.code = 200
                    response.msg = "添加成功"


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "add":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格     必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                # 'title': request.POST.get('title'),    # 标题    非必须
                # 'content': request.POST.get('content'),  # 内容    非必须
            }
            product_type = int(request.POST.get('product_type')) if request.POST.get('product_type') else ''

            forms_obj = ProductAddForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                article_data_list = json.loads(request.POST.get('article_data'))
                cover_picture_list = json.loads(request.POST.get('cover_picture_id'))

                global product_owner
                if product_type == 1:             #代表公司产品
                    product_owner = ''
                elif product_type == 2:           #代表个人产品
                    product_owner = user_id

                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                product_obj = models.zgld_product.objects.create(
                    user_id=product_owner,
                    company_id=company_id,
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )

                # 封面图片绑定到产品。
                product_id = product_obj.id
                picture_objs = models.zgld_product_picture.objects.filter(id__in=cover_picture_list)
                picture_objs.update(product_id=product_id)

                if article_data_list:
                    print('article_data_list 1 ------>>', article_data_list, type(article_data_list))
                    for article_data in article_data_list:
                        print('article_data_list 2 ------>>', article_data, type(article_data))
                        if 'title' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                title=article_data.get('title'),
                                type=1,
                                order=article_data.get('order')

                            )
                        elif 'content' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                content=article_data.get('content'),
                                type=2,
                                order=article_data.get('order')
                            )
                        elif 'picture_id' in article_data:
                            picture_id = article_data.get('picture_id')
                            picture_obj = models.zgld_product_picture.objects.filter(id=picture_id)
                            picture_obj.update(product_id=product_id, order=article_data.get('order'))

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 上传产品图片的接口
        elif oper_type == "add_picture":
            response = Response.ResponseObj()

            forms_obj = imgUploadForm(request.POST)
            if forms_obj.is_valid():
                img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
                timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
                img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
                chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
                expanded_name = img_name.split('.')[-1]  # 扩展名

                img_name = timestamp + "_" + str(chunk) + '.' + expanded_name

                img_save_path = "/".join(
                    [BasePath, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product', 'tmp', img_name])
                print('img_save_path -->', img_save_path)
                # print('img_data -->', img_data)
                img_data = base64.b64decode(img_data.encode('utf-8'))
                with open(img_save_path, 'wb') as f:
                    f.write(img_data)

                response.code = 200
                response.msg = "上传成功"
            else:
                response.code = 303
                response.msg = "上传异常"
                response.data = json.loads(forms_obj.errors.as_json())
            return JsonResponse(response.__dict__)

        # 产品图片合并请求
        elif oper_type == "upload_complete":

            response = Response.ResponseObj()
            forms_obj = imgMergeForm(request.POST)
            if forms_obj.is_valid():
                img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
                timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
                chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
                expanded_name = img_name.split('.')[-1]  # 扩展名
                picture_type = forms_obj.cleaned_data.get('picture_type')  # 图片的类型  (1, '产品封面的图片'), (2, '产品介绍的图片')

                img_name = timestamp + '.' + expanded_name
                img_path = "/".join(['statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product', img_name])
                img_save_path = "/".join([BasePath, img_path])
                file_obj = open(img_save_path, 'ab')
                for chunk in range(chunk_num):
                    file_name = timestamp + "_" + str(chunk) + '.' + expanded_name

                    file_save_path = "/".join(
                        [BasePath, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product', 'tmp', file_name])

                    with open(file_save_path, 'rb') as f:
                        file_obj.write(f.read())
                        # file_content += f.read()
                    os.remove(file_save_path)

                product_picture_obj = models.zgld_product_picture.objects.create(picture_type=picture_type,
                                                                                 picture_url=img_path)

                response.data = {
                    'picture_type': product_picture_obj.picture_type,
                    'picture_id': product_picture_obj.id,
                    'picture_url': product_picture_obj.picture_url,

                }
                response.code = 200
                response.msg = "添加图片成功"

            else:
                response.code = 303
                response.msg = "上传异常"
                response.data = json.loads(forms_obj.errors.as_json())



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

