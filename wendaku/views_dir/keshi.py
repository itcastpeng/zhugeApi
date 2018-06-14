from django.shortcuts import render
from wendaku import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
import json
from publicFunc.condition_com import conditionCom
from wendaku.forms.keshi_verify import KeshiAddForm, KeshiUpdateForm, KeshiSelectForm


# def getData(ret_data, pid_id):
#     models.Keshi.objects.filter(pid_id=pid_id)


# 获取排序后的权限数据
def get_paixu_data(models_obj, level=1, pid=None):
    objs = models_obj.objects.select_related('pid')
    if not pid:
        objs = objs.filter(pid=None).order_by('id')
    else:
        objs = objs.filter(pid_id=pid).order_by('id')

    result_data_list = []
    result_data_tree = []
    for obj in objs:
        oper_user_username = ''
        pid_id = ''
        pid__name = ''

        #  如果有oper_user字段 等于本身名字
        if obj.oper_user:
            oper_user_username = obj.oper_user.username

        if obj.pid:
            pid_id = obj.pid.id
            pid__name = obj.pid.name

        current_data = {
            'id': obj.id,
            'name': obj.name,
            'create_date': obj.create_date,
            'pid__name': pid__name,
            'pid_id': pid_id,
            'oper_user__username': oper_user_username,
            'level': level,
        }

        result_data_list.append(current_data)

        children_result_data_list, result_data_tree_children = get_paixu_data(models_obj, level + 1, pid=obj.id)
        print('result_data_listresult_data_list -->', result_data_list)
        result_data_list.extend(children_result_data_list)

        current_data['children'] = result_data_tree_children
        current_data['expand'] = True
        if current_data['level'] > 1:
            num = (level - 1) * 4 + 1
            current_data['name'] = '|' + '-' * num + ' ' + current_data['name']

        result_data_tree.append(current_data)

        print('result_data_list -->', result_data_list)
        print('result_data_tree -->', result_data_tree)

    return result_data_list, result_data_tree

@csrf_exempt
@account.is_token(models.UserProfile)
def keshi(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # forms_obj = KeshiSelectForm(request.GET)
        # if forms_obj.is_valid():
        #     current_page = forms_obj.cleaned_data['current_page']
        #     length = forms_obj.cleaned_data['length']
        #     order = request.GET.get('order', '-create_date')
        #
        #     field_dict = {
        #         'id': '',
        #         'name': '__contains',
        #         'create_date': '',
        #         'pid_id': '',
        #         'oper_user__username': '',
        #     }
        #     q = conditionCom(request, field_dict)
        #     print('q -->', q)
        #
        #     ret_data = []
        #     objs = models.Keshi.objects.select_related('pid', 'oper_user').filter(q).order_by(order)
        #     count = objs.count()
        #
        #     print("length -->", type(length), length)
        #     if length != 0:
        #         start_line = (current_page - 1) * length
        #         stop_line = start_line + length
        #         objs = objs[start_line: stop_line]
        #
        #     for obj in objs:
        #         if obj.pid:
        #             pid__name = obj.pid.name
        #             pid_id = obj.pid.id
        #         else:
        #             pid__name = ""
        #             pid_id = ""
        #
        #         ret_data.append({
        #             'id': obj.id,
        #             'name': obj.name,
        #             'create_date': obj.create_date,
        #             'pid__name': pid__name,
        #             'pid_id': pid_id,
        #             'oper_user__username': obj.oper_user.username,
        #         })
        #     print('ret_data -->', ret_data)

            result_data_list, result_data_tree = get_paixu_data(models.Keshi)
            print(result_data_list)
            response.code = 200
            response.data = {
                'ret_data': result_data_list,
                # 'data_count': count,
                'result_data_tree': result_data_tree
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
                'name': name,
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
            objs = models.Keshi.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                if models.Keshi.objects.filter(pid_id=obj.id):
                    response.code = 304
                    response.msg = "含有子级数据,请先删除或转移子级数据"
                else:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            role_update = models.Keshi.objects.filter(id=o_id)
            if role_update:
                form_data = {
                    'o_id': o_id,
                    'name': request.POST.get('name'),
                    'oper_user_id': request.GET.get('user_id'),
                    'pid_id': request.POST.get('pid_id')
                }
                forms_obj = KeshiUpdateForm(form_data)
                if forms_obj.is_valid():
                    o_id = forms_obj.cleaned_data['o_id']
                    name = forms_obj.cleaned_data['name']
                    oper_user_id = forms_obj.cleaned_data['oper_user_id']
                    pid_id = forms_obj.cleaned_data['pid_id']
                    print("o_id -->", o_id)
                    #  查询数据库  用户id
                    user_objs = models.Keshi.objects.filter(
                        id=o_id
                    )
                    if user_objs:
                        user_objs.update(
                            name=name,
                            oper_user_id=oper_user_id,
                            pid_id=pid_id
                        )
                        response.code = 200
                        response.msg = "修改成功"
                    else:
                        response.code = 302
                        response.msg = "操作 id 不存在"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())
                    print(response.msg)
        else:
            response.code = 402
            response.msg = "请求异常"

        return JsonResponse(response.__dict__)
