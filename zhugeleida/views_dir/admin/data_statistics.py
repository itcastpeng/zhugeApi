from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserSelectForm
from django.db.models import Q, Count, Sum
import json, datetime
from publicFunc.time_screen import time_screen
from publicFunc.base64 import b64decode

# 统计数据 调用类
class statistical_objs():

    def __init__(self, q, o_id, detail_data_type):
        self.q = q
        self.o_id = o_id
        self.detail_data_type = detail_data_type

    # 复制昵称 次数及数据（员工）
    def copy_the_nickname(self):
        copy_nickname_obj = models.ZgldUserOperLog.objects.filter(user_id=self.o_id)
        count = copy_nickname_obj.count()
        return count

    # 有效对话次数（员工）
    def number_valid_conversations(self):
        effective_dialogue = 0
        # if article_id:
        #     zgld_chatinfo_objs = models.zgld_chatinfo.objects.raw(
        #         """select id, DATE_FORMAT(create_date, '%%Y-%%m-%%d') as cdt
        #         from zhugeleida_zgld_chatinfo where article_id = {article_id} and userprofile_id={userprofile_id} and article_id is not null group by cdt, article_id, customer_id;""".format(
        #             article_id=article_id, userprofile_id=obj.id))
        # else:
        zgld_chatinfo_objs = models.zgld_chatinfo.objects.raw(
            """select id, DATE_FORMAT(create_date, '%%Y-%%m-%%d') as cdt 
            from zhugeleida_zgld_chatinfo where userprofile_id={} and article_id is not null group by cdt, article_id, customer_id;""".format(
                self.o_id)
        )

        for zgld_chatinfo_obj in zgld_chatinfo_objs:
            start_date_time = zgld_chatinfo_obj.cdt + ' 00:00:00'  # 按天区分
            stop_date_time = zgld_chatinfo_obj.cdt + ' 23:59:59'

            msg_objs = models.zgld_chatinfo.objects.filter(
                userprofile_id=self.o_id,
                article_id=zgld_chatinfo_obj.article_id,
                customer_id=zgld_chatinfo_obj.customer_id,
                create_date__gte=start_date_time,
                create_date__lte=stop_date_time,
            ).order_by('create_date')

            dialogue_count = msg_objs.count()
            if dialogue_count >= 6:  # 判断该客户在该文章中 对话 低于六次不达有效对话标准
                send_type_user = 0
                send_type_customer = 0
                for msg_obj in msg_objs:
                    send_type = int(msg_obj.send_type)
                    if send_type == 1:
                        send_type_user += 1
                    else:
                        send_type_customer += 1
                if send_type_user < send_type_customer:
                    effective_dialogue = int(send_type_user / 3)
                else:
                    effective_dialogue = int(send_type_customer / 3)

        return effective_dialogue

    # 响应平均时长（员工）
    def average_response_time(self):
        average_response = 0
        data_list = []
        info_objs = models.zgld_chatinfo.objects.filter(
            self.q,
            userprofile_id=self.o_id,
            article_id__isnull=False,
        ).values('customer_id', 'article_id').distinct()
        for info_obj in info_objs:
            chatinfo_objs = models.zgld_chatinfo.objects.filter(
                userprofile_id=self.o_id,
                article_id=info_obj.get('article_id'),
                customer_id=info_obj.get('customer_id'),
            ).order_by('create_date')
            if chatinfo_objs.count() > 1:
                flag = False
                data_dict = {'start_date': '', 'stop_date': ''}
                for chatinfo_obj in chatinfo_objs:
                    send_type = int(chatinfo_obj.send_type)
                    if send_type == 2:
                        data_dict['start_date'] = chatinfo_obj.create_date
                        flag = True
                    if flag:
                        if send_type == 1:
                            data_dict['stop_date'] = chatinfo_obj.create_date
                            break
                if data_dict['start_date'] and data_dict['stop_date']:
                    data_list.append(data_dict)
        num = 0
        len_data = len(data_list)
        for i in data_list:
            date = i.get('stop_date') - i.get('start_date')
            num += date.seconds
        if num != 0 and len_data != 0:
            average_response = int(num / len_data)
        return average_response


    # 点击量（文章）
    def click_the_quantity(self):
        forward_count = 0
        click_count = 0
        read_count_obj = models.zgld_article_to_customer_belonger.objects.filter(self.q).values('user_id').annotate(
            read_count=Sum('read_count'), forward_count=Sum('forward_count')).filter(article_id=self.o_id)
        if read_count_obj:
            click_count = read_count_obj[0].get('read_count')
            forward_count = read_count_obj[0].get('forward_count')

        return forward_count, click_count # 转发量 和 点击量

    # 阅读总时长/平均时长（文章）
    def the_reading_time(self):
        objs = models.ZgldUserOperLog.objects.filter(self.q, article_id=self.o_id, oper_type=4)
        count = objs.count()
        reading_time = 0
        for i in objs:
            reading_time += i.reading_time
        avg_reading_count = 0
        if reading_time != 0:
            avg_reading_count = int(reading_time / count)

        return reading_time, avg_reading_count

    # 视频查看时长统计/平均时长（文章）
    def video_view_duration(self):
        video_average_playing_time = 0
        video_time_num_list = []
        time_objs = models.ZgldUserOperLog.objects.filter(
            self.q,
            article_id=self.o_id,
            oper_type=3,
            video_time__isnull=False
        )

        for time_obj in time_objs:
            video_time_num_list.append(time_obj.video_time)

        video_view_count = 0
        len_video = len(video_time_num_list)
        if len_video > 0:
            for i in video_time_num_list:
                video_view_count += i
            video_average_playing_time = int(video_view_count / len_video)

        data = {
            'video_view_count': video_view_count,
            'video_average_playing_time': video_average_playing_time,
            'len_video': len_video
        }

        return data

    # 点击对话框（文章）
    def click_the_dialog_box(self):
        click_dialog_obj = models.ZgldUserOperLog.objects.filter(
            self.q,
            user_id=self.o_id,
            oper_type=2,
            article__isnull=False)
        click_dialog_num = 0
        for i in click_dialog_obj:
            click_dialog_num += i.click_dialog_num

        return click_dialog_num

    # 主动发送消息（文章）
    def active_message(self):
        result_data = []
        [result_data.append({'customer_id': i.get('customer_id'), 'article_id': i.get('article_id')}) for i in
         models.zgld_chatinfo.objects.filter(self.q, article_id=self.o_id, send_type=2,
             article__isnull=False).values(
             'customer_id', 'article_id').distinct()]
        data_list = []
        user_active_send_num = 0
        for i in result_data:
            infoObjs = models.zgld_chatinfo.objects.filter(
                customer_id=i.get('customer_id'),
                article_id=i.get('article_id'),
            ).order_by('-create_date')
            if infoObjs:
                infoObj = infoObjs[0]
                if int(infoObj.send_type) == 2:
                    user_active_send_num += 1

                    if self.detail_data_type and self.detail_data_type == 'active_message': # 是否查看详情
                        content = eval(infoObj.content)
                        if int(content.get('info_type')) == 2:
                            text = content.get('product_cover_url')
                        else:
                            text = b64decode(content.get('msg'))
                        data_list.append({
                            'customer_username':b64decode(infoObj.customer.username),
                            'content':text,
                            'create_date':infoObj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                        })

        data = {
            'data_list': data_list,
            'user_active_send_num': user_active_send_num,
        }
        return data

    # 拨打电话（文章）
    def call_phone(self):
        objs = models.zgld_accesslog.objects.filter(
            self.q,
            article_id=self.o_id,
            action=10
        )
        call_phone_num = objs.count()

        data_list = []
        if self.detail_data_type and self.detail_data_type == 'call_phone':
            for obj in objs:
                data_list.append({
                    'customer_username': b64decode(obj.customer.username),
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })

        data = {
            'call_phone_num': call_phone_num,
            'data_list': data_list,
        }
        return data

    # 文章点赞次数（文章）
    def thumb_up_number(self):
        objs = models.zgld_accesslog.objects.filter(
            self.q,
            article_id=self.o_id,
            action=19
        )

        click_thumb_num = objs.count()
        data_list = []

        if self.detail_data_type and self.detail_data_type == 'thumb_up_number':
            for obj in objs:
                data_list.append({
                    'customer_name': b64decode(obj.customer.username),
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })
        data = {
            'click_thumb_num': click_thumb_num,
            'data_list': data_list
        }

        return data

    # 文章评论（文章）
    def article_comments(self):
        objs = models.zgld_article_comment.objects.filter(
            self.q,
            article_id=self.o_id,
            # is_audit_pass=1 # 该评论是否审核
        )
        data_list = []
        if self.detail_data_type and self.detail_data_type == 'article_comments': # 点击详情 避免无用数据
            for obj in objs:
                is_audit_pass = '未审核'
                if int(obj.is_audit_pass) == 1:
                    is_audit_pass = '已审核'

                data_list.append({
                    'customer_username':b64decode(obj.from_customer.username),
                    'content': b64decode(obj.content),
                    'is_audit_pass': is_audit_pass,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })

        article_comments_num = objs.count()
        data = {
            'article_comments_num': article_comments_num,
            'data_list': data_list,
        }
        return data




# cerf  token验证
# 雷达后台首页 数据统计
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            order = request.GET.get('order', '-create_date')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            number_days = request.GET.get('number_days')  # 天数
            start_time = request.GET.get('start_time')  # 天数 开始时间
            stop_time = request.GET.get('stop_time')  # 天数 结束时间


            if not start_time and not stop_time: # 时间筛选
                start_time, stop_time = time_screen(number_days)


            company_id = request.GET.get('company_id')  # 区分公司
            public_q = Q()
            if company_id:
                public_q.add(Q(company_id=company_id), Q.AND)

            # 文章数据分析
            if oper_type == 'article_data_analysis':
                detail_type = request.GET.get('detail_type')  # 点击某个详情页面
                """
                detail_type 判断 进入详情类型 起因: 后台数据偏多 利用该参数判断 跳进某个详情页面 避免不进详情 查询到详情数据
                article_comments    查询评论详情
                thumb_up_number     点赞详情
                call_phone          拨打电话
                active_message      主动发送消息
                
                """
                article_id = request.GET.get('article_id')  # 区分文章
                q = Q()
                q.add(Q(create_date__gte=start_time) & Q(create_date__lte=stop_time), Q.AND)

                if article_id:
                    public_q.add(Q(id=article_id), Q.AND)

                objs = models.zgld_article.objects.filter(public_q)

                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []

                detail_data_type = None
                if detail_type:
                    if not article_id: # 点击详情必传文章ID
                        response.code = 301
                        response.msg = '查询文章失败'
                        return JsonResponse(response.__dict__)
                    else:
                        detail_data_type = detail_type
                for obj in objs:

                    statistical_obj = statistical_objs(q, obj.id, detail_data_type)         # 实例化 数据统计

                    # forward_count, click_count = click_the_quantity(q, obj.id)                      # 转发量 点击量
                    # reading_time, avg_reading_count = the_reading_time(q, obj.id)                   # 阅读总时长 和 阅读平均时长
                    # video_view_data = video_view_duration(q, obj.id)
                    # video_view_count = video_view_data.get('video_view_count')                      # 视频查看总时长
                    # len_video = video_view_data.get('len_video')                                    # 观看视频总数
                    # video_average_playing_time = video_view_data.get('video_average_playing_time')  # 平均时长
                    click_dialog_num = statistical_obj.click_the_dialog_box()                              # 点击对话框
                    print('click_dialog_num---------> ', click_dialog_num)
                    user_active_send_data = statistical_obj.active_message()                                # 主动发送数据
                    call_phone_data = statistical_obj.call_phone()                                          # 拨打电话数据
                    click_thumb_data = statistical_obj.thumb_up_number()                                    # 文章点赞数据
                    article_comments_data = statistical_obj.article_comments()                              # 文章评论数据

                    ret_data.append({
                        'id': obj.id,
                        'article_name': obj.title,                      # 文章名称
                        # 'forward_count': forward_count,                 # 文章转发量
                        # 'click_count': click_count,                     # 文章点击量
                        # 'reading_time': reading_time,                   # 文章阅读总时长
                        # 'avg_reading_count': avg_reading_count,         # 文章阅读平均时长
                        # 'video_view_count': video_view_count,           # 视频阅读总时长
                        # 'video_average_playing_time': video_average_playing_time, # 视频阅读平均时长
                        # 'len_video': len_video,                         # 视频播放次数
                        # 'click_dialog_num': click_dialog_num,           # 点击对话框


                        'user_active_send_num': user_active_send_data.get('user_active_send_num'),      # 主动发送消息数量
                        'user_active_send_data': user_active_send_data.get('data_list'),                # 主动发送消息数据

                        'call_phone_num': call_phone_data.get('call_phone_num'),                        # 拨打电话次数
                        'call_phone_data': call_phone_data.get('data_list'),                            # 拨打电话数据

                        'click_thumb_num': click_thumb_data.get('click_thumb_num'),                     # 文章点赞次数
                        'click_thumb_data': click_thumb_data.get('data_list'),                          # 文章点赞数据

                        'article_comments_num': article_comments_data.get('article_comments_num'),      # 文章评论次数
                        'article_comments_data': article_comments_data.get('data_list'),                # 文章评论数据
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }
                response.note = {
                    'id': '文章ID',
                    'article_name': '文章名称',
                    'forward_count': '文章转发量',
                    'click_count': '文章点击量',
                    'reading_time': '文章阅读总时长',
                    'avg_reading_count': '文章阅读平均时长',
                    'video_view_count': '视频阅读总时长',
                    'video_average_playing_time': '视频阅读平均时长',
                    'len_video': '视频播放次数',
                    'click_dialog_num': '点击对话框',

                    'user_active_send_num': '主动发送消息',
                    'user_active_send_data--主动发送数据': {
                        'customer_username': '客户名称',
                        'content': '发送内容',
                        'create_date':'发送消息时间'
                    },


                    'call_phone_num': '拨打电话次数',
                    'call_phone_data--拨打电话数据': {
                        'customer_name': '客户名称',
                        'create_date': '点赞时间',
                    },


                    'click_thumb_num': '文章点赞次数',
                    'click_thumb_data--文章点赞数据':{
                        'customer_name': '客户名称',
                        'create_date': '点赞时间',
                    },

                    'article_comments_num': '文章评论次数',
                    'article_comments_data--文章评论详情': {
                        'customer_username':'客户名称',
                        'content': '评论内容',
                        'is_audit_pass': '是否审核',
                        'create_date': '评论时间',
                    },
                }

            # 员工数据分析
            elif oper_type == 'employee_data_analysis':
                id = request.GET.get('id') # 查询单个员工
                if id:
                    public_q.add(Q(id=id), Q.AND)

                # 获取该公司所有员工信息
                objs = models.zgld_userprofile.objects.filter(public_q)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                ret_data = []

                q = Q()
                q.add(Q(create_date__gte=start_time) & Q(create_date__lte=stop_time), Q.AND) # 时间筛选

                for obj in objs:

                    detail_data_type = ''
                    statistical_obj = statistical_objs(q, obj.id, detail_data_type)

                    copy_nickname = statistical_obj.copy_the_nickname() # 复制昵称次数

                    effective_dialogue = statistical_obj.number_valid_conversations()  # 有效对话次数

                    average_response = statistical_obj.average_response_time() # 咨询平均响应时长


                    ret_data.append({
                        'id': obj.id,
                        'copy_nickname': copy_nickname,             # 复制昵称
                        'username': obj.username,                   # 员工姓名
                        'effective_dialogue': effective_dialogue,   # 有效对话
                        'average_response': average_response,       # 平均响应时长
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }

                response.note = {
                    'username': '咨询用户名称',
                    'copy_nickname': '复制昵称次数',
                    'effective_dialogue': '有效对话',
                    'average_response': '平均响应时长',
                }

        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)
