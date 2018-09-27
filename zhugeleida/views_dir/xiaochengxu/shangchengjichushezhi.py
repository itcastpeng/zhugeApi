from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.goodsClass_verify import AddForm, UpdateForm, SelectForm
import json,os,sys
from django.db.models import Q
from django.db.models import F


@csrf_exempt
@account.is_token(models.zgld_customer)
def jiChuSheZhiOper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')
        if oper_type == 'addOrUpdate':
            shangChengName = request.POST.get('shangChengName', '')
            shangHuHao = request.POST.get('shangHuHao', '')
            shangHuMiYao = request.POST.get('shangHuMiYao', '')
            lunbotu = request.POST.get('lunbotu', '')
            if shangHuHao or shangHuMiYao:
                response.code = 301
                response.data = ''
                if len(shangHuHao) > 30:
                    response.msg = '当前商户号长度{}, 不能超过30位！'.format(len(shangHuHao))
                    return JsonResponse(response.__dict__)
                if len(shangHuMiYao) != 32:
                    response.msg = '当前商户秘钥长度{}, 请输入32位正确秘钥！'.format(len(shangHuMiYao))
                    return JsonResponse(response.__dict__)
                if not shangChengName:
                    response.msg = '设置支付配置前, 请先配置商城名称！'
                    return JsonResponse(response.__dict__)
            if user_id:
                if not shangChengName:
                    response.code = 301
                    response.msg = '请配置商城名称！'
                else:
                    userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(userProfile_id=user_id)
                    response.code = 200
                    if userObjs:
                        userObjs.update(
                            shangChengName=shangChengName,
                            shangHuHao=shangHuHao,
                            shangHuMiYao=shangHuMiYao,
                            lunbotu=lunbotu
                        )
                        response.msg = '修改成功'
                    else:
                        models.zgld_shangcheng_jichushezhi.objects.create(
                            shangChengName=shangChengName,
                            shangHuHao=shangHuHao,
                            shangHuMiYao=shangHuMiYao,
                            lunbotu=lunbotu,
                            userProfile_id=user_id
                        )
                        response.msg = '创建成功'
                    response.data = ''
            else:
                response.code = 500
                response.msg = '请先登录,进行操作！'
                response.data = ''
                return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
