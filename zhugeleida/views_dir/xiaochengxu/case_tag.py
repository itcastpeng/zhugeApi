from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import datetime
from django.db.models import Q
from publicFunc.condition_com import conditionCom
from zhugeleida.views_dir.xiaochengxu.case_manage import case_manage_public


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
            name__contains = request.GET.get('name__contains')

            if name__contains: # 搜索tag创建 搜索日志
                print('name__contains--> ', name__contains, company_id)
                if len(name__contains) > 60:
                    response.code = 301
                    response.msg = '搜索过长'
                    return JsonResponse(response.__dict__)

                now = datetime.datetime.today()
                tag_objs = models.zgld_search_history.objects.filter(
                    company_id=company_id,
                    user_customer_belonger_id=user_id,
                    history_tag=name__contains,
                )
                if tag_objs:
                    tag_objs.update(create_date=now)
                else:
                    models.zgld_search_history.objects.create(
                        user_customer_belonger_id=user_id,
                        history_tag=name__contains,
                        company_id=company_id,
                    )

            field_dict = {
                'tag_id': '',
                'name__contains': '', #标签搜索
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            q.add(Q(**{'company_id': company_id}), Q.AND)

            tag_list = models.zgld_case_tag.objects.filter(q).values('id','name').order_by('-create_date')
            tag_data = list(tag_list)
            search_tag_list = []
            for tag_id in tag_list:
                search_tag_list.append(tag_id['id'])

            response_data = case_manage_public(request, is_search=1, tag_list=search_tag_list) # 搜索出来所有数据
            response.code = 200
            response.data = {
                'data_list': response_data.data,
                'ret_data': tag_data,
                'data_count': tag_list.count(),
            }

        ##历史标签记录
        elif oper_type == 'history_case_list':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            field_dict = {
                'history_tag': '__contains',  # 标签搜索
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.zgld_search_history.objects.filter(
                company_id=company_id,
                user_customer_belonger_id=user_id
            ).order_by('-create_date')

            data_list = []
            if objs:
                objs = objs[0:13]
                for obj in objs:
                    data_list.append(obj.history_tag)

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'data_list': data_list
            }
            response.note = {

            }

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


