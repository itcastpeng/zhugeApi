from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.website_verify import WebsiteAddForm,WebsiteTemplateUpdateForm,WebsiteTemplateAddForm, DepartmentUpdateForm, DepartmentSelectForm
import json
from publicFunc.condition_com import conditionCom
import requests
from ..conf import *
from django.db.models import Q

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def website(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1   
        field_dict = {
            'id': '',
            'create_date': '',
        }
        company_id = request.GET.get('company_id')
        q = conditionCom(request, field_dict)
        q.add(Q(**{'id': company_id}), Q.AND)

        objs = models.zgld_company.objects.filter(q).order_by('-create_date')
        count = objs.count()


        # 获取所有数据
        ret_data = []
        # 获取第几页的数据
        for obj in objs:
            ret_data.append({
                'id': obj.id,
                'name': obj.name,
                'website_content': json.loads(obj.website_content),
                'create_date': obj.create_date,
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
@account.is_token(models.zgld_admin_userprofile)
def website_oper(request, oper_type,o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "edit":
            website_data = {
                'user_id': request.GET.get('user_id'),
                'company_id': o_id,
                'website_content': request.POST.get('website_content'),
            }

            forms_obj = WebsiteAddForm(website_data)

            if forms_obj.is_valid():
                company_id  =  forms_obj.cleaned_data.get('company_id')
                website_content = forms_obj.cleaned_data.get('website_content')
                obj = models.zgld_company.objects.get(id=company_id)
                obj.website_content = website_content
                obj.save()
                response.code = 200
                response.msg = "保存成功"


            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def website_template(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        field_dict = {
            'id': '',
            'name': '',
            'create_date': '',
        }
        # company_id = request.GET.get('company_id')
        q = conditionCom(request, field_dict)
        # q.add(Q(**{'id': company_id}), Q.AND)

        objs = models.zgld_website_template.objects.filter(q).order_by('-create_date')
        count = objs.count()


        # 获取所有数据
        ret_data = []
        # 获取第几页的数据
        for obj in objs:
            ret_data.append({
                'id': obj.id,
                'name': obj.name,
                'template_content': json.loads(obj.template_content),
                'create_date': obj.create_date,
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
@account.is_token(models.zgld_admin_userprofile)
def website_template_oper(request, oper_type,o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "update":
            template_data = {
                'user_id': request.GET.get('user_id'),
                'template_id': o_id,
                'name': request.POST.get('name'),
                'template_content': request.POST.get('template_content'),
            }

            forms_obj = WebsiteTemplateUpdateForm(template_data)

            if forms_obj.is_valid():
                template_id  =  forms_obj.cleaned_data.get('template_id')
                template_content = forms_obj.cleaned_data.get('template_content')
                name = forms_obj.cleaned_data.get('name')
                obj = models.zgld_website_template.objects.get(id=template_id)
                obj.name = name
                obj.template_content = template_content
                obj.save()
                response.code = 200
                response.msg = "保存成功"


            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        elif oper_type == "add":
            template_data = {
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'template_content': request.POST.get('template_content'),
            }

            forms_obj = WebsiteTemplateAddForm(template_data)

            if forms_obj.is_valid():
                template_content = forms_obj.cleaned_data.get('template_content')
                name = forms_obj.cleaned_data.get('name')
                obj = models.zgld_website_template.objects.create(
                    template_content = template_content,
                    name =name
                )
                response.code = 200
                response.msg = "保存成功"


            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'delete':
            template_id = o_id

            objs = models.zgld_website_template.objects.filter(id=template_id)

            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                # print("验证不通过")
                response.code = 301
                response.msg = '模板ID不存在'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
