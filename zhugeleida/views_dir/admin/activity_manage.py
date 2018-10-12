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
from zhugeleida.forms.admin.activity_manage_verify import SetFocusGetRedPacketForm, ActivityAddForm, FeedbackSelectForm

import json
from django.db.models import Q

import os
import base64


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def activity_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 设置关注领红包
        if oper_type == 'set_focus_get_redPacket':

            is_focus_get_redpacket = request.POST.get('is_focus_get_redpacket')
            focus_get_money = request.POST.get('focus_get_money')
            focus_total_money = request.POST.get('focus_total_money')
            user_id = request.GET.get('user_id')

            form_data = {
                'is_focus_get_redpacket': is_focus_get_redpacket,
                'focus_get_money': focus_get_money,
                'focus_total_money': focus_total_money,
            }

            forms_obj = SetFocusGetRedPacketForm(form_data)
            if forms_obj.is_valid():
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
                gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

                if gongzhonghao_app_objs:
                    gongzhonghao_app_objs.update(
                        is_focus_get_redpacket=is_focus_get_redpacket,
                        focus_get_money=focus_get_money,
                        focus_total_money=focus_total_money
                    )
                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '设置成功'

                else:
                    response.code = 301
                    response.msg = '公众号不存在'


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        elif oper_type == 'product_list':
            print('request.GET----->', request.GET)
            forms_obj = ProductSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                product_type = forms_obj.cleaned_data.get('product_type')

                # 如果为1 代表是公司的官网
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-recommend_index')

                q1 = Q()
                q1.connector = 'and'
                user_obj = models.zgld_admin_userprofile.objects.filter(id=user_id)[0]
                company_id = user_obj.company_id
                # role_id = user_obj.role_id

                if product_type == 1:  # 展示公司 产品
                    q1.children.append(('user_id__isnull', True))
                elif product_type == 2:  # 展示个人 产品
                    q1.children.append(('user_id__isnull', False))

                # if role_id == 1:  # 为超级管理员 展示出所有公司的产品
                #     search_company_id = request.GET.get('company_id')  # 当有搜索条件,如 公司搜索
                #     if search_company_id:
                #         q1.children.append(('company_id', search_company_id))
                #
                # elif role_id == 2:  # 为管理员 展示出自己所属公司的产品
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

                print('-----q1---->>', q1)
                objs = models.zgld_product.objects.select_related('user', 'company').filter(q1).order_by(order)
                count = objs.count()
                print('-----objs----->>', objs)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []

                if objs:
                    for obj in objs:
                        product_id = obj.id

                        if obj.user_id:
                            publisher = obj.user.username
                        else:
                            publisher = obj.company.name

                        content = {
                            'cover_data': json.loads(obj.content).get('cover_data')

                        }

                        ret_data.append({
                            'product_id': product_id,
                            'content': content,  # 封面地址的URL
                            'name': obj.name,  # 产品名称
                            'price': obj.price,  # 价格
                            'publisher_date': obj.create_date.strftime("%Y-%m-%d %H:%M:%S"),  # 发布日期。
                            'publisher': publisher,  # 发布者
                            'status': obj.get_status_display(),
                            'recommend_index': obj.recommend_index,  # 产品推荐指数
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
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())


        elif oper_type == 'feedback_list':
            user_id = request.GET.get('user_id')

            user_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
            role_id = user_obj.role_id
            print('-----role id ---->>', role_id)
            forms_obj = FeedbackSelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                if int(role_id) == 1:  # 为超级管理员 展示出所有公司的产品
                    search_company_id = request.GET.get('company_id')  # 当有搜索条件,如 公司搜索
                    field_dict = {
                        'id': '',
                        'company__name': '__contains',
                        'status': '',

                    }

                    q = conditionCom(request, field_dict)
                    if search_company_id:
                        q.add(Q(**{'user__company_id': search_company_id}), Q.AND)

                    objs = models.zgld_user_feedback.objects.select_related('user').filter(q).order_by(order)
                    count = objs.count()
                    print('-----objs----->>', objs)

                    ret_data = []
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    if objs:
                        for obj in objs:
                            ret_data.append({
                                'id': obj.id,
                                'user_id': obj.user_id,
                                'user_name': obj.user.username,
                                'problem_type': obj.problem_type,
                                'problem_type_text': obj.get_problem_type_display(),
                                'content': json.loads(obj.content),
                                'company_name': obj.user.company.name,
                                'company_id': obj.user.company_id,
                                'status': obj.status,
                                'status_text': obj.get_status_display()
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
                    response.msg = '列表无数据'

            return JsonResponse(response.__dict__)


    else:
        # 查询关注红包
        if  oper_type == 'query_focus_get_redPacket':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

            if objs:
                obj = objs[0]
                is_focus_get_redpacket = obj.is_focus_get_redpacket
                focus_get_money = obj.focus_get_money
                focus_total_money = obj.focus_total_money
                #  查询成功 返回200 状态码
                response.data = {
                    'is_focus_get_redpacket': is_focus_get_redpacket,  # 关注领取红包是否(开启)
                    'focus_get_money': focus_get_money,  # 关注领取红包金额
                    'focus_total_money': focus_total_money  # 红包总金额
                }
                response.code = 200
                response.msg = '设置成功'

            else:
                response.code = 301
                response.msg = '公众号不存在'

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def activity_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 删除-个人产品
        if oper_type == "delete":
            user_id = request.GET.get('user_id')
            user_obj = models.zgld_admin_userprofile.objects.filter(id=user_id)
            role_id = user_obj[0].role_id
            company_id = user_obj[0].company_id

            # if role_id == 1:  # 管理员 ，能删除官网的产品和个人的所有的产品。
            product_objs = models.zgld_product.objects.filter(id=o_id, company_id=company_id)
            if product_objs:
                product_objs.delete()

                response.code = 200
                response.msg = "删除成功"

            # elif role_id == 2 or role_id == 3:  # 普通用户只能删除自己的公司的个人产品。
            #     product_objs = models.zgld_product.objects.filter(id=o_id, company_id=company_id)
            #
            #     if product_objs:
            #         product_objs.delete()
            #
            #         response.code = 200
            #         response.msg = "删除成功"

            else:
                response.code = 301
                response.msg = '产品不存在'

        elif oper_type == "change_status":
            print('-------change_status------->>', request.POST)
            status = int(request.POST.get('status'))
            user_id = request.GET.get('user_id')
            product_objs = models.zgld_product.objects.filter(id=o_id)
            print('product_objs--------->', product_objs)

            if product_objs:

                # if not product_objs[0].user_id:  # 用户ID不存在，说明它是企业发布的产品，只能被推荐和取消推荐，不能被下架和上架。
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


        elif oper_type == "update":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'product_id': o_id,  # 标题    非必须
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格    非必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                'content': request.POST.get('content'),  # 内容 非必须
            }

            forms_obj = ProductUpdateForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                product_id = forms_obj.cleaned_data.get('product_id')

                product_obj = models.zgld_product.objects.filter(id=product_id)
                product_obj.update(
                    name=forms_obj.cleaned_data.get('name'),
                    price=forms_obj.cleaned_data.get('price'),
                    reason=forms_obj.cleaned_data.get('reason'),
                    content=forms_obj.cleaned_data.get('content')
                )

                response.code = 200
                response.msg = "添加成功"


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "add":

            user_id =  request.GET.get('user_id')
            company_id =  request.GET.get('company_id')
            activity_name =  request.POST.get('activity_name')
            article_id =  request.POST.get('article_id'),  # 文章ID
            activity_total_money =  request.POST.get('activity_total_money')
            activity_single_money = request.POST.get('activity_single_money')
            reach_forward_num =  request.POST.get('reach_forward_num')
            start_time = request.POST.get('start_time')
            end_time =  request.POST.get('end_time')

            form_data = {

                'company_id': company_id,
                'activity_name': activity_name,     # 活动名称
                'article_id': article_id,  # 文章ID
                'activity_total_money': activity_total_money,    # 活动总金额(元)
                'activity_single_money':activity_single_money,  # 单个金额(元)
                'reach_forward_num': reach_forward_num,  # 达到多少次发红包(转发次数)
                'start_time':start_time,  # 达到多少次发红包(转发次数)
                'end_time':end_time,  # 达到多少次发红包(转发次数)
            }

            forms_obj = ActivityAddForm(form_data)
            if forms_obj.is_valid():

                models.zgld_gongzhonghao_app.objects.filter(id=company_id)

                product_obj = models.zgld_product.objects.create(

                    company_id=company_id,
                    name=forms_obj.cleaned_data.get('name'),
                    price=forms_obj.cleaned_data.get('price'),
                    reason=forms_obj.cleaned_data.get('reason'),
                )


                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        ## 修改推荐指数-影响产品展示排序。
        elif oper_type == 'recommend_index':
            form_data = {
                'user_id': request.GET.get('user_id'),
                'product_id': o_id,  # 产品ID
                'recommend_index': request.POST.get('recommend_index')  # 排序优先级。
            }

            forms_obj = RecommendIndexForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                product_id = forms_obj.cleaned_data.get('product_id')
                recommend_index = forms_obj.cleaned_data.get('recommend_index')

                product_obj = models.zgld_product.objects.filter(id=product_id)
                product_obj.update(
                    recommend_index=recommend_index
                )

                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 303
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())


        elif oper_type == "change_feedback_status":
            print('-------change_status------->>', request.POST)
            status = int(request.POST.get('status'))

            feedback_objs = models.zgld_user_feedback.objects.filter(id=o_id)

            if feedback_objs:

                # if not product_objs[0].user_id:  # 用户ID不存在，说明它是企业发布的产品，只能被推荐和取消推荐，不能被下架和上架。
                feedback_objs.update(
                    status=status
                )
                response.code = 200
                response.msg = "修改状态成功"
                response.data = {
                    # 'feedback_id': feedback_objs[0].id,
                    # 'status': feedback_objs[0].get_status_display(),
                    # 'status_code': feedback_objs[0].status
                }

            else:

                response.code = 302
                response.msg = '产品不存在'

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
