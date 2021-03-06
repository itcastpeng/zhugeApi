from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.access_roles import AddForm, UpdateForm, SelectForm
import json


# cerf  token验证
# 权限查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def access_rules(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'name': '__contains',
            }

            q = conditionCom(request, field_dict)

            if  request.GET.get('super_id_id__isnull'):
                q.add(Q(**{"super_id_id__isnull": True}), Q.AND)


            objs = models.zgld_access_rules.objects.select_related('super_id').filter(q).order_by(order)

            ret_data = []
            count = objs.count()

            for obj in objs:

                super_name = ''
                if obj.super_id:
                    super_name = obj.super_id.name

                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'title': obj.title,
                    'super_id': obj.super_id_id,
                    'super_name': super_name,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            return JsonResponse(response.__dict__)

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  权限操作
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def access_rules_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":

        # 添加权限
        if oper_type == "add":
            form_data = {
                'name': request.POST.get('name'),
                'title': request.POST.get('title'),
                'super_id_id': request.POST.get('super_id_id'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                # print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                models.zgld_access_rules.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除权限
        elif oper_type == "delete":
            # 删除 ID
            objs = models.zgld_access_rules.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

        # 修改权限
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'title': request.POST.get('title'),
                'super_id_id': request.POST.get('super_id_id')
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                # name = forms_obj.cleaned_data['name']
                # url_path = forms_obj.cleaned_data['url_path']
                # super_id_id = forms_obj.cleaned_data['super_id_id']
                del forms_obj.cleaned_data['o_id']
                #  查询数据库  用户id
                objs = models.zgld_access_rules.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    # objs.update(
                    #     name=name,
                    #     url_path=url_path,
                    #     super_id_id=super_id_id,
                    # )
                    objs.update(**forms_obj.cleaned_data)

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
