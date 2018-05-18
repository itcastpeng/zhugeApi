from django.shortcuts import render
from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publickFunc.condition_com import conditionCom
from zhugeproject.forms.xuqiu_verify import AddForm, UpdateForm, SelectForm
import json


# cerf  token验证 需求展示模块
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def xuqiu_select(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_time')
            field_dict = {
                'id': '',
                'demand_user': '__contains',    # 需求人
                'is_system': '__contains',      # 属于哪个功能
                'create_time': '',
                'is_remark': '',                # 备注
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.ProjectNeed_Demand.objects.filter(q).order_by(order)
            count = objs.count()
            print('objs -- -  >',objs)
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            #
            # 返回的数据
            ret_data = []
            #
            for obj in objs:
                # print('oper_user_username -->', oper_user_username)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'demand_user': obj.demand_user.username,
                    'is_system': obj.is_system.name,
                    'create_time': obj.create_time,
                    'is_remark': obj.is_remark,
                })
                print('ret - - >',ret_data)
                #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改 需求表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def xuqiu_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'o_id': o_id,
                'demand_user_id': request.POST.get('demand_user_id'),
                'is_system_id': request.POST.get('is_system_id'),
                'is_remark': request.POST.get('is_remark')
            }
            #  创建 form验证 实例（参数默认转成字典）
            print('进入')
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print('验证通过')
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                add_xuqiu = models.ProjectNeed_Demand.objects.create(**forms_obj.cleaned_data)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                # print('xxxxxxxxxxxxx->>>>',user_id,now_time,add_xuqiu.id)
                models.ProjectDemand_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    is_system_id=add_xuqiu.id,
                    is_remark='xx在xx时间添加了一个需求',
                )
                response.code = 200
                response.msg = "添加成功"
            else:
                # print(forms_obj.errors)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectDemand_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    # is_system_id=add_xuqiu.id,
                    is_remark='xx在xx时间添加需求FORM验证失败',
                )
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            xuqiu_objs = models.ProjectNeed_Demand.objects.filter(id=o_id)
            if xuqiu_objs:
                # print('xuqiu_objs --- >',xuqiu_objs[0].id)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectDemand_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    is_system_id=xuqiu_objs[0].id,
                    is_remark='xx在xx时间删除需求成功',
                )
                xuqiu_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectDemand_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    # is_system_id=xuqiu_objs[0].id,
                    is_remark='xx在xx时间删除需求失败用户ID不存在',
                )
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            form_data = {
                'o_id': o_id,
                'demand_user_id': request.POST.get('demand_user_id'),
                'is_system_id': request.POST.get('is_system_id'),
                'is_remark':request.POST.get('is_remark')
            }
            print('form_data -  - -- > ',form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print('forms_obj.cleaned_data 0- - - > ',forms_obj.cleaned_data)
                demand_user_id = forms_obj.cleaned_data['demand_user_id']
                is_system_id = forms_obj.cleaned_data['is_system_id']
                is_remark = forms_obj.cleaned_data['is_remark']
                #  查询数据库  用户id
                user_obj = models.ProjectNeed_Demand.objects.filter(
                    id=o_id
                )
                print('------------->',demand_user_id,is_system_id)
                #  更新 数据
                if user_obj:
                    user_obj.update(
                        demand_user_id=demand_user_id,
                        is_system_id=is_system_id,
                        is_remark=is_remark
                    )
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    user_id = request.GET.get('user_id')
                    models.ProjectDemand_Log.objects.create(
                        name_id=user_id,
                        create_time=now_time,
                        # is_system_id=user_obj.id,
                        is_remark='xx在xx时间修改需求成功',
                    )
                    response.code = 200
                    response.msg = "修改成功"


                else:
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    user_id = request.GET.get('user_id')
                    models.ProjectDemand_Log.objects.create(
                        name_id=user_id,
                        create_time=now_time,
                        # is_system_id=user_obj.id,
                        is_remark='xx在xx时间修改需求失败ID不存在',
                    )
                    response.code = 303
                    response.msg = '修改ID不存在'

            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectDemand_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    # is_system_id=user_obj.id,
                    is_remark='xx在xx时间修改需求失败FORM验证失败',
                )

                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        user_id = request.GET.get('user_id')
        models.ProjectDemand_Log.objects.create(
            name_id=user_id,
            create_time=now_time,
            is_remark='xx在xx时间修改需求失败请求异常',
        )
        print("验证不通过")
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
