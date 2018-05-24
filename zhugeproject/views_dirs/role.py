
from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from zhugeproject.forms.role_verify import AddForm, UpdateForm, SelectForm
import json
from zhugeproject.publick import xuqiu_or_gongneng_log
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
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            role_data = {
                'name' : request.POST.get('name'),
            }
            forms_obj = AddForm(role_data)
            if forms_obj.is_valid():
                models.ProjectRole.objects.create(**forms_obj.cleaned_data)
                remark = '{}添加新角色：{}'.format(username_log, role_data['name'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 200
                response.msg = "添加成功"
            else:
                remark = '{}添加新角色:{},FORM验证未通过'.format(username_log, role_data['name'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            role_objs = models.ProjectRole.objects.filter(id=o_id)
            if role_objs:
                for obj in role_objs:
                    name = obj.name
                    remark = '{}删除角色:{}成功,ID为{}}'.format(username_log, name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    role_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                remark = '{}删除角色ID失败:{},用户ID不存在'.format(username_log, o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 302
                response.msg = '角色ID不存在'

        elif oper_type == "update":
            form_data = {
                'role_id': o_id,
                'name': request.POST.get('name'),
                'oper_user_id': request.GET.get('user_id'),
            }
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
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
                    remark = '{}修改角色为{},ID:{}'.format(username_log,name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    remark = '{}修改角色{}失败ID不存在,ID为:{}'.format(username_log, name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    response.code = 303
                    response.msg = '修改角色ID不存在'
            else:
                remark = '{}修改角色ID为{}FORM验证失败'.format(username_log, o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        user_id = request.GET.get('user_id')
        username_log = models.ProjectUserProfile.objects.get(id=user_id)
        remark = '{}请求操作用户失败请求异常'.format(username_log)
        xuqiu_or_gongneng_log.gongneng_log(request, remark)

        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
