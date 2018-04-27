from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime

from wendaku.forms.user import UserForm, UserUpdateForm
import json


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.UserProfile)
def user(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        current_page = int(request.GET.get('current_page', 1))
        length = int(request.GET.get('length', 10))
        start_line = (current_page - 1) * length
        stop_line = start_line + length
        # 链表查询   查询所有

        userprofile_objs = models.UserProfile.objects.select_related('role', 'oper_user').all()[start_line:stop_line]
        user_data = []
        for obj in userprofile_objs:
            #  如果有oper_user字段 等于本身名字
            if obj.oper_user:
                oper_user_username = obj.oper_user.username
            else:
                oper_user_username = ''
            # print('oper_user_username -->', oper_user_username)
            #  将查询出来的数据 加入列表
            user_data.append({
                'user_id': obj.id,
                'username': obj.username,
                'role': obj.role.name,
                'create_date': obj.create_date,
                'last_login_date': obj.last_login_date,
                'oper_user': oper_user_username,
            })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'user_data': user_data
            }
    else:
        response.code = 402
        response.msg = "请求异常"
        response.data = {'':''}
    return JsonResponse(response.__dict__)


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.UserProfile)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = UserForm(request.POST)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                # print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                models.UserProfile.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            models.UserProfile.objects.filter(id=o_id).delete()
            response.code = 200
            response.msg = "删除成功"

        elif oper_type == "update":
            # 获取ID 用户名 及 角色
            form_data = {
                'user_id': o_id,
                'username': request.POST.get('username'),
                'role_id': request.POST.get('role_id'),
            }

            forms_obj = UserUpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                user_id = forms_obj.cleaned_data['user_id']
                username = forms_obj.cleaned_data['username']
                role_id = forms_obj.cleaned_data['role_id']
                #  查询数据库  用户id
                user_obj = models.UserProfile.objects.filter(
                    id = user_id
                )
                #  更新 数据
                user_obj.update(username=username,role_id=role_id)
                print(user_obj)

                response.code = 200
                response.msg = "修改成功"
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
