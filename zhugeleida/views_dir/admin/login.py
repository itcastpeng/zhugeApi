from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime


@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    username = request.POST.get('username')
    password = request.POST.get('password')
    print(username, account.str_encrypt(password))
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

            if not userprofile_obj.token:
                token = account.get_token(account.str_encrypt(password))
                userprofile_obj.token = token
            else:
                token = userprofile_obj.token
            request.session['user_id'] = userprofile_obj.id

            response.code = 200
            response.msg = '登录成功'

            last_login_date_obj = userprofile_obj.last_login_date
            last_login_date = last_login_date_obj.strftime('%Y-%m-%d %H:%M:%S') if last_login_date_obj else ''
            rules_list = [ i[0]  for i in  userprofile_obj.role.rules.values_list('title')]
            response.data = {
                'token': token,
                'user_id': userprofile_obj.id,
                'set_avatar': userprofile_obj.avatar,
                'company_name' : userprofile_obj.company.name,
                'company_id' : userprofile_obj.company_id,
                'role_id': userprofile_obj.role_id,
                'role_name': userprofile_obj.role.name,
                'avatar':  userprofile_obj.avatar,
                'last_login_date': last_login_date
            }

            userprofile_obj.last_login_date = datetime.datetime.now()
            userprofile_obj.save()
        else:
            response.code = 306
            response.msg = "账户未启用"

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





