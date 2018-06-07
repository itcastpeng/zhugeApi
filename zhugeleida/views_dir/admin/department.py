from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.department_verify import DepartmentAddForm, DepartmentUpdateForm, DepartmentSelectForm
import json
from publicFunc.condition_com import conditionCom


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def department(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1   
        field_dict = {
            'id': '',
            'name': '__contains',
            'create_date': '',

        }
        q = conditionCom(request, field_dict)
        print('q -->', q)

        objs = models.zgld_department.objects.filter(q).order_by('-create_date')
        count = objs.count()

        # 获取所有数据
        ret_data = []
        # 获取第几页的数据
        for obj in objs:
            ret_data.append({
                'id': obj.id,
                'name': obj.name,
                'parentid': obj.parentid_id,
                'department_id': obj.id,
                'create_date': obj.create_date,
                'order': obj.order,
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
@account.is_token(models.zgld_userprofile)
def department_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add":
            department_data = {
                'name': request.POST.get('name'),
                'parentid_id': request.POST.get('parentid')

            }
            forms_obj = DepartmentAddForm(department_data)
            if forms_obj.is_valid():
                models.zgld_department.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('------delete o_id --------->>', o_id)

            # department_relate_user = models.zgld_department.objects.get(id=o_id).zgld_userprofile_set.all()

            department_objs = models.zgld_department.objects.filter(id=o_id)
            if department_objs:
                department_objs.delete()

                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '部门ID不存在'

        elif oper_type == "update":
            form_data = {
                'department_id': o_id,
                'name': request.POST.get('name'),
                'parentid_id': request.POST.get('parentid')

            }

            print(form_data)
            forms_obj = DepartmentUpdateForm(form_data)
            if forms_obj.is_valid():
                name = forms_obj.cleaned_data['name']
                department_id = forms_obj.cleaned_data['department_id']
                print(department_id)
                department_objs = models.zgld_department.objects.filter(
                    id=department_id
                )
                if department_objs:
                    department_objs.update(
                        name=name
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 302
                    response.msg = '部门ID不存在'
            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
