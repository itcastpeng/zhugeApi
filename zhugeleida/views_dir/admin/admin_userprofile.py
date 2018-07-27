from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.admin_userprofile import AddForm, UpdateForm, SelectForm
import json


# cerf  token验证 用户展示模块
@csrf_exempt
# @account.is_token(models.zgld_admin_userprofile)
def admin_userprofile(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',

            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.zgld_admin_userprofile.objects.select_related('company', 'role').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                #  将查询出来的数据 加入列表

                ret_data.append({
                    'id': obj.id,
                    'avatar': obj.avatar,
                    'username': obj.username,
                    'company_name': obj.company.name,
                    'company_id': obj.company_id,
                    'role_id': obj.role_id,
                    'role_name': obj.role.name,
                    'status': obj.status,
                    'status_text': obj.get_status_display(),
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'last_login_date': obj.last_login_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改
@csrf_exempt
# @account.is_token(models.zgld_admin_userprofile)
def admin_userprofile_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'login_user': request.POST.get('login_user'),
                'username': request.POST.get('username'),
                'company_id': request.POST.get('company_id'),
                'password': request.POST.get('password'),
                'position': request.POST.get('position'),
                'role_id': request.POST.get('role_id'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                models.zgld_admin_userprofile.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            objs = models.zgld_admin_userprofile.objects.filter(id=o_id)

            if objs:

                if o_id == request.GET.get('user_id'):
                    response.code = 305
                    response.msg = "不允许删除自己"
                    return JsonResponse(response.__dict__)

                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'id': o_id,
                'login_user': request.POST.get('login_user'),
                'username': request.POST.get('username'),
                'company_id': request.POST.get('company'),
                'password': request.POST.get('password'),
                'position': request.POST.get('position'),
                'role_id': request.POST.get('role_id'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                id = forms_obj.cleaned_data['id']

                del forms_obj.cleaned_data['id']
                #  查询数据库  用户id
                objs = models.zgld_admin_userprofile.objects.filter(
                    id=id
                )
                #  更新 数据
                if objs:
                    # objs.update(
                    #     name=name,
                    #     url_path=url_path,
                    #     super_id_id=super_id_id,
                    # )
                    objs.update(**forms_obj.cleaned_data)

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
