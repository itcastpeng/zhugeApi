from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.customer_verify import CustomerAddForm,  Customer_information_UpdateForm,Customer_UpdateForm , CustomerSelectForm
import json


# cerf  token验证 用户展示模块
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
            objs = models.zgld_customer.objects.select_related('belonger').filter(q).all().order_by(order)

            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            print('=====  objs ====>',objs)

            for obj in objs:
                superior_obj = models.zgld_customer.objects.get(id=obj.id).superior
                if superior_obj :
                    print('obj.superior.username--->',superior_obj.username)
                    superior_username = superior_obj.username
                else:
                    superior_username = ''

                tag_list = []
                tag_obj = models.zgld_customer.objects.get(id=obj.id).zgld_tag_set.all()

                for t_obj in tag_obj:
                    tag_list.append(t_obj.name)
                    print('--->>',tag_list)

                information_obj = models.zgld_information.objects.get(id=obj.id)

                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'openid': obj.openid,
                    'avator': obj.avator,
                    'expected_time': obj.expected_time,    #预计成交时间
                    'expedted_pr': obj.expedted_pr,        #预计成交概率
                    'superior': superior_username,         #所属上级
                    'belonger': obj.belonger.name,         #所属用户
                    'source': obj.source,                  #来源
                    'memo_name': obj.memo_name,           #备注名
                    'phone': information_obj.phone,       #手机号
                    'email': information_obj.email,       #email
                    'company': information_obj.company,   #公司
                    'position': information_obj.position, #位置
                    'address': information_obj.address,   #地址
                    'birthday': information_obj.birthday, #生日
                    'mem': information_obj.mem,           #备注
                    'tag': tag_list
                })
                print('-------for 2 ---->>',ret_data)

            #  查询成功 返回200 状态码
            print('----ret_data----->',ret_data)

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

        if  oper_type == "delete":
            # 删除 ID
            user_objs = models.zgld_customer.objects.filter(id=o_id)
            if user_objs:
                user_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update_customer":

                form_data = {
                    'id': o_id,
                    'tag_list': request.POST.getlist('tag_list'),
                    'expected_time':request.POST.get('expected_time'),
                    'expedted_pr' : request.POST.get('expedted_pr')
                }

                forms_obj = Customer_UpdateForm(form_data)
                if forms_obj.is_valid():
                    print(forms_obj.cleaned_data)
                    obj = models.zgld_customer.objects.get(id=o_id)
                    obj.zgld_tag_set = form_data['tag_list']
                    obj.expected_time = forms_obj.cleaned_data['expected_time']
                    obj.expedted_pr = forms_obj.cleaned_data['expedted_pr']
                    obj.save()

                    response.code = 200
                    response.msg = "添加成功"

                else:
                    response.code = 301
                    response.msg = '用户ID不存在'


        elif oper_type == "update_information":
            # 更新客户表的具体信息
            form_data = {
                'id': int(o_id),
                'source': request.POST.get('source'),
                'memo_name': request.POST.get('memo_name'),
                'phone': request.POST.get('phone'),
                'email': request.POST.get('email'),
                'company': request.POST.get('company'),
                'position': request.POST.get('position'),
                'address': request.POST.get('address'),
                'birthday': request.POST.get('birthday'),
                'mem': request.POST.get('mem'),
            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = Customer_information_UpdateForm(form_data)

            if forms_obj.is_valid():
                print("验证通过", forms_obj.cleaned_data )

                information_obj = models.zgld_information.objects.filter(customer_id=o_id)
                if information_obj:

                    information_obj.update(
                        customer_id =  o_id,
                        source= forms_obj.cleaned_data['source'],
                        memo_name = forms_obj.cleaned_data['memo_name'],
                        company = forms_obj.cleaned_data['company'],
                        position = forms_obj.cleaned_data['position'],
                        address =  forms_obj.cleaned_data['address'],
                        birthday = forms_obj.cleaned_data['birthday'],
                        mem =  forms_obj.cleaned_data['mem']
                    )
                    response.code = 200
                    response.msg = '添加成功'
                else:

                    models.zgld_information.objects.create(
                        customer_id =  o_id,
                        source= forms_obj.cleaned_data['source'],
                        memo_name = forms_obj.cleaned_data['memo_name'],
                        company = forms_obj.cleaned_data['company'],
                        position = forms_obj.cleaned_data['position'],
                        address =  forms_obj.cleaned_data['address'],
                        birthday = forms_obj.cleaned_data['birthday'],
                        mem =  forms_obj.cleaned_data['mem']
                    )

                response.code = 200
                response.msg = '添加成功'

            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


