from django.shortcuts import render
from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeproject.forms.gongneng_verify import AddForm, UpdateForm, SelectForm
from publickFunc.condition_com import conditionCom
import json
import datetime


# 数据的展示
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def gongneng_select(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            print('验证成功')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            order = request.GET.get('order', 'id')

            field_dict = {
                'item_name':'',
                'create_time':'',
                'oper_user':'__contains',
                'is_function':'',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            # 获取所有数据
            objs = models.ProjectFunction.objects.select_related('oper_user','item_name').filter(
                q).order_by(order)
            count = objs.count()
            print('objs- --  ->',objs)
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []

            # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'item_name': obj.item_name.item_name,
                    'create_time': obj.create_time,
                    'oper_user__username': obj.oper_user.username,
                    'is_function': obj.is_function,
                })

            response.code = 200
            response.data = {
                'ret_data': ret_data,
                'data_count': count
            }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


#  增删改
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def gongneng_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            print('开始入库')
            forms_obj = AddForm(request.POST)
            if forms_obj.is_valid():
                print('forms_obj.forms_obj -->',forms_obj.cleaned_data)
                models.ProjectFunction.objects.create(**forms_obj.cleaned_data)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间增加了一个功能'
                )
                response.code = 200
                response.msg = "添加成功"
            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间FORM验证失败'
                )
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('o_id -->', o_id)
            objs = models.ProjectFunction.objects.filter(id=o_id)
            if objs:
                objs.delete()
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间删除一个功能'
                )
                response.code = 200
                response.msg = "删除成功"
            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间删除不存在功能'
                )
                response.code = 302
                response.msg = '功能不存在'

        elif oper_type == "update":
            print('进入update')
            form_data = {
                'tid': o_id,
                'item_name_id':request.POST.get('item_name_id'),
            }
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print('form验证')
                objs = models.ProjectFunction.objects.filter(id=o_id)
                if objs:
                    objs.update(
                        item_name_id = forms_obj.cleaned_data['item_name_id'],
                    )
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    user_id = request.GET.get('user_id')
                    models.ProjectWork_Log.objects.create(
                        name_id=user_id,
                        create_time=now_time,
                        remark='xx在xx时间修改一个项目'
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    user_id = request.GET.get('user_id')
                    models.ProjectWork_Log.objects.create(
                        name_id=user_id,
                        create_time=now_time,
                        remark='xx在xx时间修改功能ID不存在'
                    )
                    response.code = 302
                    response.msg = "操作id不存在"
            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间修改功能FORM验证失败'
                )
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        user_id = request.GET.get('user_id')
        models.ProjectWork_Log.objects.create(
            name_id=user_id,
            create_time=now_time,
            remark='xx在xx时间请求操作功能异常'
        )
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
