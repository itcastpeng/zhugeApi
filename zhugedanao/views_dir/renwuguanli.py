from ribao import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ribao.forms.renwuguanli_verify import AddForm, UpdateForm, SelectForm
import json
from publicFunc.condition_com import conditionCom


@csrf_exempt
@account.is_token(models.RibaoUserProfile)
def renwuguanli(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            print('开始 -----> ')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'task_name': '__contains',
                'detail' : '' ,
                'belog_task':'__contains',
                'director':'__contains',
                'issuer':'' ,
                'boor_urgent':'',
                'create_date':'',
                'estimated_time':'',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.RibaoTaskManage.objects.select_related('belog_task','director').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 获取所有数据
            ret_data = []
            # 获取第几页的数据
            print('objs -->',objs)
            for obj in objs:
                ret_data.append({
                'id':obj.id,
                'task_name':obj.task_name,
                'detail' : obj.detail,
                'belog_task':obj.belog_task.project_name,
                'director':obj.director.person_people.username,
                'issuer':obj.issuer,
                'boor_urgent':obj.boor_urgent,
                'create_date':obj.create_date,
                'estimated_time':obj.estimated_time,
                })
            print('ret_data -- >',ret_data)
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
                'o_id':o_id,
                'task_name': request.POST.get('task_name'),
                # 'issuer': request.GET.get('user_id'),
                # 'detail' : request.POST.get('detail') ,
                # 'belog_task':request.POST.get('belog_task'),
                # 'director':request.POST.get('director'),
                # 'boor_urgent':request.POST.get('boor_urgent'),
                # 'estimated_time':request.POST.get('estimated_time')
            }
            print(form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                task_name = forms_obj.cleaned_data['task_name']
                # issuer = forms_obj.cleaned_data['issuer']
                # belog_task_id = forms_obj.cleaned_data['belog_task_id']
                # director = forms_obj.cleaned_data['director']
                # detail = forms_obj.cleaned_data['detail']
                # boor_urgent = forms_obj.cleaned_data['boor_urgent']
                role_objs = models.RibaoTaskManage.objects.filter(
                    id=o_id,
                )
                if role_objs:
                    role_objs.update(
                        task_name=task_name,
                        # issuer=issuer,
                        # belog_task=belog_task_id,
                        # director=director,
                        # detail=detail,
                        # boor_urgent=boor_urgent,
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
