from django.shortcuts import render, HttpResponse
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.oper_log_verify import OperLogAddForm
import json







# cerf  token验证
# 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def oper_log_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 客户复制咨询名称(记录次数)
        if oper_type == "add":
            form_data = {
                'oper_type': o_id,
                'user_id': user_id,
            }
            forms_obj = OperLogAddForm(form_data)

            if forms_obj.is_valid():
                models.ZgldUserOperLog.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "记录成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 客户点击咨询对话框次数
@csrf_exempt
@account.is_token(models.zgld_customer)
def update_click_dialog_num(request):
    response = Response.ResponseObj()
    customer_id = request.GET.get('user_id')
    u_id = request.GET.get('u_id')
    article_id = request.GET.get('article_id')
    objs = models.ZgldUserOperLog.objects.filter(
        article_id=article_id,
        customer_id=customer_id,
        user_id=u_id,
        oper_type=2,
    )
    if objs:
        objs[0].click_dialog_num = objs[0].click_dialog_num + 1
        objs[0].save()
    else:
        models.ZgldUserOperLog.objects.create(
            article_id=article_id,
            customer_id=customer_id,
            user_id=u_id,
            oper_type=2,
            click_dialog_num=1
        )
    response.code = 200
    return JsonResponse(response.__dict__)

