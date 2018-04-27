from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from wendaku.forms.role import RoleForm, RoleUpdateForm
import time
import datetime
import json
@csrf_exempt
@account.is_token(models.UserProfile)
def role(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        current_page = int(request.GET.get('current_page', 1))
        length = int(request.GET.get('length', 10))
        order = request.GET.get('order', '-create_date')

        start_line = (current_page - 1) * length
        stop_line = start_line + length

        # 获取所有数据
        role_objs = models.Role.objects.select_related('oper_user').all().order_by(order)
        role_data = []

        # 获取第几页的数据
        for role_obj in role_objs[start_line: stop_line]:
            role_data.append({
                'id': role_obj.id,
                'name': role_obj.name,
                'create_date': role_obj.create_date,
                'oper_user__username': role_obj.oper_user.username,
            })
        response.code = 200
        response.data = {
            'role_data': list(role_data),
            'data_count': role_objs.count()
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


@csrf_exempt
@account.is_token(models.UserProfile)
def role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            role_data = {
                'name' : request.POST.get('name'),
                'oper_user_id':request.POST.get('oper_user_id')
            }
            forms_obj = RoleForm(role_data)
            if forms_obj.is_valid():
                models.Role.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.Role.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            role_update = models.Role.objects.filter(id=o_id)
            if role_update:
                role_data_update = {
                    'name':request.POST.get('name'),
                    'oper_user_id': request.POST.get('oper_user_id')
                }
                forms_obj = RoleForm(role_data_update)
                if forms_obj.is_valid():
                    name = forms_obj.cleaned_data['name']
                    role_update.update(name=name)
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 302
                    response.msg = '用户ID不存在'
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
