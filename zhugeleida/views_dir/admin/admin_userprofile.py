from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.admin_userprofile import AddForm, UpdateForm, SelectForm,SwitchAdminUserForm, UpdateCustomerForm
import json


# cerf  token验证
# 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
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

            objs = models.zgld_admin_userprofile.objects.select_related('company', 'role').filter(
                q,
                company__admin_is_hidden=0,     # 后台不隐藏的查询出来
            ).order_by(order)
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
                        'login_user': obj.login_user,
                        'username': obj.username,
                        'position' : obj.position,
                        'password' : '',
                        'company_name': obj.company.name,
                        'company_id': obj.company_id,
                        'role_id': obj.role_id,
                        'role_name': obj.role.name,
                        'status': obj.status,
                        'status_text': obj.get_status_display(),
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                        # 'last_login_date': obj.last_login_date.strftime('%Y-%m-%d %H:%M:%S')
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
@account.is_token(models.zgld_admin_userprofile)
def admin_userprofile_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        # 添加用户
        if oper_type == "add":
            form_data = {
                'login_user': request.POST.get('login_user'),

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

        # 删除用户
        elif oper_type == "delete":
            # 删除 ID
            objs = models.zgld_admin_userprofile.objects.filter(id=o_id)

            if objs:

                if int(o_id) == int(request.GET.get('user_id')):
                    response.code = 305
                    response.msg = "不允许删除自己"
                    return JsonResponse(response.__dict__)

                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

        # 修改用户
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'id': o_id,
                'login_user': request.POST.get('login_user'),

                'company_id': request.POST.get('company_id'),
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

                if not  request.POST.get('password'):
                    del forms_obj.cleaned_data['password']


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
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改用户 是否启用 状态
        elif oper_type == "update_status":

            status = request.POST.get('status')    #(1, "启用"),  (2, "未启用"),
            user_id = request.GET.get('user_id')

            objs = models.zgld_admin_userprofile.objects.filter(id=o_id)

            if objs:

                if int(user_id) == int(o_id):
                    response.code = 305
                    response.msg = "不能修改自己"

                else:
                    objs.update(status=status)
                    response.code = 200
                    response.msg = "修改成功"

        # 切换用户
        elif oper_type == "switch_admin_user":
            print('----->',request.POST)

            user_id =  request.GET.get('user_id')
            form_data = {
                'user_id' :  user_id,
                'switch_admin_user_id': o_id,  # 要切换的用户ID

            }

            forms_obj = SwitchAdminUserForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                switch_admin_user_id = forms_obj.cleaned_data.get('switch_admin_user_id')

                #  查询数据库  用户id
                obj = models.zgld_admin_userprofile.objects.get(
                    id=switch_admin_user_id
                )


                response.data = {
                    'token': obj.token,
                    'user_id': obj.id,
                    'company_name': obj.company.name,
                    'company_id': obj.company_id,
                    'role_id': obj.role_id,
                    'role_name': obj.role.name,
                    'avatar': obj.avatar,
                    'weChatQrCode' : obj.company.weChatQrCode

                }

                response.code = 200
                response.msg = "获取成功"


            else:
                print("--- 验证不通过 --->")
                # print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

            # 修改用户启用状态

        # 修改顾客管理设置(企业管理-用户管理-顾客管理)
        elif oper_type == 'update_customer_settings':
            form_obj = UpdateCustomerForm(request.POST)
            if form_obj.is_valid():
                articles_read_customers = form_obj.cleaned_data.get('articles_read_customers')
                article_reading_time = form_obj.cleaned_data.get('article_reading_time')
                is_same_label = form_obj.cleaned_data.get('is_same_label')
                obj = models.zgld_admin_userprofile.objects.get(id=user_id)

                company_objs = models.zgld_company.objects.filter(id=obj.company_id)
                company_objs.update(
                    articles_read_customers=articles_read_customers,
                    article_reading_time=article_reading_time,
                    is_same_label=is_same_label
                )

                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
    else:

        # 查询顾客管理设置
        if oper_type == 'get_customer_settings':
            obj = models.zgld_admin_userprofile.objects.get(id=user_id)

            data = {
                'articles_read_customers': obj.company.articles_read_customers,
                'article_reading_time': obj.company.article_reading_time,
                'is_same_label': obj.company.is_same_label,
            }
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': data
            }
            response.note = {
                'articles_read_customers': '客户累计阅读文章数',
                'article_reading_time': '每篇文章阅读时长',
                'is_same_label': '是否匹配相同标签的文章',
            }

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
