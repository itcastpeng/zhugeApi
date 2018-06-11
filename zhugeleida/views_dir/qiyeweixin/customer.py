from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.customer_verify import  Customer_information_UpdateForm,Customer_UpdateForm , CustomerSelectForm
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
            order = request.GET.get('order', '-create_date') #排序为成交率; 最后跟进时间; 最后活动时间
            field_dict = {
                'id': '',
                'username': '__contains',
                'belonger__username': '__contains',   #归属人
                'superior__username': '__contains',   #上级人
                'expected_time': '__contains',     #预测成交时间
                'expedted_pr' : '__contains',      #预测成交概率
                'source'  : '',
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
            if objs:
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
                    info_obj = models.zgld_information.objects.filter(id=obj.id)
                    ai_pr = 0
                    phone = info_obj[0].phone if info_obj else ''
                    email = info_obj[0].email if info_obj else ''
                    company = info_obj[0].company if info_obj else ''
                    position = info_obj[0].position if info_obj else ''
                    address = info_obj[0].address if info_obj else ''
                    birthday = info_obj[0].birthday if info_obj else ''
                    mem = info_obj[0].mem if info_obj else ''

                    ret_data.append({
                        'id': obj.id,
                        'username': obj.username,
                        'openid': obj.openid,
                        'headimgurl': obj.headimgurl,
                        'expected_time': obj.expected_time,  # 预计成交时间
                        'expedted_pr': obj.expedted_pr,  # 预计成交概率
                        'ai_pr': ai_pr,  # AI 预计成交概率
                        'superior': superior_username,  # 所属上级
                        'belonger': obj.belonger.username,  # 所属用户
                        'source': obj.source,  # 来源
                        'memo_name': obj.memo_name,  # 备注名
                        'phone': phone,              # 手机号
                        'email': email,              # email
                        'company': company,                # 公司
                        'position': position,  # 位置
                        'address': address,  # 地址
                        'birthday': birthday,  # 生日
                        'mem': mem,  # 备注
                        'tag': tag_list
                    })


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
                'memo_name': request.POST.get('username'),
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
                        company = forms_obj.cleaned_data['company'],
                        phone = forms_obj.cleaned_data['phone'],
                        email = forms_obj.cleaned_data['email'],
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
                        company = forms_obj.cleaned_data['company'],
                        phone=forms_obj.cleaned_data['phone'],
                        email=forms_obj.cleaned_data['email'],
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


