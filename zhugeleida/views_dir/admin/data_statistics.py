from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.user_verify import UserSelectForm
from django.db.models import Q, Count, Sum
from publicFunc.time_screen import time_screen
from publicFunc.base64 import b64decode
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
                        count = average_response_time_len
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












# # # 获取 发送的消息
# def get_msg(content):
#     # print('content-----content---------------content---> ', content)
#     data = {
#         'msg': '',
#         'product_cover_url': '',
#         'product_name': '',
#         'product_price': '',
#         'url': '',
#     }
#     if content:
#
#         # content = content.replace('null', '\'\'')
#         try:
#             content = eval(content)
#         except Exception:
#             content = content
#
#         info_type = int(content.get('info_type'))
#         # print('content----------> ', content)
#         if content:
#             if info_type in [1, 3, 6]:
#                 if content.get('msg'):
#                     data['msg'] = b64decode(content.get('msg'))
#
#             elif info_type in [2]:
#                 # print('content---> ', content)
#                 # print("content.get('product_cover_url')-------> ", content.get('product_cover_url'))
#                 data['product_cover_url'] = content.get('product_cover_url')
#                 data['product_name'] = content.get('product_name')
#                 data['product_price'] = content.get('product_price')
#
#             elif info_type in [4, 5]:
#                 data['url'] = content.get('url')
#         data['info_type'] = info_type
#     return data
#
# # 统计数据 调用类
# class statistical_objs():
#
#     def __init__(self, q, o_id, detail_data_type, current_page, length, start_date=None, stop_date=None):
#         self.q = q
#         self.o_id = o_id
#         self.detail_data_type = detail_data_type
#         self.current_page = current_page
#         self.length = length
#         self.start_date = start_date
#         self.stop_date = stop_date
#
#     # 复制昵称 次数及数据（员工）
#     def copy_the_nickname(self):
#         copy_nickname_obj = models.ZgldUserOperLog.objects.filter(
#             self.q,
#             user_id=self.o_id,
#             oper_type=1
#         ).order_by('-create_date')
#         count = copy_nickname_obj.count()
#         data_list = []
#         if self.detail_data_type and self.detail_data_type == 'copy_the_nickname':
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 copy_nickname_obj = copy_nickname_obj[start_line: stop_line]
#             for obj in copy_nickname_obj:
#                 customer__username = ''
#                 if obj.customer:
#                     customer__username = b64decode(obj.customer.username)
#                 data_list.append({
#                     'customer__username': customer__username,
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#
#         data = {
#             'copy_nickname_count': str(count) + '次',
#             'data_list': data_list,
#             'count': count
#         }
#         return data
#
#     # 有效对话次数（员工）
#     def number_valid_conversations(self):
#         data_list = []
#         effective_dialogue = 0
#         is_number_valid_conversations = False # 判断是否查询了详情
#         if self.detail_data_type and self.detail_data_type == 'number_valid_conversations':  #
#             is_number_valid_conversations = True
#
#         zgld_chatinfo_objs = models.zgld_chatinfo.objects.raw(          # 查询出符合条件的用户和客户 已天为单位
#             """select id, DATE_FORMAT(create_date, '%%Y-%%m-%%d') as cdt
#             from zhugeleida_zgld_chatinfo where userprofile_id={userprofile_id} and create_date >= '{start_date}' and create_date <= '{stop_date}' group by cdt, customer_id;""".format(
#                 userprofile_id=self.o_id,
#                 start_date=self.start_date,
#                 stop_date=self.stop_date
#             )
#         )
#         for zgld_chatinfo_obj in zgld_chatinfo_objs:
#             effective_num = 0 # 查看详情单个人次数
#             customer__username = ''
#             result_data = []
#             start_date_time = zgld_chatinfo_obj.cdt + ' 00:00:00'  # 按天区分
#             stop_date_time = zgld_chatinfo_obj.cdt + ' 23:59:59'
#             msg_objs = models.zgld_chatinfo.objects.filter(
#                 userprofile_id=self.o_id,
#                 customer_id=zgld_chatinfo_obj.customer_id,
#                 create_date__gte=start_date_time,
#                 create_date__lte=stop_date_time,
#             ).order_by('create_date')
#             dialogue_count = msg_objs.count()       # 查询出该用户和该客户聊天总数
#             # if is_number_valid_conversations:
#             #     if self.length != 0:
#             #         start_line = (self.current_page - 1) * self.length
#             #         stop_line = start_line + self.length
#             #         msg_objs = msg_objs[start_line: stop_line]
#
#             if dialogue_count >= 6:  # 判断该客户在该文章中 对话 低于六次不达有效对话标准
#                 send_type_user = 0      # 咨询发送消息
#                 send_type_customer = 0  # 客户发送消息
#                 flag = False            # 判断该客户和该用户是否 存在有效聊天
#                 for msg_obj in msg_objs:
#
#                     send_type = int(msg_obj.send_type)
#
#                     text = get_msg(msg_obj.content) # 获取聊天内容
#
#                     if send_type == 1:
#                         send_type_user += 1
#                         name = msg_obj.userprofile.username     # 咨询名称
#                         avatar = msg_obj.userprofile.avatar     # 头像
#                     else:
#                         send_type_customer += 1
#                         name = ''
#                         if msg_obj.customer.username:
#                             name = b64decode(msg_obj.customer.username) # 客户名称
#                         avatar = msg_obj.customer.headimgurl     # 头像
#
#                     if is_number_valid_conversations: # 查询详情
#                         result_data.append({
#                             'send_type': send_type,
#                             'avatar': avatar,
#                             'name': name,
#                             'msg': text.get('msg'),
#                             'product_cover_url': text.get('product_cover_url'),
#                             'product_name': text.get('product_name'),
#                             'product_price': text.get('product_price'),
#                             'url': text.get('url'),
#                             'info_type': text.get('info_type'),
#                             'create_date': msg_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         })
#                     customer__username = ''
#                     if msg_obj.customer.username:
#                         customer__username = b64decode(msg_obj.customer.username)
#                 send_type_user = int(send_type_user / 3)
#                 send_type_customer = int(send_type_customer / 3)
#                 if send_type_user < send_type_customer:
#                     num = send_type_user
#                 else:
#                     num = send_type_customer
#
#                 if num > 0:
#                     flag = True
#
#                 if send_type_user >= 1 and send_type_customer >= 1:
#                     effective_num += num
#
#                 if is_number_valid_conversations:  # 查询详情
#                     if flag:
#                         data_list.append({
#                             'customer__username': customer__username,
#                             'create_date': result_data[0].get('create_date'),
#                             'result_data':result_data,
#                             'effective_num':effective_num # 单个人 有效次数
#                         })
#
#             if effective_num >= 1:
#                 effective_dialogue += 1
#
#         data = {
#             'effective_dialogue': str(effective_dialogue) + '次',
#             'data_list': data_list,
#             'count': effective_dialogue,
#         }
#
#         return data
#
#     # 咨询响应平均时长（员工）
#     def average_response_time(self):
#         average_response = 0
#         result_data = []
#         info_objs = models.zgld_chatinfo.objects.filter(
#             self.q,
#             userprofile_id=self.o_id,
#             article_id__isnull=False,
#         ).values('customer_id', 'customer__username', 'article_id').distinct()
#         data_list = []
#         num = 0
#         start_line = 0
#         stop_line = 9
#         if self.length != 0:
#             start_line = (self.current_page - 1) * self.length
#             stop_line = start_line + self.length
#
#         for info_obj in info_objs:
#             chatinfo_objs = models.zgld_chatinfo.objects.filter(
#                 userprofile_id=self.o_id,
#                 article_id=info_obj.get('article_id'),
#                 customer_id=info_obj.get('customer_id'),
#             ).order_by('create_date')
#             if chatinfo_objs.count() > 1:
#                 flag = False
#                 data_dict = {'start_date': '', 'stop_date': ''}
#                 for chatinfo_obj in chatinfo_objs:
#                     send_type = int(chatinfo_obj.send_type)
#                     if send_type == 2:
#                         data_dict['start_date'] = chatinfo_obj.create_date
#                         flag = True
#                     if flag:
#                         if send_type == 1:
#                             data_dict['stop_date'] = chatinfo_obj.create_date
#                             break                                               # 只统计该用户第一次聊天回应时长
#                 if data_dict['start_date'] and data_dict['stop_date']:
#                     result_data.append(data_dict)
#                     date = data_dict['stop_date'] - data_dict['start_date']
#                     if self.detail_data_type and self.detail_data_type == 'average_response_time':
#                         num += 1
#                         data_list.append({
#                             'customer__username': b64decode(info_obj.get('customer__username')),
#                             'start_date': data_dict['start_date'].strftime('%Y-%m-%d %H:%M:%S'),
#                             'stop_date': data_dict['stop_date'].strftime('%Y-%m-%d %H:%M:%S'),
#                             'response_time': date.seconds
#                         })
#             if self.detail_data_type and self.detail_data_type == 'average_response_time':
#                 if num >= stop_line:
#                     break
#                 elif num <= start_line:
#                     continue
#
#         num = 0
#         len_data = len(result_data)
#         for i in result_data:
#             date = i.get('stop_date') - i.get('start_date')
#             num += date.seconds
#         if num != 0 and len_data != 0:
#             average_response = int(num / len_data)
#         data = {
#             'average_response': str(average_response) + '秒',
#             'data_list': data_list,
#             'count': len_data,
#         }
#
#         return data
#
#     # 发送小程序 （员工）
#     def sending_applet(self):
#         data_list = []
#         objs = models.zgld_accesslog.objects.filter(
#             self.q,
#             user_id=self.o_id,
#             action=23
#         )
#         if self.detail_data_type and self.detail_data_type == 'sending_applet':
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#             for obj in objs:
#                 data_list.append({
#                     'customer__username': b64decode(obj.customer.username),
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#
#         sending_applet_num = objs.count()
#         data = {
#             'sending_applet_num': str(sending_applet_num) + '次',
#             'data_list': data_list,
#             'count': sending_applet_num,
#         }
#
#         return data
#
#
#
#     # 转发量(文章)
#     def forwarding_article(self):
#         objs = models.zgld_accesslog.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             action__in=[15, 16]
#         ).order_by('-create_date')
#         forwarding_article_count = objs.count()
#         data_list = []
#         if self.detail_data_type and self.detail_data_type == 'forwarding_article':
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#             for obj in objs:
#                 data_list.append({
#                     'customer__username': b64decode(obj.customer.username),
#                     'user_username': obj.user.username,
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#
#         data = {
#             'forwarding_article_count': str(forwarding_article_count) + '次',
#             'data_list': data_list,
#             'count': forwarding_article_count
#         }
#         return data
#
#     # 点击量（文章）
#     def click_the_quantity(self):
#         objs = models.zgld_accesslog.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             action=14
#         ).order_by('-create_date')
#         data_list = []
#         click_count = objs.count()
#         if self.detail_data_type and self.detail_data_type == 'click_the_quantity':
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#             for obj in objs:
#                 data_list.append({
#                     'customer__username': b64decode(obj.customer.username),
#                     'user_username': obj.user.username,
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#
#         data = {
#             'click_count': str(click_count) + '次',     # 点击量
#             'data_list': data_list,
#             'count': click_count
#         }
#
#         return data
#
#     # 阅读总时长/平均时长（文章）
#     def the_reading_time(self):
#         objs = models.ZgldUserOperLog.objects.filter(self.q, article_id=self.o_id, oper_type=4)
#         count = objs.count()
#         article_reading_time_count = 0
#         for obj in objs:
#             article_reading_time_count += obj.reading_time
#
#         data_list = []
#         if self.detail_data_type and self.detail_data_type == 'the_reading_time':
#             objs = models.ZgldUserOperLog.objects.filter(
#                 self.q, article_id=self.o_id, oper_type=4
#             )
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#             for obj in objs:
#                 data_list.append({
#                     'customer__username': b64decode(obj.customer.username),
#                     'reading_time': obj.reading_time,
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#
#         avg = 0
#         if int(article_reading_time_count) > 0:
#             avg = int(article_reading_time_count / count)
#
#         text = str(article_reading_time_count) + '秒/' + str(avg) + '秒'
#         data = {
#             'text': text,
#             'data_list': data_list,
#             'count': count
#         }
#
#         return data
#
#     # 视频查看时长统计/平均时长（文章）
#     def video_view_duration(self):
#         time_objs = models.ZgldUserOperLog.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             oper_type=3,
#             video_time__isnull=False
#         )
#
#         len_video = time_objs.count()
#
#         video_view_count = 0
#         for time_obj in time_objs:
#             video_view_count += time_obj.video_time
#         video_average_playing_time = 0
#         if video_view_count > 0:
#             video_average_playing_time = int(video_view_count / len_video)
#
#         data_list = []
#         count = len_video
#         if self.detail_data_type and self.detail_data_type == 'video_view_duration':
#             video_objs = models.ZgldUserOperLog.objects.filter(
#                 self.q,
#                 article_id=self.o_id,
#                 oper_type=3,
#                 video_time__isnull=False
#             ).select_related('customer').values('customer_id', 'customer__username').annotate(Sum('video_time'), Count('id'))
#             count = video_objs.count()
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 video_objs = video_objs[start_line: stop_line]
#
#             for video_obj in video_objs:
#                 avg = 0
#                 if int(video_obj.get('video_time__sum')) > 0:
#                     avg = int(video_obj.get('video_time__sum') / video_obj.get('id__count'))
#                 data_list.append({
#                     'customer__username': b64decode(video_obj.get('customer__username')),
#                     'id__count': video_obj.get('id__count'),
#                     'video_time__sum': video_obj.get('video_time__sum'),
#                     'avg': avg,
#                 })
#
#         # 几次查看视频 / 查看平均时长 / 查看视频总时长
#         text = str(len_video)+ '次/' + str(video_view_count) + '秒/' + str(video_average_playing_time) + '秒'
#         data = {
#             'video_num_count_avg': text,
#             'data_list': data_list,
#             'count': count
#         }
#
#         return data
#
#     # 点击对话框（文章）
#     def click_the_dialog_box(self):
#         click_dialog_obj = models.ZgldUserOperLog.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             oper_type=2,
#         )
#
#         data_list = []
#         click_dialog_num = click_dialog_obj.count()
#
#         if self.detail_data_type and self.detail_data_type == 'click_the_dialog_box':
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 click_dialog_obj = click_dialog_obj[start_line: stop_line]
#             for i in click_dialog_obj:
#                 data_list.append({
#                     'customer__username': b64decode(i.customer.username),
#                     'create_date': i.create_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#
#         data = {
#             'click_dialog_num': str(click_dialog_num) + '次',
#             'data_list': data_list,
#             'count': click_dialog_num,
#         }
#
#         return data
#
#     # 主动发送消息（文章）
#     def active_message(self):
#         result_data = []
#         [result_data.append({'customer_id': i.get('customer_id'), 'article_id': i.get('article_id')}) for i in
#          models.zgld_chatinfo.objects.filter(self.q, article_id=self.o_id, send_type=2,
#              article__isnull=False).values(
#              'customer_id', 'article_id').distinct()]
#         data_list = []
#         user_active_send_num = 0
#
#         count = len(result_data)
#         if self.length != 0:
#             start_line = (self.current_page - 1) * self.length
#             stop_line = start_line + self.length
#             result_data = result_data[start_line: stop_line]
#
#
#         for i in result_data:
#             infoObjs = models.zgld_chatinfo.objects.filter(
#                 customer_id=i.get('customer_id'),
#                 article_id=i.get('article_id'),
#             ).order_by('-create_date')
#             if infoObjs:
#                 infoObj = infoObjs[0]
#                 send_type = int(infoObj.send_type)
#                 if send_type == 2:
#                     user_active_send_num += 1
#
#                 if self.detail_data_type and self.detail_data_type == 'active_message': # 是否查看详情
#                     if send_type == 2:
#                         content = eval(infoObj.content)
#                         text = get_msg(content)
#
#                         data_list.append({
#                             'customer__username':b64decode(infoObj.customer.username),
#                             'msg': text.get('msg'),
#                             'product_cover_url': text.get('product_cover_url'),
#                             'product_name': text.get('product_name'),
#                             'product_price': text.get('product_price'),
#                             'url': text.get('url'),
#                             'info_type': text.get('info_type'),
#                             'create_date':infoObj.create_date.strftime('%Y-%m-%d %H:%M:%S')
#                         })
#
#         data = {
#             'data_list': data_list,
#             'user_active_send_num': str(user_active_send_num) + '次',
#             'count': count,
#         }
#         return data
#
#     # 拨打电话（文章）
#     def call_phone(self):
#         objs = models.zgld_accesslog.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             action=10
#         )
#         call_phone_num = objs.count()
#
#         data_list = []
#         if self.detail_data_type and self.detail_data_type == 'call_phone':
#
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#
#             for obj in objs:
#                 data_list.append({
#                     'customer__username': b64decode(obj.customer.username),
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#
#         data = {
#             'call_phone_num': str(call_phone_num) + '次',
#             'data_list': data_list,
#             'count': call_phone_num,
#         }
#         return data
#
#     # 文章点赞次数（文章）
#     def thumb_up_number(self):
#         objs = models.zgld_article_action.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             status=1
#         )
#
#         click_thumb_num = objs.count()
#         data_list = []
#         # print('click_thumb_num----------> ', click_thumb_num)
#         if self.detail_data_type and self.detail_data_type == 'thumb_up_number':
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#             for obj in objs:
#                 data_list.append({
#                     'customer__name': b64decode(obj.customer.username),
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#         data = {
#             'click_thumb_num': str(click_thumb_num) + '次',
#             'data_list': data_list,
#             'count': click_thumb_num
#         }
#
#         return data
#
#     # 文章评论（文章）
#     def article_comments(self):
#         objs = models.zgld_article_comment.objects.filter(
#             self.q,
#             article_id=self.o_id,
#             # is_audit_pass=1 # 该评论是否审核
#         )
#         data_list = []
#         if self.detail_data_type and self.detail_data_type == 'article_comments': # 点击详情 避免无用数据
#             if self.length != 0:
#                 start_line = (self.current_page - 1) * self.length
#                 stop_line = start_line + self.length
#                 objs = objs[start_line: stop_line]
#             for obj in objs:
#                 is_audit_pass = '未审核'
#                 if int(obj.is_audit_pass) == 1:
#                     is_audit_pass = '已审核'
#
#                 data_list.append({
#                     'customer__username':b64decode(obj.from_customer.username),
#                     'content': b64decode(obj.content),
#                     'is_audit_pass': is_audit_pass,
#                     'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#
#         article_comments_num = objs.count()
#         data = {
#             'article_comments_num': str(article_comments_num) + '条',
#             'data_list': data_list,
#             'count': article_comments_num,
#         }
#         return data




# 雷达后台首页 数据统计
# @csrf_exempt
# @account.is_token(models.zgld_admin_userprofile)
# def data_statistics(request, oper_type):
#     response = Response.ResponseObj()
#     if request.method == "GET":
#         forms_obj = UserSelectForm(request.GET)
#         if forms_obj.is_valid():
#             current_page = forms_obj.cleaned_data['current_page']
#             length = forms_obj.cleaned_data['length']
#             number_days = request.GET.get('number_days')  # 天数
#             start_time = request.GET.get('start_time')  # 天数 开始时间
#             stop_time = request.GET.get('stop_time')  # 天数 结束时间
#
#
#             if not start_time and not stop_time: # 时间筛选
#                 start_time, stop_time = time_screen(number_days)
#
#
#             company_id = request.GET.get('company_id')  # 区分公司
#             public_q = Q()
#             if company_id:
#                 public_q.add(Q(company_id=company_id), Q.AND)
#
#             detail_type = request.GET.get('detail_type')  # 点击某个详情页面
#
#             # 文章数据分析
#             if oper_type == 'article_data_analysis':
#                 """
#                 detail_type 判断 进入详情类型 起因: 后台数据偏多 利用该参数判断 跳进某个详情页面 避免不进详情 查询到详情数据
#                 article_comments    查询评论详情
#                 thumb_up_number     点赞详情
#                 call_phone          拨打电话详情
#                 active_message      主动发送消息详情
#                 click_the_dialog_box 点击对话框详情
#                 video_view_duration 视频详情
#                 the_reading_time    文章阅读详情
#                 click_the_quantity  点击量详情
#                 forwarding_article  转发量详情
#
#                 """
#                 article_id = request.GET.get('article_id')  # 区分文章
#                 q = Q()
#                 q.add(Q(create_date__gte=start_time) & Q(create_date__lte=stop_time), Q.AND)
#
#                 if article_id:
#                     public_q.add(Q(id=article_id), Q.AND)
#
#                 objs = models.zgld_article.objects.filter(public_q).order_by('-create_date')
#                 data_count = objs.count()
#
#                 if not article_id:
#                     if length != 0:
#                         start_line = (current_page - 1) * length
#                         stop_line = start_line + length
#                         objs = objs[start_line: stop_line]
#
#                 ret_data = []
#
#                 detail_data_type = None
#                 if detail_type:
#                     if not article_id: # 点击详情必传文章ID
#                         response.code = 301
#                         response.msg = '查询文章失败'
#                         return JsonResponse(response.__dict__)
#                     else:
#                         detail_data_type = detail_type
#
#                 for obj in objs:
#
#                     statistical_obj = statistical_objs(q, obj.id, detail_data_type, current_page, length)         # 实例化 数据统计
#
#                     forwarding_article_data = statistical_obj.forwarding_article()                          # 转发量
#                     click_quantity_data = statistical_obj.click_the_quantity()                              # 点击量
#                     the_reading_data = statistical_obj.the_reading_time()                                   # 文章阅读数据
#                     video_view_data = statistical_obj.video_view_duration()                                 # 视频数据
#                     click_dialog_data = statistical_obj.click_the_dialog_box()                              # 点击对话框数据
#                     user_active_send_data = statistical_obj.active_message()                                # 主动发送数据
#                     call_phone_data = statistical_obj.call_phone()                                          # 拨打电话数据
#                     click_thumb_data = statistical_obj.thumb_up_number()                                    # 文章点赞数据
#                     article_comments_data = statistical_obj.article_comments()                              # 文章评论数据
#
#                     count = 0
#                     if detail_data_type == 'forwarding_article':    # 转发
#                         count = forwarding_article_data.get('count')
#                     elif detail_data_type == 'click_the_quantity':  # 点击
#                         count = click_quantity_data.get('count')
#                     elif detail_data_type == 'the_reading_time':    # 阅读
#                         count = the_reading_data.get('count')
#                     elif detail_data_type == 'video_view_duration': # 视频
#                         count = video_view_data.get('count')
#                     elif detail_data_type == 'click_the_dialog_box': # 点击对话框
#                         count = click_dialog_data.get('count')
#                     elif detail_data_type == 'active_message':      # 主动发送消息
#                         count = user_active_send_data.get('count')
#                     elif detail_data_type == 'call_phone':          # 拨打电话
#                         count = call_phone_data.get('count')
#                     elif detail_data_type == 'thumb_up_number':     # 点赞
#                         count = click_thumb_data.get('count')
#                     elif detail_data_type == 'article_comments':    # 查询评论
#                         count = article_comments_data.get('count')
#
#                     ret_data.append({
#                         'id': obj.id,
#                         'article_name': obj.title,                      # 文章名称
#
#                         'forward_num': forwarding_article_data.get('forwarding_article_count'),         # 文章转发数量
#                         'forward_data': forwarding_article_data.get('data_list'),                       # 文章转发数据
#
#                         'click_num': click_quantity_data.get('click_count'),                            # 文章点击数量
#                         'click_data': click_quantity_data.get('data_list'),                             # 文章点击数据
#
#                         'avg_reading_info': the_reading_data.get('text'),                               # 文章阅读信息
#                         'avg_reading_data': the_reading_data.get('data_list'),                          # 文章阅读数据
#
#                         'len_video_text': video_view_data.get('video_num_count_avg'),                   # 视频信息
#                         'len_video_data': video_view_data.get('data_list'),                             # 视频数据
#
#                         'click_dialog_num': click_dialog_data.get('click_dialog_num'),                  # 点击对话框
#                         'click_dialog_data': click_dialog_data.get('data_list'),                        # 点击对话框
#
#                         'user_active_send_num': user_active_send_data.get('user_active_send_num'),      # 主动发送消息数量
#                         'user_active_send_data': user_active_send_data.get('data_list'),                # 主动发送消息数据
#
#                         'call_phone_num': call_phone_data.get('call_phone_num'),                        # 拨打电话次数
#                         'call_phone_data': call_phone_data.get('data_list'),                            # 拨打电话数据
#
#                         'click_thumb_num': click_thumb_data.get('click_thumb_num'),                     # 文章点赞次数
#                         'click_thumb_data': click_thumb_data.get('data_list'),                          # 文章点赞数据
#
#                         'article_comments_num': article_comments_data.get('article_comments_num'),      # 文章评论次数
#                         'article_comments_data': article_comments_data.get('data_list'),                # 文章评论数据
#
#                         'count':count
#                     })
#
#                 response.code = 200
#                 response.msg = '查询成功'
#                 response.data = {
#                     'ret_data': ret_data,
#                     'count': data_count,
#                 }
#                 response.note = {
#                     'id': '文章ID',
#                     'article_name': '文章名称',
#                     'forward_count': '文章转发量',
#                     'forward_data--文章转发数据': {
#                         "customer_username": "客户名称",
#                         "user_username": "员工名称",
#                         "create_date": "点击时间",
#                     },
#
#                     'click_count': '文章点击量',
#                     'click_data--文章点击数据': {
#                         "customer_username": "客户名称",
#                         "user_username": "员工名称",
#                         "create_date": "点击时间",
#                     },
#
#                     'avg_reading_info': '文章阅读信息',
#                     'avg_reading_data': {
#                         "customer__username": "客户名称",
#                         "reading_time": '阅读时长',
#                         "create_date": "阅读时间",
#                     },
#
#                     'len_video_text': '视频信息',
#                     'len_video_data--视频详情': {
#                         'customer__username': '客户名称',
#                         'id__count': '播放次数',
#                         'video_time__sum': '总时长',
#                         'avg': '平均时长',
#                     },
#
#                     'click_dialog_num': '点击对话框次数',
#                     'click_dialog_data--点击对话框数据': {
#                         'customer_username': '客户名称',
#                         'create_date': '发送消息时间',
#                     },
#
#                     'user_active_send_num': '主动发送消息',
#                     'user_active_send_data--主动发送数据': {
#                         'customer_username': '客户名称',
#                         'content': '发送内容',
#                         'create_date':'发送消息时间',
#                     },
#
#
#                     'call_phone_num': '拨打电话次数',
#                     'call_phone_data--拨打电话数据': {
#                         'customer_name': '客户名称',
#                         'create_date': '点赞时间',
#                     },
#
#
#                     'click_thumb_num': '文章点赞次数',
#                     'click_thumb_data--文章点赞数据':{
#                         'customer_name': '客户名称',
#                         'create_date': '点赞时间',
#                     },
#
#                     'article_comments_num': '文章评论次数',
#                     'article_comments_data--文章评论详情': {
#                         'customer_username':'客户名称',
#                         'content': '评论内容',
#                         'is_audit_pass': '是否审核',
#                         'create_date': '评论时间',
#                     },
#                 }
#
#             # 员工数据分析
#             elif oper_type == 'employee_data_analysis':
#                 id = request.GET.get('id') # 查询单个员工
#                 if id:
#                     public_q.add(Q(id=id), Q.AND)
#                 # 获取该公司所有员工信息
#                 objs = models.zgld_userprofile.objects.filter(public_q).order_by('-create_date')
#                 data_count = objs.count()
#                 if not id:
#                     if length != 0:
#                         start_line = (current_page - 1) * length
#                         stop_line = start_line + length
#                         objs = objs[start_line: stop_line]
#                 ret_data = []
#                 q = Q()
#                 q.add(Q(create_date__gte=start_time) & Q(create_date__lte=stop_time), Q.AND) # 时间筛选
#                 for obj in objs:
#                     """
#                     copy_the_nickname           复制昵称详情
#                     number_valid_conversations  有效对话详情
#                     average_response_time       平均响应时长详情
#                     sending_applet              发送小程序详情
#
#                     """
#                     statistical_obj = statistical_objs(q, obj.id, detail_type, current_page, length, start_time, stop_time)
#                     copy_nickname_data = statistical_obj.copy_the_nickname()                    # 复制昵称
#                     effective_dialogue_data = statistical_obj.number_valid_conversations()      # 有效对话
#                     average_response_data = statistical_obj.average_response_time()             # 咨询平均响应时长
#                     sending_applet_data = statistical_obj.sending_applet()                      # 发送小程序
#
#                     count = 0
#                     if detail_type == 'copy_the_nickname':
#                         count = copy_nickname_data.get('count')
#                     elif detail_type == 'number_valid_conversations':
#                         count = effective_dialogue_data.get('count')
#                     elif detail_type == 'average_response_time':
#                         count = average_response_data.get('count')
#                     elif detail_type == 'sending_applet':
#                         count = sending_applet_data.get('count')
#
#                     ret_data.append({
#                         'id': obj.id,
#                         'user_name': obj.username,                                                             # 员工名称
#
#                         'copy_nickname': copy_nickname_data.get('copy_nickname_count'),                     # 复制昵称次数
#                         'copy_nickname_data': copy_nickname_data.get('data_list'),                          # 复制昵称数据
#
#                         'effective_dialogue_num': effective_dialogue_data.get('effective_dialogue'),        # 有效对话数量
#                         'effective_dialogue_data': effective_dialogue_data.get('data_list'),                # 有效对话数据
#
#                         'average_response_avg': average_response_data.get('average_response'),              # 平均响应时长
#                         'average_response_data': average_response_data.get('data_list'),                    # 平均响应时长
#
#                         'sending_applet_num': sending_applet_data.get('sending_applet_num'),                # 发送小程序数量
#                         'sending_applet_data': sending_applet_data.get('data_list'),                        # 发送小程序数据
#                         'count': count,
#                     })
#
#                 response.code = 200
#                 response.msg = '查询成功'
#                 response.data = {
#                     'ret_data': ret_data,
#                     'count': data_count,
#                 }
#                 response.note = {
#                     'username': '咨询用户名称',
#
#                     'copy_nickname': '复制昵称次数',
#                     'copy_nickname_data--复制昵称数据': {
#                         'customer__username': '客户名称',
#                         'create_date': '复制昵称时间',
#                     },
#
#                     'effective_dialogue_num': '有效对话数量',
#                     'effective_dialogue_data': {
#                         'name': '发送消息人名称',
#                         'text': '发送的消息',
#                         'create_date': '发送消息时间',
#                     },
#
#                     'average_response_avg': '平均响应时长',
#                     'average_response_data--平均响应时长数据': {
#                         'customer__username': '客户名称',
#                         'start_date': '客户发送对话时间',
#                         'stop_date': '咨询回复时间',
#                         'response_time': '响应时长',
#                     },
#
#                     'sending_applet_num': '发送小程序数量',
#                     'sending_applet_data--发送小程序数据': {
#                         'customer__username': '客户名称',
#                         'create_date': '创建时间',
#                     },
#                 }
#
#
#         else:
#             response.code = 301
#             response.data = json.loads(forms_obj.errors.as_json())
#
#     return JsonResponse(response.__dict__)
# #
