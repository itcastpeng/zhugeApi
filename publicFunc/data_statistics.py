from zhugeleida import models
from django.db.models import Q, Count, Sum
from publicFunc.base64 import b64decode
import json

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

# 统计数据 调用类
class statistical_objs():

    def __init__(self, o_id):
        self.o_id = o_id

    # 复制昵称 次数及数据（员工）
    def copy_the_nickname(self):
        copy_nickname_obj = models.ZgldUserOperLog.objects.filter(
            user_id=self.o_id,
            oper_type=1
        ).order_by('-create_date')
        data_list = []
        for obj in copy_nickname_obj:
            customer__username = ''
            if obj.customer:
                customer__username = obj.customer.username
                if customer__username:
                    customer__username = b64decode(customer__username)

            data_list.append({
                'customer__username': customer__username,
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
            })

        return data_list

    # 有效对话次数（员工）
    def number_valid_conversations(self):
        data_list = []
        effective_dialogue = 0

        zgld_chatinfo_objs = models.zgld_chatinfo.objects.raw(          # 查询出符合条件的用户和客户 已天为单位
            """select id, DATE_FORMAT(create_date, '%%Y-%%m-%%d') as cdt 
            from zhugeleida_zgld_chatinfo where userprofile_id={userprofile_id}  group by cdt, customer_id;""".format(
                userprofile_id=self.o_id,
            )
        )
        for zgld_chatinfo_obj in zgld_chatinfo_objs:
            effective_num = 0 # 查看详情单个人次数
            customer__username = ''
            result_data = []
            start_date_time = zgld_chatinfo_obj.cdt + ' 00:00:00'  # 按天区分
            stop_date_time = zgld_chatinfo_obj.cdt + ' 23:59:59'
            msg_objs = models.zgld_chatinfo.objects.filter(
                userprofile_id=self.o_id,
                customer_id=zgld_chatinfo_obj.customer_id,
                create_date__gte=start_date_time,
                create_date__lte=stop_date_time,
            ).order_by('create_date')
            dialogue_count = msg_objs.count()       # 查询出该用户和该客户聊天总数

            if dialogue_count >= 6:  # 判断该客户在该文章中 对话 低于六次不达有效对话标准
                send_type_user = 0      # 咨询发送消息
                send_type_customer = 0  # 客户发送消息
                flag = False            # 判断该客户和该用户是否 存在有效聊天
                for msg_obj in msg_objs:

                    send_type = int(msg_obj.send_type)
                    text = get_msg(msg_obj.content) # 获取聊天内容

                    if send_type == 1:
                        send_type_user += 1
                        name = msg_obj.userprofile.username     # 咨询名称
                        avatar = msg_obj.userprofile.avatar     # 头像
                    else:
                        send_type_customer += 1
                        name = ''
                        if msg_obj.customer.username:
                            name = b64decode(msg_obj.customer.username) # 客户名称
                        avatar = msg_obj.customer.headimgurl     # 头像

                    result_data.append({
                        'send_type': send_type,
                        'avatar': avatar,
                        'name': name,
                        'msg': text.get('msg'),
                        'product_cover_url': text.get('product_cover_url'),
                        'product_name': text.get('product_name'),
                        'product_price': text.get('product_price'),
                        'url': text.get('url'),
                        'info_type': text.get('info_type'),
                        'create_date': msg_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                    customer__username = ''
                    if msg_obj.customer.username:
                        customer__username = b64decode(msg_obj.customer.username)
                send_type_user = int(send_type_user / 3)
                send_type_customer = int(send_type_customer / 3)
                if send_type_user < send_type_customer:
                    num = send_type_user
                else:
                    num = send_type_customer

                if num > 0:
                    flag = True

                if send_type_user >= 1 and send_type_customer >= 1:
                    effective_num += num


                if flag:
                    data_list.append({
                        'customer__username': customer__username,
                        'create_date': result_data[0].get('create_date'),
                        'result_data':result_data,
                        'effective_num':effective_num # 单个人 有效次数
                    })

            if effective_num >= 1:
                effective_dialogue += 1

        data = {
            'data_list': data_list,
            'effective_dialogue': effective_dialogue,
        }

        return data

    # 咨询响应平均时长（员工）
    def average_response_time(self):
        average_response = 0
        result_data = []
        info_objs = models.zgld_chatinfo.objects.filter(
            userprofile_id=self.o_id,
            article_id__isnull=False,
        ).values('customer_id', 'customer__username', 'article_id').distinct()
        data_list = []

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
                            break                                               # 只统计该用户第一次聊天回应时长

                if data_dict['start_date'] and data_dict['stop_date']:
                    result_data.append(data_dict)
                    date = data_dict['stop_date'] - data_dict['start_date']
                    data_list.append({
                        'customer__username': b64decode(info_obj.get('customer__username')),
                        'start_date': data_dict['start_date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'stop_date': data_dict['stop_date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'response_time': date.seconds
                    })

        num = 0
        len_data = len(result_data)
        for i in result_data:
            date = i.get('stop_date') - i.get('start_date')
            num += date.seconds
        if num != 0 and len_data != 0:
            average_response = int(num / len_data)

        data = {
            'average_response': str(average_response) + '秒',
            'data_list': data_list,
        }

        return data

    # 发送小程序 （员工）
    def sending_applet(self):
        data_list = []
        objs = models.zgld_accesslog.objects.filter(
            user_id=self.o_id,
            action=23
        )

        for obj in objs:
            data_list.append({
                'customer__username': b64decode(obj.customer.username),
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return data_list



    # 转发量(文章)
    def forwarding_article(self):
        objs = models.zgld_accesslog.objects.filter(
            article_id=self.o_id,
            action__in=[15, 16]
        ).order_by('-create_date')
        data_list = []
        for obj in objs:
            data_list.append({
                'customer__username': b64decode(obj.customer.username),
                'user_username': obj.user.username,
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return data_list

    # 点击量（文章）
    def click_the_quantity(self):
        objs = models.zgld_accesslog.objects.filter(
            article_id=self.o_id,
            action=14
        ).order_by('-create_date')
        data_list = []
        click_count = objs.count()
        for obj in objs:
            data_list.append({
                'customer__username': b64decode(obj.customer.username),
                'user_username': obj.user.username,
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return data_list

    # 阅读总时长/平均时长（文章）
    def the_reading_time(self):

        data_list = []
        objs = models.ZgldUserOperLog.objects.filter(
            article_id=self.o_id,
            oper_type=4
        )

        for obj in objs:
            data_list.append({
                'customer__username': b64decode(obj.customer.username),
                'reading_time': obj.reading_time,
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return data_list

    # 视频查看时长统计/平均时长（文章）
    def video_view_duration(self):

        time_objs = models.ZgldUserOperLog.objects.filter(
            article_id=self.o_id,
            oper_type=3,
            video_time__isnull=False
        )
        len_video = time_objs.count()
        video_view_count = 0
        for time_obj in time_objs:
            video_view_count += time_obj.video_time

        video_average_playing_time = 0
        if video_view_count > 0:
            video_average_playing_time = int(video_view_count / len_video)

        video_objs = models.ZgldUserOperLog.objects.filter(
            article_id=self.o_id,
            oper_type=3,
            video_time__isnull=False
        ).select_related(
            'customer'
        ).values(
            'customer_id',
            'customer__username'
        ).annotate(
            Sum('video_time'),
            Count('id')
        )


        data_list = []
        for video_obj in video_objs:
            avg = 0
            if int(video_obj.get('video_time__sum')) > 0:
                avg = int(video_obj.get('video_time__sum') / video_obj.get('id__count'))
            data_list.append({
                'customer__username': b64decode(video_obj.get('customer__username')),
                'id__count': video_obj.get('id__count'),
                'video_time__sum': video_obj.get('video_time__sum'),
                'avg': avg,

                # 记录后端使用
                'video_average_playing_time': video_average_playing_time,  # 平均阅读时长
                'video_view_count': video_view_count,
                'len_video': len_video,
            })


        return data_list

    # 点击对话框（文章）
    def click_the_dialog_box(self):
        click_dialog_obj = models.ZgldUserOperLog.objects.filter(
            article_id=self.o_id,
            oper_type=2,
        )
        data_list = []
        for i in click_dialog_obj:
            data_list.append({
                'customer__username': b64decode(i.customer.username),
                'create_date': i.create_date.strftime('%Y-%m-%d %H:%M:%S')
            })

        return data_list

    # 主动发送消息（文章）
    def active_message(self):
        result_data = []
        [result_data.append({'customer_id': i.get('customer_id'), 'article_id': i.get('article_id')}) for i in
         models.zgld_chatinfo.objects.filter(article_id=self.o_id, send_type=2,
             article__isnull=False).values(
             'customer_id', 'article_id').distinct()]

        data_list = []
        for i in result_data:
            infoObjs = models.zgld_chatinfo.objects.filter(
                customer_id=i.get('customer_id'),
                article_id=i.get('article_id'),
            ).order_by('-create_date')

            if infoObjs:
                infoObj = infoObjs[0]
                send_type = int(infoObj.send_type)

                if send_type == 2:
                    content = eval(infoObj.content)
                    text = get_msg(content)

                    data_list.append({
                        'customer__username':b64decode(infoObj.customer.username),
                        'msg': text.get('msg'),
                        'product_cover_url': text.get('product_cover_url'),
                        'product_name': text.get('product_name'),
                        'product_price': text.get('product_price'),
                        'url': text.get('url'),
                        'info_type': text.get('info_type'),
                        'create_date':infoObj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                    })

        return data_list

    # 拨打电话（文章）
    def call_phone(self):
        objs = models.zgld_accesslog.objects.filter(
            article_id=self.o_id,
            action=10
        )
        data_list = []
        for obj in objs:
            data_list.append({
                'customer__username': b64decode(obj.customer.username),
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return data_list

    # 文章点赞次数（文章）
    def thumb_up_number(self):
        objs = models.zgld_article_action.objects.filter(
            article_id=self.o_id,
            status=1
        )
        data_list = []
        for obj in objs:
            data_list.append({
                'customer__name': b64decode(obj.customer.username),
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
            })

        return data_list

    # 文章评论（文章）
    def article_comments(self):
        objs = models.zgld_article_comment.objects.filter(
            article_id=self.o_id,
        )
        data_list = []
        for obj in objs:
            is_audit_pass = '未审核'
            if int(obj.is_audit_pass) == 1:
                is_audit_pass = '已审核'

            data_list.append({
                'customer__username':b64decode(obj.from_customer.username),
                'content': b64decode(obj.content),
                'is_audit_pass': is_audit_pass,
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return data_list


