from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.customer_verify import CustomerAddForm,  CustomerSelectForm
import json


# cesrf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def customer(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = CustomerSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'openid': '__contains',
                'belonger__name': '__contains',
                'expected_time': '',
                'create_date': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.zgld_customer.objects.select_related('superior', 'belonger','information').filter(q).order_by(order)

            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            for obj in objs:

                if obj.superior:
                    print('obj.superior.username--->',obj.superior.username)
                    superior_username = obj.superior.username
                else:
                    superior_username = ''
                # print('oper_user_username -->', oper_user_username)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'openid': obj.openid,
                    'avator': obj.avator,
                    'expected_time': obj.expected_time,
                    'expedted_pr': obj.expedted_pr,
                    'belonger': obj.belonger.name,
                    'superior': superior_username,
                    'source': obj.information.source,
                    'memo_name': obj.information.memo_name,
                    'phone': obj.information.phone,
                    'position': obj.information.position,
                    'birthday': obj.information.birthday,
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


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def customer_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add":

            form_data = {
                'openid': request.POST.get('openid'),
                'username': request.POST.get('username'),
                'expected_time': request.POST.get('expected_time'),
                'belonger': request.POST.get('belonger'),
                'superior': request.POST.get('superior'),

                'source': request.POST.get('source'),
                'memo_name': request.POST.get('memo_name'),

            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = CustomerAddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过",forms_obj.cleaned_data)

                # print(forms_obj.cleaned_data)
                #  添加数据库
                # print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                # obj = models.zgld_customer.objects.create(**forms_obj.cleaned_data)

                models.zgld_customer.objects.create(
                    openid = form_data['openid'],
                    username = form_data['username'],
                    expected_time = form_data['expected_time'],
                )

                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


