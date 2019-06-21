from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.plugin_verify import ReportAddForm, ReportUpdateForm, ReportSelectForm, ReportSignUpAddForm
import time
import datetime
import json
from django.db.models import Q
from zhugeleida.public.condition_com import conditionCom
import base64


# 公众号插件报名查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_report(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == "plugin_list":

            # 获取参数 页数 默认1
            forms_obj = ReportSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  #
                company_id = request.GET.get('company_id')  #

                field_dict = {
                    'id': '',
                    'user_id': '',
                    'user__company_id': company_id,
                }

                request_data = request.GET.copy()
                q = conditionCom(request_data, field_dict)

                objs = models.zgld_plugin_report.objects.select_related('user').filter(q).order_by(order)
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
                    print('vobj.zgld_article_set------------> ', obj.zgld_article_set)
                    print('vobj.zgld_article_set------------> ', obj.zgld_article_set.all())
                    print('vobj.zgld_article_set------------> ', obj.zgld_article_set.filter(plugin_report_id=obj.id))
                    is_update_plugin = True  # 是否可以修改报名插件
                    if obj.zgld_article_set.filter(plugin_report_id=obj.id): # 如果有文章使用了报名插件 则不能修改
                        is_update_plugin = False

                    read_count = obj.read_count
                    report_customer_objs = models.zgld_report_to_customer.objects.select_related('user',
                                                                                                 'activity').filter(
                        activity_id=obj.id)
                    join_num = report_customer_objs.count()
                    if read_count == 0:
                        convert_pr = 0
                    else:
                        convert_pr = format(float(join_num) / float(read_count), '.2f')

                    ret_data.append({
                        'id': obj.id,
                        'belong_user_id': obj.user.id,
                        'belong_user': obj.user.username,
                        # 广告位
                        'ad_slogan': obj.ad_slogan,  # 广告语
                        'sign_up_button': obj.sign_up_button,  # 报名按钮
                        # 报名页
                        'title': obj.title,  # 活动标题
                        'read_count': read_count,  # 阅读数量
                        'join_num': join_num,  # 参与人数
                        'convert_pr': convert_pr,  # 转化率
                        # 'name_list' :name_list_data,
                        'leave_message': obj.leave_message,
                        'introduce': obj.introduce,  # 活动说明
                        'is_get_phone_code': obj.is_get_phone_code,  # 是否获取手机验证码
                        'skip_link': obj.skip_link,  # 跳转链接
                        'is_update_plugin': is_update_plugin,  # 是否可以修改报名插件
                        'create_date': obj.create_date.strftime("%Y-%m-%d %H:%M")
                    })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'report_customer':

            forms_obj = ReportSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                activity_id =  forms_obj.cleaned_data['activity_id']
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

                name_list_data = []
                objs = models.zgld_report_to_customer.objects.select_related('user', 'activity').filter(
                    activity_id=activity_id).order_by(order)
                count = objs.count()
                if objs:

                    if length != 0:
                        print('current_page -->', current_page)
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    for obj in objs:
                        name_list_data.append({

                            'customer_name': obj.customer_name,
                            'customer_phone': obj.phone,
                            'sign_up_time': obj.create_date,
                            'leave_message': obj.leave_message,
                            'user_id': obj.user_id,
                            'user_name': obj.user.username,
                        })
                else:
                    name_list_data = []

                response.code = 200
                response.data = {
                    'ret_data': name_list_data,
                    'count': count,
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 公众号插件报名操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def plugin_report_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加插件报名
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
                'is_get_phone_code': request.POST.get('is_get_phone_code'),  # 是否获取手机验证码
                'skip_link': request.POST.get('skip_link'),  # 跳转链接

            }

            forms_obj = ReportAddForm(report_data)

            if forms_obj.is_valid():
                print('======forms_obj.cleaned_data====>', forms_obj.cleaned_data)

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

                obj = models.zgld_plugin_report.objects.create(**dict_data)

                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除插件报名
        elif oper_type == "delete":
            print('------delete o_id --------->>', o_id)
            user_id = request.GET.get('user_id')
            mingpian_objs = models.zgld_plugin_report.objects.filter(id=o_id)

            if mingpian_objs:
                article_set_count = mingpian_objs[0].zgld_article_set.all().count()
                if article_set_count == 0:
                    mingpian_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 300
                    response.msg = '插件有关联的文章,可解除关联后删除'

            else:
                response.code = 302
                response.msg = '活动不存在'

        # 修改插件报名
        elif oper_type == "update":
            report_data = {
                'id': o_id,
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
                    'leave_message': request.POST.get('leave_message'),  # 留言
                }


                report_id = forms_obj.cleaned_data['id']
                objs = models.zgld_plugin_report.objects.filter(
                    id=report_id
                )
                objs.update(**dict_data)

                article_objs = models.zgld_article.objects.filter(plugin_report_id=report_id)
                if article_objs:
                    article_obj = article_objs[0]
                    obj = objs[0]
                    insert_ads =  {
                        'id': report_id,
                        'belong_user_id': obj.user_id,
                        'belong_user': obj.user.username,
                        # 广告位
                        'ad_slogan': forms_obj.cleaned_data['ad_slogan'],  # 广告语
                        'sign_up_button': forms_obj.cleaned_data['sign_up_button'],  # 报名按钮
                        # 报名页
                        'title': forms_obj.cleaned_data['title'],  # 活动标题

                        # 'name_list' :name_list_data,
                        'leave_message': request.POST.get('leave_message'),
                        'introduce': forms_obj.cleaned_data['introduce'],  # 活动说明

                        'skip_link': forms_obj.cleaned_data['skip_link'],
                        'type': 'baoming',
                        'create_date': obj.create_date.strftime("%Y-%m-%d %H:%M"),
                    }

                    article_obj.insert_ads = json.dumps(insert_ads)
                    article_obj.sava()

                response.code = 200
                response.msg = "修改成功"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 客户 报名活动
        elif oper_type == "sign_up_activity":
            report_data = {
                'customer_id': request.GET.get('user_id'),
                'activity_id': o_id,  # 活动ID
                'customer_name': request.POST.get('customer_name'),  # 客户姓名
                'phone': request.POST.get('phone'),  # 客户报名手机号
                'phone_verify_code': request.POST.get('phone_verify_code'),  # 客户报名手机号发送的验证码。
                'leave_message': request.POST.get('leave_message'),  # 留言
            }

            forms_obj = ReportSignUpAddForm(report_data)

            if forms_obj.is_valid():

                activity_id = o_id  # 广告语
                customer_id = int(forms_obj.cleaned_data.get('customer_id'))  # 报名按钮
                # 报名页
                customer_name = forms_obj.cleaned_data['customer_name']  # 活动标题
                phone = forms_obj.cleaned_data['phone']  # 活动说明
                phone_verify_code = forms_obj.cleaned_data['phone_verify_code']
                leave_message = forms_obj.cleaned_data['leave_message']
                print('------------>>', activity_id, customer_id)

                obj = models.zgld_report_to_customer.objects.filter(
                    activity_id=activity_id,  # 广告语
                    customer_id=customer_id,  # 报名按钮
                )

                if obj:
                    obj.update(leave_message=leave_message)

                else:
                    models.zgld_report_to_customer.objects.create(
                        activity_id=activity_id,  # 广告语
                        customer_id=customer_id,  # 报名按钮
                        leave_message=leave_message  # 报名按钮
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
