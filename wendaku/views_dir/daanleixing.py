from django.shortcuts import render
from wendaku import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from wendaku.forms.daan_leixing_verify import DaanAddForm, DaanUpdateForm, DaanSelectForm
from publicFunc.condition_com import conditionCom
import json


@csrf_exempt
@account.is_token(models.UserProfile)
def daanleixing(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = DaanSelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
            }
            q = conditionCom(request, field_dict)
            # 获取所有数据
            objs = models.DaAnLeiXing.objects.select_related('oper_user').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []

            # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'create_date': obj.create_date,
                    'oper_user__username': obj.oper_user.username,
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


@csrf_exempt
@account.is_token(models.UserProfile)
def daanleixing_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            role_data = {
                'name': request.POST.get('name'),
                'oper_user_id': request.GET.get('user_id')
            }
            print(role_data)
            forms_obj = DaanAddForm(role_data)
            if forms_obj.is_valid():
                models.DaAnLeiXing.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.DaAnLeiXing.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '本词不存在'

        elif oper_type == "update":
            form_data = {
                'role_id': o_id,
                'name': request.POST.get('name'),
                'oper_user_id': request.GET.get('user_id'),
            }

            forms_obj = DaanUpdateForm(form_data)
            if forms_obj.is_valid():
                name = forms_obj.cleaned_data['name']
                role_id = forms_obj.cleaned_data['role_id']
                daanleixing_objs = models.DaAnLeiXing.objects.filter(
                    id=role_id
                )
                if daanleixing_objs:
                    daanleixing_objs.update(
                        name=name
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
