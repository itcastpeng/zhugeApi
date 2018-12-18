
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.company_verify import CompanyAddForm, CompanyUpdateForm, \
    CompanySelectForm,AgentAddForm,TongxunluAddForm,ThreeServiceAddForm

import datetime
import json
from publicFunc.condition_com import conditionCom
from zhugeleida.public.condition_com  import conditionCom,validate_agent,datetime_offset_by_month,validate_tongxunlu

from django.db.models import Q, F
# 查询公司
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
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
                # print('---- obj.account_expired_time --->>',obj.account_expired_time,'|',datetime.datetime.now())

                available_days = (obj.account_expired_time - datetime.datetime.now()).days  # 还剩多天可以用
                used_days = (datetime.datetime.now() - obj.create_date).days  # 用户使用了多少天了

                customer_num = models.zgld_user_customer_belonger.objects.filter(
                    user__company_id=obj.id).count()  # 已获取客户数
                user_count = models.zgld_userprofile.objects.filter(company_id=obj.id).count()  # # 员工总数

                ret_data.append({
                    'name': obj.name,
                    'company_id': obj.id,
                    'charging_start_time': obj.charging_start_time.strftime('%Y-%m-%d'),
                    'open_length_time': obj.open_length_time,
                    'mingpian_available_num': obj.mingpian_available_num ,

                    'remarks':  obj.remarks,
                    # 'corp_id': obj.corp_id,
                    # 'tongxunlu_secret': obj.tongxunlu_secret,
                    'create_date': obj.create_date.strftime('%Y-%m-%d'),
                    'is_show_jszc': obj.is_show_jszc,
                    'is_show_jszc_text': obj.get_is_show_jszc_display(),
                    'user_count': user_count,        # 用户总数
                    'customer_num': customer_num,    # 拥有的客户数量
                    'available_days': available_days, #剩余天数
                    'used_days': used_days,
                    'account_expired_time': obj.account_expired_time.strftime('%Y-%m-%d'),


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


# 企业微信展示授权信息
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
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
                app_objs = company_objs[0].zgld_app_set.filter(company_id=company_id, app_type=3)

                is_validate = False
                if app_objs: # 通讯录
                    is_validate =  app_objs[0].is_validate

                ret_data.append({
                    'name' : '通讯录',
                    'is_validate': is_validate,
                    'app_type': 3
                })

                name = ''
                # app_objs = list(company_objs[0].zgld_app_set.filter(company_id=company_id).values('id','name','is_validate','app_type'))
                app_objs = company_objs[0].zgld_app_set.filter(company_id=company_id,app_type=1)

                if app_objs: # AI雷达
                    name = app_objs[0].name
                    is_validate =  app_objs[0].is_validate

                ret_data.append({
                    'name': name,
                    'is_validate': is_validate,
                    'app_type': 1
                })

                name = ''
                is_validate = False
                app_objs = company_objs[0].zgld_app_set.filter(company_id=company_id, app_type=2)
                if app_objs:  # Boss雷达
                    name = app_objs[0].name
                    is_validate = app_objs[0].is_validate

                ret_data.append({
                    'name': name,
                    'is_validate': is_validate,
                    'app_type': 2
                })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,

                }
            else:
                response.code = 400
                response.msg = "公司不存在"


        elif oper_type == "query_service_settings":
            type = request.GET.get('type')
            # q = Q()
            #
            # if type:
            #     q.add(Q(**{'three_services_type': type}), Q.AND)


            # 获取所有数据
            ret_data = []

            for type in [1,2,3]:
                name = ''
                if type == 1:
                    name = '企业微信第三方服务商'
                elif type == 2:
                    name = '公众号第三方平台'
                elif type == 3:
                    name = '小程序第三方平台'

                objs = models.zgld_three_service_setting.objects.filter(three_services_type=type)

                status = 0
                status_text = '未通过'
                if objs:
                    status_text = objs[0].get_status_display()
                    status =  objs[0].status

                ret_data.append({
                    'type' : type, # 类型
                    'name': name,  #
                    'status' : status,           # 状态为1,代表通过。0 代表 未1通过
                    'status_text' : status_text   # 状态为1,代表通过。0 代表 未1通过
                })

            response.code = 200
            response.data = {
                'ret_data': ret_data,
                'data_count': 3
            }

        return JsonResponse(response.__dict__)


    elif request.method == "POST":


        if oper_type == "edit_service_setting":

            config = request.POST.get('config')
            type =  request.POST.get('type')

            _data = {
                'config': config,
                'type' : type
            }

            forms_obj = ThreeServiceAddForm(_data)
            if forms_obj.is_valid():
                objs = models.zgld_three_service_setting.objects.filter(three_services_type=type)

                if objs:
                    objs.update(
                        config=config,
                        status=1
                    )
                else:
                    models.zgld_three_service_setting.objects.create(
                        three_services_type=type,
                        config=config,
                        status=1
                    )
                response.code = 200
                response.msg = '添加成功'

            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


# 公司操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def company_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加公司
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
                # if open_length_time == 1: # (1, "一个月"),
                charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                account_expired_time = datetime_offset_by_month(charging_start_time,open_length_time)

                # elif   open_length_time == 2:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time,2)
                # elif open_length_time == 3:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 3)
                #
                # elif open_length_time == 4:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 12)
                # elif open_length_time == 5:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 24)

                company_data = {
                    'name': request.POST.get('name'),
                    'charging_start_time': charging_start_time,    #开始付费时间
                    'open_length_time': open_length_time,          #开通时长
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

        # 修改公司
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


                charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                account_expired_time = datetime_offset_by_month(charging_start_time, open_length_time)


                # if open_length_time == 1:  # (1, "一个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 1)
                # elif open_length_time == 2:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 2)
                # elif open_length_time == 3:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 3)
                #
                # elif open_length_time == 4:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 12)
                # elif open_length_time == 5:  # (2, "三个月"),
                #     charging_start_time = datetime.datetime.strptime(charging_start_time, '%Y-%m-%d')
                #     account_expired_time = datetime_offset_by_month(charging_start_time, 24)

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

        # 雷达AI APP秘钥添加。
        elif oper_type == "update_agent":
            agent_data = {
                'company_id': o_id,
                # 'name' : request.POST.get('name').strip(), #应用的名字
                'agent_id': request.POST.get('agent_id').strip(),
                'app_secret': request.POST.get('app_secret').strip(),
                'app_type': request.POST.get('app_type').strip()
            }
            forms_obj = AgentAddForm(agent_data)

            if forms_obj.is_valid():

                company_id =  forms_obj.cleaned_data.get('company_id')
                # name =  forms_obj.cleaned_data.get('name')
                app_type =  forms_obj.cleaned_data.get('app_type') #  (1,'AI雷达'),  (2,'Boss雷达')
                agent_id =  forms_obj.cleaned_data.get('agent_id')
                app_secret =  forms_obj.cleaned_data.get('app_secret')

                corp_id =  models.zgld_company.objects.get(id=company_id).corp_id
                if not corp_id:
                    response.code = 400
                    response.msg = "请您先填写企业微信corp_id"
                    return JsonResponse(response.__dict__)

                data = {
                    'company_id': company_id,
                    'corp_id': corp_id,  #企业应用id
                    'app_secret' : app_secret,
                    'agent_id' : agent_id,
                    'app_type' : app_type
                }

                result_validate = validate_agent(data)
                is_validate = False
                if result_validate.code != 0:
                    return JsonResponse(result_validate.__dict__)

                else:
                    print('-----result_validate.data--------->>',result_validate.data)
                    is_validate = True
                    name = result_validate.data.get('name')
                    agent_id = result_validate.data.get('agentid')

                objs = models.zgld_app.objects.filter(app_type=app_type,company_id=company_id)
                if objs:
                    objs.update(
                        name=name,
                        app_type=app_type,
                        is_validate = is_validate,
                        agent_id = agent_id,
                        app_secret = app_secret
                    )
                else:
                    models.zgld_app.objects.create(
                        is_validate = is_validate,
                        name=name,
                        app_type=app_type,
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

        # 修改通讯录
        elif oper_type == "update_tongxunlu":
            company_data = {
                'company_id': o_id,
                'corp_id': request.POST.get('corp_id').strip(),
                'tongxunlu_secret': request.POST.get('tongxunlu_secret').strip(),
                'weChatQrCode': request.POST.get('weChatQrCode')
            }

            forms_obj = TongxunluAddForm(company_data)
            if forms_obj.is_valid():

                company_id  =  forms_obj.cleaned_data.get('company_id')
                corp_id =  forms_obj.cleaned_data.get('corp_id')
                tongxunlu_secret =  forms_obj.cleaned_data.get('tongxunlu_secret')
                weChatQrCode =  forms_obj.cleaned_data.get('weChatQrCode')

                data = {
                    'corp_id': corp_id,
                    'tongxunlu_secret': tongxunlu_secret,
                    'company_id': company_id,

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
                    tongxunlu_secret = tongxunlu_secret,
                    weChatQrCode=weChatQrCode
                )
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除公司
        elif oper_type == "delete":
            print('------delete o_id --------->>',o_id)
            company_objs = models.zgld_company.objects.filter(id=o_id)

            if company_objs:
                # if company_objs[0].zgld_admin_userprofile_set.all().count() == 0:
                   company_objs.delete()

                   company_objs[0].zgld_admin_userprofile_set.all().delete()
                   company_objs[0].zgld_userprofile_set.all().delete()
                   company_objs[0].zgld_customer_set.all().delete()
                   company_objs[0].zgld_gongzhonghao_app_set.all().delete()
                   company_objs[0].zgld_xiaochengxu_app_set.all().delete()


                   response.code = 200
                   response.msg = "删除成功"

                # else:
                #     response.code = 303
                #     response.msg = "该企业有关联用户,请转移用户后再试"

            else:
                response.code = 302
                response.msg = '公司ID不存在'

        # 修改是否展示 产品还是商城
        elif oper_type == 'change_shopping_type':

            shopping_type = request.POST.get('shopping_type')

            if  shopping_type:
                company_objs = models.zgld_company.objects.filter(id=o_id)

                if company_objs:
                    company_objs.update(
                        shopping_type=shopping_type
                    )
                    response.code = 200
                    response.msg = "设置成功"

                else:
                    response.code = 302
                    response.msg = '公司不存在'
            else:
                response.code = 303
                response.msg = '购物类型不能为空'

        elif oper_type == "is_show_technical_support":

            status = request.POST.get('status')  # (1, "启用"),  (2, "未启用"),
            user_id = request.GET.get('user_id')

            objs = models.zgld_company.objects.filter(id=o_id)

            if objs:
                if status:
                    objs.update(is_show_jszc=status)
                    response.code = 200
                    response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "用户不存在"



    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
