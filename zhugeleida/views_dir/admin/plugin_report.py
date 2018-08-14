
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.plugin_verify import ReportAddForm,ReportUpdateForm, ReportSelectForm,ReportSignUpAddForm
import time
import datetime
import json
from django.db.models import Q
from zhugeleida.public.condition_com import conditionCom


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_report(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = ReportSelectForm(request.GET)
        if forms_obj.is_valid():
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')  #

            field_dict = {
                'id': '',
                'user_id' : '',
            }

            request_data = request.GET.copy()
            q = conditionCom(request_data, field_dict)

            objs = models.zgld_plugin_report.objects.filter(q).order_by(order)
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
                name_list_data = []
                read_count =  obj.read_count
                join_num = models.zgld_report_to_customer.objects.filter(activity_id=obj.id).count()
                if read_count == 0:
                    convert_pr = 0
                else:
                    convert_pr = format(float(join_num) / float(read_count), '.2f')

                report_customer_obj = models.zgld_report_to_customer.objects.filter(activity_id=obj.id)
                if report_customer_obj:
                    for r_obj in report_customer_obj:

                        j_objs = models.zgld_information.objects.filter(customer_id=r_obj.customer_id).values('id',
                                                                                                              'customer__zgld_report_to_customer__leave_message',
                                                                                                              'customer__username',
                                                                                                              'customer__phone',
                                                                                                              'customer__zgld_information__create_date')

                        for j_obj in j_objs:
                            name_list_data.append({
                                'customer_name': j_obj.get('customer__username'),
                                'customer_phone': j_obj.get('customer__zgld_information__phone'),
                                'sign_up_time': j_obj.get('customer__zgld_information__create_date'),
                                'leave_message': j_obj.get('customer__zgld_report_to_customer__leave_message'),
                            })
                else:
                    name_list_data = []

                ret_data.append({
                    'id': obj.id,
                    'belong_user_id': obj.user.id,
                    'belong_user': obj.user.username,
                    #广告位
                    'ad_slogan': obj.ad_slogan,     #广告语
                    'sign_up_button': obj.sign_up_button,  #报名按钮
                    #报名页
                    'title': obj.title,  #活动标题
                    'read_count': read_count,  # 阅读数量
                    'join_num': join_num,  # 参与人数
                    'convert_pr': convert_pr,  # 转化率
                    'name_list' :name_list_data,
                    # 'customer_username': obj.customer.username,    #客户姓名
                    # 'customer_memo_name': obj.customer.memo_name,  #客户昵称
                    # 'customer_phone':obj.phone,  #活动标题
                    # 'phone' : obj.phone,    #手机号
                    # 'leave_message' : obj.leave_message,     #留言

                    'introduce': obj.introduce,      #活动说明
                    'is_get_phone_code' : obj.is_get_phone_code,    #是否获取手机验证码
                    'skip_link' : obj.skip_link,    #跳转链接
                    'create_date' : obj.create_date.strftime("%Y-%m-%d %H:%M")
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


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_report_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add":
            report_data = {
                'user_id': request.GET.get('user_id'),
                'ad_slogan': request.POST.get('ad_slogan'),  # 广告语
                'sign_up_button': request.POST.get('sign_up_button'),  # 报名按钮
                # 报名页
                'title': request.POST.get('title'),  # 活动标题

                # 'customer_username': request.POST.get('username),  # 客户姓名
                # 'customer_memo_name': obj.customer.memo_name,  # 客户昵称
                # 'customer_phone': obj.phone,
                # 'leave_message': obj.leave_message,  # 留言
                'introduce': request.POST.get('introduce'),  # 活动说明
                'is_get_phone_code':request.POST.get('is_get_phone_code'),  # 是否获取手机验证码
                'skip_link': request.POST.get('skip_link'),                 # 跳转链接

            }

            forms_obj = ReportAddForm(report_data)

            if forms_obj.is_valid():
                print('======forms_obj.cleaned_data====??', forms_obj.cleaned_data)

                dict_data = {
                    'user_id': request.GET.get('user_id'),
                    #广告位
                    'ad_slogan': forms_obj.cleaned_data['ad_slogan'],  # 广告语
                    'sign_up_button': forms_obj.cleaned_data['sign_up_button'],  # 报名按钮
                    # 报名页
                    'title': forms_obj.cleaned_data['title'],  # 活动标题
                    'introduce': forms_obj.cleaned_data['introduce'],  # 活动说明
                    'is_get_phone_code': request.POST.get('is_get_phone_code'),  # 是否获取手机验证码
                    'skip_link': forms_obj.cleaned_data['skip_link'],
                    'leave_message': request.POST.get('leave_message')  # 留言
                }

                obj = models.zgld_plugin_report.objects.create(**dict_data)

                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('------delete o_id --------->>',o_id)
            user_id = request.GET.get('user_id')
            mingpian_objs = models.zgld_plugin_report.objects.filter(id=o_id,user_id=user_id)

            if mingpian_objs:
               mingpian_objs.delete()
               response.code = 200
               response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '活动不存在'

        elif oper_type == "update":
            report_data = {
                'id' : o_id,
                'user_id': request.GET.get('user_id'),
                'ad_slogan': request.POST.get('ad_slogan'),  # 广告语
                'sign_up_button': request.POST.get('sign_up_button'),  # 报名按钮
                # 报名页
                'title': request.POST.get('title'),  # 活动标题

                # 'customer_username': request.POST.get('username),  # 客户姓名
                # 'customer_memo_name': obj.customer.memo_name,  # 客户昵称
                # 'customer_phone': obj.phone,
                # 'leave_message': obj.leave_message,  # 留言
                'introduce': request.POST.get('introduce'),  # 活动说明
                'skip_link': request.POST.get('skip_link'),

            }

            forms_obj = ReportUpdateForm(report_data)
            if forms_obj.is_valid():
                dict_data = {
                    'user_id': request.GET.get('user_id'),
                    # 广告位
                    'ad_slogan': forms_obj.cleaned_data['ad_slogan'],  # 广告语
                    'sign_up_button': forms_obj.cleaned_data['sign_up_button'],  # 报名按钮
                    # 报名页
                    'title': forms_obj.cleaned_data['title'],  # 活动标题
                    'introduce': forms_obj.cleaned_data['introduce'],  # 活动说明
                    'is_get_phone_code': request.POST.get('is_get_phone_code'),  # 是否获取手机验证码
                    'skip_link': forms_obj.cleaned_data['skip_link'],
                    'leave_message': request.POST.get('leave_message')  # 留言
                }
                user_id = request.GET.get('user_id')
                report_id = forms_obj.cleaned_data['id']
                obj = models.zgld_plugin_report.objects.filter(
                    id=report_id, user_id=user_id
                )
                obj.update(**dict_data)

                response.code = 200
                response.msg = "修改成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "sign_up_activity": # 报名活动
            report_data = {
                'customer_id': request.GET.get('user_id'),
                'activity_id': o_id,      # 活动ID
                'customer_name': request.POST.get('customer_name'),  # 客户姓名
                'phone': request.POST.get('phone'),                  # 客户报名手机号
                'phone_verify_code': request.POST.get('phone_verify_code'),        # 客户报名手机号发送的验证码。
                'leave_message': request.POST.get('leave_message'),  #留言
            }

            forms_obj = ReportSignUpAddForm(report_data)

            if forms_obj.is_valid():

                activity_id =  o_id  # 广告语
                customer_id =  int(forms_obj.cleaned_data.get('customer_id'))   # 报名按钮
                # 报名页
                customer_name =  forms_obj.cleaned_data['customer_name']   # 活动标题
                phone = forms_obj.cleaned_data['phone']                    # 活动说明
                phone_verify_code =  forms_obj.cleaned_data['phone_verify_code']
                leave_message =  forms_obj.cleaned_data['leave_message']
                print('------------>>',activity_id,customer_id)

                obj = models.zgld_report_to_customer.objects.filter(
                    activity_id=activity_id,  # 广告语
                    customer_id=customer_id,  # 报名按钮
                )

                if obj:
                    obj.update(leave_message = leave_message)

                else:
                    models.zgld_report_to_customer.objects.create(
                        activity_id =  activity_id,  # 广告语
                        customer_id =  customer_id,  # 报名按钮
                        leave_message =  leave_message  # 报名按钮
                    )

                customer_obj = models.zgld_customer.objects.get(id=customer_id)
                customer_obj.username = customer_name
                customer_obj.phone = phone  # 报名手机号
                customer_obj.save()


                response.code = 200
                response.msg = "添加成功"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())




    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
