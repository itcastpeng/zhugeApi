from ribao import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ribao.forms.xiangmuguanli_verify import AddForm, UpdateForm, SelectForm
import json

from publickFunc.condition_com import conditionCom

@csrf_exempt
@account.is_token(models.RibaoUserProfile)
def xiangmuguanli(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            print('current_page -->',current_page)
            length = forms_obj.cleaned_data['length']
            print('length-->',length)
            order = request.GET.get('order', '-person_people')

            field_dict = {
                'id': '',
                'project_name': '__contains',
                'person_people_username': '__contains',
            }
            q = conditionCom(request, field_dict)
            objs = models.RibaoProjectManage.objects.select_related('person_people').filter(q).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 获取所有数据
            ret_data = []
            # # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'project_name': obj.project_name,
                    'person_people': obj.person_people.username,
                })
            print(ret_data)
            print(ret_data)
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
def xiangmuguanli_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            role_data = {
                'project_name' : request.POST.get('project_name'),
                'person_people_id': request.POST.get('person_people_id')
            }
            forms_obj = AddForm(role_data)
            if forms_obj.is_valid():
                print(forms_obj.cleaned_data)
                models.RibaoProjectManage.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            role_objs = models.RibaoProjectManage.objects.filter(id=o_id)
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
                'project_name': request.POST.get('project_name'),
                'person_people_id': request.POST.get('person_people_id')
            }
            print(form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                name = forms_obj.cleaned_data['project_name']
                pro_id = o_id
                proj_objs = models.RibaoProjectManage.objects.filter(
                    id=pro_id
                )
                if proj_objs:
                    proj_objs.update(
                        project_name=name
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
