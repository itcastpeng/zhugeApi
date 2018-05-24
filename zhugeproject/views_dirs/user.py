from zhugeproject import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from publicFunc.condition_com import conditionCom
from zhugeproject.forms.user_verify import AddForm, UpdateForm, SelectForm
import json
from zhugeproject.public import insert_log

models_userprofile_name = 'project_userprofile'
models_userprofile_obj = getattr(models, models_userprofile_name)

# 权限表中对应的id
quanxian_id = 5

insert_oper_type_id = 1
delete_oper_type_id = 2
update_oper_type_id = 3
select_oper_type_id = 4


@csrf_exempt
@account.is_token(models_userprofile_obj)
def user(request):
    user_id = request.GET.get('user_id')
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'create_date': '',
                'last_login_date': '',
            }
            q = conditionCom(request, field_dict)
            objs = models_userprofile_obj.objects.select_related('role').filter(q).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            for obj in objs:
                print(dir(obj))
                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'role_id': obj.role.id,
                    'create_date': obj.create_date,
                    'last_login_date': obj.last_login_date,
                    'status': obj.get_status_display(),
                })

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }

            # 记录日志
            insert_log.caozuo(user_id, quanxian_id, select_oper_type_id, '查询')
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models_userprofile_obj)
def user_oper(request, oper_type, o_id):
    user_id = request.GET.get('user_id')

    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'username': request.POST.get('username'),
                'role_id': request.POST.get('role_id'),
                'password': request.POST.get('password')
            }
            # form 验证
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                user_obj = models_userprofile_obj.objects.create(**forms_obj.cleaned_data)

                # 记录日志
                remark = '添加 [{}]   ID: [{}]'.format(user_obj.username, user_obj.id)
                insert_log.caozuo(user_id, quanxian_id, insert_oper_type_id, remark)

                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            username_log = models_userprofile_obj.objects.get(id=user_id)
            # 删除 ID
            user_objs = models_userprofile_obj.objects.filter(id=o_id)
            if user_objs:
                user_obj = user_objs[0]

                oper_user_obj = models.project_userprofile.objects.get(id=user_id)
                if oper_user_obj == user_obj:
                    response.code = 303
                    response.msg = "该数据不允许删除"
                else:
                    # 记录日志
                    remark = '将 [{}] 删除   ID: [{}]'.format(user_obj.username, o_id)
                    insert_log.caozuo(user_id, quanxian_id, delete_oper_type_id, remark)

                    user_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            form_data = {
                'o_id': o_id,
                'username': request.POST.get('username'),
                'role_id': request.POST.get('role_id'),
            }
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                username = forms_obj.cleaned_data['username']
                role_id = forms_obj.cleaned_data['role_id']
                user_objs = models_userprofile_obj.objects.filter(
                    id=o_id
                )

                if user_objs:
                    user_obj = user_objs[0]

                    # 记录日志
                    remark = '将 [{}] 修改为 [{}]   ID: [{}]'.format(json.dumps(form_data), json.dumps(forms_obj.cleaned_data), o_id)
                    insert_log.caozuo(user_id, quanxian_id, update_oper_type_id, remark)

                    user_obj.username = username
                    user_obj.role_id = role_id
                    user_obj.save()

                    response.code = 200
                    response.msg = "修改成功"

                else:
                    response.code = 302
                    response.msg = '修改ID不存在'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
