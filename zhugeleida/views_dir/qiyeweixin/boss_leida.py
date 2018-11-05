from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.timezone import now, timedelta, datetime
from publicFunc.condition_com import conditionCom
from django.db.models import Count
from django.db.models import Q
from zhugeleida.forms.boosleida.boos_leida_verify import QueryHaveCustomerDetailForm, QueryHudongHaveCustomerDetailPeopleForm, LineInfoForm
import base64, json


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

        user_obj = models.zgld_admin_userprofile.objects.select_related('company').filter(id=user_id)
        #print('------user_obj----->', user_obj)

        company_name = user_obj[0].company.name
        company_id = user_obj[0].company_id
        mingpian_available_num = user_obj[0].company.mingpian_available_num  # 可开通名片数量
        user_count = models.zgld_userprofile.objects.filter(company_id=company_id).count()  # # 员工总数
        available_days = (user_obj[0].company.account_expired_time - datetime.now()).days  # 还剩多天可以用
        used_days = (datetime.now() - user_obj[0].company.create_date).days  # 用户使用了多少天了

        user_ids = models.zgld_userprofile.objects.select_related('company').filter(company_id=company_id).values_list(
            'id')
        user_list = []
        if user_ids:
            for u_id in user_ids: user_list.append(u_id[0])
        customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).values_list(
            'customer_id').distinct().count()  # 已获取客户数

        ret_data = {
            'company_name': company_name,
            'username': user_obj[0].username,
            'mingpian_num': mingpian_available_num,  # 可开通名片数
            'user_count': user_count,  # 员工总数
            'expired_time': user_obj[0].company.account_expired_time.strftime("%Y-%m-%d"),  # 过期时间
            'open_up_date': user_obj[0].company.create_date.strftime("%Y-%m-%d"),  # 开通时间
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


def deal_search_time(data, q):
    user_id = data.get('user_id')
    user_obj = models.zgld_userprofile.objects.select_related('company').get(id=user_id)
    company_id = user_obj.company_id

    user_ids = models.zgld_userprofile.objects.select_related('company').filter(company_id=company_id).values_list('id')
    user_list = []
    if user_ids:
        for u_id in user_ids: user_list.append(u_id[0])

    customer_num = models.zgld_customer.objects.filter(company_id=company_id).filter(q).count()
    # customer_num = models.zgld_user_customer_belonger.objects.filter(user_id__in=user_list).filter(q).values_list('customer_id').distinct().count()  # 已获取客户数
    #print('-----customer_num----->', customer_num)

    customer_num_dict = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q).aggregate(
        browse_num=Count('popularity'))
    browse_num = customer_num_dict.get('browse_num')

    follow_num = models.zgld_follow_info.objects.filter(user_customer_flowup__user__company=company_id).filter(
        q).count()

    user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q).aggregate(
        praise_num=Count('praise'))  # 被点赞总数
    praise_num = user_pop_queryset.get('praise_num')

    comm_num_of_customer = models.zgld_user_customer_belonger.objects.filter(user__company_id=company_id,
                                                                             is_customer_msg_num__gte=1,
                                                                             is_user_msg_num__gte=1).count()

    user_forward_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q).aggregate(
        forward_num=Count('forward'))  # 被点赞总数
    forward_num = user_forward_queryset.get('forward_num')
    saved_total_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=8).filter(
        q).count()  # 保存
    query_product_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=7).filter(
        q).count()  # 咨询产品
    view_website_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=4).filter(q).count()

    ret = {
        'customer_num': customer_num,  # 客户总数
        'browse_num': browse_num,  # 浏览总数
        'follow_num': follow_num,  # 跟进客户数

        'comm_num_of_customer': comm_num_of_customer,
        'forward_num': forward_num,  # 被转发的总数  -包括转发名片，但是不包括转发产品
        'saved_total_num': saved_total_num,  # 被保存总数-包括保存手机号（action=8）

        'praise_num': praise_num,  # 被点赞总数
        'query_product_num': query_product_num,  # 被点赞总数
        'view_website_num': view_website_num,  # 被点赞总数

    }
    return ret


def deal_line_info(data):
    index_type = int(data.get('index_type'))
    start_time = data.get('start_time')
    stop_time = data.get('stop_time')
    # user_list = data.get('user_list')
    company_id = data.get('company_id')

    q1 = Q()
    q1.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
    q1.add(Q(**{'create_date__lte': stop_time}), Q.AND)  # 小于
    #print('---->start_time', start_time)

    if index_type == 1:  # 客户总数

        customer_num = models.zgld_user_customer_belonger.objects.filter(user__company_id=company_id).filter(
            q1).values_list('customer_id').distinct().count()  # 已获取客户数
        return customer_num

    elif index_type == 2:  # 咨询客户数
        comm_num_of_customer = models.zgld_user_customer_belonger.objects.filter(user__company_id=company_id,
                                                                                 is_customer_msg_num__gte=1).count()
        return comm_num_of_customer


    elif index_type == 3:  # 跟进客户数  # 近15日客户活跃度
        follow_num = models.zgld_follow_info.objects.filter(
            user_customer_flowup__customer__company_id=company_id).filter(q1).count()
        return follow_num

    elif index_type == 4:  # 浏览总数 [客户活跃度]
        browse_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=1).filter(q1).values(
            'customer_id').distinct().count()  # 浏览名片的总数(包含着保存名片)
        return browse_num

    # elif index_type == 4:  # 被转发总数
    #     forward_num = models.zgld_accesslog.objects.filter(user_id__in=user_list,action=6).filter(q1).count()  # 被转发的总数-不包括转发产品
    #     return forward_num
    #
    # elif index_type == 5:  # 被保存总数
    #     saved_total_num = models.zgld_accesslog.objects.filter(user_id__in=user_list, action=8).filter(q1).count()  # 保存手机号
    #     return saved_total_num
    #
    # elif index_type == 6:  # 被赞总数
    #     user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q1).values_list('popularity')
    #     praise_sum = 0
    #     for i in user_pop_queryset:
    #         praise_sum = praise_sum + i[0]  # 被点赞总数
    #     return  praise_sum


def deal_sale_ranking_data(data, q):
    type = data.get('type')
    company_id = data.get('company_id')

    ranking_data = ''

    if type == 'customer_data':  # 按客户人数

        user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer','user__gender',
                                                                                                'customer_parent').filter(
            q)

        user_have_customer_num_list_objs = user_customer_belonger_objs.values('user_id', 'user__username',
                                                                              'user__avatar','user__gender').annotate(
            have_customer_num=Count('customer')).distinct()


        objs = list(user_have_customer_num_list_objs)

        for i in range(1, len(objs)):
            if objs[i]['have_customer_num'] > objs[i - 1]['have_customer_num']:
                temp = objs[i]['have_customer_num']
                user_id = objs[i]['user_id']
                user__username = objs[i]['user__username']
                user__avatar = objs[i]['user__avatar']
                user__gender = objs[i]['user__gender']

                for j in range(i - 1, -1, -1):
                    if objs[j]['have_customer_num'] < temp:
                        objs[j + 1]['have_customer_num'] = objs[j]['have_customer_num']
                        objs[j + 1]['user_id'] = objs[j]['user_id']
                        objs[j + 1]['user__username'] = objs[j]['user__username']
                        objs[j + 1]['user__avatar'] = objs[j]['user__avatar']
                        objs[j + 1]['user__gender'] = objs[j]['user__gender']

                        index = j  # 记下应该插入的位置
                    else:
                        break

                    objs[index]['have_customer_num'] = temp
                    objs[index]['user_id'] = user_id
                    objs[index]['user__username'] = user__username
                    objs[index]['user__avatar'] = user__avatar
                    objs[index]['user__gender'] = user__gender

        ranking_data = objs



    elif type == 'follow_num':  # 按跟进人数

        follow_info_objs = models.zgld_follow_info.objects.select_related('user_customer_flowup').filter(
            user_customer_flowup__user__company_id=company_id).filter(q)

        follow_info_list_objs = follow_info_objs.values(
            'user_customer_flowup__user_id',
            'user_customer_flowup__user__avatar',
            'user_customer_flowup__user__gender',
            'user_customer_flowup__user__username'
        ).annotate(have_customer_num=Count('user_customer_flowup__customer_id', 'user_customer_flowup__user_id'))


        objs = list(follow_info_list_objs)

        for i in range(1, len(objs)):
            if objs[i]['have_customer_num'] > objs[i - 1]['have_customer_num']:
                temp = objs[i]['have_customer_num']
                user_customer_flowup__user_id = objs[i]['user_customer_flowup__user_id']
                user_customer_flowup__user__avatar = objs[i]['user_customer_flowup__user__avatar']
                user_customer_flowup__user__gender = objs[i]['user_customer_flowup__user__gender']
                user_customer_flowup__user__username = objs[i]['user_customer_flowup__user__username']

                for j in range(i - 1, -1, -1):
                    if objs[j]['have_customer_num'] < temp:
                        objs[j + 1]['have_customer_num'] = objs[j]['have_customer_num']
                        objs[j + 1]['user_customer_flowup__user_id'] = objs[j]['user_customer_flowup__user_id']
                        objs[j + 1]['user_customer_flowup__user__avatar'] = objs[j]['user_customer_flowup__user__avatar']
                        objs[j + 1]['user_customer_flowup__user__gender'] = objs[j]['user_customer_flowup__user__gender']
                        objs[j + 1]['user_customer_flowup__user__username'] = objs[j]['user_customer_flowup__user__username']

                        index = j  # 记下应该插入的位置
                    else:
                        break

                    objs[index]['have_customer_num'] = temp
                    objs[index]['user_customer_flowup__user_id'] = user_customer_flowup__user_id
                    objs[index]['user_customer_flowup__user__avatar'] = user_customer_flowup__user__avatar
                    objs[index]['user_customer_flowup__user__gender'] = user_customer_flowup__user__gender
                    objs[index]['user_customer_flowup__user__username'] = user_customer_flowup__user__username

        ranking_data = objs


    elif type == 'consult_num':  # 按咨询人数


        chatinfo_objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
            userprofile__company_id=company_id).filter(q).filter(send_type=2)

        chatinfo_list_objs = chatinfo_objs.values(
            'userprofile_id',
            'userprofile__avatar',
            'userprofile__username',
            'userprofile__gender',
        ).annotate(have_customer_num=Count('customer_id', 'userprofile_id'))

        objs = list(chatinfo_list_objs)

        for i in range(1, len(objs)):
            if objs[i]['have_customer_num'] > objs[i - 1]['have_customer_num']:
                temp = objs[i]['have_customer_num']
                userprofile_id = objs[i]['userprofile_id']
                userprofile__avatar = objs[i]['userprofile__avatar']
                userprofile__username = objs[i]['userprofile__username']
                userprofile__gender = objs[i]['userprofile__gender']

                for j in range(i - 1, -1, -1):
                    if objs[j]['have_customer_num'] < temp:
                        objs[j + 1]['have_customer_num'] = objs[j]['have_customer_num']
                        objs[j + 1]['userprofile_id'] = objs[j]['userprofile_id']
                        objs[j + 1]['userprofile__avatar'] = objs[j]['userprofile__avatar']
                        objs[j + 1]['userprofile__username'] = objs[j]['userprofile__username']
                        objs[j + 1]['userprofile__gender'] = objs[j]['userprofile__gender']

                        index = j  # 记下应该插入的位置
                    else:
                        break

                    objs[index]['have_customer_num'] = temp
                    objs[index]['userprofile_id'] = userprofile_id
                    objs[index]['userprofile__avatar'] = userprofile__avatar
                    objs[index]['userprofile__username'] = userprofile__username
                    objs[index]['userprofile__gender'] = userprofile__gender


        ranking_data = objs


    elif type == 'expect_chengjiaolv':

        user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer',
                                                                                                'customer_parent').filter(
            user__company_id=company_id).filter(q)

        customer_list_objs = user_customer_belonger_objs.values('user_id', 'user__username','user__gender' ,'user__avatar').annotate(
            have_customer_num=Count('customer'))



        objs = list(customer_list_objs)

        for i in range(1, len(objs)):
            if objs[i]['have_customer_num'] > objs[i - 1]['have_customer_num']:
                temp = objs[i]['have_customer_num']
                user_id = objs[i]['user_id']
                user__username = objs[i]['user__username']
                user__avatar = objs[i]['user__avatar']
                user__gender = objs[i]['user__gender']

                for j in range(i - 1, -1, -1):
                    if objs[j]['have_customer_num'] < temp:
                        objs[j + 1]['have_customer_num'] = objs[j]['have_customer_num']
                        objs[j + 1]['user_id'] = objs[j]['user_id']
                        objs[j + 1]['user__username'] = objs[j]['user__username']
                        objs[j + 1]['user__avatar'] = objs[j]['user__avatar']
                        objs[j + 1]['user__gender'] = objs[j]['user__gender']

                        index = j  # 记下应该插入的位置
                    else:
                        break

                    objs[index]['have_customer_num'] = temp
                    objs[index]['user_id'] = user_id
                    objs[index]['user__username'] = user__username
                    objs[index]['user__avatar'] = user__avatar
                    objs[index]['user__gender'] = user__gender

            ranking_data = objs


    return ranking_data


def deal_customer_flowup_info(data):
    now_time = datetime.now()
    query_user_id = data.get('query_user_id')
    customer_id_list = data.get('customer_id_list')

    user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(
        user_id=query_user_id, customer_id__in=customer_id_list).order_by('create_date')

    last_interval_msg = '还未跟进过'
    if user_customer_belonger_objs:
        for customer_obj in user_customer_belonger_objs:

            last_follow_time = customer_obj.last_follow_time  # 关联的跟进表是否有记录值，没有的话说明没有跟进记录。
            if not last_follow_time:
                last_interval_msg = '还未跟进过'
                customer_status = '还未跟进过'

            elif last_follow_time:

                day_interval = (now_time - last_follow_time).days
                if int(day_interval) == 0:
                    last_interval_msg = '今天跟进'
                    customer_status = '今天跟进'

                else:
                    if int(day_interval) == 1:
                        last_interval_msg = '昨天跟进'
                        customer_status = '昨天已跟进'
                    else:
                        day_interval = day_interval - 1
                        last_interval_msg = '%s天前跟进过' % (day_interval)
                        customer_status = last_follow_time.strftime('%Y-%m-%d')

    return last_interval_msg


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def home_page_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":

        # 查询预计成交率客户信息 | 查询按客户\新增客户(天数)具体信息
        if oper_type == 'query_have_customer_detail_people':

            days = request.POST.get('days')
            # type = request.POST.get('type')
            expedted_pr = request.POST.get('expedted_pr')
            query_user_id = request.POST.get('query_user_id')
            current_page = request.GET.get('current_page')
            length = request.GET.get('length')

            request_data_dict = {
                # 'type': type,
                'days': days,
                'query_user_id': query_user_id,
                'current_page': current_page,  # 文章所属用户的ID
                'length': length,
            }

            forms_obj = QueryHaveCustomerDetailForm(request_data_dict)
            if forms_obj.is_valid():

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                now_time = datetime.now()
                q1 = Q()
                q1.add(Q(**{'user_id': query_user_id}), Q.AND)  # 大于等于

                if days:  # 为0 是查询所有的用户。
                    if int(days) != 0:
                        days = int(days)
                        start_time = (now_time - timedelta(days=days)).strftime("%Y-%m-%d")
                        stop_time = now_time.strftime("%Y-%m-%d")
                        q1.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                        q1.add(Q(**{'create_date__lte': stop_time}), Q.AND)

                if expedted_pr:
                    if expedted_pr == '1_50_pr':
                        q1.add(Q(**{'expedted_pr__gte': 1}), Q.AND)  # 大于等于
                        q1.add(Q(**{'expedted_pr__lte': 50}), Q.AND)
                    elif expedted_pr == '51_80_pr':
                        q1.add(Q(**{'expedted_pr__gte': 51}), Q.AND)  # 大于等于
                        q1.add(Q(**{'expedted_pr__lte': 80}), Q.AND)

                    elif expedted_pr == '81_99_pr':
                        q1.add(Q(**{'expedted_pr__gte': 81}), Q.AND)  # 大于等于
                        q1.add(Q(**{'expedted_pr__lte': 99}), Q.AND)

                    elif expedted_pr == '100_pr':
                        q1.add(Q(**{'expedted_pr': 100}), Q.AND)  # 大于等于

                objs = models.zgld_user_customer_belonger.objects.filter(q1)

                if objs:

                    count = objs.count()
                    # objs = objs.values('customer_id', 'expedted_pr', 'expected_time',
                    #                    'customer__username',
                    #                    'customer__headimgurl',
                    #                    'customer__sex')
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    ret_data = []

                    for obj in objs:
                        last_interval_msg = '还未跟进过'
                        last_follow_time = obj.last_follow_time  # 关联的跟进表是否有记录值，没有的话说明没有跟进记录。
                        if not last_follow_time:
                            last_interval_msg = '还未跟进过'

                        elif last_follow_time:

                            day_interval = (now_time - last_follow_time).days
                            if int(day_interval) == 0:
                                last_interval_msg = '今天跟进'


                            else:
                                if int(day_interval) == 1:
                                    last_interval_msg = '昨天跟进'

                                else:
                                    day_interval = day_interval - 1
                                    last_interval_msg = '%s天前跟进过' % (day_interval)

                        try:
                            username = base64.b64decode(obj.customer.username)
                            customer_name = str(username, 'utf-8')
                            #print('----- 解密b64decode username----->', username)
                        except Exception as e:
                            #print('----- b64decode解密失败的 customer_id 是 | e ----->', obj.customer_id, "|", e)
                            customer_name = '客户ID%s' % (obj.customer_id)

                        ret_data.append({
                            'customer_id': obj.customer_id,
                            'customer_username': customer_name,
                            'headimgurl': obj.customer.headimgurl,
                            'customer_sex': obj.customer.sex,
                            'expected_time': obj.expected_time,  # 预计成交时间
                            'expedted_pr': obj.expedted_pr,  # 预计成交概率

                            'source': obj.source,  # 来源
                            'customer_status': last_interval_msg,  # 最后跟进时间

                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'count': count

                    }

        elif oper_type == 'query_hudong_have_customer_detail_people':

            type = request.POST.get('type')

            days = request.POST.get('days')
            query_user_id = request.POST.get('query_user_id')
            current_page = request.GET.get('current_page')
            length = request.GET.get('length')

            request_data_dict = {
                'type' : type,
                'days': days,
                'query_user_id': query_user_id,
                'current_page': current_page,  # 文章所属用户的ID
                'length': length,
            }

            forms_obj = QueryHudongHaveCustomerDetailPeopleForm(request_data_dict)
            if forms_obj.is_valid():

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                now_time = datetime.now()
                q1 = Q()


                if  days:  # 为0是查询所有的用户。

                    days = int(days)
                    start_time = (now_time - timedelta(days=days)).strftime("%Y-%m-%d")
                    stop_time = now_time.strftime("%Y-%m-%d")
                    q1.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                    q1.add(Q(**{'create_date__lte': stop_time}), Q.AND)

                customer_id_list_objs = ''
                if type == 'chat':
                    q1.add(Q(**{'userprofile_id': query_user_id}), Q.AND)  # 大于等于
                    q1.add(Q(**{'send_type': 2}), Q.AND)  # 大于等于

                    customer_id_list_objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(q1).values_list(
                        'customer_id').distinct()

                elif type == 'follow':
                    q1.add(Q(**{'user_customer_flowup__user_id': query_user_id}), Q.AND)  # 大于等于
                    customer_id_list_objs = models.zgld_follow_info.objects.select_related('user_customer_flowup').filter(q1).values_list('user_customer_flowup__customer_id').distinct()
                #print('---- customer_id_list_objs --->>',customer_id_list_objs)


                customer_id_list = [ c[0] for c  in list(customer_id_list_objs) ]
                #print('----customer_id_list----->>',customer_id_list)

                q2 = Q()
                q2.add(Q(**{'customer_id__in': customer_id_list}), Q.AND)
                q2.add(Q(**{'user_id': query_user_id}), Q.AND)
                objs = models.zgld_user_customer_belonger.objects.filter(q2)
                print('--- [query_hudong_have_customer_detail_people] customer_id_list ---->',customer_id_list)

                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    #print('--- start_line ------>',start_line,stop_line)
                    objs = objs[start_line: stop_line]

                if objs:


                    ret_data = []

                    for obj in objs:
                        last_interval_msg = '还未跟进过'
                        last_follow_time = obj.last_follow_time  # 关联的跟进表是否有记录值，没有的话说明没有跟进记录。
                        if not last_follow_time:
                            last_interval_msg = '还未跟进过'

                        elif last_follow_time:

                            day_interval = (now_time - last_follow_time).days
                            if int(day_interval) == 0:
                                last_interval_msg = '今天跟进'


                            else:
                                if int(day_interval) == 1:
                                    last_interval_msg = '昨天跟进'

                                else:
                                    day_interval = day_interval - 1
                                    last_interval_msg = '%s天前跟进过' % (day_interval)

                        try:
                            username = base64.b64decode(obj.customer.username)
                            customer_name = str(username, 'utf-8')
                            #print('----- 解密b64decode username----->', username)
                        except Exception as e:
                            #print('----- b64decode解密失败的 customer_id 是 | e ----->', obj.customer_id, "|", e)
                            customer_name = '客户ID%s' % (obj.customer_id)

                        ret_data.append({
                            'customer_id': obj.customer_id,
                            'customer_username': customer_name,
                            'headimgurl': obj.customer.headimgurl,
                            'customer_sex': obj.customer.sex,
                            'expected_time': obj.expected_time,  # 预计成交时间
                            'expedted_pr': obj.expedted_pr,  # 预计成交概率

                            'source': obj.source,  # 来源
                            'customer_status': last_interval_msg,  # 最后跟进时间

                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'count': count

                    }

            else:
                response.code = 402
                response.msg = "请求未通过"
                response.data = json.loads(forms_obj.errors.as_json())

    else:

        if oper_type == "acount_data":
            ret_data = {}
            data = request.GET.copy()
            # 汇总数据
            q1 = Q()
            ret_data['count_data'] = deal_search_time(data, q1)

            # 昨天数据
            q2 = Q()
            now_time = datetime.now()
            start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q2.add(Q(**{'create_date__lte': stop_time}), Q.AND)
            ret_data['yesterday_data'] = deal_search_time(data, q2)

            q3 = Q()
            start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q3.add(Q(**{'create_date__lte': stop_time}), Q.AND)
            ret_data['nearly_seven_days'] = deal_search_time(data, q3)

            q4 = Q()
            start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            q4.add(Q(**{'create_date__lte': stop_time}), Q.AND)
            ret_data['nearly_thirty_days'] = deal_search_time(data, q4)

            # 今日新增
            # q5 = Q()
            # now_time = datetime.now().strftime("%Y-%m-%d")
            # q5.add(Q(**{'create_date__gte': now_time}), Q.AND)
            # ret_data['today_data'] = deal_search_time(data, q5)

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,

            }

        elif oper_type == "line_info":
            # print('request.POST', request.POST)

            forms_obj = LineInfoForm(request.POST)

            if forms_obj.is_valid():

                user_id = request.GET.get('user_id')
                user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
                company_id = user_obj[0].company_id

                data = request.POST.copy()

                data['company_id'] = company_id

                ret_data = {}
                for index in ['index_type_1', 'index_type_2', 'index_type_2', 'index_type_3', 'index_type_4']:
                    ret_dict = {}
                    if index == 'index_type_1':
                        data['index_type'] = 1
                    elif index == 'index_type_2':
                        data['index_type'] = 2
                    elif index == 'index_type_3':
                        data['index_type'] = 3
                    elif index == 'index_type_4':
                        data['index_type'] = 4

                    for day in [7, 15, 30]:
                        ret_list = []
                        if index == 'index_type_4' and day != 15:
                            continue

                        for _day in range(int(day), 0, -1):
                            now_time = datetime.now()
                            start_time = (now_time - timedelta(days=_day)).strftime("%Y-%m-%d")
                            stop_time = (now_time - timedelta(days=_day - 1)).strftime("%Y-%m-%d")
                            # stop_time = now_time.strftime("%Y-%m-%d")
                            data['start_time'] = start_time
                            data['stop_time'] = stop_time
                            ret_list.append({'statics_date': start_time, 'value': deal_line_info(data)})

                        # print('------- ret_list ------->>', ret_list)
                        if day == 7:
                            ret_dict['nearly_seven_days'] = ret_list
                        elif day == 15:
                            ret_dict['nearly_fifteen_days'] = ret_list
                        elif day == 30:
                            ret_dict['nearly_thirty_days'] = ret_list

                    ret_data[index] = ret_dict

                # if index_type == 5: #客户与我的互动
                # ret_data = {}
                ret_dict = {}
                ret_list = []

                user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).aggregate(
                    praise_num=Count('praise'))  # 被点赞总数
                praise_num = user_pop_queryset.get('praise_num')

                saved_total_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,
                    action=8).count()  # 保存电话
                query_product_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,
                    action=7).count()  # 咨询产品

                user_forward_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).aggregate(
                    forward_num=Count('forward'))  # 转发名片
                forward_num = user_forward_queryset.get('forward_num')

                call_phone_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,  # 拨打电话
                    action=10).count()

                _ret_dict = {

                    'praise_num': praise_num,  # 被点赞总数
                    'query_product_num': query_product_num,  # 咨询产品
                    'forward_mingpian_num': forward_num,  # 转发名片
                    'call_phone_num': call_phone_num,  # 拨打电话
                    'saved_phone_num': saved_total_num,  # 保存电话
                }

                # ret_list.append(_ret_dict)
                # # ret_dict['nearly_fifteen_days'] = ret_list
                ret_data['index_type_5'] = _ret_dict
                # print('------ ret_data ------->>>', ret_data)

                # if index_type == 6: #客户与我的互动
                # ret_data = {}
                ret_list = []

                view_mingpian = models.zgld_accesslog.objects.filter(user__company_id=company_id,
                    action=1).count()  # 保存电话

                view_product_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,
                    action=2).count()  # 咨询产品

                view_website_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,  # 拨打电话
                    action=4).count()

                # _ret_dict = {
                #     'praise_num': view_mingpian,                  # 被点赞总数
                #     'query_product_num': view_product_num,        # 咨询产品
                #     'forward_mingpian_num': view_website_num,     # 转发名片
                # }
                view_mingpian = int(view_mingpian)
                view_product_num = int(view_product_num)
                view_website_num = int(view_website_num)
                total = sum([view_mingpian, view_product_num, view_website_num])

                # print('--- total ----->', total)
                _ret_dict = {
                    'view_mingpian': '{:.2f}'.format(view_mingpian / total * 100),
                    'view_product_num': '{:.2f}'.format(view_product_num / total * 100),
                    'view_website_num': '{:.2f}'.format(view_website_num / total * 100)
                }

                # ret_list.append(_ret_dict)
                ret_data['index_type_6'] = _ret_dict

                # 查询成功 返回200 状态码

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data
                }

            else:
                response.code = 303
                response.msg = "未验证通过"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == "sales_ranking_customer_num":
            forms_obj = LineInfoForm(request.POST)

            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
                company_id = user_obj[0].company_id
                ret_data = {}
                # 汇总数据
                q1 = Q()
                data = {'type': 'customer_data'}

                q1.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等
                ret_data['total_num_have_customer'] = deal_sale_ranking_data(data, q1)

                # 昨天数据
                q2 = Q()
                now_time = datetime.now()
                start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q2.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q2.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['yesterday_new_customer'] = deal_sale_ranking_data(data, q2)

                q3 = Q()
                start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q3.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q3.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['nearly_seven_new_customer'] = deal_sale_ranking_data(data, q3)

                q4 = Q()
                start_time = (now_time - timedelta(days=15)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q4.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q4.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['nearly_fifteen_new_customer'] = deal_sale_ranking_data(data, q4)

                q5 = Q()
                start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q5.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q5.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q5.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['nearly_thirty_new_customer'] = deal_sale_ranking_data(data, q5)

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data
                }

        elif oper_type == "hudong_pinlv_customer_num":

            user_id = request.GET.get('user_id')
            user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
            company_id = user_obj[0].company_id
            ret_data = {}

            for type in ['follow_num', 'consult_num']:
                data = {'type': type, 'company_id': company_id}
                ret_dict = {}

                # # 汇总数据
                # q1 = Q()
                # q1.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                # ret_data['total_num_have_customer'] = deal_sale_ranking_data(data,q1)

                # 昨天数据
                q2 = Q()
                now_time = datetime.now()
                start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q2.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['yesterday_data'] = deal_sale_ranking_data(data, q2)

                q3 = Q()
                start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q3.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['nearly_seven_data'] = deal_sale_ranking_data(data, q3)

                q4 = Q()
                start_time = (now_time - timedelta(days=15)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q4.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['nearly_fifteen_data'] = deal_sale_ranking_data(data, q4)

                q5 = Q()
                start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q5.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q5.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['nearly_thirty_data'] = deal_sale_ranking_data(data, q5)

                ret_data[type] = ret_dict

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data
            }

        elif oper_type == "expect_chengjiaolv_customer_num":
            user_id = request.GET.get('user_id')
            user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
            company_id = user_obj[0].company_id

            # for  pr in  in ['1_50','51_80','81_99','100']:
            ret_dict = {}
            q2 = Q()
            data = {'type': 'expect_chengjiaolv',
                    'company_id': company_id
                    }

            q2.add(Q(**{'expedted_pr__gte': 1}), Q.AND)  # 大于等于
            q2.add(Q(**{'expedted_pr__lte': 50}), Q.AND)
            ret_dict['pr_1_50'] = deal_sale_ranking_data(data, q2)

            q3 = Q()
            q3.add(Q(**{'expedted_pr__gte': 51}), Q.AND)  # 大于等于
            q3.add(Q(**{'expedted_pr__lte': 80}), Q.AND)
            ret_dict['pr_51_80'] = deal_sale_ranking_data(data, q3)

            q4 = Q()
            q4.add(Q(**{'expedted_pr__gte': 81}), Q.AND)  # 大于等于
            q4.add(Q(**{'expedted_pr__lte': 99}), Q.AND)
            ret_dict['pr_81_99'] = deal_sale_ranking_data(data, q4)

            q5 = Q()
            q5.add(Q(**{'expedted_pr': 100}), Q.AND)  # 大于等于
            ret_dict['pr_100'] = deal_sale_ranking_data(data, q5)

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_dict
            }

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)

