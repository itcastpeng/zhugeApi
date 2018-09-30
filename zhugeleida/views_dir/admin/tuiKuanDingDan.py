from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.tuiKuanDingDan_verify import AddForm, SelectForm
import json, base64
from django.db.models import Q

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def tuiKuanDingDanShow(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        status = request.GET.get('status')
        u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
        xiaochengxu_id = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
        q = Q()
        if status:
            q.add(Q(tuiKuanStatus=status), Q.AND)

        objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.select_related(
            'orderNumber'
        ).filter(
            orderNumber__shangpinguanli__parentName__xiaochengxu_app__xiaochengxuApp_id=xiaochengxu_id
        ).filter(q)

        objsCount = objs.count()
        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]
        otherData = []
        for obj in objs:
            tuikuan = ''
            if obj.tuiKuanDateTime:
                tuikuan = obj.tuiKuanDateTime.strftime('%Y-%m-%d %H:%M:%S')
            otherData.append({
                'id':obj.id,
                'orderNumber_id':obj.orderNumber_id,
                'orderNumber':obj.orderNumber.orderNumber,
                'tuiKuanYuanYin':obj.tuiKuanYuanYin,
                'shengChengDateTime':obj.shengChengDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                'tuiKuanDateTime':tuikuan,
                'tuiKuanStatus':obj.tuiKuanStatus,
                'tuikuanzhanghao':'123456',
                'tuikuanjine': obj.orderNumber.yingFuKuan,
                'statusName':obj.get_tuiKuanStatus_display()
            })
            response.data = {
                'otherData':otherData,
                'objsCount':objsCount,
            }
        response.code = 200
        response.msg = '查询成功'
    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)





@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def tuiKuanDingDanOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':
        if oper_type == 'add':
            otherData = {
                'orderNumber':request.POST.get('orderNumber'),
                'tuiKuanYuanYin':request.POST.get('tuiKuanYuanYin'),
            }
            forms_obj = AddForm(otherData)
            if forms_obj.is_valid():
                print('验证通过')
                formObjs = forms_obj.cleaned_data
                models.zgld_shangcheng_tuikuan_dingdan_management.objects.create(
                    orderNumber_id=formObjs.get('orderNumber'),
                    tuiKuanYuanYin=formObjs.get('tuiKuanYuanYin')
                )
                response.code = 200
                response.msg = '添加退款订单成功！'
                response.data = ''
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == 'updateStatus':
            status = request.POST.get('status')
            objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(id=o_id)
            if status:
                if int(status) == 1:
                    objs.update(tuiKuanStatus=2)
                elif int(status) == 2:
                    objs.update(tuiKuanStatus=3)
                else:
                    objs.update(tuiKuanStatus=4)
                response.code = 200
                response.msg = '修改成功'
                response.data = ''
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)




