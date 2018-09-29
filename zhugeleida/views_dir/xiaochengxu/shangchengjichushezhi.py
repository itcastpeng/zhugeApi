from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def jiChuSheZhiOper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == 'addOrUpdate':
            u_id = request.GET.get('user_id')
            shangChengName = request.POST.get('shangChengName', '')
            shangHuHao = request.POST.get('shangHuHao', '')
            shangHuMiYao = request.POST.get('shangHuMiYao', '')
            lunbotu = request.POST.get('lunbotu', '')
            yongjin = request.POST.get('yongjin', '')
            zhengshu = request.POST.get('zhengshu', '')
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
            if u_id:
                if not shangChengName:
                    response.code = 301
                    response.msg = '请配置商城名称！'
                else:
                    u_idObjs = models.zgld_userprofile.objects.filter(id=u_id)
                    xiaochengxu = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
                    userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu[0].id)
                    response.code = 200
                    if userObjs:
                        userObjs.update(
                            shangChengName=shangChengName,
                            shangHuHao=shangHuHao,
                            shangHuMiYao=shangHuMiYao,
                            lunbotu=lunbotu,
                            yongjin=yongjin,
                            xiaochengxucompany_id=xiaochengxu[0].company_id,
                            zhengshu=zhengshu
                        )
                        response.msg = '修改成功'
                    else:
                        models.zgld_shangcheng_jichushezhi.objects.create(
                            shangChengName=shangChengName,
                            shangHuHao=shangHuHao,
                            shangHuMiYao=shangHuMiYao,
                            lunbotu=lunbotu,
                            xiaochengxuApp_id=xiaochengxu[0].id,
                            yongjin=yongjin,
                            xiaochengxucompany_id=xiaochengxu[0].company_id,
                            zhengshu=zhengshu
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
