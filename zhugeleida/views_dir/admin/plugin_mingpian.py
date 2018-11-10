
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.plugin_verify import MingpianAddForm,MingpianSelectForm, MingpianUpdateForm
import time
import datetime
import json
from django.db.models import Q
from zhugeleida.public.condition_com import conditionCom

# 公众号-插件名片查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_mingpian (request):
    response = Response.ResponseObj()

    if request.method == "GET":
            # 获取参数 页数 默认1

        forms_obj = MingpianSelectForm(request.GET)
        if forms_obj.is_valid():
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

            field_dict = {
                'id': '',
                'user_id' : '',
                'status': '',           # 按状态搜索, (1,'已发'),  (2,'未发'),
                'user_id__in' : '',    # 【暂时不用】 按员工搜索文章、目前只显示出自己的文章
                'title': '__contains',  # 按文章标题搜索
            }

            request_data = request.GET.copy()
            q = conditionCom(request_data, field_dict)

            objs = models.zgld_plugin_mingpian.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                print('current_page -->', current_page)
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 获取所有数据
            ret_data = []
            # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'mingpian_id': obj.id,
                    'name': obj.name,           # 名片名称
                    'username': obj.username,   # 姓名
                    'phone': obj.phone,         # 状态
                    'create_date': obj.create_date,      #文章创建时间
                    'avatar' : obj.avatar,     #文章图片链接
                    'webchat_code' : obj.webchat_code,     #文章图片链接
                    'position' : obj.position,     #文章图片链接

                })
            response.code = 200
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 公众号-插件名片操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_mingpian_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 添加名片
        if oper_type == "add":
            article_data = {
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'avatar': request.POST.get('avatar'),
                'username': request.POST.get('username'),
                'phone': request.POST.get('phone'),
                'webchat_code': request.POST.get('webchat_code'),
                'position': request.POST.get('position'),

            }

            forms_obj = MingpianAddForm(article_data)

            if forms_obj.is_valid():

                dict_data = {
                    'user_id': request.GET.get('user_id'),
                    'name' :forms_obj.cleaned_data['name'],
                    'avatar' :forms_obj.cleaned_data['avatar'],
                    'username' :forms_obj.cleaned_data['username'],
                    'phone' :forms_obj.cleaned_data['phone'],
                    'webchat_code' :forms_obj.cleaned_data['webchat_code'],
                    'position' :forms_obj.cleaned_data['position'],
                }

                models.zgld_plugin_mingpian.objects.create(**dict_data)

                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除名片
        elif oper_type == "delete":
            print('------delete o_id --------->>',o_id)
            user_id = request.GET.get('user_id')
            mingpian_objs = models.zgld_plugin_mingpian.objects.filter(id=o_id,user_id=user_id)

            if mingpian_objs:
               mingpian_objs.delete()
               response.code = 200
               response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '文章不存在'

        # 修改名片
        elif oper_type == "update":
            mingpain_data = {
                'mingpain_id' : o_id,
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'avatar': request.POST.get('avatar'),
                'username': request.POST.get('username'),
                'phone': request.POST.get('phone'),
                'webchat_code': request.POST.get('webchat_code'),
                'position': request.POST.get('position'),
            }

            forms_obj = MingpianUpdateForm(mingpain_data)
            if forms_obj.is_valid():
                dict_data = {
                    'user_id': request.GET.get('user_id'),
                    'name': forms_obj.cleaned_data['name'],
                    'avatar': forms_obj.cleaned_data['avatar'],
                    'username': forms_obj.cleaned_data['username'],
                    'phone': forms_obj.cleaned_data['phone'],
                    'webchat_code': forms_obj.cleaned_data['webchat_code'],
                    'position': forms_obj.cleaned_data['position'],
                }
                user_id = request.GET.get('user_id')
                mingpain_id = forms_obj.cleaned_data['mingpain_id']
                obj = models.zgld_plugin_mingpian.objects.filter(
                    id=mingpain_id, user_id=user_id
                )
                obj.update(**dict_data)

                response.code = 200
                response.msg = "修改成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
