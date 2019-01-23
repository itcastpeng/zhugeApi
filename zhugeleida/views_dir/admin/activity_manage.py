from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.activity_manage_verify import SetFocusGetRedPacketForm, ActivityAddForm, ActivitySelectForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm

import json
from django.db.models import Q, Sum, Count
import xlwt,os, random


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def activity_manage(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":

        # 设置关注领红包
        if oper_type == 'set_focus_get_redPacket':

            is_focus_get_redpacket = request.POST.get('is_focus_get_redpacket')
            focus_get_money = request.POST.get('focus_get_money')

            focus_total_money = request.POST.get('focus_total_money')
            max_single_money = request.POST.get('max_single_money')
            min_single_money = request.POST.get('min_single_money')
            mode = request.POST.get('mode')

            user_id = request.GET.get('user_id')

            form_data = {
                'is_focus_get_redpacket': is_focus_get_redpacket,
                'focus_get_money': focus_get_money,
                'mode' : mode,
                'focus_total_money': focus_total_money,
                'max_single_money' : max_single_money,
                'min_single_money' : min_single_money
            }

            forms_obj = SetFocusGetRedPacketForm(form_data)
            if forms_obj.is_valid():
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id

                gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

                if not  focus_total_money:
                    focus_total_money = 0
                if not  max_single_money:
                    max_single_money = 0

                if not  min_single_money:
                    min_single_money = 0

                if gongzhonghao_app_objs:
                    gongzhonghao_app_objs.update(
                        is_focus_get_redpacket=is_focus_get_redpacket,
                        focus_get_money=focus_get_money,
                        mode = mode,
                        focus_total_money=focus_total_money,
                        max_single_money=max_single_money,
                        min_single_money=min_single_money,
                    )
                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '设置成功'

                else:
                    response.code = 301
                    response.msg = '公众号不存在'


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 查询关注红包
        if oper_type == 'query_focus_get_redPacket':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

            if objs:
                obj = objs[0]
                is_focus_get_redpacket = obj.is_focus_get_redpacket
                focus_get_money = obj.focus_get_money
                focus_total_money = obj.focus_total_money
                min_single_money = obj.min_single_money
                max_single_money = obj.max_single_money
                mode = obj.mode
                reason = obj.reason
                if reason == '发放成功':
                    reason = ''

                #  查询成功 返回200 状态码
                response.data = {
                    'is_focus_get_redpacket': is_focus_get_redpacket,  # 关注领取红包是否(开启)
                    'focus_get_money': focus_get_money,  # 关注领取红包金额
                    'focus_total_money': focus_total_money,  # 红包总金额
                    'reason': reason,  # 提示

                    'mode' : mode,
                    'max_single_money' : max_single_money,
                    'min_single_money' : min_single_money,
                }
                response.code = 200
                response.msg = '设置成功'

            else:
                response.code = 301
                response.msg = '公众号不存在'

        # 查询 文章-活动(任务)
        elif oper_type == 'activity_list':

            print('request.GET----->', request.GET)

            forms_obj = ActivitySelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                product_type = forms_obj.cleaned_data.get('product_type')

                # 如果为1 代表是公司的官网
                user_id = request.GET.get('user_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))

                search_activity_name = request.GET.get('activity_name')  #
                if search_activity_name:
                    q1.children.append(('activity_name__contains', search_activity_name))

                article_title = request.GET.get('article_title')  #
                if article_title:
                    q1.children.append(('article__title__contains', article_title))

                activity_id = request.GET.get('activity_id')  #
                if activity_id:
                    q1.children.append(('id', activity_id))

                search_activity_status = request.GET.get('status')  #
                now_date_time = datetime.datetime.now()
                if search_activity_status:
                    if int(search_activity_status) == 3:
                        q1.children.append(('status', search_activity_status))  #

                    elif int(search_activity_status) == 2:

                        q1.children.append(('start_time__lte', now_date_time))
                        q1.children.append(('end_time__gte', now_date_time))
                        q1.children.append(('status__in', [1, 2, 4]))

                    elif int(search_activity_status) == 1:
                        q1.children.append(('start_time__gt', now_date_time))
                        q1.children.append(('status__in', [1, 2, 4]))
                    elif int(search_activity_status) == 4:
                        q1.children.append(('end_time__lt', now_date_time))
                        q1.children.append(('status__in', [1, 2, 4]))

                print('-----q1---->>', q1)
                objs = models.zgld_article_activity.objects.select_related('article', 'company').filter(q1).order_by(
                    order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if objs:
                    for obj in objs:
                        reason = obj.reason  # 已发红包金额
                        if reason:
                            if '成功' in reason:
                                reason = ''

                        start_time = obj.start_time
                        end_time = obj.end_time
                        status = obj.status
                        status_text = ''
                        if status != 3:

                            if now_date_time >= start_time and now_date_time <= end_time:  # 活动开启并活动在进行中
                                status = 2
                                status_text = '进行中'
                            elif now_date_time < start_time:
                                status = 1
                                status_text = '未启用'
                            elif now_date_time > end_time:
                                status = 4
                                status_text = '已结束'
                        else:

                            status_text = '已终止'

                        ret_data.append({
                            'article_id': obj.article_id,
                            'article_title': obj.article.title,
                            'company_id': obj.company_id,

                            'activity_id': obj.id,  # 活动Id
                            'activity_name': obj.activity_name,  # 分享文章名称
                            'activity_total_money': obj.activity_total_money,  # 活动总金额
                            'activity_single_money': obj.activity_single_money or '',  # 单个金额
                            'max_single_money': obj.max_single_money or '',  # 单个金额
                            'min_single_money': obj.min_single_money or '',  # 单个金额
                            'reach_forward_num': obj.reach_forward_num,  # 达到多少次发红包
                            'already_send_redPacket_num': obj.already_send_redPacket_num or 0,  # 已发放发红包个数[领取条件]
                            'status': status,
                            'status_text': status_text,
                            'start_time': obj.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'end_time': obj.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'reason': reason,
                            'mode' : obj.mode,
                            'reach_stay_time' : obj.reach_stay_time,   # 满足多少秒发红包；默认是0,代表不设限制。
                            'is_limit_area' : obj.is_limit_area,       # 是否地区限制
                            'limit_area' : json.loads(obj.limit_area), # 限制的地区列表 ['山西','广东','河北']


                        })

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }


            else:

                response.code = 301
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())

        # 查询 活动发红包记录
        elif oper_type == 'send_activity_redPacket':

            company_id = request.GET.get('company_id')
            article_id = request.GET.get('article_id')
            activity_id = request.GET.get('activity_id')

            status = request.GET.get('status')
            customer_name = request.GET.get('customer_name')  # 当有搜索条件 如 搜索产品名称

            forms_obj = ArticleRedPacketSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count
                # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count
                q1 = Q()
                q1.connector = 'and'
                if status:
                    q1.children.append(('status', status))

                if customer_name:
                    q1.children.append(('customer__username__contains', customer_name))

                activity_redPacket_objs = models.zgld_activity_redPacket.objects.select_related('customer', 'article',
                                                                                                'activity',
                                                                                                'company').filter(
                    article_id=article_id,
                    activity_id=activity_id,
                    should_send_redPacket_num__gt=0,
                ).filter(q1).order_by(order)

                count = activity_redPacket_objs.count()
                if activity_redPacket_objs:  # 说明有人参加活动

                    if length != 0:
                        print('current_page -->', current_page)
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        activity_redPacket_objs = activity_redPacket_objs[start_line: stop_line]

                    ret_data = []
                    for obj in activity_redPacket_objs:

                        activity_objs = models.zgld_article_activity.objects.filter(id=activity_id).order_by(
                            '-create_date')
                        activity_obj = activity_objs[0]
                        start_time = activity_obj.start_time
                        end_time = activity_obj.end_time

                        forward_read_num = models.zgld_activity_redPacket.objects.filter(
                            customer_parent_id=obj.customer_id, activity_id=activity_id, create_date__lte=end_time,
                            create_date__gte=start_time).values_list('customer_id').distinct().count()

                        forward_stay_time_dict = models.zgld_article_to_customer_belonger.objects.filter(
                            customer_parent_id=obj.customer_id, article_id=article_id, create_date__lte=end_time,
                            create_date__gte=start_time).aggregate(forward_stay_time=Sum('stay_time'))

                        forward_stay_time = forward_stay_time_dict.get('forward_stay_time')
                        if not forward_stay_time:
                            forward_stay_time = 0

                        print('-----forward_read_num forward_stay_time --->>', forward_read_num, forward_stay_time)
                        obj.forward_read_count = forward_read_num
                        obj.forward_stay_time = forward_stay_time

                        activity_obj = models.zgld_article_activity.objects.get(id=activity_id)
                        reach_forward_num = activity_obj.reach_forward_num  # 达到多少次发红包(转发阅读后次数))
                        already_send_redPacket_num = obj.already_send_redPacket_num  # 已发放次数
                        already_send_redPacket_money = obj.already_send_redPacket_money  # 已发红包金额

                        shoudle_send_num = ''
                        if reach_forward_num != 0:  # 不能为0
                            forward_read_num = int(forward_read_num)
                            divmod_ret = divmod(forward_read_num, reach_forward_num)
                            shoudle_send_num = divmod_ret[0]
                            yushu = divmod_ret[1]

                        customer_area = obj.customer.province + obj.customer.city

                        _forward_stay_time = conversion_seconds_hms(forward_stay_time)
                        customer_id = obj.customer_id
                        customer_username = obj.customer.username
                        customer_username = conversion_base64_customer_username_base64(customer_username, customer_id)
                        status = obj.status
                        if status in [2, 3, 4]:
                            status_text = '未发'
                            status = 2
                        else:
                            status_text = '已发'
                            status = 1

                        ret_data.append({
                            'id': obj.id,
                            'status': status,  # 状态
                            'status_text': status_text,  # 状态

                            'customer_username': customer_username,  # 客户名字
                            'customer_id': obj.customer_id,  # 客户ID
                            'customer_headimgurl': obj.customer.headimgurl,  # 客户的头像
                            'customer_sex_text': obj.customer.get_sex_display() or '',  # 性别
                            'customer_sex': obj.customer.sex or '',  # 客户的头像
                            'customer_area': customer_area,  # 客户的所在地区

                            'forward_read_num': forward_read_num,  # 转发文章被阅读数量
                            'forward_stay_time': _forward_stay_time,  # 转发文章被查看时长

                            'already_send_redPacket_money': already_send_redPacket_money,  # 已发红包金额
                            'already_send_redPacket_num': already_send_redPacket_num,  # 已经发放次数
                            'should_send_redPacket_num': shoudle_send_num,  # 应该发放的次数
                            'send_log': json.loads(obj.send_log),  # 应该发放的次数

                        })

                        response.code = 200
                        response.msg = '获取成功'
                        response.data = {
                            'ret_data': ret_data,
                            'count': count,
                        }



                else:
                    response.code = 301
                    response.msg = '[无记录]活动发红包记录表'
                    print('------[无记录]活动发红包记录表 activity_id ----->>', activity_id)

        # 活动消费 查询
        elif oper_type == 'query_total_xiaofei':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            now_date_time = datetime.datetime.now()
            objs = models.zgld_article_activity.objects.filter(company_id=company_id,
                                                               end_time__gte=now_date_time).exclude(status=3)

            if objs:

                already_send_redPacket_money_dict = objs.aggregate(
                    already_send_redPacket_money=Sum('already_send_redPacket_money'))
                already_send_redPacket_money = already_send_redPacket_money_dict.get('already_send_redPacket_money')

                if not already_send_redPacket_money:
                    already_send_redPacket_money = 0

                activity_total_money_dict = objs.aggregate(activity_total_money=Sum('activity_total_money'))
                activity_total_money = activity_total_money_dict.get('activity_total_money')
                if not activity_total_money:
                    activity_total_money = 0

                dai_xiaofei_money = activity_total_money - already_send_redPacket_money

                #  查询成功 返回200 状态码
                response.data = {
                    'activity_total_money': activity_total_money,  # 活动总金额
                    'already_send_redPacket_money': already_send_redPacket_money,  # 已发红包
                    'dai_xiaofei_money': dai_xiaofei_money  # 剩余待消费金额
                }

                response.code = 200
                response.msg = '获取成功'

            else:
                response.data = {
                    'activity_total_money': 0,  # 活动总金额
                    'already_send_redPacket_money': 0,  # 已发红包
                    'dai_xiaofei_money': 0  # 剩余待消费金额
                }
                response.code = 200
                response.msg = '活动不存在'

        # 查询
        elif oper_type == 'query_focus_gongzhonghao_customer':
            company_id = request.GET.get('company_id')
            is_receive_redPacket = request.GET.get('is_receive_redPacket')

            forms_obj = QueryFocusCustomerSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  #
                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('user_type', 1))
                q1.children.append(('company_id', company_id))
                q1.children.append(('is_subscribe', 1)) # 已经关注
                if is_receive_redPacket:
                    q1.children.append(('is_receive_redPacket', is_receive_redPacket))

                objs = models.zgld_customer.objects.filter(q1).order_by(order)

                count = objs.count()
                if objs:  # 说明有人参加活动
                    if length != 0:
                        print('current_page -->', current_page)
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    ret_data = []
                    for obj in objs:
                        customer_id = obj.id
                        customer_username = obj.username
                        customer_username = conversion_base64_customer_username_base64(customer_username, customer_id)

                        province = obj.province if obj.province else ''
                        city =  obj.city if obj.city else ''

                        ret_data.append({
                            'id': customer_id,
                            'customer_username': customer_username,
                            'customer_headimgurl': obj.headimgurl,  # 客户的头像
                            'customer_sex_text': obj.get_sex_display() or '',  # 性别
                            'customer_sex': obj.sex or '',  # 客户的头像

                            'area': province + ' ' + city,  # 地区
                            'is_receive_redPacket': obj.is_receive_redPacket,  #   (0, '没有发送过关注红包'), (1, '发送了关注红包')
                            'is_receive_redPacket_text': obj.get_is_receive_redPacket_display(),  # (0, '取消订阅该公众号'), (1, '已经订阅该公众号')
                            'redPacket_money': obj.redPacket_money,
                            'subscribe_time': obj.subscribe_time.strftime('%Y-%m-%d %H:%M:%S') if obj.subscribe_time else '',  # 关注时间

                        })

                        response.code = 200
                        response.msg = '获取成功'
                        response.data = {
                            'ret_data': ret_data,
                            'count': count,
                        }
                else:
                    response.code = 301
                    response.msg = '数据为空'

        # 生成关注领红包的Excel表格
        elif oper_type == 'generate_focus_redPacket_excel':
            company_id = request.GET.get('company_id')
            start_time = request.GET.get('start_time')
            end_time = request.GET.get('end_time')


            data_list = [['编号','姓名','性别','地区','红包金额','是否关注','关注时间']]
            book = xlwt.Workbook()  # 新建一个excel

            q1 = Q()
            q1.connector = 'and'
            q1.children.append(('user_type', 1))
            q1.children.append(('company_id', company_id))
            q1.children.append(('create_date__gte', start_time))
            q1.children.append(('create_date__lte', end_time))
            # q1.children.append(('is_subscribe', 1))  # 已经关注
            q1.children.append(('is_receive_redPacket', 1)) # (1, '发送了关注红包')

            objs = models.zgld_customer.objects.filter(q1).order_by('-create_date')

            if objs:  # 说明有人参加活动

                index = 0
                for obj in objs:
                    customer_id = obj.id
                    customer_username = obj.username
                    customer_username = conversion_base64_customer_username_base64(customer_username, customer_id)

                    province = obj.province if obj.province else ''
                    city = obj.city if obj.city else ''
                    area =  province + ' ' + city,  # 地区
                    subscribe_time = obj.subscribe_time.strftime('%Y-%m-%d %H:%M:%S') if obj.subscribe_time else ''
                    is_subscribe = obj.is_subscribe
                    subscribe = ''
                    if is_subscribe == 0:
                        subscribe = '未关注'
                    elif is_subscribe ==1:
                        subscribe = '已关注'

                    index = index + 1
                    data_list.append([
                        index,customer_username, obj.get_sex_display() or '', area,
                        obj.redPacket_money,subscribe,
                        subscribe_time,  # 关注时间
                    ])

            print('----data_list -->>',data_list)

            sheet = book.add_sheet('sheet1')  # 添加一个sheet页
            row = 0  # 控制行
            for stu in data_list:
                col = 0  # 控制列
                for s in stu:  # 再循环里面list的值，每一列
                    sheet.write(row, col, s)
                    col += 1
                row += 1


            excel_name = '领取红包详情_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            download_excel_path = 'http://api.zhugeyingxiao.com/' + os.path.join('statics', 'zhugeleida', 'fild_upload',
                                                                                 '{}.xlsx'.format(excel_name))
            book.save(os.path.join(os.getcwd(), 'statics', 'zhugeleida', 'fild_upload', '{}.xlsx'.format(excel_name)))
            response.data = {'download_excel_path': download_excel_path}
            response.code = 200
            response.msg = '生成生成'



    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def activity_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 删除-个人产品
        if oper_type == "delete":

            objs = models.zgld_article_activity.objects.filter(id=o_id)

            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 301
                response.msg = '活动不存在或者正在进行中'

        # 修改个人产品
        elif oper_type == 'update':

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            activity_id = o_id
            activity_name = request.POST.get('activity_name')
            article_id = request.POST.get('article_id')  # 文章ID
            activity_total_money = request.POST.get('activity_total_money')
            activity_single_money = request.POST.get('activity_single_money')
            reach_forward_num = request.POST.get('reach_forward_num')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            reach_stay_time = request.POST.get('reach_stay_time')  # 达到多少秒发红包
            limit_area = request.POST.get('limit_area')
            is_limit_area = request.POST.get('is_limit_area')

            mode = request.POST.get('mode')
            max_single_money = request.POST.get('max_single_money')
            min_single_money = request.POST.get('min_single_money')


            form_data = {

                'company_id': company_id,
                'activity_id': activity_id,  # 活动名称
                'activity_name': activity_name,  # 活动名称

                'article_id': article_id,  # 文章ID
                'activity_total_money': activity_total_money,  # 活动总金额(元)
                'activity_single_money': activity_single_money,  # 单个金额(元)
                'reach_forward_num': reach_forward_num,  # 达到多少次发红包(转发次数)
                'start_time': start_time,  # 达到多少次发红包(转发次数)
                'end_time': end_time,  # 达到多少次发红包(转发次数)

                'max_single_money' : max_single_money,
                'min_single_money' : min_single_money,

                'mode' : mode,  #红包发送方式
                'reach_stay_time': reach_stay_time,  # 达到多少秒
                'is_limit_area': is_limit_area       # 是否限制区域
            }

            forms_obj = ActivityUpdateForm(form_data)
            if forms_obj.is_valid():

                reach_stay_time = forms_obj.cleaned_data.get('reach_stay_time')

                if not  is_limit_area: # 没有限制
                    limit_area = json.dumps('[]')


                objs = models.zgld_article_activity.objects.filter(id=activity_id, company_id=company_id)
                if not activity_single_money:
                    activity_single_money = 0
                if not min_single_money:
                    min_single_money = 0
                if not max_single_money:
                    max_single_money = 0

                if objs:
                    objs.update(
                        article_id=article_id,
                        activity_name=activity_name.strip(),
                        activity_total_money=activity_total_money,
                        activity_single_money=activity_single_money,
                        max_single_money=max_single_money,
                        min_single_money=min_single_money,
                        reach_forward_num=reach_forward_num,
                        start_time=start_time,
                        end_time=end_time,
                        mode=mode,
                        reach_stay_time=reach_stay_time,
                        is_limit_area=is_limit_area,
                        limit_area=limit_area,
                    )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 增加红包活动
        elif oper_type == "add":

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            activity_name = request.POST.get('activity_name')
            article_id = request.POST.get('article_id')  # 文章ID
            activity_total_money = request.POST.get('activity_total_money')
            activity_single_money = request.POST.get('activity_single_money')
            reach_forward_num = request.POST.get('reach_forward_num')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            reach_stay_time = request.POST.get('reach_stay_time')  #达到多少秒发红包
            limit_area = request.POST.get('limit_area')
            is_limit_area = request.POST.get('is_limit_area')

            mode = request.POST.get('mode')
            max_single_money = request.POST.get('max_single_money')
            min_single_money = request.POST.get('min_single_money')

            if not activity_single_money:
                activity_single_money = 0
            if not min_single_money:
                min_single_money = 0
            if not max_single_money:
                max_single_money = 0

            form_data = {

                'company_id': company_id,
                'activity_name': activity_name,  # 活动名称
                'article_id': article_id,  # 文章ID
                'activity_total_money': activity_total_money,  # 活动总金额(元)
                'activity_single_money': activity_single_money,  # 单个金额(元)
                'reach_forward_num': reach_forward_num,  # 达到多少次发红包(转发次数)
                'start_time': start_time,  #
                'end_time': end_time,  #
                'mode' : mode,

                'max_single_money' : max_single_money,
                'min_single_money' : min_single_money,

                'reach_stay_time' : reach_stay_time, #达到多少秒
                'is_limit_area' : is_limit_area,     # 是否限制区域

            }

            forms_obj = ActivityAddForm(form_data)
            if forms_obj.is_valid():
                reach_stay_time = forms_obj.cleaned_data.get('reach_stay_time')

                if not  is_limit_area: # 没有限制
                    limit_area = json.dumps('[]')


                models.zgld_article_activity.objects.create(
                    article_id=article_id,
                    company_id=company_id,
                    activity_name=activity_name.strip(),
                    activity_total_money=activity_total_money,
                    activity_single_money=activity_single_money,
                    reach_forward_num=reach_forward_num,
                    start_time=start_time,
                    end_time=end_time,
                    mode=mode,
                    reach_stay_time=reach_stay_time,
                    is_limit_area=is_limit_area,
                    limit_area=limit_area,
                )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改活动状态
        elif oper_type == "change_artivity_status":
            print('-------change_status------->>', request.POST)
            status = request.POST.get('status')

            article_objs = models.zgld_article_activity.objects.filter(id=o_id)

            if article_objs:

                article_objs.update(
                    status=status
                )
                response.code = 200
                response.msg = "修改状态成功"


            else:

                response.code = 302
                response.msg = '活动不存在'

    return JsonResponse(response.__dict__)
