from django.shortcuts import render, HttpResponse
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.qiyeweixin.oper_log_verify import OperLogAddForm
import json


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def oper_log(request):
    print("request.GET -->", request.GET)
    print("request.POST -->", request.POST)
    return HttpResponse("xxx")


# cerf  token验证
# 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def oper_log_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'oper_type': o_id,
                'user_id': user_id,
            }
            forms_obj = OperLogAddForm(form_data)

            if forms_obj.is_valid():
                models.ZgldUserOperLog.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "记录成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)

#
# # 用户操作
# #  csrf  token验证
# @csrf_exempt
# @account.is_token(models.zgld_userprofile)
# def oper_log_oper(request, oper_type, o_id):
#     response = Response.ResponseObj()
#
#     if request.method == "POST":
#         # 添加用户
#         if oper_type == "add":
#             form_data = {
#
#                 'username': request.POST.get('username'),
#                 'role_id': request.POST.get('role_id'),
#                 'password': request.POST.get('password'),
#                 'company_id':  request.POST.get('company_id')
#             }
#             #  创建 form验证 实例（参数默认转成字典）
#             forms_obj = UserAddForm(form_data)
#             if forms_obj.is_valid():
#                 print("验证通过")
#                 # print(forms_obj.cleaned_data)
#                 #  添加数据库
#                 print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
#
#                 models.zgld_userprofile.objects.create(**forms_obj.cleaned_data)
#                 response.code = 200
#                 response.msg = "添加成功"
#             else:
#                 print("验证不通过")
#                 print(forms_obj.errors)
#                 response.code = 301
#                 print(forms_obj.errors.as_json())
#                 response.msg = json.loads(forms_obj.errors.as_json())
#
#         # 删除用户
#         elif oper_type == "delete":
#             # 删除 ID
#             user_objs = models.zgld_userprofile.objects.filter(id=o_id)
#             if user_objs:
#                 user_objs.delete()
#                 response.code = 200
#                 response.msg = "删除成功"
#             else:
#                 response.code = 302
#                 response.msg = '用户ID不存在'
#
#         # 修改用户
#         elif oper_type == "update":
#             # 获取ID 用户名 及 角色
#             form_data = {
#                 'user_id': o_id,
#                 'username': request.POST.get('username'),
#                 'role_id': request.POST.get('role_id'),
#             }
#             print(request.POST)
#             forms_obj = UserUpdateForm(form_data)
#             if forms_obj.is_valid():
#
#                 user_id = forms_obj.cleaned_data['user_id']
#                 username = forms_obj.cleaned_data['username']
#                 role_id = forms_obj.cleaned_data['role_id']
#                 user_obj = models.zgld_userprofile.objects.filter(
#                     id=user_id
#                 )
#                 if user_obj:
#                     user_obj.update(
#                         username=username, role_id=role_id
#                     )
#                     response.code = 200
#                     response.msg = "修改成功"
#                 else:
#                     response.code = 303
#                     response.msg = json.loads(forms_obj.errors.as_json())
#
#             else:
#                 response.code = 301
#                 response.msg = json.loads(forms_obj.errors.as_json())
#
#     else:
#         response.code = 402
#         response.msg = "请求异常"
#
#     return JsonResponse(response.__dict__)
