
from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeproject.forms.role_verify import AddForm, UpdateForm, SelectForm
import time
import datetime
import json

from publickFunc.condition_com import conditionCom

@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def role_select(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')

            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.ProjectRole.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
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
                    'role_id': obj.id,
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
@account.is_token(models.ProjectUserProfile)
def role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            role_data = {
                'name' : request.POST.get('name'),
            }
            forms_obj = AddForm(role_data)
            if forms_obj.is_valid():
                print('forms_obj -->',forms_obj.cleaned_data)
                models.ProjectRole.objects.create(**forms_obj.cleaned_data)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间添加了一个角色'
                )
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                # print(forms_obj.errors)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间添加角色FORM验证失败'
                )
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.ProjectRole.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间删除了一个角色'
                )
            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间添删除角色失败ID不存在'
                )
                response.code = 302
                response.msg = '角色ID不存在'

        elif oper_type == "update":
            form_data = {
                'role_id': o_id,
                'name': request.POST.get('name'),
                'oper_user_id': request.GET.get('user_id'),
            }
            print(form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                name = forms_obj.cleaned_data['name']
                role_id = forms_obj.cleaned_data['role_id']
                print(role_id)
                role_objs = models.ProjectRole.objects.filter(
                    id=role_id
                )
                if role_objs:
                    role_objs.update(
                        name=name
                    )
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    user_id = request.GET.get('user_id')
                    models.ProjectWork_Log.objects.create(
                        name_id=user_id,
                        create_time=now_time,
                        remark='xx在xx时间修改角色'
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    user_id = request.GET.get('user_id')
                    models.ProjectWork_Log.objects.create(
                        name_id=user_id,
                        create_time=now_time,
                        remark='xx在xx时间修改角色失败ID不存在')
                    response.code = 302
                    response.msg = '角色ID不存在'
            else:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                user_id = request.GET.get('user_id')
                models.ProjectWork_Log.objects.create(
                    name_id=user_id,
                    create_time=now_time,
                    remark='xx在xx时间修改角色,FORM验证失败')
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        user_id = request.GET.get('user_id')
        models.ProjectWork_Log.objects.create(
            name_id=user_id,
            create_time=now_time,
            remark='xx在xx时间请求操作角色数据请求异常')
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
