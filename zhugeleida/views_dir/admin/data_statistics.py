from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserSelectForm
import json
import requests
from zhugeapi_celery_project import tasks
from django.db.models import Q
import redis
from zhugeleida.public.common import jianrong_create_qiyeweixin_access_token
from zhugeleida.public.WorkWeixinOper import WorkWeixinOper


# cerf  token验证
# 雷达后台首页 数据统计
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = request.GET.get('user_id')
            order = request.GET.get('order', '-create_date')

            field_dict = {
                'id': '',
            }
            q = conditionCom(request, field_dict)

            print('------q------>>',q)
            # 获取用户信息
            admin_userobj = models.zgld_admin_userprofile.objects.get(id=user_id)
            role_id = admin_userobj.role_id
            company_id = admin_userobj.company_id

            user_objs = models.zgld_admin_userprofile.objects.filter(
                q,
                company_id=company_id,
            )







            ret_data = []
            #  查询成功 返回200 状态码




            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)







@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "GET":
        pass


    else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
#

