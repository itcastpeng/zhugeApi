from publickFunc.condition_com import conditionCom
from wendaku import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from wendaku.forms.guanjianci_verify import AddForm, UpdateForm,SelectForm
import json

models_name = 'GuanJianCi'
models_obj = getattr(models, models_name)


# 获取排序后的权限数据
# def get_paixu_data(models_obj, level=1, pid=None):
#     objs = models_obj.objects.select_related('pid')
#     if not pid:
#         objs = objs.filter(pid=None).order_by('order_num')
#     else:
#         objs = objs.filter(pid_id=pid).order_by('order_num')
#
#     result_data_list = []
#     result_data_tree = []
#     for obj in objs:
#         oper_user_username = ''
#         pid_id = ''
#         pid__name = ''
#
#         #  如果有oper_user字段 等于本身名字
#         if obj.oper_user:
#             oper_user_username = obj.oper_user.username
#
#         if obj.pid:
#             pid_id = obj.pid.id
#             pid__name = obj.pid.title
#
#         current_data = {
#             'id': obj.id,
#             'path': obj.path,
#             'icon': obj.icon,
#             'title': obj.title,
#             'pid_id': pid_id,
#             'pid__name': pid__name,
#             'order_num': obj.order_num,
#             'create_date': obj.create_date,
#             'component': obj.component,
#             'oper_user__username': oper_user_username,
#             'level': level,
#         }
#         result_data_list.append(current_data)
#
#         children_result_data_list, result_data_tree_children = get_paixu_data(models_obj, level + 1, pid=obj.id)
#         print('result_data_listresult_data_list -->', result_data_list)
#         result_data_list.extend(children_result_data_list)
#
#         current_data['children'] = result_data_tree_children
#         current_data['expand'] = True
#         if current_data['level'] > 1:
#             num = (level - 1) * 4 + 1
#             current_data['title'] = '|' + '-' * num + ' ' + current_data['title']
#
#         result_data_tree.append(current_data)
#
#         print('result_data_list -->', result_data_list)
#         print('result_data_tree -->', result_data_tree)
#
#     return result_data_list, result_data_tree


@csrf_exempt
@account.is_token(models.UserProfile)
def guanjianci(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order','oper_user')
            start_line = (current_page - 1) * length
            stop_line = start_line + length

            field_dict = {
                'id': '',
                'content': '__contains',
                'oper_user__username': '__contains',
            }
            q = conditionCom(request, field_dict)
            # 获取所有数据
            objs = models.GuanJianCi.objects.select_related('oper_user').filter(q).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []

            # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'content': obj.content,
                    'oper_user__username': obj.oper_user.username,
                })
            response.code = 200
            response.data = {
                'ret_data': ret_data,
                'data_count': count
            }
    return JsonResponse(response.__dict__)


#  增删改 关键词表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.UserProfile)
def guanjianci_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    print('进入')
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'o_id': o_id,
                'oper_user_id': request.GET.get('user_id'),
                'content': request.POST.get('content'),
            }
            print("form_data -->", form_data)
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                del forms_obj.cleaned_data['o_id']
                print('forms_obj.cleaned_data-->', forms_obj.cleaned_data)
                models_obj.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())


        elif oper_type == "delete":
            # 删除 ID
            objs = models_obj.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'


        elif oper_type == "update":

            # 获取ID 用户名 及 角色
            form_data = {
                'o_id': o_id,
                'oper_user_id': request.GET.get('user_id'),
                'content': request.POST.get('content'),
            }
            print('form_data --> ', form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                content = forms_obj.cleaned_data['content']
                #  查询数据库  用户id
                user_obj = models_obj.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if user_obj:
                    user_obj.update(
                        content=content,
                    )
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















