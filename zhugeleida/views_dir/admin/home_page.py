from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.timezone import timedelta
import datetime
from zhugeleida.forms.admin import homepage_verify
import json
from django.db.models import Q, Sum


# cerf  token验证
# 查询当前登录用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def home_page(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        user_obj = models.zgld_admin_userprofile.objects.select_related('company').filter(id=user_id)
        company_name = user_obj[0].company.name
        company_id = user_obj[0].company_id
        mingpian_available_num = user_obj[0].company.mingpian_available_num                 # 可开通名片数量
        user_count = models.zgld_userprofile.objects.filter(company_id=company_id).count()  # # 员工总数

        account_expired_time = user_obj[0].company.account_expired_time
        charging_start_time = user_obj[0].company.charging_start_time
        create_date = user_obj[0].company.create_date

        # available_days = (account_expired_time - datetime.datetime.now()).days  # 还剩多天可以用
        # used_days = (datetime.datetime.now() - user_obj[0].company.create_date).days  # 用户使用了多少天了

        customer_num = models.zgld_customer.objects.filter(company_id=company_id).count()
        now_date = datetime.datetime.now()
        used_days = ''
        available_days = ''
        if now_date > charging_start_time and now_date < account_expired_time:
            used_days = (now_date - charging_start_time).days  # 用户使用了多少天了
            available_days = (account_expired_time - now_date).days  # 还剩多天可以用

        elif now_date >= account_expired_time:
            used_days = (account_expired_time - charging_start_time).days  # 用户使用了多少天了
            available_days = 0  # 还剩多天可以用

        elif now_date <= charging_start_time:
            used_days = 0
            available_days = (account_expired_time - charging_start_time).days


        ret_data = {
            'company_name': company_name,
            'username': user_obj[0].username,
            'mingpian_num': mingpian_available_num,  # 可开通名片数
            'user_count': user_count,  # 员工总数
            'expired_time': account_expired_time.strftime("%Y-%m-%d"),  # 过期时间
            'open_up_date': create_date.strftime("%Y-%m-%d"),  # 开通时间
            'available_days': available_days,  # 可用天数
            'used_days': used_days,  # 剩余可用天数
            'customer_num': customer_num,  # 已获取客户数
        }
        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,

        }
    return JsonResponse(response.__dict__)


# 统计 转发、浏览、点赞、客户跟进总数
def deal_search_time(data, q):
    user_id = data.get('user_id')
    user_obj = models.zgld_admin_userprofile.objects.select_related('company').filter(id=user_id)
    company_id = user_obj[0].company_id

    # customer_num = models.zgld_user_customer_belonger.objects.select_related('user').filter(
    #     user__company_id=company_id).filter(q).values_list('customer_id').distinct().count()    # 已获取客户数

    customer_num = models.zgld_customer.objects.filter(company_id=company_id).filter(q).count()

    follow_num = models.zgld_follow_info.objects.select_related('user_customer_flowup').filter(
        user_customer_flowup__user__company=company_id).filter(q).count()

    browse_num = models.zgld_accesslog.objects.select_related('user').filter(user__company_id=company_id,
                                                                             action__in=[1,14]).filter(q).count()  # 浏览名片的总数(包含着保存名片)

    forward_num = models.zgld_accesslog.objects.select_related('user').filter(user__company_id=company_id,
                                                                              action__in=[6,15,16]).filter(q).count()  # 被转发的总数-不包括转发产品

    saved_total_num = models.zgld_accesslog.objects.select_related('user').filter(user__company_id=company_id,
                                                                                  action=8).filter(q).count()  # 保存手机号

    # objs = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q).values('company_id').annotate(Sum('praise'))
    # praise__sum = 0
    # if objs:
    #     obj = objs[0]
    #     praise__sum = obj.get('praise__sum')
    praise__sum = models.zgld_accesslog.objects.select_related('user').filter(user__company_id=company_id,
                                                                              action__in=[9, 19]).filter(q).count()  # 被转发的总数-不包括转发产品

    ret = {
        'customer_num': customer_num,  # 客户总数
        # 'new_add_customer': ,        # 跟进客户数
        'follow_num': follow_num,  # 跟进客户数
        'browse_num': browse_num,  # 浏览总数
        'forward_num': forward_num,  # 被转发的总数  -包括转发名片，但是不包括转发产品
        'saved_total_num': saved_total_num,  # 被保存总数-包括保存手机号（action=8）
        'praise_sum': praise__sum,  # 被点赞总数
    }
    return ret


# 统计 转发点赞次数 某时间段
def deal_line_info(data):
    index_type = int(data.get('index_type'))
    start_time = data.get('start_time')
    stop_time = data.get('stop_time')
    company_id = data.get('company_id')

    q1 = Q()
    # q1.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
    # q1.add(Q(**{'create_date__lt': stop_time}), Q.AND)  # 小于
    q1.add(Q(create_date__contains=start_time), Q.AND)

    # 客户总数
    if index_type == 1:
        # customer_num = models.zgld_user_customer_belonger.objects.filter(
        #     q1,
        #     user__company_id=company_id,
        #     customer__create_date__contains=start_time
        # ).values('customer_id').distinct()  # 已获取客户数
        customer_num = models.zgld_customer.objects.filter(q1, company_id=company_id).count()

        return customer_num

    # 跟进总数  last_follow_time__isnull
    elif index_type == 2:
        follow_num = models.zgld_follow_info.objects.select_related('user_customer_flowup').filter(
            q1,
            user_customer_flowup__user__company=company_id
        ).count()

        return follow_num

    # 浏览总数
    elif index_type == 3:
        browse_num = models.zgld_accesslog.objects.select_related('user').filter(
            q1,
            user__company_id=company_id,
            action=1
        ).count()  # 浏览名片的总数(包含着保存名片)
        return browse_num

    # 被转发总数
    elif index_type == 4:
        forward_num = models.zgld_accesslog.objects.select_related('user').filter(
            q1,
            user__company_id=company_id,
            action=6
        ).count()  # 被转发的总数-不包括转发产品
        return forward_num

    # 被保存总数
    elif index_type == 5:
        saved_total_num = models.zgld_accesslog.objects.select_related('user').filter(
            q1,
            user__company_id=company_id,
            action=8
        ).count()  # 保存手机号
        return saved_total_num

    # 被赞总数
    elif index_type == 6:
        # objs = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q1).values('company_id').annotate(
        #     Sum('praise'))
        # praise__sum = 0
        # if objs:
        #     obj = objs[0]
        #     praise__sum = obj.get('praise__sum')
        praise__sum = models.zgld_accesslog.objects.select_related('user').filter(
            q1,
            user__company_id=company_id,
            action__in=[9, 19]
        ).count()  # 被转发的总数-不包括转发产品

        return praise__sum


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def home_page_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        # 统计-数据概览
        if oper_type == "line_info":
            forms_obj = homepage_verify.LineInfoForm(request.POST)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                user_obj = models.zgld_admin_userprofile.objects.select_related('company').filter(id=user_id)
                company_id = user_obj[0].company_id
                days = forms_obj.data.get('days')

                data = request.POST.copy()
                data['company_id'] = company_id

                ret_data = []
                for day in range(int(days), 0, -1):
                    print('day-------> ', day)
                    now_time = datetime.datetime.now()
                    start_time = (now_time - timedelta(days=day)).strftime("%Y-%m-%d")
                    stop_time = (now_time - timedelta(days=day - 1)).strftime("%Y-%m-%d")
                    print('start_time, stop_time--------> ', start_time, stop_time)
                    # stop_time = now_time.strftime("%Y-%m-%d")
                    data['start_time'] = start_time
                    data['stop_time'] = stop_time
                    ret_data.append({'statics_date': start_time, 'value': deal_line_info(data)})

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data
                }

            else:
                response.code = 303
                response.msg = "上传异常"
                response.data = json.loads(forms_obj.errors.as_json())

    else:
        # 调用deal_search_time 统计今日, 近七天, 三十天数据
        if oper_type == "acount_data":
            ret_data = {}
            data = request.GET.copy()
            # 汇总数据
            q1 = Q()
            ret_data['count_data'] = deal_search_time(data, q1)

            # 昨天数据
            q2 = Q()
            now_time = datetime.datetime.now()
            start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q2.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['yesterday_data'] = deal_search_time(data, q2)

            q3 = Q()
            start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q3.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['nearly_seven_days'] = deal_search_time(data, q3)

            q4 = Q()
            start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q4.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['nearly_thirty_days'] = deal_search_time(data, q4)

            # 今日新增
            q5 = Q()
            now_time = datetime.datetime.now().strftime("%Y-%m-%d")
            q5.add(Q(**{'create_date__gte': now_time}), Q.AND)
            ret_data['today_data'] = deal_search_time(data, q5)

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
