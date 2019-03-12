from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.action_verify import ActionSelectForm, ActionCountForm, ActionCustomerForm, SelectForm
from zhugeleida import models
from django.db.models import Count
from publicFunc.condition_com import conditionCom
from django.db.models import Q
from datetime import datetime, timedelta
import json
from publicFunc.base64 import b64encode, b64decode
import base64
# 跟进数据
def follow_up_data(user_id, request, data_type=None):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']

        q = Q()
        deletionTime = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        start_time = deletionTime + ' 00:00:00'
        stop_time = deletionTime + ' 23:59:59'
        q.add(Q(create_date__gte=start_time) & Q(user_id=user_id), Q.AND)
        q.add(Q(create_date__lte=stop_time), Q.AND)
        print('q--------> ', q)

        # ----------------------------点击对话框次数-----------------------------------
        click_dialog_objs = models.ZgldUserOperLog.objects.filter(
            q,
            oper_type=2,
            article__isnull=False
        ).values('customer_id', 'customer__username').distinct()
        click_dialog_num = click_dialog_objs.count()


        # ------------------------------拨打电话次数----------------------------------
        make_phone_call_objs = models.zgld_accesslog.objects.filter(
            q,
            action=10,
        ).values('customer_id', 'customer__username').distinct()
        make_phone_call_count = make_phone_call_objs.count()


        # # ----------------------------符合匹配条件查询文章数据------------------------------
        article_conditions = models.ZgldUserOperLog.objects.filter(
            oper_type=3,
            article__isnull=False
        ).values('article__tags', 'customer_id', 'customer__username', 'customer__headimgurl'
        ).annotate(Count('id')).distinct()
        # 是否以标签分类↑

        result_data = []
        if_article_conditions = 0
        for i in article_conditions:
            if i.get('id__count') >= 3:  # 条数大于等于
                article_tags = models.ZgldUserOperLog.objects.filter(
                    oper_type=3,
                    customer_id=i.get('customer_id'),
                )

                num = 0 # 该人查看的所有文章总时长
                count = 0 # 该人满足条件总数
                for article_tag in article_tags:
                    if article_tag.reading_time >= 60:  # 该人查看文章总时长 大于60秒
                        num += article_tag.reading_time
                        count += 1

                eval_num = 0
                if num > 0:
                    eval_num = int(num / count)

                result_data.append({
                    'customer_id': i.get('customer_id'),
                    'customer__username': b64decode(i.get('customer__username')),
                    'customer__headimgurl':i.get('customer__headimgurl'),
                    'id__count': i.get('id__count'),
                    'reading_time': num,  # 阅读时长
                    'eval_num': eval_num,                      # 平均时长
                })

                if count >= 3:
                    if_article_conditions += 1

        data_list = []
        if data_type:
            if data_type == 'dialog':
                # 点击对话框 详情
                for click_dialog_obj in click_dialog_objs:
                    objs = models.ZgldUserOperLog.objects.filter(
                        q,
                        oper_type=2,
                        article__isnull=False,
                        customer_id=click_dialog_obj.get('customer_id')
                    ).order_by('-create_date')[0]
                    data_list.append({
                        'id': objs.id,
                        'customer__headimgurl': objs.customer.headimgurl,
                        'customer_id': click_dialog_obj.get('customer_id'),
                        'customer__username': b64decode(click_dialog_obj.get('customer__username')),
                        'time': objs.create_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
            elif data_type == 'phone_call':
                # 拨打电话次数详情
                for make_phone_call_obj in make_phone_call_objs:
                    objs = models.zgld_accesslog.objects.filter(
                        q,
                        action=10,
                        customer_id=make_phone_call_obj.get('customer_id')
                    ).order_by('-create_date')[0]
                    data_list.append({
                        'id': objs.id,
                        'customer__headimgurl': objs.customer.headimgurl,
                        'customer_id': make_phone_call_obj.get('customer_id'),
                        'customer__username': b64decode(make_phone_call_obj.get('customer__username')),
                        'time': objs.create_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
            else:
                data_list = result_data

        count = len(data_list)  # 总数

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            data_list = data_list[start_line: stop_line]

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'click_dialog_num':click_dialog_num,
            'make_phone_call_count':make_phone_call_count,
            'if_article_conditions':if_article_conditions,
            'ret_data':data_list,
            'data_count':count
        }
        response.note['click_dialog_num'] = '点击对话框次数'
        response.note['make_phone_call_count'] = '拨打电话次数'
        response.note['if_article_conditions'] = '满足搜索条件数量'
        response.note['data_type'] = 'article=条件查询 / dialog=点击对话框 / phone_call=拨打电话次数'

    else:
        response.code = 301
        response.data = json.loads(forms_obj.errors.as_json())

    return response


# 访问日志操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def action(request, oper_type):
    '''
     分页获取访问的全部日志信息
    :param request:
    :return:
    '''
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        response = Response.ResponseObj()

        # 雷达-时间
        if oper_type == 'time':
            forms_obj = ActionSelectForm(request.GET)
            if forms_obj.is_valid():
                customer_id = request.GET.get('customer_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'action': '',
                    'create_date__gte': '',

                }

                q = conditionCom(request, field_dict)
                q.add(Q(**{'user_id': user_id}), Q.AND)
                if customer_id:
                    q.add(Q(**{'customer_id': customer_id}), Q.AND)

                create_date__gte = request.GET.get('create_date__gte')
                create_date__lt = request.GET.get('create_date__lt')
                action = request.GET.get('action')

                if action:  # 表示是行为中的请求
                    if not create_date__gte:
                        now_time = datetime.now()
                        create_date__gte = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                        q.add(Q(**{'create_date__gte': create_date__gte}), Q.AND)

                    if create_date__lt:
                        stop_time = (datetime.strptime(create_date__lt, '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")
                        q.add(Q(**{'create_date__lt': stop_time}), Q.AND)

                objs = models.zgld_accesslog.objects.select_related('user', 'customer').filter(q).order_by(order)
                objs.update(is_new_msg=False)

                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    try:
                        username = base64.b64decode(obj.customer.username)
                        username = str(username, 'utf-8')
                        # print('----- 解密b64decode User_id username----->', username)
                    except Exception as e:
                        # print('----- b64decode解密失败的 customer_id 是----->', obj.customer_id)
                        username = '客户ID%s' % (obj.customer_id)

                    ret_data.append({
                        'user_id': obj.user_id,
                        'customer_username': username,
                        'customer_id': obj.customer_id,
                        'headimgurl': obj.customer.headimgurl,
                        'customer_source': obj.customer.user_type,
                        'customer_source_text': obj.customer.get_user_type_display(),
                        'log': username + obj.remark,
                        'create_date': obj.create_date,
                    })

                response.code = 200
                response.msg = '查询日志记录成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

                return JsonResponse(response.__dict__)

        # # 获取新的日志信息
        # elif oper_type == 'get_new_log':
        #     forms_obj = ActionSelectForm(request.GET)
        #     if forms_obj.is_valid():
        #         response = Response.ResponseObj()
        #
        #         order = request.GET.get('order', '-create_date')
        #
        #         field_dict = {
        #             'user_id': '',
        #             'action': '',
        #         }
        #
        #         q = conditionCom(request, field_dict)
        #         q.add(Q(**{'is_new_msg': True}), Q.AND)
        #
        #
        #         objs = models.zgld_accesslog.objects.select_related('user', 'customer').filter(q).order_by(order)
        #         count = objs.count()
        #
        #         ret_data = []
        #         for obj in objs:
        #
        #             try:
        #                 username = base64.b64decode(obj.customer.username)
        #                 username = str(username, 'utf-8')
        #                 print('----- 解密b64decode 客户的username----->', username)
        #             except Exception as e:
        #                 print('----- b64decode解密失败的 customer_id 是----->', obj.customer_id)
        #                 username = '客户ID%s' % (obj.customer_id)
        #
        #
        #             ret_data.append({
        #                 'user_id': obj.user_id,
        #                 'customer_id': obj.customer_id,
        #                 'action' : obj.get_action_display(),
        #                 'log': username + obj.remark,
        #                 'create_date': obj.create_date,
        #             })
        #
        #         # print('----ret_data----->>', ret_data)
        #         objs.update(is_new_msg=False)
        #         response.code = 200
        #         response.msg = '查询日志记录成功'
        #         response.data = {
        #             'ret_data': ret_data,
        #             'data_count': count,
        #         }
        #
        #         return JsonResponse(response.__dict__)

        # 雷达-行为
        elif oper_type == 'count':
            forms_obj = ActionCountForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('user_id')

                field_dict = {
                    'id': '',
                    'user_id': '',
                    'create_date__gte': '',
                    # 'create_date__lt': '',

                }

                q = conditionCom(request, field_dict)

                create_date__gte = request.GET.get('create_date__gte')
                create_date__lt = request.GET.get('create_date__lt')
                if not create_date__gte:
                    now_time = datetime.now()
                    create_date__gte = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                    q.add(Q(**{'create_date__gte': create_date__gte}), Q.AND)

                if create_date__lt:
                    stop_time = (datetime.strptime(create_date__lt, '%Y-%m-%d') + timedelta(days=1)).strftime(
                        "%Y-%m-%d")
                    q.add(Q(**{'create_date__lt': stop_time}), Q.AND)

                # print('q  ---->', q)

                objs = models.zgld_accesslog.objects.filter(q).values('action').annotate(Count('action'))
                # print('count_action_data -->', objs)

                detail_dict = {}
                for obj in objs:
                    # print('---------->>', obj['action'], obj['action__count'])
                    detail_dict[obj.get('action')] = obj['action__count']

                action_dict = {

                    1: '查看名片',
                    2: '查看产品',  # 查看您的产品; 查看竞价排名; 转发了竞价排名。
                    3: '查看动态',  # 查看了公司的动态。 评论了您的企业动态。
                    4: '查看官网',  # 查看了您的官网 , 转发了您官网。
                    5: '复制微信',
                    6: '转发名片',
                    7: '咨询产品',
                    8: '保存电话',
                    9: '觉得靠谱',  # 取消了对您的靠谱
                    10: '拨打电话',
                    11: '播放语音',
                    12: '复制邮箱',
                }

                print('----detail_dict----->>', detail_dict)

                response.code = 200
                response.msg = '查询日志记录成功'
                response.data['action'] = action_dict
                response.data['detail'] = detail_dict
                response.data['user_id'] = user_id

                return JsonResponse(response.__dict__)

        # 雷达-人
        elif oper_type == 'customer':
            forms_obj = ActionCustomerForm(request.GET)
            response = Response.ResponseObj()
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'id': '',
                    'user_id': '',
                    'name': '__contains',
                    'create_date__gte': '',
                }
                q = conditionCom(request, field_dict)
                create_date__gte = request.GET.get('create_date__gte')
                create_date__lt = request.GET.get('create_date__lt')
                if not create_date__gte:
                    now_time = datetime.now()
                    create_date__gte = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                    q.add(Q(**{'create_date__gte': create_date__gte}), Q.AND)

                if create_date__lt:
                    stop_time = (datetime.strptime(create_date__lt, '%Y-%m-%d') + timedelta(days=1)).strftime(
                        "%Y-%m-%d")
                    q.add(Q(**{'create_date__lt': stop_time}), Q.AND)

                # print('----q-->>',q)
                objs = models.zgld_accesslog.objects.select_related(
                    'user','customer'
                ).filter(q).values(
                    'customer__headimgurl', 'customer_id','customer__username'
                ).annotate(Count('action'))
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_list = []
                for obj in objs:

                    customer_id = obj['customer_id']
                    action_count = obj['action__count']
                    customer_username = obj['customer__username']
                    headimgurl = obj['customer__headimgurl']

                    try:
                        print('----- 解密b64decode 客户的username----->', customer_username)
                        customer_name = base64.b64decode(customer_username)
                        customer_name = str(customer_name, 'utf-8')

                    except Exception as e:
                        print('----- b64decode解密失败的 customer_id 是----->', customer_id)
                        customer_name = '客户ID%s' % (customer_id)

                    insert_data = {
                        'customer_id': customer_id,
                        'action_count': action_count,
                        'customer_username': customer_name,
                        'headimgurl': headimgurl,
                    }
                    if not ret_list:  # 首次添加
                        ret_list.append(insert_data)

                    else:  # ret_list 中有数据
                        for index, data in enumerate(ret_list):
                            if data['action_count'] < action_count:
                                ret_list.insert(index, insert_data)
                                break
                        else:
                            ret_list.append(insert_data)

                # print('ret_list -->', ret_list)
                response.code = 200
                response.msg = '查询日志记录成功'
                response.data = ret_list

            return JsonResponse(response.__dict__)

        # 雷达-人-详情
        elif oper_type == 'customer_detail':
            response = Response.ResponseObj()
            print('------ request.GET ----->>',request.GET)

            field_dict = {
                'customer_id': '',
                'user_id': '',
                'create_date__gte' : '',
                # 'create_date__lt' : ''
            }

            customer_id = request.GET.get('customer_id')
            q = conditionCom(request, field_dict)

            create_date__gte = request.GET.get('create_date__gte')
            create_date__lt = request.GET.get('create_date__lt')

            if not create_date__gte:
                now_time = datetime.now()
                create_date__gte = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                q.add(Q(**{'create_date__gte': create_date__gte}), Q.AND)

            if create_date__lt:
                stop_time = (datetime.strptime(create_date__lt, '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")
                q.add(Q(**{'create_date__lt': stop_time}), Q.AND)

            # print('----- 没毛病 customer_detail q --->>',q)
            objs = models.zgld_accesslog.objects.select_related('user','customer').filter(q).values('customer_id', 'action').annotate(Count('action'))
            # print('--- 没毛病 customer_detail objs---->>',list(objs))
            ret_data = []
            action_dict = {}
            for i in models.zgld_accesslog.action_choices:
                action_dict[i[0]] = i[1]


            temp_dict = {}
            for obj in objs:
                print('obj -->', obj)
                customer_id = obj['customer_id']
                action_count = obj['action__count']

                action = obj['action']
                if customer_id in temp_dict:
                    temp_dict[customer_id]['totalCount'] += action_count
                    temp_dict[customer_id]['detail'].append({
                        "count": action_count,
                        "name": action_dict[action],
                        "action": action,
                    })
                else:
                    temp_dict[customer_id] = {
                        "totalCount": action_count,
                        "customer_id": customer_id,
                        "detail": [
                            {
                                "count": action_count,
                                "name": action_dict[action],
                                "action": action,
                            }
                        ]
                    }


            ret_data.append(temp_dict[customer_id])

            response.code = 200
            response.msg = '查询日志记录成功'
            response.data = ret_data

            return JsonResponse(response.__dict__)

        # 雷达--时间--统计数据
        elif oper_type =='time_data':
            data_type= request.GET.get('data_type')

            if data_type:
                data = follow_up_data(user_id, request, data_type)
                response.code = data.code
                response.msg = data.msg
                response.data = data.data
                response.note = data.note
            else:
                response_data = follow_up_data(user_id, request)  # 统计数据
                response.code = response_data.code
                response.msg = response_data.msg
                response.data = {
                    'click_dialog_num': response_data.data.get('click_dialog_num'),
                    'make_phone_call_count': response_data.data.get('make_phone_call_count'),
                    'if_article_conditions': response_data.data.get('if_article_conditions'),
                }
                response.note = {
                    'click_dialog_num': '点击对话框次数',
                    'make_phone_call_count': '拨打电话次数',
                    'if_article_conditions': '满足条件查询数量',
                }
        return JsonResponse(response.__dict__)
