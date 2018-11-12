
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
from django.db.models import Q
from zhugeleida.public.condition_com import conditionCom


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
                # 'phone_verify_code': request.POST.get('phone_verify_code'),        #客户报名手机号发送的验证码。
                'leave_message': request.POST.get('leave_message'),  #留言
            }

            forms_obj = ReportSignUpAddForm(report_data)

            if forms_obj.is_valid():
                uid = request.POST.get('uid')
                activity_id =  o_id  # 广告语
                customer_id =  int(forms_obj.cleaned_data.get('customer_id'))   # 报名按钮
                # 报名页
                customer_name =  forms_obj.cleaned_data['customer_name']   # 活动标题
                phone = forms_obj.cleaned_data['phone']                    # 活动说明
                # phone_verify_code =  forms_obj.cleaned_data['phone_verify_code']
                leave_message =  forms_obj.cleaned_data['leave_message']
                print('------------>>',activity_id,customer_id)

                obj = models.zgld_report_to_customer.objects.filter(
                    activity_id=activity_id,
                    customer_id=customer_id,
                    user_id=uid,
                )

                if obj:
                    obj.update(leave_message = leave_message)

                else:
                    models.zgld_report_to_customer.objects.create(
                        activity_id =  activity_id,     #
                        customer_id =  customer_id,     #
                        leave_message =  leave_message  #
                    )

                customer_obj = models.zgld_customer.objects.get(id=customer_id)
                customer_obj.phone = phone  # 报名手机号
                customer_obj.save()


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
