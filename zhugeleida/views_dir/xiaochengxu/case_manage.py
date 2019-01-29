from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.case_manage_verify import SetFocusGetRedPacketForm, CaseAddForm, CaseSelectForm, CaseUpdateForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm

import json,datetime
from django.db.models import Q,F, Sum, Count

@csrf_exempt
@account.is_token(models.zgld_customer)
def case_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        # 查询案例
        if oper_type == 'case_list':

            print('request.GET----->', request.GET)

            forms_obj = CaseSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                user_id = request.GET.get('user_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-update_date')

                ## 搜索条件
                search_tag_id = request.GET.get('search_tag_id')  #
                case_id = request.GET.get('case_id')  #
                search_activity_status = request.GET.get('status')  #
                customer_name = request.GET.get('customer_name')  #


                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))

                if customer_name:
                    q1.children.append(('customer_name__contains', customer_name))

                if case_id:
                    q1.children.append(('id', case_id))

                # now_date_time = datetime.datetime.now()
                if search_activity_status:
                    q1.children.append(('status', search_activity_status))  #

                if search_tag_id:
                    tag_ids_list = []
                    tag_ids_list.append(int(search_tag_id))
                    q1.children.append(('tags__in', tag_ids_list))  #



                    ## 记录热门搜索的想项目 和 历史搜索记录
                    if search_tag_id:

                        _case_objs = models.zgld_case_tag.objects.filter(id=search_tag_id)
                        if _case_objs:
                            tag_name = _case_objs[0].name
                            _case_objs.update(
                                search_amount=F('search_amount') + 1
                            )

                            customer_objs = models.zgld_customer.objects.filter(id=user_id)
                            if customer_objs:
                                _history_tags_record =  customer_objs[0].history_tags_record
                                history_tags_record = json.loads(_history_tags_record)
                                history_tags_record.append( {
                                    'tag_id': search_tag_id,
                                    'tag_name' : tag_name
                                })

                                customer_objs.update(
                                    history_tags_record=json.dumps(history_tags_record)
                                )


                print('-----q1---->>', q1)
                objs = models.zgld_case.objects.select_related('company').filter(q1).order_by(order).exclude(status=3)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if objs:

                    for obj in objs:
                        status = obj.status
                        status_text = obj.get_status_display()
                        cover_picture = obj.cover_picture
                        if cover_picture:
                            cover_picture =  json.loads(cover_picture)

                        case_id = obj.case_id

                        ## 查找出最新更新的日记
                        diary_objs = models.zgld_diary.objects.filter(case_id=case_id).order_by('-create_date')
                        if diary_objs:
                            diary_obj = diary_objs[0]
                            title = diary_obj.title

                        ret_data.append({
                            'case_id': case_id,
                            'company_id': obj.company_id,
                            'customer_name': obj.customer_name,
                            'headimgurl': obj.headimgurl,
                            'cover_picture' : cover_picture,

                            'status': status,
                            'status_text': status_text,

                            'update_date': obj.update_date.strftime('%Y-%m-%d %H:%M:%S') if obj.update_date else '',
                            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
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



    return JsonResponse(response.__dict__)


