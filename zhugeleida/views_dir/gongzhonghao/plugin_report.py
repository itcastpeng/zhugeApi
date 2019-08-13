
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.gongzhonghao.plugin_verify import ReportAddForm,ReportUpdateForm, ReportSelectForm,ReportSignUpAddForm
import time
import datetime
import json

from zhugeleida.public.common import action_record,conversion_base64_customer_username_base64

# 插件活动报名
@csrf_exempt
@account.is_token(models.zgld_customer)
def plugin_report_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 客户 报名活动
        if oper_type == "sign_up_activity":
            report_data = {
                'customer_id': request.GET.get('user_id'),
                'activity_id': o_id,      # 活动ID
                'customer_name': request.POST.get('customer_name'),  # 客户姓名
                'phone': request.POST.get('phone'),                  # 客户报名手机号
                'address': request.POST.get('address'),              # 地址
                # 'phone_verify_code': request.POST.get('phone_verify_code'),        #客户报名手机号发送的验证码。
                'leave_message': request.POST.get('leave_message'),  #留言
            }

            forms_obj = ReportSignUpAddForm(report_data)
            print('address--------------------------------------------------> ', report_data)
            if forms_obj.is_valid():
                uid = request.POST.get('uid')
                activity_id =  o_id  # 广告语
                customer_id =  forms_obj.cleaned_data.get('customer_id')   # 报名按钮
                customer_name =  forms_obj.cleaned_data.get('customer_name')   # 报名按钮
                address =  forms_obj.cleaned_data.get('address')   # 地址
                # 报名页
                phone = forms_obj.cleaned_data['phone']                    # 活动说明

                leave_message =  forms_obj.cleaned_data['leave_message']
                print('------------>>',activity_id,customer_id)

                obj = models.zgld_report_to_customer.objects.filter(
                    activity_id=activity_id,
                    phone = phone,
                )

                if obj:
                    obj.update(customer_name =  customer_name,leave_message=leave_message, address=address)

                else:
                    models.zgld_report_to_customer.objects.create(
                        activity_id =  activity_id,     #
                        customer_name =  customer_name,     #
                        leave_message =  leave_message,  #
                        user_id = uid,
                        phone = phone,
                        address=address
                    )


                if uid and customer_id:  # 发送的文字消息
                    title = models.zgld_article.objects.get(id=activity_id).title
                    # username = models.zgld_customer.objects.get(id=customer_id).username
                    # username = conversion_base64_customer_username_base64(username, customer_id)

                    remark = '报名参加了文章《%s》的活动,具体详情在后台查看' % (title)

                    data = {
                        'action': 17,  # 代表发送客户聊天信息
                        'uid': uid,
                        'user_id': customer_id
                    }
                    action_record(data, remark)

                response.code = 200
                response.msg = "添加成功"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
