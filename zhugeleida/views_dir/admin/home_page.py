from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
# from datetime import datetime
from django.utils.timezone import now, timedelta,datetime

from publicFunc.condition_com import conditionCom

from django.db.models import Q
from django.db.models import Sum
from django import forms
import json

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
        user_count = models.zgld_userprofile.objects.filter(company_id=company_id).count()  #  # 员工总数
        available_days = (user_obj[0].company.user_expired - datetime.now()).days     #还剩多天可以用
        used_days = (datetime.now() - user_obj[0].company.create_date).days           #用户使用了多少天了

        user_ids = models.zgld_userprofile.objects.select_related('company').filter(company_id=company_id).values_list('id')
        user_list = []
        if user_ids:
            for u_id in user_ids: user_list.append(u_id[0])
        customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).count()  # 已获取客户数


        ret_data = {
            'company_name': company_name,
            'username': user_obj[0].username,
            'mingpian_num': mingpian_available_num,  # 可开通名片数
            'user_count': user_count,  # 员工总数
            'expired_time': user_obj[0].company.user_expired.strftime("%Y-%m-%d"),  # 过期时间
            'open_up_date': user_obj[0].company.create_date.strftime("%Y-%m-%d"),  # 开通时间
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


    return JsonResponse(response.__dict__)


# 验证数据指标的传参
class LineInfoForm(forms.Form):


    days = forms.CharField(
        required=True,
        error_messages={
            # 'required': "天数不能为空",
            'invalid': "天数不能为空",
        }
    )
    index_type =  forms.CharField(
        required=True,
        error_messages={
            # 'required': "类型不能为空",
            'invalid':  "必须是整数类型"
        }
    )



@csrf_exempt
@account.is_token(models.zgld_userprofile)
def home_page_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == "acount_data":

            ret_data = {}
            data = request.GET.copy()
            #汇总数据
            q1 = Q()
            ret_data['count_data'] = deal_search_time(data,q1)

            #昨天数据
            q2 = Q()
            now_time = datetime.now()
            start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q2.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['yesterday_data'] = deal_search_time(data, q2)

            q3 = Q()
            start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q2.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['nearly_seven_days'] = deal_search_time(data, q3)

            q4 = Q()
            start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q2.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['nearly_thirty_days'] = deal_search_time(data, q4)

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,

            }



    elif  request.method == "POST":

        if oper_type == "line_info":
            print('request.POST',request.POST)

            forms_obj = LineInfoForm(request.POST)

            if forms_obj.is_valid():

                user_id = request.GET.get('user_id')
                user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
                company_id = user_obj[0].company_id
                days = forms_obj.data.get('days')

                user_ids = models.zgld_userprofile.objects.select_related('company').filter(company_id=company_id).values_list('id')
                user_list = []
                if user_ids:
                    for u_id in user_ids: user_list.append(u_id[0])

                data = request.POST.copy()
                data['user_list'] = user_list
                data['company_id'] = company_id


                ret_data = []
                for day in range(int(days),0,-1):

                   now_time = datetime.now()
                   start_time = (now_time - timedelta(days=day)).strftime("%Y-%m-%d")
                   # stop_time = now_time.strftime("%Y-%m-%d")
                   data['start_time'] = start_time
                   ret_data.append({'statics_date' : start_time, 'value' : deal_line_info(data)})


                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,

                }

            else:
                response.code = 303
                response.msg = "上传异常"
                response.data = json.loads(forms_obj.errors.as_json())

    else:
         response.code = 402
         response.msg = "请求异常"

    return JsonResponse(response.__dict__)

def deal_search_time(data,q):
    user_id = data.get('user_id')
    user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
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
        'customer_num': customer_num,  # 客户总数
        # 'new_add_customer': ,                 # 跟进客户数
        'follow_num': follow_num,  # 跟进客户数
        'browse_num': browse_num,  # 浏览总数
        'forward_num': forward_num,  # 被转发的总数  -包括转发名片，但是不包括转发产品
        'saved_total_num': saved_total_num,  # 被保存总数-包括保存手机号（action=8）
        'praise_sum': praise_sum,  # 被点赞总数
    }
    return  ret


def deal_line_info(data):
    index_type = int(data.get('index_type'))
    start_time = data.get('start_time')
    user_list = data.get('user_list')
    company_id = data.get('company_id')
    print('user_list',user_list)

    q1 = Q()
    q1.add(Q(**{'create_date__contains': start_time}), Q.AND)  # 大于等于
    print('start_time',start_time)

    if index_type == 1:  # 客户总数

        customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).filter(create_date__contains=start_time).count()  # 已获取客户数
        return customer_num

    elif index_type == 2:  # 跟进总数
        follow_customer_folowup_obj = models.zgld_user_customer_flowup.objects.filter(user_id__in=user_list,
                                                                                      last_follow_time__isnull=False)
        follow_num = 0
        if follow_customer_folowup_obj:
            follow_id_list = []
            for f_obj in follow_customer_folowup_obj:
                follow_id_list.append(f_obj.id)
            follow_num = models.zgld_follow_info.objects.filter(user_customer_flowup_id__in=follow_id_list).filter(
                q1).count()
        return follow_num

    elif index_type == 3:  # 浏览总数
        browse_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,
                                                          action=1).filter().count()  # 浏览名片的总数(包含着保存名片)
        return browse_num

    elif index_type == 4:  # 被转发总数
        forward_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,action=6).filter(q1).count()  # 被转发的总数-不包括转发产品
        return forward_num

    elif index_type == 5:  # 被保存总数
        saved_total_num = models.zgld_accesslog.objects.filter(user_id__in=user_list, action=8).filter(q1).count()  # 保存手机号
        return saved_total_num

    elif index_type == 6:  # 被赞总数
        user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q1).values_list('popularity')
        praise_sum = 0
        for i in user_pop_queryset:
            praise_sum = praise_sum + i[0]  # 被点赞总数
        return  praise_sum