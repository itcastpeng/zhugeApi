from ribao import models
from publickFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ribao.forms.renwuguanli_verify import AddForm, UpdateForm, SelectForm
import json
from publickFunc.condition_com import conditionCom


@csrf_exempt
@account.is_token(models.RibaoUserProfile)
def renwuguanli(request):
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
                'oper_user__username': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.RibaoRole.objects.select_related('oper_user').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 获取所有数据
            ret_data = []
            # 获取第几页的数据
            for obj in objs:

                oper_user__username = ''
                if obj.oper_user:
                    oper_user__username = obj.oper_user.username

                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'role_id': obj.id,
                    'create_date': obj.create_date,
                    'oper_user__username': oper_user__username,
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
@account.is_token(models.RibaoUserProfile)
def renwuguanli_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            role_data = {
                'issuer': request.GET.get('user_id'),
                'task_name': request.POST.get('task_name'),
                'belog_task_id': request.POST.get('belog_task_id'),
                'director_id': request.POST.get('director_id'),
                'boor_urgent': request.POST.get('boor_urgent'),
            }
            print(role_data)
            forms_obj = AddForm(role_data)
            if forms_obj.is_valid():
                print(forms_obj.cleaned_data)
                models.RibaoTaskManage.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.RibaoTaskManage.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '角色ID不存在'

        elif oper_type == "update":
            form_data = {
                'task_name': request.POST.get('task_name'),
                'issuer': request.GET.get('user_id'),

            }
            print(form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                task_name = forms_obj.cleaned_data['task_name']
                role_id = forms_obj.cleaned_data['role_id']
                print(role_id)
                role_objs = models.RibaoTaskManage.objects.filter(
                    id=o_id
                )
                if role_objs:
                    role_objs.update(
                        name=task_name
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 302
                    response.msg = '角色ID不存在'
            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
