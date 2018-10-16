from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.shangchengshezhi_verify import jichushezhi, zhifupeizhi, yongjinshezhi
import json, zipfile, os, random

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def jiChuSheZhiShow(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
    xiaochengxu = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
    if xiaochengxu:
        userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu[0].id)
        user_id_mallStatus = models.zgld_company.objects.filter(id=u_idObjs[0].company_id)
        mallStatus = user_id_mallStatus[0].get_shopping_type_display()
        mallStatusID = user_id_mallStatus[0].shopping_type
        otherData = []
        for obj in userObjs:
            lunbotu = ''
            if obj.lunbotu:
                lunbotu = json.loads(obj.lunbotu)
            otherData.append({
                'shangChengName': obj.shangChengName,
                'shangHuHao': obj.shangHuHao,
                'shangHuMiYao': obj.shangHuMiYao,
                'lunbotu': lunbotu,
                'yongjin': obj.yongjin,
                'xiaochengxuApp': obj.xiaochengxuApp.name,
                'xiaochengxuApp_id': obj.xiaochengxuApp_id,
                'xiaochengxucompany_id': obj.xiaochengxucompany_id,
                'xiaochengxucompany': obj.xiaochengxucompany.name,
                'zhengshu': obj.zhengshu,
                'mallStatus':mallStatus,
                'mallStatusID':mallStatusID

            })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData':otherData}
    else:
        response.code = 301
        response.msg = '您未注册公司, 请联系管理员！'
        response.data = ''
    return JsonResponse(response.__dict__)

def addSmallProgram(request):
    xiaochengxuid = request.GET.get('xiaochengxuid')
    response = Response.ResponseObj()
    # u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
    # xiaochengxu_id = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
    userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxuid)
    if not userObjs:
        models.zgld_shangcheng_jichushezhi.objects.create(
            xiaochengxuApp_id=xiaochengxuid
        )
        response.code = 200
        response.msg = '添加成功'
    else:
        response.code = 301
        response.msg = '该小程序已创建设置'
    return JsonResponse(response.__dict__)

# 商城设置
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def jiChuSheZhiOper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
    xiaochengxu_id = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
    userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu_id[0].id)
    if request.method == "POST":
        if oper_type == 'jichushezhi':
            resultData = {
                'mallStatus' : request.POST.get('mallStatus'),          # 是否打开 商城 1为产品 2为商城
                'shangChengName' : request.POST.get('shangChengName'),
                'lunbotu' : request.POST.get('lunbotu'),
            }
            forms_obj = jichushezhi(resultData)
            if forms_obj.is_valid():
                formObjs = forms_obj.cleaned_data
                print('验证通过')
                if int(resultData.get('mallStatus')) == 2:
                    models.zgld_company.objects.filter(id=user_id).update(shopping_type=2)
                # if userObjs:
                userObjs.update(
                    shangChengName=formObjs.get('shangChengName'),
                    lunbotu=formObjs.get('lunbotu'),
                )
                response.msg = '修改成功'
                # else:
                #     models.zgld_shangcheng_jichushezhi.objects.create(
                #         shangChengName=formObjs.get('shangChengName'),
                #         lunbotu=formObjs.get('lunbotu'),
                #     )
                #     response.msg = '创建成功'
                response.code = 200
                response.data = ''
            else:
                response.code = 301
                response.msg = '未通过'
                response.data = json.loads(forms_obj.errors.as_json())
        if oper_type == 'zhifupeizhi':
            resultData = {
                'shangHuHao': request.POST.get('shangHuHao'),
                'shangHuMiYao': request.POST.get('shangHuMiYao'),
                'zhengshu': request.POST.get('zhengshu'),
            }
            forms_obj = zhifupeizhi(resultData)
            if forms_obj.is_valid():
                print('支付配置 验证成功')
                formObjs = forms_obj.cleaned_data
                zhengShuPath = formObjs.get('zhengshu')
                # if userObjs:
                userObjs.update(
                    shangHuHao=formObjs.get('shangHuHao'),
                    shangHuMiYao=formObjs.get('shangHuMiYao'),
                    zhengshu=zhengShuPath
                )
                response.msg = '修改成功'
                # else:
                #     models.zgld_shangcheng_jichushezhi.objects.create(
                #         shangHuHao=formObjs.get('shangHuHao'),
                #         shangHuMiYao=formObjs.get('shangHuMiYao'),
                #         zhengshu=zhengShuPath
                #     )
                #     response.msg = '创建成功'
                zhengshupath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + '/' + zhengShuPath
                file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'secretKeyFile') + '/' + formObjs.get('shangHuHao')
                file_zip = zipfile.ZipFile(zhengshupath, 'r')
                for file in file_zip.namelist():
                    file_zip.extract(file, r'{}'.format(file_dir))
                file_zip.close()
                os.remove(zhengShuPath)
                userObjs.update(zhengshu=file_dir)
                response.code = 200
                response.data = ''
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())

        if oper_type == 'yongjinshezhi':
            resultData = {
                'yongjin': request.POST.get('yongjin'),
            }
            forms_obj = yongjinshezhi(resultData)
            if forms_obj.is_valid():
                formObjs = forms_obj.cleaned_data
                # if userObjs:
                userObjs.update(
                    yongjin=formObjs.get('yongjin')
                )
                response.msg = '修改成功'
                # else:
                #     models.zgld_shangcheng_jichushezhi.objects.create(
                #         yongjin=formObjs.get('yongjin'),
                #     )
                response.code = 200
                response.data = ''
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
