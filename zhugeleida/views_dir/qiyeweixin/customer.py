from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.customer_verify import  Customer_information_UpdateForm,Customer_UpdateExpectedTime_Form ,Customer_UpdateExpedtedPr_Form, CustomerSelectForm
from django.db.models import Q
from publicFunc.base64 import b64encode, b64decode
import base64, json, datetime, time


# cerf  token验证
# 查询客户详细信息
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
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')

            order = request.GET.get('order', '-create_date') #排序为成交率; 最后跟进时间; 最后活动时间
            field_dict = {
                'id': '',
                'username': '__contains',
                'belonger__username': '__contains',   #归属人
                'superior__username': '__contains',   #上级人
                'expected_time': '__contains',     #预测成交时间
                'source'  : '',
                'create_date': '',
            }

            q = conditionCom(request, field_dict)
            q.add(Q(**{'id': customer_id}), Q.AND)

            print('q-------------> ', q)
            objs = models.zgld_customer.objects.filter(q).order_by(order)

            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            for obj in objs:

                data = {
                    'email':'',         # 邮箱
                    'company':'',       # 公司
                    'position':'',      # 职位
                    'address':'',       # 地址
                    'birthday':'',      # 生日
                    'mem':'',           # 备注
                    'sex':'',           # 性别
                    'memo_name':'',     # 备注名称
                }
                tag_list = []
                tag_obj = models.zgld_customer.objects.get(id=obj.id).zgld_tag_set.all()

                for t_obj in tag_obj:
                    tag_list.append(t_obj.name)

                info_objs = models.zgld_information.objects.filter(
                    customer_id=obj.id,
                    user_id=user_id
                )
                if info_objs:
                    info_obj = info_objs[0]
                    email = info_obj.email
                    company = info_obj.company
                    position = info_obj.position
                    address = info_obj.address
                    birthday = info_obj.birthday
                    mem = info_obj.mem
                    sex = info_obj.sex
                    note_name = info_obj.note_name


                    if email:
                        data['email'] = email
                    if company:
                        data['company'] = company
                    if position:
                        data['position'] = position
                    if address:
                        data['address'] = address
                    if birthday:
                        data['birthday'] = birthday
                    if mem:
                        data['mem'] = mem
                    if sex:
                        data['sex'] = sex
                    if note_name:
                        data['memo_name'] = b64decode(note_name)


                belonger_obj = models.zgld_user_customer_belonger.objects.get(customer_id=obj.id,user_id=user_id)
                day_interval =  datetime.datetime.today() - obj.create_date

                expedted_pr = belonger_obj.expedted_pr
                expected_time = belonger_obj.expected_time

                data['phone'] = obj.phone  # 手机号
                data['id'] =  obj.id
                data['username'] =  b64decode(obj.username)
                data['headimgurl'] =  obj.headimgurl
                data['expected_time'] =  expected_time # 预计成交时间
                data['expedted_pr'] =  expedted_pr  # 预计成交概率
                data['ai_pr'] =  expedted_pr  # AI 预计成交概率
                data['user_type'] =  obj.user_type
                data['source'] =  belonger_obj.get_source_display()  # 来源
                data['tag'] =  tag_list
                data['day_interval'] = day_interval.days

                ret_data.append(
                    data
                )

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


#  增删改 客户管理
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def customer_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # # 删除客户
        # if oper_type == "delete":
        #     # 删除 ID
        #     user_objs = models.zgld_customer.objects.filter(id=o_id)
        #     if user_objs:
        #         user_objs.delete()
        #         response.code = 200
        #         response.msg = "删除成功"
        #     else:
        #         response.code = 302
        #         response.msg = '用户ID不存在'

        # # 添加客户
        # if oper_type == "update_tag":
        #
        #     tag_list =  json.loads(request.POST.get('tag_list'))
        #
        #     objs = models.zgld_tag.objects.filter(id__in=tag_list)
        #     if objs:
        #         obj = models.zgld_customer.objects.get(id=o_id)
        #         obj.zgld_tag_set = tag_list
        #         obj.save()
        #
        #         response.code = 200
        #         response.msg = "添加成功"
        #
        #     else:
        #         response.code = 301
        #         response.msg = '用户标签不存在'

        # 修改预计成交时间
        if oper_type == "update_expected_time":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'customer_id': o_id,
                'expected_time': request.POST.get('expected_time')
            }

            forms_obj = Customer_UpdateExpectedTime_Form(form_data)
            if forms_obj.is_valid():
                print('-----forms_obj.cleaned_data------->>',forms_obj.cleaned_data)
                now_time = datetime.datetime.now()
                user_id = forms_obj.cleaned_data.get('user_id')
                customer_id = forms_obj.cleaned_data.get('customer_id'),
                expected_time =  forms_obj.cleaned_data.get('expected_time')

                objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id,customer_id=customer_id)

                if objs:  # 判断关系表是否有记录。
                    objs.update(
                        last_follow_time=now_time,
                        expected_time = expected_time
                    )
                    info = '更新预计成交日期: %s' % (expected_time)
                    models.zgld_follow_info.objects.create(user_customer_flowup_id=objs[0].id, follow_info=info)
                    response.code = 200
                    response.msg = "添加成功"

                else:
                    response.code = 307
                    response.msg = "用户-客户关系不存在"

            else:
                print('---- 未通过 --->>')
                response.code = 303
                response.msg =  forms_obj.errors.as_json()

        # 修改预计成交率
        elif oper_type == "update_expected_pr":

            form_data = {
                'customer_id': o_id,
                'expedted_pr': request.POST.get('expedted_pr')
            }

            forms_obj = Customer_UpdateExpedtedPr_Form(form_data)
            if forms_obj.is_valid():
                print(forms_obj.cleaned_data)
                user_id = request.GET.get('user_id')
                customer_id = forms_obj.cleaned_data.get('customer_id')
                now_time = datetime.datetime.now()
                expedted_pr = forms_obj.cleaned_data.get('expedted_pr')

                objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id,customer_id=customer_id)

                if objs:
                    if 'NaN' in expedted_pr:
                        expedted_pr = 0
                    else:
                        expedted_pr = int(expedted_pr)

                    objs.update(
                        last_follow_time=now_time,
                        expedted_pr=expedted_pr
                    )

                    info = '更新预计成交率为: %s' % (expedted_pr)
                    models.zgld_follow_info.objects.create(user_customer_flowup_id=objs[0].id,follow_info=info)

                    response.code = 200
                    response.msg = "添加成功"

                else:
                    response.code = 307
                    response.msg = "用户-客户关系不存在"

            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

        # 编辑资料信息
        elif oper_type == "update_information":

            # 更新客户表的具体信息
            form_data = {
                'id': int(o_id),
                'sex': request.POST.get('sex'),             # 性别
                'note_name': request.POST.get('username'),  # 备注名称
                'phone': request.POST.get('phone'),         # 电话
                'email': request.POST.get('email'),         # 邮箱
                'company': request.POST.get('company'),     # 在职公司
                'position': request.POST.get('position'),   # 职位
                'address': request.POST.get('address'),     # 地址
                'birthday': request.POST.get('birthday'),   # 生日
                'mem': request.POST.get('mem'),             # 备注
            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = Customer_information_UpdateForm(form_data)
            if forms_obj.is_valid():
                note_name = forms_obj.cleaned_data.get('note_name')
                note_name = b64encode(note_name)

                # encodestr = base64.b64encode(memo_name.encode('utf-8'))
                # memo_name = str(encodestr, 'utf-8')
                # print("----验证通过--->", forms_obj.cleaned_data,memo_name)
                # customer_obj = models.zgld_customer.objects.filter(id=o_id)
                # customer_obj.update(
                #     username = memo_name
                # )

                information_obj = models.zgld_information.objects.filter(
                    customer_id=o_id,
                    user_id=user_id
                )

                if information_obj:
                    information_obj.update(
                        customer_id =  o_id,
                        user_id=user_id,
                        sex = forms_obj.cleaned_data.get('sex'),
                        company = forms_obj.cleaned_data.get('company'),
                        phone = forms_obj.cleaned_data.get('phone'),
                        email = forms_obj.cleaned_data.get('email'),
                        position = forms_obj.cleaned_data.get('position'),
                        address =  forms_obj.cleaned_data.get('address'),
                        birthday = forms_obj.cleaned_data.get('birthday'),
                        mem =  forms_obj.cleaned_data.get('mem'),
                        note_name=note_name,
                    )
                    response.code = 200
                    response.msg = '修改成功'

                else:
                    models.zgld_information.objects.create(
                        customer_id =  o_id,
                        user_id=user_id,
                        note_name=note_name,
                        sex= int(forms_obj.cleaned_data.get('sex')),
                        company = forms_obj.cleaned_data.get('company'),
                        phone=forms_obj.cleaned_data.get('phone'),
                        email=forms_obj.cleaned_data.get('email'),
                        position = forms_obj.cleaned_data.get('position'),
                        address =  forms_obj.cleaned_data.get('address'),
                        birthday = forms_obj.cleaned_data.get('birthday'),
                        mem =  forms_obj.cleaned_data.get('mem')
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


