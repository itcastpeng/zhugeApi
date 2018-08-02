
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.company_verify import CompanyAddForm, CompanyUpdateForm, \
    CompanySelectForm,AgentAddForm,TongxunluAddForm
import time
import datetime
import json

from publicFunc.condition_com import conditionCom
from zhugeleida.public.condition_com  import conditionCom,validate_agent,datetime_offset_by_month,validate_tongxunlu
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def company(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
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

            data = request.GET.copy()
            q = conditionCom(data, field_dict)
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
                    'name': obj.name,
                    'company_id': obj.id,
                    'charging_start_time': obj.charging_start_time,
                    'open_length_time': obj.open_length_time,
                    'mingpian_available_num': obj.mingpian_available_num ,
                    'corp_id': obj.corp_id,
                    'tongxunlu_secret': obj.tongxunlu_secret,
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
@account.is_token(models.zgld_userprofile)
def author_status(request,oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        if oper_type == "author_status":
            company_id = request.GET.get('company_id')

            company_objs = models.zgld_company.objects.filter(id=company_id)

            # 获取所有数据
            ret_data = []
            # 获取第几页的数据
            if company_objs:
                is_validate = company_objs[0].is_validate

                ret_data.append({
                    'name' : '通讯录',
                    'is_validate': is_validate,

                })

                for app_name in ["AI雷达","Boss雷达"]:
                    app_objs  = company_objs[0].zgld_app_set.filter(company_id=company_id,name=app_name)
                    if app_objs:
                        ret_data.append({
                            'name': app_name,
                            'is_validate': is_validate,
                            'create_date': company_objs[0].create_date,
                        })
                    else:
                        ret_data.append({
                            'name': app_name,
                            'is_validate': False,
                            'create_date': company_objs[0].create_date,
                        })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,

                }
            else:
                response.code = 400
                response.msg = "公司不存在"

    return JsonResponse(response.__dict__)




@csrf_exempt
@account.is_token(models.zgld_userprofile)
def company_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add_company":
            company_data = {
                'name' : request.POST.get('name'),
                'charging_start_time' : request.POST.get('charging_start_time'),
                'open_length_time' : request.POST.get('open_length_time'),
                'mingpian_available_num': request.POST.get('mingpian_available_num').strip()

            }
            forms_obj = CompanyAddForm(company_data)
            if forms_obj.is_valid():

                charging_start_time = str(forms_obj.cleaned_data.get('charging_start_time'))
                open_length_time = forms_obj.cleaned_data.get('open_length_time')

                account_expired_time = datetime.datetime.now()
                if open_length_time == 1: # (1, "一个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time,1)
                elif   open_length_time == 2:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time,3)
                elif open_length_time == 3:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 6)
                elif open_length_time == 4:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 12)
                elif open_length_time == 5:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 24)

                company_data = {
                    'name': request.POST.get('name'),
                    'charging_start_time': charging_start_time,  #开始付费时间
                    'open_length_time': open_length_time,        #开通时长
                    'mingpian_available_num':  request.POST.get('mingpian_available_num'),
                    'account_expired_time' : account_expired_time, #账户过期时间
                    'remarks' : request.POST.get('remarks')
                }

                models.zgld_company.objects.create(**company_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update_company":

            company_data = {
                'company_id': o_id,
                'name': request.POST.get('name'),
                'charging_start_time': request.POST.get('charging_start_time'),
                'open_length_time': request.POST.get('open_length_time'),
                'mingpian_available_num': request.POST.get('mingpian_available_num').strip()
            }
            forms_obj = CompanyUpdateForm(company_data)
            if forms_obj.is_valid():

                charging_start_time = str(forms_obj.cleaned_data.get('charging_start_time'))
                open_length_time = forms_obj.cleaned_data.get('open_length_time')

                account_expired_time = datetime.datetime.now()
                if open_length_time == 1:  # (1, "一个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 1)
                elif open_length_time == 2:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 3)
                elif open_length_time == 3:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 6)
                elif open_length_time == 4:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 12)
                elif open_length_time == 5:  # (2, "三个月"),
                    charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                    account_expired_time = datetime_offset_by_month(charging_start_time, 24)

                company_data = {
                    'name': request.POST.get('name'),
                    'charging_start_time': charging_start_time,  # 开始付费时间
                    'open_length_time': open_length_time,        # 开通时长
                    'mingpian_available_num': request.POST.get('mingpian_available_num'),
                    'account_expired_time': account_expired_time,  # 账户过期时间
                    'remarks': request.POST.get('remarks')
                }

                company_id = forms_obj.cleaned_data.get('company_id')
                company_objs = models.zgld_company.objects.filter(
                    id=company_id
                )
                if company_objs:
                    company_objs.update(**company_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update_agent":  #雷达AI APP秘钥添加。
            agent_data = {
                'company_id': o_id,
                'name' : request.POST.get('name').strip(), #应用的名字
                'agent_id': request.POST.get('agent_id').strip(),
                'app_secret': request.POST.get('app_secret').strip()
            }
            forms_obj = AgentAddForm(agent_data)

            if forms_obj.is_valid():

                company_id =  forms_obj.cleaned_data.get('company_id')
                name =  forms_obj.cleaned_data.get('name')
                agent_id =  forms_obj.cleaned_data.get('agent_id')
                app_secret =  forms_obj.cleaned_data.get('app_secret')

                corp_id =  models.zgld_company.objects.get(id=company_id).corp_id
                if not corp_id:
                    response.code = 400
                    response.msg = "请您先填写企业微信corp_id"
                    return JsonResponse(response.__dict__)

                data = {
                    'corp_id': corp_id,
                    'app_secret' : app_secret
                }

                result_validate = validate_agent(data)
                is_validate = False
                if result_validate.code != 0:
                    return JsonResponse(result_validate.__dict__)
                else:
                    is_validate = True

                objs = models.zgld_app.objects.filter(name=name,company_id=company_id)
                if objs:
                    objs.update(
                        is_validate = is_validate,
                        agent_id = agent_id,
                        app_secret = app_secret
                    )
                else:
                    models.zgld_app.objects.create(
                        is_validate = is_validate,
                        name=name,
                        agent_id=agent_id,
                        app_secret= app_secret,
                        company_id = company_id
                    )

                response.code = 200
                response.msg = "保存成功"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update_tongxunlu":
            company_data = {
                'company_id': o_id,
                'corp_id': request.POST.get('corp_id').strip(),
                'tongxunlu_secret': request.POST.get('tongxunlu_secret').strip()
            }

            forms_obj = TongxunluAddForm(company_data)
            if forms_obj.is_valid():

                company_id  =  forms_obj.cleaned_data.get('company_id')
                corp_id =  forms_obj.cleaned_data.get('corp_id')
                tongxunlu_secret =  forms_obj.cleaned_data.get('tongxunlu_secret')

                data = {
                    'corp_id': corp_id,
                    'tongxunlu_secret': tongxunlu_secret,
                }
                result_validate = validate_tongxunlu(data)
                is_validate = False
                if result_validate.code != 0:
                    return JsonResponse(result_validate.__dict__)
                else:
                    is_validate = True

                obj=models.zgld_company.objects.filter(id=company_id)
                obj.update(
                    is_validate = is_validate,
                    corp_id = corp_id,
                    tongxunlu_secret = tongxunlu_secret
                )
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


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
