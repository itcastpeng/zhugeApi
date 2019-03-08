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


# 用户咨询 / 文章客户 操作日志
@csrf_exempt
@account.is_token(models.zgld_customer)
def update_click_dialog_num(request, oper_type):
    response = Response.ResponseObj()
    u_id = request.GET.get('u_id')
    article_id = request.GET.get('article_id')
    customer_id = request.GET.get('user_id')

    # 客户点击咨询对话框次数
    if oper_type == 'update_click_dialog_num':
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

    # 记录查看文章视频时长
    elif oper_type == 'article_video_duration':
        video_time = request.GET.get('video_time')
        if video_time:
            objs = models.ZgldUserOperLog.objects.filter(
                article_id=article_id,
                customer_id=customer_id,
                user_id=u_id,
                oper_type=3
            )
            if objs:
                objs.update(video_time=video_time)
            else:
                models.ZgldUserOperLog.objects.create(
                    article_id=article_id,
                    customer_id=customer_id,
                    user_id=u_id,
                    oper_type=3,
                    video_time=video_time,
                )

    # 记录文章阅读时长
    elif oper_type == 'article_reading_time':
        reading_time = request.GET.get('reading_time')
        if reading_time:
            objs = models.ZgldUserOperLog.objects.filter(
                article_id=article_id,
                customer_id=customer_id,
                user_id=u_id,
                oper_type=4
            )
            if objs:
                objs.update(reading_time=reading_time)
            else:
                models.ZgldUserOperLog.objects.create(
                    article_id=article_id,
                    customer_id=customer_id,
                    user_id=u_id,
                    oper_type=4,
                    reading_time=reading_time
                )

    response.code = 200
    return JsonResponse(response.__dict__)

