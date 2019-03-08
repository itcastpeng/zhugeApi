from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserSelectForm
import json
from django.db.models import Q, Count, Sum


# cerf  token验证
# 雷达后台首页 数据统计
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            order = request.GET.get('order', '-create_date')

            field_dict = {
                'id': '',
            }
            q = conditionCom(request, field_dict)

            print('------q------>>', q)

            # 获取用户信息
            objs = models.zgld_userprofile.objects.filter(
                q,
                company_id=company_id,
            )
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                read_count = 0
                forward_count = 0

                # --------------------------复制昵称次数---------------------------
                copy_nickname = models.ZgldUserOperLog.objects.filter(user_id=obj.id).count()

                # ----------------------------点击量 转发量------------------------------
                read_count_obj = models.zgld_article_to_customer_belonger.objects.values('user_id').annotate(
                    read_count=Sum('read_count'), forward_count=Sum('forward_count')).filter(user_id=obj.id)
                if read_count_obj:
                    read_count = read_count_obj[0].get('read_count')
                    forward_count = read_count_obj[0].get('forward_count')

                # --------------------------拨打电话次数------------------------
                phone_call_num = models.zgld_accesslog.objects.filter(user_id=obj.id, action=10).count()

                #  ----------------------------用戶主动发送消息--------------------------
                data_list = []
                [data_list.append({'customer_id': i.get('customer_id'), 'article_id': i.get('article_id')}) for i in
                 models.zgld_chatinfo.objects.filter(userprofile_id=obj.id, send_type=2, article__isnull=False).values(
                     'customer_id', 'article_id').distinct()]

                user_active_send_num = 0
                for i in data_list:
                    infoObjs = models.zgld_chatinfo.objects.filter(
                        customer_id=i.get('customer_id'),
                        article_id=i.get('article_id'),
                        userprofile_id=obj.id).order_by('-create_date')
                    if infoObjs:
                        if int(infoObjs[0].send_type) == 2:
                            user_active_send_num += 1

                # -------------------------------客户点击对话框次数-----------------------
                click_dialog_obj = models.ZgldUserOperLog.objects.filter(user_id=obj.id, oper_type=2,
                    article__isnull=False)
                click_dialog_num = 0
                for i in click_dialog_obj:
                    click_dialog_num += i.click_dialog_num

                # --------------------------------有效对话次数--------------------------
                effective_dialogue = 0
                zgld_chatinfo_objs = models.zgld_chatinfo.objects.raw(
                    """select id, DATE_FORMAT(create_date, '%%Y-%%m-%%d') as cdt 
                    from zhugeleida_zgld_chatinfo where userprofile_id={} and article_id is not null group by cdt, article_id, customer_id;""".format(obj.id))

                for zgld_chatinfo_obj in zgld_chatinfo_objs:
                    start_date_time = zgld_chatinfo_obj.cdt + ' 00:00:00'
                    stop_date_time = zgld_chatinfo_obj.cdt + ' 23:59:59'

                    msg_objs = models.zgld_chatinfo.objects.filter(
                        userprofile_id=obj.id,
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


                # --------------------------------咨询平均响应时长------------------------
                average_response = 0
                data_list = []
                info_objs = models.zgld_chatinfo.objects.filter(
                    userprofile_id=obj.id,
                    article_id__isnull=False,
                ).values('customer_id', 'article_id').distinct()
                for info_obj in info_objs:
                    chatinfo_objs = models.zgld_chatinfo.objects.filter(
                        userprofile_id=obj.id,
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

                #--------------------------视频查看时长统计--------------------
                video_average_playing_time = 0
                video_time_num_list = []
                time_objs = models.ZgldUserOperLog.objects.filter(
                    user_id=obj.id,
                    oper_type=3,
                    video_time__isnull=False
                )

                for time_obj in time_objs:
                    video_time_num_list.append(time_obj.video_time)

                num = 0
                len_video = len(video_time_num_list)
                if len_video > 0:
                    for i in video_time_num_list:
                        num += i
                    video_average_playing_time = int(num / len_video)

                # ------------------------------统计文章查看时长----------------------
                article_reading_time = 0
                article_reading_time_objs = models.ZgldUserOperLog.objects.filter(
                    user_id=obj.id,
                    oper_type=4,
                    reading_time__isnull=False
                )
                num = 0
                for article_reading_time_obj in article_reading_time_objs:
                    num += int(article_reading_time_obj.reading_time)
                if article_reading_time_objs.count() > 0:
                    article_reading_time = int(num / article_reading_time_objs.count())



                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'copy_nickname': copy_nickname,
                    'read_count': read_count,
                    'forward_count': forward_count,
                    'phone_call_num': phone_call_num,
                    'click_dialog_num': click_dialog_num,
                    'user_active_send_num': user_active_send_num,
                    'effective_dialogue': effective_dialogue,
                    'average_response': average_response,
                    'video_average_playing_time': video_average_playing_time,
                    'article_reading_time': article_reading_time,
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
                'read_count': '点击量',
                'forward_count': '转发量',
                'phone_call_num': '拨打电话次数',
                'click_dialog_num': '客户点击对话框次数',
                'user_active_send_num': '客户主动发送消息数量',
                'effective_dialogue': '有效对话',
                'average_response': '平均响应时长',
                'video_average_playing_time': '文章视频查看平均时长',
                'article_reading_time': '文章查看时长',
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "GET":
        pass


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
#
