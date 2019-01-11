from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime


import json
from publicFunc import account
from zhugeleida.forms.admin.login import ModifyPwdForm, LoginForm


@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    username = request.POST.get('username')
    password = request.POST.get('password')

    form_obj = LoginForm(request.POST)

    if form_obj.is_valid():
        # 查询数据库
        userprofile_objs = models.zgld_admin_userprofile.objects.select_related('company').filter(
            login_user=username,  # 成员姓名, 以后要换成name(登录的用户名)
            # md5加密 密码
            password=account.str_encrypt(password),
            status=1
        )
        print('--- password=account.str_encrypt(password) --->>',account.str_encrypt(password))
        if userprofile_objs:
            print('用户存在')
            # 如果有数据 查询第一条对象

            userprofile_obj = userprofile_objs[0]
            if userprofile_obj.status == 1:
                # 如果没有token 则生成 token
                is_reset_password = userprofile_obj.is_reset_password
                company_id = userprofile_obj.company_id

                account_expired_time = userprofile_obj.company.account_expired_time

                if datetime.datetime.now() <= account_expired_time:
                    print('用户没有过期,可以使用')
                    if not userprofile_obj.token:
                        token = account.get_token(account.str_encrypt(password))
                        userprofile_obj.token = token
                    else:
                        token = userprofile_obj.token
                    gzh_notice_qrcode = ''
                    gzh_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                    if gzh_objs:
                        gzh_notice_qrcode = gzh_objs[0].gzh_notice_qrcode

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

                        'weChatQrCode': userprofile_obj.company.weChatQrCode,
                        'gzh_notice_qrcode' : gzh_notice_qrcode,
                    }
                    print('response.data  -->', response.data )

                    userprofile_obj.last_login_date = datetime.datetime.now()
                    userprofile_obj.save()
                    response.code = 200
                    response.msg = '登录成功'

                else:
                    company_name = userprofile_obj.company.name
                    response.code = 403
                    response.msg = '账户过期'
                    print('-------- 雷达后台账户过期: %s-%s | 过期时间:%s ------->>' % (company_id, company_name, account_expired_time))
            else:
                response.code = 306
                response.msg = "账户未启用"

        else:
            response.code = 401
            response.msg = "账号或密码错误"

    else:
        response.code = 402
        response.msg = "请求异常"
        response.data = json.loads(form_obj.errors.as_json())

    return JsonResponse(response.__dict__)


@csrf_exempt
# @account.is_token(models.zgld_admin_userprofile)
def modify_password(request):
    response = Response.ResponseObj()

    if request.method == "POST":
        print('-----request.method.post()-------->>', request.POST)
        user_id = request.GET.get('user_id')
        form_obj = ModifyPwdForm(request.POST)

        if form_obj.is_valid():
            password = form_obj.cleaned_data.get('password1')
            userprofile_obj = models.zgld_admin_userprofile.objects.get(id=user_id)

            if userprofile_obj:
                userprofile_obj.password = password
                userprofile_obj.is_reset_password = True  # 已经重置密码
                userprofile_obj.last_login_date = datetime.datetime.now()
                userprofile_obj.save()
                response.code = 200
                response.msg = "修改密码成功"
        else:
            response.code = 402
            # response.msg = "两次密码输入不一致"
            # print('---- 修改密码 formobj----->>',form_obj.errors.as_json())
            response.msg = json.loads(form_obj.errors.as_json())
    else:
        response.code = 401
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 根据用户角色获取该角色对应的权限
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def login_rules(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        userprofile_obj = models.zgld_admin_userprofile.objects.select_related('role').get(id=user_id)
        rules_list = [i[0] for i in userprofile_obj.role.rules.values_list('title')]

        response.code = 200
        response.data = {
            'rules_list': rules_list,
        }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)





