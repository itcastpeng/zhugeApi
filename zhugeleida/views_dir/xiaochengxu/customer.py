from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.customer_verify import  Customer_information_UpdateForm,Customer_UpdateExpectedTime_Form ,Customer_UpdateExpedtedPr_Form, CustomerSelectForm
import json
from django.db.models import Q
import base64

# cerf  token验证
# 查询客户管理
@csrf_exempt
@account.is_token(models.zgld_customer)
def customer(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = CustomerSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            customer_id = request.GET.get('user_id')

            order = request.GET.get('order', '-create_date') #排序为成交率; 最后跟进时间; 最后活动时间
            field_dict = {
                'create_date': '',
            }

            q = conditionCom(request, field_dict)
            q.add(Q(**{'id': customer_id}), Q.AND)

            objs = models.zgld_customer.objects.filter(q).order_by(order)

            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            if objs:
                for obj in objs:

                    tag_list = []
                    tag_obj = models.zgld_customer.objects.get(id=obj.id).zgld_tag_set.all()

                    for t_obj in tag_obj:
                        tag_list.append(t_obj.name)

                    info_obj = models.zgld_information.objects.filter(customer_id=obj.id)

                    phone = obj.phone
                    email = info_obj[0].email if info_obj else ''
                    company = info_obj[0].company if info_obj else ''
                    position = info_obj[0].position if info_obj else ''
                    address = info_obj[0].address if info_obj else ''
                    birthday = info_obj[0].birthday if info_obj else ''
                    mem = info_obj[0].mem if info_obj else ''
                    sex = info_obj[0].sex if info_obj else ''


                    day_interval =  datetime.datetime.today() - obj.create_date

                    encodestr = base64.b64decode(obj.username)
                    customer_name = str(encodestr, 'utf-8')


                    ret_data.append({
                        'id': obj.id,
                        'username': customer_name,
                        'headimgurl': obj.headimgurl,

                        'user_type' : obj.user_type,
                        'memo_name': customer_name,  # 备注名
                        'phone': phone,              # 手机号
                        'sex':  sex,
                        'day_interval': day_interval.days,
                        'email': email,              # email
                        'company': company,                # 公司
                        'position':position,  # 位置
                        'address': address,  # 地址
                        'birthday': birthday,  # 生日
                        'mem': mem,  # 备注
                        'tag': tag_list
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




