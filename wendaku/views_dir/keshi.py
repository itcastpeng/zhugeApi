from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
import json
from wendaku.forms.keshi_verify import KeshiAddForm,KeshiUpdateForm,KeshiSelectForm
@csrf_exempt
@account.is_token(models.UserProfile)
def keshi(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = KeshiSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            keshi_data = []
            keshiprofile_objs = models.Keshi.objects.select_related('Keshi','UserProfile').all().order_by(order)
            print(keshiprofile_objs)
            for  keshi_objs in keshiprofile_objs[start_line: stop_line]:

                keshi_data.append({
                    'id': keshi_objs.id,
                    'name': keshi_objs.name,
                    'create_date': keshi_objs.create_date,
                    'pid_id':keshi_objs.pid_id
                    # 'oper_user__username': keshi_objs.oper_user.username,
                })
                print(keshi_data)
                response.code = 200
                response.data = {
                    'role_data': list(keshi_objs),
                    'data_count':len(keshi_objs)
                }
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.UserProfile)
def keshi_role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    oper_user_id = request.GET.get('user_id')
    pid_id = request.POST.get('pid_id')
    name = request.POST.get('name')

    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'oper_user_id': oper_user_id,
                'pid_id': pid_id,
                'name':name,
            }
            forms_obj = KeshiAddForm(form_data)
            if forms_obj.is_valid():
                # models.Keshi.objects.create(name=name,oper_user_id=user_id,pid_id=user_id)

                # print("forms_obj.cleaned_data --> ", forms_obj.cleaned_data)
                models.Keshi.objects.create(**forms_obj.cleaned_data)

                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 300
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.Keshi.objects.filter(id=o_id)
            if role_objs:
                role_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
                role_update = models.Keshi.objects.filter(id=o_id)
                if role_update:
                    form_data = {
                        'user_id': o_id,
                        'name': request.POST.get('name'),
                        'oper_user_id': request.GET.get('user_id'),
                        'pid_id':request.POST.get('pid_id')
                    }
                    print(form_data)
                    forms_obj = KeshiUpdateForm(form_data)
                    if forms_obj.is_valid():
                        user_id = forms_obj.cleaned_data['user_id']
                        name = forms_obj.cleaned_data['name']
                        oper_user_id = forms_obj.cleaned_data['oper_user_id']
                        #  查询数据库  用户id
                        user_obj = models.Keshi.objects.filter(
                            id=user_id
                        )
                        #  更新 数据
                        user_obj.update(name=name)

                        response.code = 200
                        response.msg = "修改成功"
                    else:
                        response.code = 302
                        response.msg = '用户ID不存在'
        else:
            response.code = 402
            response.msg = "请求异常"

        return JsonResponse(response.__dict__)
