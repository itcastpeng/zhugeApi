from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
from datetime import datetime
from django.utils.timezone import now, timedelta

from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserAddForm, UserUpdateForm, UserSelectForm
import json
from ..conf import *
import requests
from zhugeleida.views_dir.qiyeweixin.qr_code_auth import create_small_program_qr_code
from zhugeapi_celery_project import tasks
from django.db.models import Q
from django.db.models import Sum


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def home_page(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        order = request.GET.get('order', '-create_date')
        field_dict = {
            'id': '',
        }
        q = conditionCom(request, field_dict)
        user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)

        company_name = user_obj[0].company.name
        company_id = user_obj[0].company_id
        mingpian_available_num = user_obj[0].company.mingpian_available_num  # 可开通名片数量
        user_count = user_obj.filter(company_id=company_id).count()  #
        used_days = user_obj[0].user_expired.day() - datetime.datetime.now().day
        available_days = user_obj[0].user_expired.day() - user_obj[0].create_date.day()

        user_ids = models.zgld_userprofile.objects.select_related('company').filter(company_id=company_id).values_list('id')
        user_list = []
        if user_ids:
            for u_id in user_ids: user_list.append(u_id[0])
        customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).count()  # 已获取客户数

        ret_data = {}
        ret_data['count_data'] = {
            'company_name': company_name,
            'username': user_obj[0].username,
            'mingpian_available_num': mingpian_available_num,  # 可开通名片数
            'user_count': user_count,  # 员工总数
            'expired_time': user_obj[0].user_expired,  # 过期时间
            'open_up_date': user_obj[0].company.create_date,  # 开通时间
            'available_days': available_days,  # 可用天数
            'used_days': used_days,         # 剩余可用天数
            'customer_num': customer_num,   # 已获取客户数
        }

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,

        }

    # else:
    #     response.code = 402
    #     response.msg = "请求异常"
    #     response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def home_page_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == "acount_data":
            # user_id = request.GET.get('user_id')
            # user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
            #
            # company_name = user_obj[0].company.name
            # company_id = user_obj[0].company_id
            #
            # user_ids = models.zgld_userprofile.objects.select_related('company').filter(
            #     company_id=company_id).values_list('id')
            # user_list = []
            # if user_ids:
            #     for u_id in user_ids: user_list.append(u_id[0])
            #
            #
            # customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).count()  # 已获取客户数
            #
            # follow_customer_folowup_obj = models.zgld_user_customer_flowup.objects.filter(user_id__in=user_list,
            #                                                                               last_follow_time__isnull=False)
            #
            # follow_num = 0
            # if follow_customer_folowup_obj:
            #     follow_id_list = []
            #     for f_obj in follow_customer_folowup_obj:
            #         follow_id_list.append(f_obj.id)
            #     follow_num = models.zgld_follow_info.objects.filter(user_customer_flowup_id__in=follow_id_list).count()
            #
            # browse_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,
            #                                                   action=1).count()  # 浏览名片的总数(包含着保存名片)
            #
            # # q1 = Q()
            # # q1.add(Q(**{'action': 1}), Q.AND)
            # # q1.add(Q(**{'action': 6}), Q.AND)
            # forward_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,
            #                                                    action=6).count()                             # 被转发的总数-不包括转发产品
            # saved_total_num = models.zgld_accesslog.objects.filter(user_id__in=user_list, action=8).count()  # 保存手机号
            # user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).values_list('popularity')
            # praise_sum = 0
            # for i in user_pop_queryset:
            #     praise_sum = praise_sum + i[0]   # 被点赞总数
            #
            # ret_data = {}
            # ret_data['count_data'] = {
            #     'company_name': company_name,
            #     'username': user_obj[0].username,
            #     'customer_num': customer_num,  # 客户总数
            #     # 'new_add_customer': ,                 # 跟进客户数
            #     'follow_num': follow_num,  # 跟进客户数
            #     'browse_num': browse_num,  # 浏览总数
            #     'forward_num': forward_num,  # 被转发的总数  -包括转发名片，但是不包括转发产品
            #     'saved_total_num': saved_total_num,  # 被保存总数-包括保存手机号（action=8）
            #     'praise_sum': praise_sum,    # 被点赞总数
            # }

            ret_data = {}
            data = request.GET.copy()
            #汇总数据
            q1 = Q()
            ret_data['count_data'] = deal_search_time(data,q1)

            #昨天数据
            q2 = Q()
            now_time = datetime.now()
            create_date__gte = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
            stop_time = ( now_time + timedelta(days=1)).strftime("%Y-%m-%d")
            q2.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            q2.add(Q(**{'create_date__gte': create_date__gte}), Q.AND)

            ret_data['yesterday_data'] = deal_search_time(data, q2)



            # now_time = datetime.now()
            # create_date__gte = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
            # stop_time = (datetime.strptime(create_date__lt, '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")
            # q.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            # q.add(Q(**{'create_date__gte': create_date__gte}), Q.AND)

            # yesterday = now() + timedelta(days=-1)  # 昨天
            # q1.add(Q(**{'action': 1}), Q.AND)
            # q1.add(Q(**{'action': 6}), Q.AND)
            # yesterday_customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list,create_date=yesterday).count()

            # follow_num = 0
            # if follow_customer_folowup_obj:
            #     follow_id_list = []
            #     for f_obj in follow_customer_folowup_obj:
            #         follow_id_list.append(f_obj.id)
            #     follow_num = models.zgld_follow_info.objects.filter(user_customer_flowup_id__in=follow_id_list,create_date=yesterday).count()   # 跟进客户数
            #
            # browse_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,create_date=yesterday,
            #                                                   action=1).count()  # 浏览名片的总数(包含着保存名片)
            # forward_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,create_date=yesterday,
            #                                                    action=6).count()  # 被转发的总数-不包括转发产品
            # saved_total_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,create_date=yesterday, action=8).count()  # 保存手机号
            # user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id,create_date=yesterday,).values_list('popularity')
            # praise_sum = 0
            # for i in user_pop_queryset:
            #     praise_sum = praise_sum + i[0]  # 被点赞总数

            # ret_data['yesterday_data'] = {
            #     'company_name': company_name,
            #     'username': user_obj[0].username,
            #     'customer_num': yesterday_customer_num,  # 客户总数
            #     # 'new_add_customer': ,                 # 跟进客户数
            #     'follow_num': follow_num,  # 跟进客户数
            #     'browse_num': browse_num,  # 浏览总数
            #     'forward_num': forward_num,  # 被转发的总数  -包括转发名片，但是不包括转发产品
            #     'saved_total_num': saved_total_num,  # 被保存总数-包括保存手机号（action=8）
            #     'praise_sum': praise_sum,    # 被点赞总数
            # }


            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,

            }




    else:
         response.code = 402
         response.msg = "请求异常"

    return JsonResponse(response.__dict__)

def deal_search_time(data,q):
    user_id = data.get('user_id')
    user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)

    company_name = user_obj[0].company.name
    company_id = user_obj[0].company_id

    user_ids = models.zgld_userprofile.objects.select_related('company').filter(
        company_id=company_id).values_list('id')
    user_list = []
    if user_ids:
        for u_id in user_ids: user_list.append(u_id[0])


    customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).filter(q).count()  # 已获取客户数

    follow_customer_folowup_obj = models.zgld_user_customer_flowup.objects.filter(user_id__in=user_list,
                                                                                  last_follow_time__isnull=False)

    follow_num = 0
    if follow_customer_folowup_obj:
        follow_id_list = []
        for f_obj in follow_customer_folowup_obj:
            follow_id_list.append(f_obj.id)
        follow_num = models.zgld_follow_info.objects.filter(user_customer_flowup_id__in=follow_id_list).filter(q).count()

    browse_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,
                                                      action=1).filter(q).count()  # 浏览名片的总数(包含着保存名片)

    # q1 = Q()
    # q1.add(Q(**{'action': 1}), Q.AND)
    # q1.add(Q(**{'action': 6}), Q.AND)
    forward_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,
                                                       action=6).filter(q).count()  # 被转发的总数-不包括转发产品
    saved_total_num = models.zgld_accesslog.objects.filter(user_id__in=user_list, action=8).filter(q).count()  # 保存手机号
    user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q).values_list('popularity')
    praise_sum = 0
    for i in user_pop_queryset:
        praise_sum = praise_sum + i[0]  # 被点赞总数


    ret =  {
        'company_name': company_name,
        'username': user_obj[0].username,
        'customer_num': customer_num,  # 客户总数
        # 'new_add_customer': ,                 # 跟进客户数
        'follow_num': follow_num,  # 跟进客户数
        'browse_num': browse_num,  # 浏览总数
        'forward_num': forward_num,  # 被转发的总数  -包括转发名片，但是不包括转发产品
        'saved_total_num': saved_total_num,  # 被保存总数-包括保存手机号（action=8）
        'praise_sum': praise_sum,  # 被点赞总数
    }
    return  ret


