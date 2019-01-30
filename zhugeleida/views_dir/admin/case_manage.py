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
from django.db.models import Q, Sum, Count

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def case_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        # 查询案例
        if oper_type == 'case_list':

            print('request.GET----->', request.GET)

            forms_obj = CaseSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-update_date')

                ## 搜索条件
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

                        ret_data.append({
                            'case_id': obj.id,
                            'case_name' : obj.case_name,
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


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def case_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 删除-案例
        if oper_type == "delete":

            company_id = request.GET.get('company_id')
            objs = models.zgld_case.objects.filter(id=o_id,company_id=company_id)

            if objs:
                objs.update(
                    status=3
                )
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '案例不存在'

        # 修改-案例
        elif oper_type == 'update':

            case_id = o_id
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            case_name = request.POST.get('case_name')
            customer_name = request.POST.get('customer_name')
            headimgurl = request.POST.get('headimgurl')
            status = request.POST.get('status')
            cover_picture = request.POST.get('cover_picture')  # 文章ID


            form_data = {
                'case_id' : case_id,
                'case_name' : case_name,
                'company_id': company_id,
                'customer_name': customer_name,  # 活动名称
                'headimgurl': headimgurl,  # 文章ID
                'status': status,
            }

            forms_obj = CaseUpdateForm(form_data)
            if forms_obj.is_valid():

                objs = models.zgld_case.objects.filter(company_id=company_id,id=case_id)
                if objs:
                    objs.update(
                        user_id=user_id,
                        case_name=case_name,
                        customer_name=customer_name.strip(),
                        headimgurl=headimgurl,
                        cover_picture=cover_picture,
                        status=status
                    )

                    obj =objs[0]
                    tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                    if tags_id_list:
                        obj.tags = tags_id_list

                    response.code = 200
                    response.msg = "修改成功"

                else:
                    response.code = 302
                    response.msg = "案例不存在"
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 增加-案例
        elif oper_type == "add":


            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            case_name = request.POST.get('case_name')
            customer_name = request.POST.get('customer_name')

            headimgurl = request.POST.get('headimgurl')
            status  = request.POST.get('status')
            cover_picture = request.POST.get('cover_picture')  # 文章ID

            form_data = {
                'case_name' : case_name,
                'company_id': company_id,
                'customer_name': customer_name,  # 活动名称
                'headimgurl': headimgurl,  # 文章ID
                'status': status,

            }

            forms_obj = CaseAddForm(form_data)
            if forms_obj.is_valid():

                obj = models.zgld_case.objects.create(
                    user_id=user_id,
                    case_name=case_name,
                    company_id=company_id,
                    customer_name=customer_name.strip(),
                    headimgurl=headimgurl,
                    cover_picture=cover_picture,
                    status=status
                )

                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    obj.tags = tags_id_list

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)
