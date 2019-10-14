from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.user_verify import UserSelectForm
from django.db.models import Q, Count, Sum
import json, datetime, redis

# 获取redis_name
def get_redis_name(number_days, request_type):
    if request_type == 'article':
        if number_days == 'all_days':
            redis_name = 'leida_redis_data_statistics_article'
        elif number_days == 'today':
            redis_name = 'leida_redis_data_statistics_article_today'
        elif number_days == 'seven_days':
            redis_name = 'leida_redis_data_statistics_article_seven_days'
        elif number_days == 'thirty_days':
            redis_name = 'leida_redis_data_statistics_article_thirty_days'
        else:
            redis_name = 'leida_redis_data_statistics_article_yesterday'

    else:
        if number_days == 'all_days':
            redis_name = 'leida_redis_data_statistics_user'
        elif number_days == 'today':
            redis_name = 'leida_redis_data_statistics_user_today'
        elif number_days == 'seven_days':
            redis_name = 'leida_redis_data_statistics_user_seven_days'
        elif number_days == 'thirty_days':
            redis_name = 'leida_redis_data_statistics_user_thirty_days'
        else:
            redis_name = 'leida_redis_data_statistics_user_yesterday'
    return redis_name

# 雷达后台首页 数据统计
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        """   # 参数说明    detail_type
                     
            detail_type 判断 进入详情类型 起因: 后台数据偏多 利用该参数判断 跳进某个详情页面 避免不进详情 查询到详情数据
            article_comments    查询评论详情
            thumb_up_number     点赞详情
            call_phone          拨打电话详情
            active_message      主动发送消息详情
            click_the_dialog_box 点击对话框详情
            video_view_duration 视频详情
            the_reading_time    文章阅读详情
            click_the_quantity  点击量详情
            forwarding_article  转发量详情
            --------------------------------------------------员工统计
            copy_the_nickname           复制昵称详情
            number_valid_conversations  有效对话详情
            average_response_time       平均响应时长详情
            sending_applet              发送小程序详情
        """

        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            number_days = request.GET.get('number_days')  # 天数

            company_id = request.GET.get('company_id')  # 公司

            public_q = Q()
            if company_id:
                public_q.add(Q(company_id=company_id), Q.AND)

            detail_type = request.GET.get('detail_type')  # 点击某个详情页面

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            redis_key = 'leida_data_statistics_company_{}'.format(company_id)

            # 文章数据分析
            if oper_type == 'article_data_analysis':
                redis_name = get_redis_name(number_days, 'article')

                article_id = request.GET.get('article_id')  # 区分文章

                redis_article_data = rc.hget(redis_name, redis_key)

                ret_data = []       # 数据列表
                data_count = 0      # 列表数量

                if not redis_article_data: # 如果该公司没有数据 直接返回
                    response.code = 200
                    response.msg = '暂无数据'
                    response.data = {
                        'count': data_count,
                        'ret_data': ret_data
                    }
                    return JsonResponse(response.__dict__)

                redis_article_data = eval(redis_article_data)

                objs = redis_article_data       # 查询全部文章的数据
                if article_id: # 查询单个文章数据
                    for obj in redis_article_data:
                        if int(obj.get('article_id')) == int(article_id): # 文章ID
                            objs = [obj]
                            break

                data_count = len(objs) # 列表总数

                start_line = (current_page - 1) * length
                stop_line = start_line + length
                if not detail_type:
                    objs = objs[start_line: stop_line]

                list_num = 0
                for obj in objs:
                    forwarding_article_data = obj.get('forwarding_article_data')        # 转发量
                    click_quantity_data = obj.get('click_the_quantity')                 # 点击量
                    the_reading_data = obj.get('the_reading_time')                      # 文章阅读数据
                    video_view_data = obj.get('video_view_duration')                    # 视频数据
                    click_dialog_data = obj.get('click_the_dialog_box')                 # 点击对话框数据
                    user_active_send_data = obj.get('active_message')                   # 主动发送数据
                    call_phone_data = obj.get('call_phone')                             # 拨打电话数据
                    click_thumb_data = obj.get('thumb_up_number')                       # 文章点赞数据
                    article_comments_data = obj.get('article_comments')                 # 文章评论数据

                    len_click_quantity_data = len(click_quantity_data)
                    len_forwarding_article_data = len(forwarding_article_data)
                    len_the_reading_data = len(the_reading_data.get('data_list'))
                    len_video_view_data = len(video_view_data.get('data_list'))
                    len_click_dialog_data = len(click_dialog_data)
                    len_user_active_send_data = len(user_active_send_data)
                    len_call_phone_data= len(call_phone_data)
                    len_click_thumb_data = len(click_thumb_data)
                    len_article_comments_data = len(article_comments_data)


                    ret_data.append({
                        'id': obj.get('article_id'),
                        'article_name': obj.get('article_title'),                         # 文章名称
                        'click_num': str(len_click_quantity_data) + '次',                  # 文章点击数量
                        'click_data': [],
                        'forward_num': str(len_forwarding_article_data) + '次',            # 文章转发数量
                        'forward_data': [],
                        'avg_reading_info': the_reading_data.get('text'),                 # 文章阅读数据
                        'avg_reading_data':[],
                        'len_video_text': video_view_data.get('text'),                     # 视频信息
                        'len_video_data': [],
                        'click_dialog_num': str(len_click_dialog_data) + '次',             # 点击对话框
                        'click_dialog_data': [],
                        'user_active_send_num': str(len_user_active_send_data) + '次',     # 主动发送消息数量
                        'user_active_send_data': [],
                        'call_phone_num': str(len_call_phone_data) + '次',                 # 拨打电话次数
                        'call_phone_data': [],
                        'click_thumb_num': str(len_click_thumb_data) + '次',               # 文章点赞次数
                        'click_thumb_data': [],
                        'article_comments_num': str(len_article_comments_data) + '条',     # 文章评论次数
                        'article_comments_data': [],
                    })

                    count = 0  # 详情总数
                    key = ''  # 详情键
                    detail_data = []
                    article_order_by = 'create_date'

                    # 文章点击数据
                    if detail_type == 'click_the_quantity':
                        count = len_click_quantity_data
                        key = 'click_data'
                        detail_data = click_quantity_data

                    # 文章转发数据
                    elif detail_type == 'forwarding_article':
                        count = len_forwarding_article_data
                        key = 'forward_data'
                        detail_data = forwarding_article_data

                    # 文章阅读数据
                    elif detail_type == 'the_reading_time':
                        count = len_the_reading_data
                        key = 'avg_reading_data'
                        detail_data = the_reading_data.get('data_list')

                    # 视频数据
                    elif detail_type == 'video_view_duration': # 排序问题
                        article_order_by = 'id__count'
                        count = len_video_view_data
                        key = 'video_view_data'
                        detail_data = video_view_data.get('data_list')

                    # 点击对话框数据
                    elif detail_type == 'click_the_dialog_box':
                        count = len_click_dialog_data
                        key = 'click_dialog_data'
                        detail_data = click_dialog_data

                    # 主动发送消息数据
                    elif detail_type == 'active_message':
                        count = len_user_active_send_data
                        key = 'user_active_send_data'
                        detail_data = user_active_send_data

                    # 拨打电话数据
                    elif detail_type == 'call_phone':
                        count = len_call_phone_data
                        key = 'call_phone_data'
                        detail_data = call_phone_data

                    # 点赞数据
                    elif detail_type == 'thumb_up_number':  # 点赞
                        count = len_click_thumb_data
                        key = 'click_thumb_data'
                        detail_data = click_thumb_data

                    # 查询评论数据
                    elif detail_type == 'article_comments':  # 查询评论
                        count = len_article_comments_data
                        key = 'article_comments_data'
                        detail_data = article_comments_data

                    ret_data[list_num]['count'] = count         # 数据总数

                    detail_data = sorted(detail_data, key=lambda x: x[article_order_by], reverse=True)
                    ret_data[list_num][key] = detail_data[start_line: stop_line]

                    list_num += 1

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': data_count,
                }

                response.note = {
                    'id': '文章ID',
                    'article_name': '文章名称',
                    'forward_count': '文章转发量',
                    'forward_data--文章转发数据': {
                        "customer_username": "客户名称",
                        "user_username": "员工名称",
                        "create_date": "点击时间",
                    },

                    'click_count': '文章点击量',
                    'click_data--文章点击数据': {
                        "customer_username": "客户名称",
                        "user_username": "员工名称",
                        "create_date": "点击时间",
                    },

                    'avg_reading_info': '文章阅读信息',
                    'avg_reading_data': {
                        "customer__username": "客户名称",
                        "reading_time": '阅读时长',
                        "create_date": "阅读时间",
                    },

                    'len_video_text': '视频信息',
                    'len_video_data--视频详情': {
                        'customer__username': '客户名称',
                        'id__count': '播放次数',
                        'video_time__sum': '总时长',
                        'avg': '平均时长',
                    },

                    'click_dialog_num': '点击对话框次数',
                    'click_dialog_data--点击对话框数据': {
                        'customer_username': '客户名称',
                        'create_date': '发送消息时间',
                    },

                    'user_active_send_num': '主动发送消息',
                    'user_active_send_data--主动发送数据': {
                        'customer_username': '客户名称',
                        'content': '发送内容',
                        'create_date': '发送消息时间',
                    },

                    'call_phone_num': '拨打电话次数',
                    'call_phone_data--拨打电话数据': {
                        'customer_name': '客户名称',
                        'create_date': '点赞时间',
                    },

                    'click_thumb_num': '文章点赞次数',
                    'click_thumb_data--文章点赞数据': {
                        'customer_name': '客户名称',
                        'create_date': '点赞时间',
                    },

                    'article_comments_num': '文章评论次数',
                    'article_comments_data--文章评论详情': {
                        'customer_username': '客户名称',
                        'content': '评论内容',
                        'is_audit_pass': '是否审核',
                        'create_date': '评论时间',
                    },
                }

            # 员工数据分析
            elif oper_type == 'employee_data_analysis':
                redis_name = get_redis_name(number_days, 'user')

                user_id = request.GET.get('id')  # 区分用户

                redis_user_data = rc.hget(redis_name, redis_key)
                ret_data = []
                if not redis_user_data: # 该公司没有数据直接返回
                    response.code = 200
                    response.msg = '暂无数据'
                    response.data = {
                        'red_data': ret_data,
                        'count': 0
                    }
                    return JsonResponse(response.__dict__)

                redis_user_data = eval(redis_user_data)
                objs = redis_user_data  # 查询全部用户的数据
                if user_id:  # 查询单个文章数据
                    for obj in redis_user_data:
                        if int(obj.get('user_id')) == int(user_id):  # 用户ID
                            objs = [obj]
                            break

                data_count = len(objs)  # 列表总数

                start_line = (current_page - 1) * length
                stop_line = start_line + length
                if not detail_type:
                    objs = objs[start_line: stop_line]

                list_num = 0 # 记录第几次
                for obj in objs:
                    copy_the_nickname = obj.get('copy_the_nickname')                            # 复制昵称
                    number_valid_conversations = obj.get('number_valid_conversations')          # 雷达内有效对话数据
                    average_response_time_obj = obj.get('average_response_time')                    # 平均回复时长数据
                    sending_applet = obj.get('sending_applet')                                  # 发送小程序

                    copy_the_nickname_len = len(copy_the_nickname)
                    number_valid_conversations_len = len(number_valid_conversations.get('data_list'))
                    response_time = 0
                    for i in average_response_time_obj.get('data_list'):
                        response_time += i.get('response_time')
                    average_response_time = len(average_response_time_obj.get('data_list'))
                    average_response_time_len = 0
                    if average_response_time >= 1:
                        average_response_time_len = int(response_time / average_response_time)


                    sending_applet_len = len(sending_applet)


                    ret_data.append({
                        'id': obj.get('user_id'),
                        'user_name': obj.get('user_name'),  # 员工名称

                        'copy_nickname': str(copy_the_nickname_len) + '次',               # 复制昵称次数
                        'copy_nickname_data': [],

                        'effective_dialogue_num': str(number_valid_conversations_len) + '次',       # 有效对话数量
                        'effective_dialogue_data': [],

                        'average_response_avg': str(average_response_time_len) + '秒',   # 平均响应时长
                        'average_response_data': [],  # 平均响应时长

                        'sending_applet_num': str(sending_applet_len) + '次',            # 发送小程序数量
                        'sending_applet_data': [],  # 发送小程序数据
                    })

                    count = 0
                    key = ''
                    detail_data = []
                    user_order_by = 'create_date'

                    #  复制昵称 次数及数据
                    if detail_type == 'copy_the_nickname':
                        count = copy_the_nickname_len
                        key = 'copy_nickname_data'
                        detail_data = copy_the_nickname

                    # 有效对话次数
                    elif detail_type == 'number_valid_conversations':
                        count = number_valid_conversations_len
                        key = 'effective_dialogue_data'
                        detail_data = number_valid_conversations.get('data_list')

                    # 咨询响应平均时长
                    elif detail_type == 'average_response_time':
                        count = len(average_response_time_obj.get('data_list'))
                        key = 'average_response_data'
                        detail_data = average_response_time_obj.get('data_list')
                        user_order_by = 'stop_date'

                    # 发送小程序
                    elif detail_type == 'sending_applet':
                        count = sending_applet_len
                        key = 'sending_applet_data'
                        detail_data = sending_applet

                    ret_data[list_num]['count'] = count
                    detail_data = sorted(detail_data, key=lambda x: x[user_order_by], reverse=True)
                    ret_data[list_num][key] = detail_data[start_line: stop_line]

                    list_num += 1

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': data_count,
                }
                response.note = {
                    'username': '咨询用户名称',

                    'copy_nickname': '复制昵称次数',
                    'copy_nickname_data--复制昵称数据': {
                        'customer__username': '客户名称',
                        'create_date': '复制昵称时间',
                    },

                    'effective_dialogue_num': '有效对话数量',
                    'effective_dialogue_data': {
                        'name': '发送消息人名称',
                        'text': '发送的消息',
                        'create_date': '发送消息时间',
                    },

                    'average_response_avg': '平均响应时长',
                    'average_response_data--平均响应时长数据': {
                        'customer__username': '客户名称',
                        'start_date': '客户发送对话时间',
                        'stop_date': '咨询回复时间',
                        'response_time': '响应时长',
                    },

                    'sending_applet_num': '发送小程序数量',
                    'sending_applet_data--发送小程序数据': {
                        'customer__username': '客户名称',
                        'create_date': '创建时间',
                    },
                }

            else:
                response.code = 402
                response.msg = '请求异常'

        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)



# 雷达后台首页 小程序数据统计
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def xcx_data_statistics(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    admin_user_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
    pub_q = Q() # 公共Q 条件
    pub_q.add(Q(company_id=admin_user_obj.company_id), Q.AND)

    if request.method == 'GET':

        # 员工数据分析(雷达版)
        if oper_type == 'xcx_ld_employee_data_analysis':
            """
            
            """
            form_obj = UserSelectForm(request.GET)
            if form_obj.is_valid():
                current_page = form_obj.cleaned_data['current_page']
                length = form_obj.cleaned_data['length']
                q = Q()

                user_objs = models.zgld_userprofile.objects.filter(q).order_by('-create_date')
                count = user_objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    user_objs = user_objs[start_line: stop_line]

                ret_data = []
                for obj in user_objs:
                    up_down_objs = models.zgld_up_down.objects.filter(user_id=obj.id)
                    oper_log_objs = models.ZgldUserOperLog.objects.filter(oper_type=1, user_id=obj.id)
                    dingdan_objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(yewuUser_id=obj.id)


                    ret_data.append({
                        'user_id': obj.id,
                        'user_name': obj.username,
                        'copy_nickname': oper_log_objs.count(),
                        'forwarding_business_card': obj.forward,
                        'order_number': dingdan_objs.count(),
                        'by_spectrum': up_down_objs.count(),
                        'effective_radar_communication': '雷达内有效对话',
                        'average_response_time_consultation': '咨询平均响应时长',
                    })


                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }
                response.note = {
                    'user_id': '用户ID',
                    'user_name': '用户昵称',
                    'copy_nickname': '复制昵称',
                    'forwarding_business_card': '转发名片',
                    'order_number': '订单数量',
                    'by_spectrum': '靠谱数量',
                    'effective_radar_communication': '雷达内有效对话',
                    'average_response_time_consultation': '咨询平均响应时长',
                }

            else:
                response.code = 301
                response.msg = form_obj.errors.as_json()


        # 文章数据分析(雷达版)
        elif oper_type == 'xcx_ld_article_data_analysis':
            pass

        # 员工数据分析(案例版)
        elif oper_type == 'xcx_al_employee_data_analysis':
            pass

        # 文章数据分析(案例版)
        elif oper_type == 'xcx_al_article_data_analysis':
            pass

        else:
            pass

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)









