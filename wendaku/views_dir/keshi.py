from django.shortcuts import render
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from wendaku.forms.keshi import KeshiForm,KeshiUpdateForm
@csrf_exempt
@account.is_token(models.UserProfile)
def keshi(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        current_page = int(request.GET.get('current_page', 1))
        length = int(request.GET.get('length', 10))
        start_line = (current_page - 1) * length
        stop_line = start_line + length
        # print(start_line, length)
        role_data = models.Keshi.objects.select_related('Keshi').all().values('id', 'name','create_date','oper_user__username')[start_line: stop_line]
        # print(role_data)
        response.code = 200
        response.data = {
            'role_data': list(role_data),
            'data_count':len(role_data)
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


@csrf_exempt
@account.is_token(models.UserProfile)
def keshi_role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    oper_user_id = request.GET.get('user_id')
    pid_id = request.POST.get('pid_id')
    name = request.POST.get('name')
    if request.method == "POST":
        if oper_type == "add":
            # print('request.POST-->',request.POST)
            form_data = {
                'oper_user_id': oper_user_id,
                'pid_id': pid_id,
                'name':name,
            }
            forms_obj = KeshiForm(form_data)
            print('form_data-->',form_data)
            if forms_obj.is_valid():
                # models.Keshi.objects.create(name=name,oper_user_id=user_id,pid_id=user_id)

                print("forms_obj.cleaned_data --> ", forms_obj.cleaned_data)
                models.Keshi.objects.create(**forms_obj.cleaned_data)

                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 300
                response.msg = "科室名已存在"

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
                        'oper_user_id': request.POST.get('oper_user_id'),
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
