from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.action_verify import ActionSelectForm, ActionCountForm,ActionCustomerForm
from zhugeleida import models

from django.db.models import Count
from publicFunc.condition_com import conditionCom
from django.db.models import Q


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def action(request, oper_type):
    '''
     分页获取访问的全部日志信息
    :param request:
    :return:
    '''
    if request.method == 'GET':
        if oper_type == 'time':
            forms_obj = ActionSelectForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('user_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'name': '__contains',
                }
                q = conditionCom(request, field_dict)
                print('q -->', q)

                objs = models.zgld_accesslog.objects.select_related('user', 'customer').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []


                for obj in objs:
                    ret_data.append({
                        'user_id': obj.user_id,
                        'customer_id': obj.customer_id,
                        'headimgurl': obj.customer.headimgurl,
                        'log': obj.customer.username + obj.remark,
                        'create_date': obj.create_date,
                    })

                if current_page == 1:
                    count_action_data = models.zgld_accesslog.objects.filter(user_id=user_id).values('action').annotate(
                        Count('action'))
                    print('count_action_data -->', count_action_data)

                    customer_action_data = models.zgld_accesslog.objects.filter(user_id=user_id).values('action',
                                                                                                        'customer_id',
                                                                                                        'customer__username').annotate(
                        Count('action'))
                    print('customer_action_data -->', customer_action_data)


                # {
                #     'keyvalue': {
                #         1: "官网",
                #
                #     },
                #     'data': {
                #         1:
                #     }
                # }

                response.code = 200
                response.msg = '查询日志记录成功'

                # {
                #     'time_action_list': ret_time_list,
                #     'count_action_list': ret_count_list,
                #     'customer_action_list': ret_customer_list,
                # }
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

                return JsonResponse(response.__dict__)

        elif oper_type == 'count':
            forms_obj = ActionCountForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()

                user_id = request.GET.get('user_id')

                field_dict = {
                    'id': '',
                    'user_id': '',
                    'create_date__gt': '',
                    'create_date__lt': '',
                }
                q = conditionCom(request, field_dict)

                objs = models.zgld_accesslog.objects.filter(q).values('action').annotate(
                    Count('action'))
                print('count_action_data -->', objs)

                detail_dict = {}
                for obj in objs:
                    print('---------->>', obj['action'], obj['action__count'])
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

        elif oper_type == 'customer':
            forms_obj = ActionCustomerForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('user_id')
                ret_data = []

                # current_page = forms_obj.cleaned_data['current_page']
                # length = forms_obj.cleaned_data['length']
                field_dict = {
                    'id': '',
                    'user_id': '',
                    'name': '__contains',
                    'create_date__gt': '',
                    'create_date__lt': '',
                }
                q = conditionCom(request, field_dict)

                objs = models.zgld_accesslog.objects.filter(q).values('action','customer__headimgurl','customer_id','customer__username').annotate(Count('action'))
                print('customer_action_data -->', objs)

                # if length != 0:
                #     start_line = (current_page - 1) * length
                #     stop_line = start_line + length
                #     objs = objs[start_line: stop_line]


                customer_id_list = []
                customer_username = ''
                customer__headimgurl = ''
                detail_dict = {}
                customer_id = ''
                total_num = 0
                for obj in objs:
                    print('---------->>', obj['action'], obj['action__count'])
                    customer_id_list.append(obj['customer_id'])

                ids = list(set(customer_id_list))
                print('------>>',ids)
                for c_id in  ids:
                    for obj in objs:

                        if obj['customer_id'] == c_id:
                            total_num  += obj['action__count']
                            customer_id = c_id
                            customer_username = obj['customer__username']
                            customer__headimgurl = obj['customer__headimgurl']
                            detail_dict[ obj.get('action')] = obj['action__count']

                    ret_data.append({
                                'totalCount': total_num,
                                'customer_id': customer_id,
                                'customer__username': customer_username ,
                                'user_id': user_id,
                                'headimgurl': customer__headimgurl,
                                'detail': detail_dict
                    })
                    total_num = 0

                response.code = 200
                response.msg = '查询日志记录成功'
                response.data = ret_data

                return JsonResponse(response.__dict__)

