from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from publickFunc.condition_com import conditionCom
from zhugeproject.forms.user_verify import AddForm, UpdateForm, SelectForm
import json
from zhugeproject.publick import xuqiu_or_gongneng_log


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def user_select(request):
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
            objs = models.ProjectUserProfile.objects.select_related('role').filter(q).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            # # 返回的数据
            ret_data = []
            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'role_id': obj.role.id,
                    'create_date': obj.create_date,
                    'last_login_date': obj.last_login_date,
                })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            form_data = {
                'o_id': o_id,
                'username': request.POST.get('username'),
                'role_id': request.POST.get('role_id'),
                'password': request.POST.get('password')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                models.ProjectUserProfile.objects.create(**forms_obj.cleaned_data)
                # 加入log
                remark='{}添加新用户：{}'.format(username_log,form_data['username'])
                xuqiu_or_gongneng_log.gongneng_log(request,remark)
                response.code = 200
                response.msg = "添加成功"
            else:
                remark = '{}添加新用户:{},FORM验证未通过'.format(username_log,form_data['username'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            # 删除 ID
            user_objs = models.ProjectUserProfile.objects.filter(id=o_id)
            if user_objs:
                for obj in user_objs:
                    name = obj.username
                    remark='{}删除用户:{}成功,ID为{}'.format(username_log,name,o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    user_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"

            else:
                remark='{}删除用户ID失败,用户ID不存在'.format(username_log,o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            form_data = {
                'o_id': o_id,
                'username': request.POST.get('username'),
                'role_id': request.POST.get('role_id'),
            }
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                user_id = forms_obj.cleaned_data['user_id']
                username = forms_obj.cleaned_data['username']
                role_id = forms_obj.cleaned_data['role_id']
                user_obj = models.ProjectUserProfile.objects.filter(
                    id=user_id
                )

                if user_obj:
                    user_obj.update(
                        username=username, role_id=role_id
                    )
                    remark='{}修改用户:{},ID:{}'.format(username_log,username,o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)

                    response.code = 200
                    response.msg = "修改成功"

                else:
                    remark='{}修改用户:{}失败ID不存在,ID为:{}'.format(username_log,username,o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)

                    response.code = 303
                    response.msg = '修改ID不存在'

            else:
                remark='{}修改用户ID为{}FORM验证失败'.format(username_log,o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        user_id = request.GET.get('user_id')
        username_log = models.ProjectUserProfile.objects.get(id=user_id)
        remark='{}请求操作用户失败请求异常'.format(username_log)
        xuqiu_or_gongneng_log.gongneng_log(request, remark)

        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
