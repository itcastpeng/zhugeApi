from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.case_tag_verify import CaseTagAddForm,CaseTagUpdateAddForm,CaseTagSingleAddForm
import time
import datetime
import json
from django.db.models import Q
from publicFunc.condition_com import conditionCom

# 文章的标签查询
@csrf_exempt
@account.is_token(models.zgld_customer)
def case_tag(request,oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        if oper_type == 'case_list':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            name = request.GET.get('name')

            if name: # 搜索tag创建 搜索日志
                now = datetime.datetime.today()
                tag_objs = models.zgld_search_history.objects.filter(
                    company_id=user_id,
                    history_tag=name
                )
                if tag_objs:
                    tag_objs.update(create_date=now)
                else:
                    models.zgld_search_history.objects.create(
                        company_id=user_id,
                        history_tag=name
                    )

            field_dict = {
                'tag_id': '',
                'name': '__contains', #标签搜索
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            q.add(Q(**{'company_id': company_id}), Q.AND)

            tag_list = models.zgld_case_tag.objects.filter(q).values('id','name').order_by('-create_date')
            tag_data = list(tag_list)

            response.code = 200
            response.data = {
                'ret_data': tag_data,
                'data_count': tag_list.count(),
            }

        ##历史标签记录
        elif oper_type == 'history_case_list':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            field_dict = {
                'tag_id': '',
                'name': '__contains',  # 标签搜索
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            q.add(Q(**{'company_id': company_id}), Q.AND)
            q.add(Q(**{'id': user_id}), Q.AND)
            print(q)
            customer_objs = models.zgld_customer.objects.filter(q)
            if customer_objs:
                customer_obj = customer_objs[0]
                history_tags_record = customer_obj.history_tags_record
                if history_tags_record:
                    history_tags_record = json.loads(history_tags_record)

                response.code = 200
                response.data = {
                    'ret_data': history_tags_record[0:13],

                }
            else:
                response.code = 302
                response.msg = '暂无数据'

        # 热门搜索
        elif oper_type == 'top_search_tag_list':

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            field_dict = {
                'tag_id': '',
                'name': '__contains',  # 标签搜索
            }
            q = conditionCom(request, field_dict)
            q.add(Q(**{'company_id': company_id}), Q.AND)
            print('q -->', q)

            tag_list = models.zgld_case_tag.objects.filter(q).order_by('-search_amount').values('id','name')
            tag_data = list(tag_list)[0:13]

            response.code = 200
            response.data = {
                'ret_data': tag_data,
                'data_count': tag_list.count(),
            }


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


