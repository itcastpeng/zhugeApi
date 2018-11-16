from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.action_verify import ActionSelectForm, ActionCountForm, ActionCustomerForm
from zhugeleida import models

from django.db.models import Count
from publicFunc.condition_com import conditionCom
from django.db.models import Q
from datetime import datetime, timedelta
import base64
import json

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

        # 根据时间查询 日志
        if oper_type == 'time':
            forms_obj = ActionSelectForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('user_id')
                customer_id = request.GET.get('customer_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'action': '',

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
                        print('----- 解密b64decode User_id username----->', username)
                    except Exception as e:
                        print('----- b64decode解密失败的 customer_id 是----->', obj.customer_id)
                        username = '客户ID%s' % (obj.customer_id)

                    ret_data.append({
                        'user_id': obj.user_id,
                        'customer_id': obj.customer_id,
                        'headimgurl': obj.customer.headimgurl,
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

        # 获取新的日志信息
        elif oper_type == 'get_new_log':
            forms_obj = ActionSelectForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()

                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'user_id': '',
                    'action': '',
                }

                q = conditionCom(request, field_dict)
                q.add(Q(**{'is_new_msg': True}), Q.AND)


                objs = models.zgld_accesslog.objects.select_related('user', 'customer').filter(q).order_by(order)
                count = objs.count()

                ret_data = []
                for obj in objs:

                    try:
                        username = base64.b64decode(obj.customer.username)
                        username = str(username, 'utf-8')
                        print('----- 解密b64decode 客户的username----->', username)
                    except Exception as e:
                        print('----- b64decode解密失败的 customer_id 是----->', obj.customer_id)
                        username = '客户ID%s' % (obj.customer_id)


                    ret_data.append({
                        'user_id': obj.user_id,
                        'customer_id': obj.customer_id,
                        'action' : obj.get_action_display(),
                        'log': username + obj.remark,
                        'create_date': obj.create_date,
                    })

                # print('----ret_data----->>', ret_data)
                objs.update(is_new_msg=False)
                response.code = 200
                response.msg = '查询日志记录成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

                return JsonResponse(response.__dict__)

        # 查询日志记录
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

        # 查询访问动能日志记录
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

        # 查询日志记录
        elif oper_type == 'customer_detail':
            response = Response.ResponseObj()
            field_dict = {
                'customer_id': '',
                'user_id': '',
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
                stop_time = (datetime.strptime(create_date__lt, '%Y-%m-%d') + timedelta(days=1)).strftime(
                    "%Y-%m-%d")
                q.add(Q(**{'create_date__lt': stop_time}), Q.AND)

            objs = models.zgld_accesslog.objects.select_related('user','customer').filter(q).values('customer_id', 'action').annotate(Count('action'))

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
