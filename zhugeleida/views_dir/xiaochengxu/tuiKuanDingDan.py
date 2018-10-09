from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.tuiKuanDingDan_verify import AddForm, SelectForm
import json, base64, time, random


@csrf_exempt
@account.is_token(models.zgld_customer)
def tuiKuanDingDanShow(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    u_id = request.GET.get('u_id')
    orderNumber_id = request.GET.get('orderNumber'),
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=orderNumber_id)
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
                'id': obj.id,
                'orderNumber_id': obj.orderNumber_id,
                'orderNumber': obj.orderNumber.orderNumber,
                'tuiKuanYuanYin': obj.tuiKuanYuanYin,
                'shengChengDateTime': obj.shengChengDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                'tuiKuanDateTime': tuikuan,
                'tuiKuanStatus': obj.get_tuiKuanStatus_display(),
                'goodsName':obj.orderNumber.goodsName,
                'tuiKuanPrice':obj.orderNumber.yingFuKuan
            })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'otherData':otherData,
                'objsCount':objsCount,
            }
    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)

@csrf_exempt
@account.is_token(models.zgld_customer)
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
                ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
                shijianchuoafter5 = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
                tuikuandanhao = str(ymdhms) + shijianchuoafter5 + str(random.randint(10, 99))
                print('tuikuandanhao---------> ', tuikuandanhao)
                formObjs = forms_obj.cleaned_data
                models.zgld_shangcheng_tuikuan_dingdan_management.objects.create(
                    orderNumber_id=formObjs.get('orderNumber'),
                    tuiKuanYuanYin=formObjs.get('tuiKuanYuanYin'),
                    tuikuandanhao = tuikuandanhao
                )
                response.code = 200
                response.msg = '添加退款订单成功！'
                response.data = ''
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)




