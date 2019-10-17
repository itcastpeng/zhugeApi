from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.user_verify import UserSelectForm
from publicFunc.base64 import b64decode
from django.db.models import Q, Count, Sum
import json, datetime, redis, time

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

        # 案例数据分析(案例版)
        elif oper_type == 'xcx_al_article_data_analysis':
            case_id = request.GET.get('case_id')  # 查询单日记
            task_type = request.GET.get('task_type', 0)
            """查询类型 1点击量 2转发次数 3案例查看时长 4视频查看时长 5主动点击对话框 6主动发送消息次数 7用户拨打电话次数 8点赞数 9评论数 0默认列表页"""

            detail_current_page = int(request.GET.get('detail_current_page', 1))  # 详情分页
            detail_length = int(request.GET.get('detail_length', 10))  # 详情分页
            detail_start_line = (detail_current_page - 1) * detail_length
            detail_stop_line = detail_start_line + detail_length

            form_obj = UserSelectForm(request.GET)
            if form_obj.is_valid():
                current_page = form_obj.cleaned_data['current_page']
                length = form_obj.cleaned_data['length']
                q = Q()
                if case_id:
                    q.add(Q(id=case_id), Q.AND)
                objs = models.zgld_case.objects.filter(pub_q, q).order_by('-create_date')
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    # ===========================点击量=========================
                    click_the_quantity_objs = models.zgld_accesslog.objects.filter(action=22, diary__case_id=obj.id)

                    # =========================用户主动发送消息==================
                    user_actively_clicks_dialog_box_objs = models.zgld_chatinfo.objects.select_related(
                        'userprofiles'
                    ).filter(
                        send_type__in=[1,  2],
                        userprofile__company_id=admin_user_obj.company_id,
                    ).values(
                        'userprofile_id', 'userprofile__username', 'customer_id', 'customer__username'
                    ).annotate(Count('id'))
                    user_sends_message = user_actively_clicks_dialog_box_objs.count()

                    # ===========================点赞数===========================
                    thumb_up_for_objs = models.zgld_diary_action.objects.select_related(
                        'customer'
                    ).filter(action=1, case_id=case_id)

                    # ==========================评论数==========================
                    comments_num_objs = models.zgld_diary_comment.objects.select_related(
                        'from_customer', 'diary'
                    ).filter(diary__case_id=case_id)

                    # ==========================拨打电话数======================
                    user_calls_num_objs = models.zgld_accesslog.objects.select_related(
                        'customer'
                    ).filter(
                        action=10,
                        user__company=admin_user_obj.company_id
                    )

                    #=========================点击对话框==============================
                    click_on_dialog_box_objs = models.zgld_click_on_the_dialog_box.objects.select_related(
                        'customer'
                    ).filter(
                        xcx_type=1, customer__company_id=admin_user_obj.company_id
                    )

                    # ========================案例查看时长=========================
                    view_case_diary_objs = models.zgld_record_view_case_diary_video.objects.select_related(
                        'customer'
                    ).filter(
                        log_type=1, customer__company_id=admin_user_obj.company_id
                    )
                    view_case_diary_total_length = 0 # 总时长
                    view_case_diary_avg_length = 0 # 平均时长
                    for view_case_diary_obj in view_case_diary_objs:
                        view_case_diary_total_length += view_case_diary_obj.see_time
                    if view_case_diary_objs.count() > 0:
                        view_case_diary_avg_length = int(view_case_diary_total_length / view_case_diary_objs.count())
                    case_view_total_average_duration = str(view_case_diary_total_length) + '/' + str(view_case_diary_avg_length)

                    # =========================视频查看时长=====================
                    view_video_objs = models.zgld_record_view_case_diary_video.objects.filter(
                        log_type=2, customer__company_id=admin_user_obj.company_id
                    )
                    view_video_count = view_video_objs.count()   # 查看视频次数
                    view_video_total_count = 0 # 查看视频总时长
                    view_video_avg_count = 0 # 查看视频平均时长
                    for view_video_obj in view_video_objs:
                        view_video_total_count += view_video_obj.see_time
                    if view_video_count > 0:
                        view_video_avg_count = int(view_video_total_count / view_video_count)
                    video_view_total_average_duration = str(view_video_count) + '/' + str(view_video_total_count) + '/' + str(view_video_avg_count)

                    # ============================转发===========================
                    amount_of_forwarding_q = Q()
                    amount_of_forwarding_q.add(
                        Q(diary__case__user__company_id=admin_user_obj.company_id) | Q(
                            case__user__company_id=admin_user_obj.company_id) , Q.AND
                    )
                    amount_of_forwarding_q.add(Q(diary__case_id=obj.id) | Q(case_id=obj.id), Q.AND)
                    amount_of_forwarding_objs = models.zgld_record_view_case_diary_video.objects.select_related(
                        'customer', 'diary', 'case'
                    ).filter(
                        amount_of_forwarding_q,
                        log_type=3,
                    )


                    detail_data = []
                    detail_count = 0
                    if case_id and task_type:

                        # 1点击量
                        if task_type in [1, '1']:
                            detail_count = click_the_quantity_objs.count()
                            click_the_quantity_objs = click_the_quantity_objs[detail_start_line: detail_stop_line]
                            for click_the_quantity_obj in click_the_quantity_objs:
                                detail_data.append({
                                    'user_name': click_the_quantity_obj.user.username,
                                    'customer_name': click_the_quantity_obj.customer.username,
                                })

                        # 2转发次数
                        elif task_type in [2, '2']:
                            detail_count = amount_of_forwarding_objs.count()
                            amount_of_forwarding_objs = amount_of_forwarding_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for amount_of_forwarding_obj in amount_of_forwarding_objs:
                                detail_data.append({
                                    'user_name': amount_of_forwarding_obj.user.username,
                                    'create_date': amount_of_forwarding_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    'customer_name': b64decode(amount_of_forwarding_obj.customer.username),
                                })

                        # 3案例查看时长
                        elif task_type in [3, '3']:
                            detail_count = view_case_diary_objs.count()
                            view_case_diary_objs = view_case_diary_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for view_case_diary_obj in view_case_diary_objs:
                                try:
                                    customer_name = b64decode(view_case_diary_obj.customer.username)
                                except Exception:
                                    customer_name = view_case_diary_obj.customer.username

                                detail_data.append({
                                    'customer_name': customer_name,
                                    'create_date': view_case_diary_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    'see_time': view_case_diary_obj.see_time,
                                })

                        # 4视频查看时长
                        elif task_type in [4, '4']:
                            detail_count = view_video_objs.count()
                            view_video_objs = view_video_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for view_video_obj in view_video_objs:
                                try:
                                    customer_name = b64decode(view_video_obj.customer.username)
                                except Exception:
                                    customer_name = view_video_obj.customer.username

                                detail_data.append({
                                    'customer_name': customer_name,
                                    'create_date': view_video_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    'see_time': view_video_obj.see_time,
                                })

                        # 5主动点击对话框
                        elif task_type in [5, '5']:
                            detail_count = click_on_dialog_box_objs.count()
                            click_on_dialog_box_objs = click_on_dialog_box_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for click_on_dialog_box_obj in click_on_dialog_box_objs:
                                detail_data.append({
                                    'customer_name': b64decode(click_on_dialog_box_obj.customer.username),
                                    'create_date': click_on_dialog_box_obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                                })

                        # 6主动发送消息次数
                        elif task_type in [6, '6']:
                            detail_count = user_actively_clicks_dialog_box_objs.count()
                            for user_actively_clicks_dialog_box_obj in user_actively_clicks_dialog_box_objs[detail_start_line: detail_stop_line]:
                                user_actively_clicks_objs = models.zgld_chatinfo.objects.select_related(
                                    'userprofile', 'customer'
                                ).filter(
                                    send_type__in=[2],
                                    userprofile_id=user_actively_clicks_dialog_box_obj['userprofile_id'],
                                    customer_id=user_actively_clicks_dialog_box_obj['customer_id'],
                                ).order_by('create_date')
                                user_actively_clicks_obj = user_actively_clicks_objs[0]
                                detail_data.append({
                                    'customer__username': b64decode(user_actively_clicks_obj.customer.username),
                                    'content': json.loads(user_actively_clicks_obj.content),
                                })

                        # 7用户拨打电话次数
                        elif task_type in [7, '7']:
                            detail_count = user_calls_num_objs.count()
                            user_calls_num_objs = user_calls_num_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for user_calls_num_obj in user_calls_num_objs:
                                detail_data.append({
                                    'customer_name': b64decode(user_calls_num_obj.customer.username),
                                    'create_date': user_calls_num_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                })

                        # 8点赞数
                        elif task_type in [8, '8']:
                            detail_count = thumb_up_for_objs.count()
                            thumb_up_for_objs = thumb_up_for_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for thumb_up_for_obj in thumb_up_for_objs:
                                detail_data.append({
                                    'customer_name': b64decode(thumb_up_for_obj.customer.username),
                                    'create_date': thumb_up_for_obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                                })

                        # 9评论数
                        elif task_type in [9, '9']:
                            detail_count = comments_num_objs.count()
                            comments_num_objs = comments_num_objs.order_by(
                                '-create_date'
                            )[detail_start_line: detail_stop_line]
                            for comments_num_obj in comments_num_objs:
                                detail_data.append({
                                    'customer_name': b64decode(comments_num_obj.from_customer.username),
                                    'create_date': comments_num_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    'content': b64decode(comments_num_obj.content),
                                    'is_audit_pass': comments_num_obj.get_is_audit_pass_display()
                                })


                    ret_data.append({
                        'case_id': obj.id,                          # 案例ID
                        'case_name': obj.case_name,                 # 案例名称

                        'click_the_quantity': click_the_quantity_objs.count(),              # 点击量
                        'user_sends_message': user_sends_message,                           # 用户主动发送消息
                        'thumb_up_for': thumb_up_for_objs.count(),                          # 点赞数
                        'comments_num': comments_num_objs.count(),                          # 评论数
                        'user_calls_num': user_calls_num_objs.count(),                      # 用户拨打电话
                        'user_actively_clicks_dialog_box': click_on_dialog_box_objs.count(),    # 用户主动点击对话框
                        'case_view_total_average_duration': case_view_total_average_duration,   # 案例查看 总/平均时长
                        'video_view_total_average_duration': video_view_total_average_duration, # 视频查看 次数 总/平均时长
                        'amount_of_forwarding': amount_of_forwarding_objs.count(),                 # 转发量
                        'detail_data': detail_data,                                         # 详情数据
                        'detail_count': detail_count,                                       # 详情总数
                    })



                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'ret_data': ret_data,
                }

            else:
                response.code = 301
                response.msg = form_obj.errors.as_json()


        # 员工数据分析(案例版)
        elif oper_type == 'xcx_al_employee_data_analysis':
            uid = request.GET.get('uid') # 查询单个人
            task_type = request.GET.get('task_type', 0) # 查询类型 1复制昵称 2雷达内有效对话 3响应时长 4订单数量

            detail_current_page = int(request.GET.get('detail_current_page', 1))# 详情分页
            detail_length = int(request.GET.get('detail_length', 10))            # 详情分页
            detail_start_line = (detail_current_page - 1) * detail_length
            detail_stop_line = detail_start_line + detail_length

            response.note = {
                'user_id': '用户ID',
                'user_name': '用户昵称',
                'copy_nickname': '复制昵称',
                'order_number': '订单数量',
                'effective_radar_communication': '雷达内有效对话',
                'average_response_time_consultation': '咨询平均响应时长',
                'detail_data': '详情数据',
                'detail_count': '详情总数',
            }
            form_obj = UserSelectForm(request.GET)
            if form_obj.is_valid():
                current_page = form_obj.cleaned_data['current_page']
                length = form_obj.cleaned_data['length']
                q = Q()
                if uid:
                    q.add(Q(id=uid), Q.AND)
                user_objs = models.zgld_userprofile.objects.filter(q, pub_q).order_by('-create_date')
                count = user_objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    user_objs = user_objs[start_line: stop_line]

                ret_data = []
                for obj in user_objs:

                    oper_log_objs = models.ZgldUserOperLog.objects.filter(oper_type=1, user_id=obj.id)
                    dingdan_objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli', 'shouHuoRen').filter(yewuUser_id=obj.id)

                    # ====================================================响应平均时长-=========================================
                    chatinfo_objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(send_type__in=[1, 2], userprofile_id=obj.id)
                    average_response_time_consultation_list = []
                    is_customer = False
                    zong_avg_time = 0 # 总平均响应时长
                    for chatinfo_obj in chatinfo_objs.order_by('create_date'):
                        create_date = chatinfo_obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                        customer_name = chatinfo_obj.customer.username
                        if chatinfo_obj.send_type in [2, '2'] and not is_customer: # 客户发给用户
                            average_response_time_consultation_list.append({
                                'jisuan_create_date': chatinfo_obj.create_date,
                                'create_date': create_date,
                                'customer_name': customer_name,
                            })
                            is_customer = True
                        if is_customer:
                            if chatinfo_obj.send_type in [1, '1']:
                                is_customer = False
                                average_response_time_consultation_list[-1]['recovery_time'] = create_date
                                average_response_time_consultation_list[-1]['jisuan_recovery_time'] = chatinfo_obj.create_date
                                zong_avg_time += (
                                        chatinfo_obj.create_date - average_response_time_consultation_list[-1]['jisuan_create_date']
                                ).seconds # 单次响应时间
                    if zong_avg_time and len(average_response_time_consultation_list):
                        zong_avg_time = zong_avg_time / len(average_response_time_consultation_list) # 总平均值

                    # ===========================================有效对话======================================
                    effective_radar_communication_num = 0 # 总有效对话次数
                    effective_radar_objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                        send_type__in=[1, 2], userprofile_id=obj.id)

                    customers_objs = effective_radar_objs.values('customer').annotate(Count('id')) # 查询全部客户
                    effective_radar_list = []
                    customer_num = 0
                    user_num = 0
                    effective_dict = []
                    for customers_obj in customers_objs:
                        objs = effective_radar_objs.filter(customer_id=customers_obj['customer']) # 查询单个客户

                        for radar_obj in objs:
                            if objs.count() >= 6:

                                send_type = radar_obj.send_type # 发送类型
                                text = get_msg(radar_obj.content)

                                if send_type in [1, '1']: # 用户发给客户
                                    customer_num += 1
                                    effective_dict.append({
                                        'send_type': send_type,
                                        'avatar': radar_obj.userprofile.avatar,     # 头像
                                        'name': radar_obj.userprofile.username,
                                        'msg': text.get('msg'),
                                        'product_cover_url': text.get('product_cover_url'),
                                        'product_name': text.get('product_name'),
                                        'product_price': text.get('product_price'),
                                        'url': text.get('url'),
                                        'info_type': text.get('info_type'),
                                        'create_date': radar_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    })

                                elif send_type in [2, '2']: # 客户发给用户
                                    user_num += 1
                                    effective_dict.append({
                                        'send_type': send_type,
                                        'avatar': radar_obj.customer.headimgurl,  # 头像
                                        'name': b64decode(radar_obj.customer.username),
                                        'msg': text.get('msg'),
                                        'product_cover_url': text.get('product_cover_url'),
                                        'product_name': text.get('product_name'),
                                        'product_price': text.get('product_price'),
                                        'url': text.get('url'),
                                        'info_type': text.get('info_type'),
                                        'create_date': radar_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    })

                            if customer_num >= 3 and user_num >= 3:
                                customer_num = 0
                                user_num = 0
                                effective_radar_list.append({
                                    'effective_dict': effective_dict,
                                    'user_name':b64decode(radar_obj.customer.username),
                                    'create_date':radar_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                 })
                                effective_dict = []
                                effective_radar_communication_num += 1

                    detail_data = [] # 详情数据
                    detail_count = 0 # 详情总数
                    if uid and task_type in [1, '1']: # 查询详情复制昵称
                        detail_count = oper_log_objs.count()
                        for oper_log_obj in oper_log_objs[detail_start_line: detail_stop_line]:
                            detail_data.append({
                                'customer_name': b64decode(oper_log_obj.customer.username),
                                'create_date': oper_log_obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                            })

                    elif uid and task_type in [2, '2']: # 查询详情雷达内有效对话
                        detail_count = effective_radar_communication_num
                        detail_data = effective_radar_list[detail_start_line: detail_stop_line]

                    elif uid and task_type in [3, '3']: # 查询详情 响应时长
                        detail_count = len(average_response_time_consultation_list)
                        for time_list in average_response_time_consultation_list[detail_start_line: detail_stop_line]:
                            response_time = 0
                            if time_list.get('jisuan_recovery_time') and time_list.get('jisuan_create_date'):
                                response_time = (time_list.get('jisuan_recovery_time') - time_list.get('jisuan_create_date')).seconds
                            detail_data.append({
                                'customer_name': b64decode(time_list.get('customer_name')),
                                'create_date': time_list.get('create_date'),
                                'recovery_time': time_list.get('recovery_time'),
                                'response_time': response_time,
                            })

                    elif uid and task_type in [4, '4']: # 订单数量
                        detail_count = dingdan_objs.count()
                        for dingdan_obj in dingdan_objs[detail_start_line: detail_stop_line]:
                            goods_name = ''
                            if dingdan_obj.shangpinguanli:
                                goods_name = dingdan_obj.shangpinguanli.goodsName
                            detail_data.append({
                                'unitRiceNum': dingdan_obj.unitRiceNum,
                                'goods_name': goods_name,
                                'customer_name': b64decode(dingdan_obj.shouHuoRen.username),
                                'create_date': dingdan_obj.createDate.strftime('%Y-%m-%d %H:%M:%S')
                            })


                    ret_data.append({
                        'user_id': obj.id,
                        'user_name': obj.username,
                        'copy_nickname': oper_log_objs.count(),
                        'order_number': dingdan_objs.count(),
                        'effective_radar_communication': effective_radar_communication_num,
                        'average_response_time_consultation': zong_avg_time,
                        'detail_data':detail_data,
                        'detail_count':detail_count,
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }


            else:
                response.code = 301
                response.msg = form_obj.errors.as_json()


        else:
            response.code = 402
            response.msg = '请求异常'

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)



# 获取 发送的消息
def get_msg(content):
    # print('content-----content---------------content---> ', content)
    data = {
        'msg': '',
        'product_cover_url': '',
        'product_name': '',
        'product_price': '',
        'url': '',
    }
    if content:
        try:
            content = json.loads(content)
        except Exception:
            content = content
        info_type = int(content.get('info_type'))

        if content:
            if info_type in [1, 3, 6]:
                if content.get('msg'):
                    data['msg'] = b64decode(content.get('msg'))

            elif info_type in [2]:
                # print('content---> ', content)
                # print("content.get('product_cover_url')-------> ", content.get('product_cover_url'))
                data['product_cover_url'] = content.get('product_cover_url')
                data['product_name'] = content.get('product_name')
                data['product_price'] = content.get('product_price')

            elif info_type in [4, 5]:
                data['url'] = content.get('url')
        data['info_type'] = info_type
    return data





