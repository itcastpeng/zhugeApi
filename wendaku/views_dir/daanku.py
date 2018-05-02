from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from wendaku.forms.daanku_verify import DaankuAddForm, DaankuUpdateForm, DaankuSelectForm
from publickFunc.condition_com import conditionCom
import json

# 数据的展示
@csrf_exempt
@account.is_token(models.UserProfile)
def daanku(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = DaankuSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            field_dict = {
                'id': '',
                'content': '',
                'create_date': '',
                'oper_user__username': '__contains',
                'shenhe_date': '',
                'cilei__name': '__contains',
                'keshi_name': '__contains',
                'daan_leiixng': ''
            }
            q = conditionCom(request, field_dict)
            # 获取所有数据
            role_objs = models.DaAnKu.objects.select_related('oper_user','cilei','keshi','daan_leixing').filter(q).order_by(order)
            role_data = []

            # 获取第几页的数据
            for role_obj in role_objs[start_line: stop_line]:
                role_data.append({
                    'id': role_obj.id,
                    'content': role_obj.content,
                    'create_date': role_obj.create_date,
                    'oper_user__username': role_obj.oper_user.username,
                    'shenhe_date':role_obj.shenhe_date,
                    'cilei__name':role_obj.cilei.name,
                    'keshi_name':role_obj.keshi.name,
                    'daan_leiixng':role_obj.daan_leixing.name

                })
                print(role_obj)
            response.code = 200
            response.data = {
                'role_data': list(role_data),
                'data_count': role_objs.count()
            }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


#  增删改
@csrf_exempt
@account.is_token(models.UserProfile)
def daanku_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            data = request.POST.get('data')
            role_data = {
                # # 审核人
                # 'oper_user_id':request.GET.get('user_id'),
                # 答案
                'content' : data,
                # # 词类
                # 'cilei_id':request.POST.get('cilei_id'),
                # # 科室
                # 'keshi_id':request.POST.get('keshi_id'),
                # # 答案类型
                # 'daan_leixing_id':request.POST.get('daan_leixing_id'),
            }
            forms_obj = DaankuAddForm(role_data)
            if forms_obj.is_valid():
            # data_list = request.POST.get('data_list')
            # for data in data_list:


            # print('forms_obj.forms_obj -->',forms_obj.cleaned_data)
                models.DaAnKu.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.DaAnKu.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '答案不存在'

        elif oper_type == "update":
            form_data = {
                'role_id': o_id,
                'content': request.POST.get('content'),
                'oper_user_id': request.GET.get('user_id'),
            }
            forms_obj = DaankuUpdateForm(form_data)
            if forms_obj.is_valid():
                content = forms_obj.cleaned_data['content']
                role_id = forms_obj.cleaned_data['role_id']
                daanku_objs = models.DaAnKu.objects.filter(
                    id=role_id
                )
                if daanku_objs:
                    daanku_objs.update(
                        content=content
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
