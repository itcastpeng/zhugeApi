from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from django import forms
from  zhugeleida.public.check_complex_passwd import checkPassword
import json

@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    username = request.POST.get('username')
    password = request.POST.get('password')
    print('-------用户输入 username|password------->>',username,'|' ,account.str_encrypt(password))
    # 查询数据库
    userprofile_objs = models.zgld_admin_userprofile.objects.filter(
        login_user=username,  # 成员姓名, 以后要换成name(登录的用户名)
        # md5加密 密码
        password=account.str_encrypt(password),
    )

    if userprofile_objs:
        if userprofile_objs.filter(status=1):
            # 如果有数据 查询第一条对象

            userprofile_obj = userprofile_objs[0]
            # 如果没有token 则生成 token
            is_reset_password = userprofile_obj.is_reset_password
            company_id = userprofile_obj.company_id

            company_obj = models.zgld_company.objects.get(id=company_id)
            account_expired_time = company_obj.account_expired_time

            if datetime.datetime.now() <= account_expired_time:
                if not userprofile_obj.token:
                    token = account.get_token(account.str_encrypt(password))
                    userprofile_obj.token = token
                else:
                    token = userprofile_obj.token



                response.code = 200
                response.msg = '登录成功'

                last_login_date_obj = userprofile_obj.last_login_date
                last_login_date = last_login_date_obj.strftime('%Y-%m-%d %H:%M:%S') if last_login_date_obj else ''

                response.data = {
                    'token': token,
                    'user_id': userprofile_obj.id,
                    'set_avatar': userprofile_obj.avatar,
                    'company_name' : userprofile_obj.company.name,
                    'company_id' : userprofile_obj.company_id,
                    'role_id': userprofile_obj.role_id,
                    'role_name': userprofile_obj.role.name,
                    'avatar':  userprofile_obj.avatar,
                    'last_login_date': last_login_date,
                    'is_reset_password': is_reset_password,
                    'weChatQrCode':userprofile_obj.company.weChatQrCode
                }

                userprofile_obj.last_login_date = datetime.datetime.now()
                userprofile_obj.save()

            else:
                company_name = company_obj.name
                response.code = 403
                response.msg = '账户过期'
                print('-------- 雷达后台账户过期: %s-%s | 过期时间:%s ------->>' % (company_id, company_name, account_expired_time))


        else:
            response.code = 306
            response.msg = "账户未启用"

    else:
        response.code = 401
        response.msg = "账号或密码错误"

    print('调试登录 ->', response.__dict__)
    return JsonResponse(response.__dict__)


@csrf_exempt
def modify_password(request):
    response = Response.ResponseObj()

    if request.method == "POST":
        print('-----request.method.post()-------->>',request.POST)
        user_id = request.GET.get('user_id')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        modify_form = ModifyPwdForm(request.POST)

        if modify_form.is_valid():
            password1 = password1.strip()
            password2 = password2.strip()

            if password1 == password2:

                if checkPassword(password1):

                    print('--- 密码复杂度 检测通过  ---->>')
                    userprofile_obj = models.zgld_admin_userprofile.objects.get(id=user_id)

                    if userprofile_obj:
                        userprofile_obj.password = account.str_encrypt(password1)
                        userprofile_obj.is_reset_password = True  # 已经重置密码
                        userprofile_obj.last_login_date = datetime.datetime.now()
                        userprofile_obj.save()
                        response.code = 200
                        response.msg = "修改密码成功"

                else:
                    print('--- 密码复杂度 检查未通过 ---->>')
                    response.code = 305
                    response.msg = '密码复杂度检查未通过,请检查最小长度为八位,包含大小写字母和数字'

            else:
                response.code = 306
                response.msg = "输入密码不一致"
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(modify_form.errors.as_json())
    else:
        response.code = 401
        response.msg = "账号或密码错误"

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def login_rules(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1

        user_id = request.GET.get('user_id')

        userprofile_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
        rules_list = [i[0] for i in userprofile_obj.role.rules.values_list('title')]


        response.code = 200
        response.data = {
            'rules_list': rules_list,

        }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


class ModifyPwdForm(forms.Form):   #重置密码
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)


