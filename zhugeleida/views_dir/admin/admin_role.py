from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.admin_role import AddForm, UpdateForm, SelectForm
import json


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def admin_role(request):
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
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.zgld_admin_role.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for o in objs:
                #  将查询出来的数据 加入列表
                rules_id_list = [i[0] for i in o.rules.values_list('id')]



                access_rule_objs = models.zgld_access_rules.objects.values_list('id', 'name', 'title', 'super_id_id')
                rules_data = []
                rule_dict = {}
                for obj in access_rule_objs:
                    if obj[3] == None:
                        rule_dict['children_rule_list'] = []

                        for rule in access_rule_objs:
                            if rule[3] == obj[0]:
                                rule_dict['parent_rule_id'] = obj[0]
                                if obj[0] in rules_id_list:
                                    rule_dict['selected'] = True
                                else:
                                    rule_dict['selected'] = False

                                rule_dict['parent_rule_name'] = obj[1]
                                if  rule[0]  in  rules_id_list:
                                     rule_dict['children_rule_list'].append({'children_rule_id': rule[0], 'selected':True ,'children_rule_name': rule[1]})

                                else:
                                    rule_dict['children_rule_list'].append(
                                        {'children_rule_id': rule[0], 'selected': False, 'children_rule_name': rule[1]})

                                # tag_dict[obj[0]].append({tag[0]})
                        else:

                            if obj[0] in rules_id_list:
                                rule_dict['selected'] = True
                            else:
                                rule_dict['selected'] = False

                            rule_dict['parent_rule_name'] = obj[1]
                            rule_dict['parent_rule_id'] = obj[0]

                        rules_data.append(rule_dict)
                        rule_dict = {}

                        # response.code = 200
                        # response.msg = '查询成功'
                        # response.data = {
                        #     'ret_data': ret_data,
                        #     'data_count': count,
                        # }

                ret_data.append({
                    'role_id': o.id,
                    'role_name': o.name,
                    'rules_data': rules_data,
                    'create_date': o.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            #  查询成功 返回200 状态码
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


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def admin_role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'name': request.POST.get('name'),
            }

            rules_list = json.loads(request.POST.get('rules_list')) if request.POST.get('rules_list') else []

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                obj = models.zgld_admin_role.objects.create(**forms_obj.cleaned_data)
                obj.rules = rules_list
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
            objs = models.zgld_admin_role.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']

                rules_list = json.loads(request.POST.get('rules_list')) if  request.POST.get('rules_list')  else []

                response.code = 200
                response.msg = "添加成功"
                del forms_obj.cleaned_data['o_id']
                #  查询数据库  用户id
                objs = models.zgld_admin_role.objects.filter(id=o_id)
                #  更新 数据
                if objs:
                    objs[0].rules = rules_list
                    objs.update(**forms_obj.cleaned_data)

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                print('forms_obj.errors.as_json() -->', forms_obj.errors.as_json())
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)
