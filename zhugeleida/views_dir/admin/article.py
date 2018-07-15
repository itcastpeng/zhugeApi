
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.company_verify import CompanyAddForm, CompanyUpdateForm, CompanySelectForm
import time
import datetime
import json

from publicFunc.condition_com import conditionCom

@csrf_exempt
@account.is_token(models.zgld_userprofile)
def article(request,oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
            # 获取参数 页数 默认1

       if oper_type == 'myarticle_list':

            forms_obj = CompanySelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'name': '__contains',
                    'create_date': '',
                }

                q = conditionCom(request, field_dict)
                print('q -->', q )

                objs = models.zgld_company.objects.filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    print('current_page -->', current_page)
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 获取所有数据
                ret_data = []
                # 获取第几页的数据
                for obj in objs:

                    ret_data.append({
                        'id': obj.id,
                        'name': obj.name,
                        'company_id': obj.id,
                        'create_date': obj.create_date,
                        'corp_id': obj.corp_id,
                        'tongxunlu_secret': obj.tongxunlu_secret,

                    })
                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
            return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def company_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add":
            company_data = {
                'name' : request.POST.get('name'),
                'corp_id': request.POST.get('corp_id').strip(),
                'tongxunlu_secret': request.POST.get('tongxunlu_secret').strip()
            }
            forms_obj = CompanyAddForm(company_data)
            if forms_obj.is_valid():
                models.zgld_company.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('------delete o_id --------->>',o_id)
            company_objs = models.zgld_company.objects.filter(id=o_id)

            if company_objs:
                if company_objs[0].zgld_userprofile_set.all().count() == 0:
                   company_objs.delete()
                   response.code = 200
                   response.msg = "删除成功"
                else:
                    response.code = 303
                    response.msg = "该企业有关联用户,请转移用户后再试"
            else:
                response.code = 302
                response.msg = '公司ID不存在'

        elif oper_type == "update":
            form_data = {
                'company_id': o_id,
                'name': request.POST.get('name'),
                'corp_id': request.POST.get('corp_id').strip(),
                'tongxunlu_secret': request.POST.get('tongxunlu_secret').strip()

            }
            print('-----form_data------>',form_data)
            forms_obj = CompanyUpdateForm(form_data)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data->>',forms_obj.cleaned_data)
                name = forms_obj.cleaned_data['name']
                company_id = forms_obj.cleaned_data['company_id']
                corp_id = forms_obj.cleaned_data['corp_id']
                tongxunlu_secret = forms_obj.cleaned_data['tongxunlu_secret']

                print(company_id)
                company_objs = models.zgld_company.objects.filter(
                    id=company_id
                )
                if company_objs:
                    company_objs.update(
                        name=name,
                        corp_id=corp_id,
                        tongxunlu_secret=tongxunlu_secret,
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 302
                    response.msg = '公司ID不存在'
            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
