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
from zhugeleida.forms.admin.plugin_goods_verify import PluginGoodsSelectForm, PluginGoodsUpdateForm,PluginGoodsAddForm

import json
from django.db.models import Q
from django.db.models import F
import uuid
import os
import base64

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_goods(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == 'plugin_goods_single':
            plugin_goods_type = int(request.GET.get('plugin_goods_type')) if request.GET.get('plugin_goods_type') else ''
            user_id = request.GET.get('user_id')
            plugin_goods_id = request.GET.get('plugin_goods_id')
            field_dict = {
                'id': '',
            }
            q = conditionCom(request, field_dict)
            # company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id
            # q.add(Q(**{'company_id': company_id}), Q.AND)
            q.add(Q(**{'id': plugin_goods_id}), Q.AND)

            if plugin_goods_type  == 1:   #单个官网产品展示
                q.add(Q(**{'user_id__isnull': True }), Q.AND)
            elif plugin_goods_type == 2:
                q.add(Q(**{'user_id': user_id }), Q.AND)

            objs = models.zgld_plugin_goods.objects.select_related('user', 'company').filter(q)
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

                    ret_data.append({
                        'id': obj.id,

                        'publisher': publisher,  # 发布者
                        'publisher_date': obj.create_date,  # 发布日期。

                        'name': obj.name,  # 产品名称  必填
                        'price': obj.price,  # 价格     必填
                        'reason': obj.reason,  # 推荐理由
                        'content' : json.loads(obj.content),

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


        elif oper_type == 'plugin_goods_list':
            print('request.GET----->', request.GET)
            forms_obj = PluginGoodsSelectForm(request.GET)
            if forms_obj.is_valid():

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

                objs = models.zgld_plugin_goods.objects.select_related('user', 'company').order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if objs:

                    for obj in objs:
                        content =  json.loads(obj.content)

                        ret_data.append({
                            'goods_id': obj.id,
                            'title' : obj.title,
                            'content': content,  # 封面地址的URL
                            'create_date': obj.create_date,

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

            return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_goods_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 删除-个人产品
        if oper_type == "delete":
            user_id = request.GET.get('user_id')

            plugin_goods_objs = models.zgld_plugin_goods.objects.filter(id=o_id,user_id=user_id)
            if plugin_goods_objs:
                plugin_goods_objs.delete()

                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '产品不存在'


        elif oper_type == "change_status":
            print('-------change_status------->>',request.POST)
            status = int(request.POST.get('status'))
            user_id = request.GET.get('user_id')
            plugin_goods_objs = models.zgld_plugin_goods.objects.filter(id=o_id)
            print('plugin_goods_objs--------->', plugin_goods_objs)

            if plugin_goods_objs:

                # if not plugin_goods_objs[0].user_id:  # 用户ID不存在，说明它是企业发布的产品，只能被推荐和取消推荐，不能被下架和上架。
                plugin_goods_objs.update(
                    status=status
                )
                response.code = 200
                response.msg = "修改状态成功"
                response.data = {
                    'plugin_goods_id': plugin_goods_objs[0].id,
                    'status': plugin_goods_objs[0].get_status_display(),
                    'status_code': plugin_goods_objs[0].status
                }

            else:

                response.code = 302
                response.msg = '产品不存在'


        elif oper_type == "update":
            form_data = {
                'goods_id' : o_id,
                'user_id': request.GET.get('user_id'),
                'title': request.POST.get('title'),  # 产品名称 必须
                'content': request.POST.get('content'),  # 内容    必须
            }

            forms_obj = PluginGoodsUpdateForm(form_data)
            if forms_obj.is_valid():
                goods_id = request.GET.get('goods_id')
                user_id = request.GET.get('user_id')
                content = forms_obj.cleaned_data.get('content')

                plugin_goods_objs = models.zgld_plugin_goods.objects.filter(
                        id = goods_id,user_id=user_id
                )
                if plugin_goods_objs:
                    plugin_goods_objs.update(
                        content=content
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 302
                    response.msg = "商品不存在"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        elif oper_type == "add":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'title': request.POST.get('title'),      # 产品名称 必须
                'content': request.POST.get('content'),  # 内容    必须
            }

            forms_obj = PluginGoodsAddForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                content = forms_obj.cleaned_data.get('content')

                models.zgld_plugin_goods.objects.create(
                    user_id=user_id,
                    content = content
                )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



        return JsonResponse(response.__dict__)


