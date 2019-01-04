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
def tuiKuanDingDan(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)

    orderNumber_id = request.GET.get('orderNumber'),
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=orderNumber_id)
        objsCount = objs.count()
        print('objs---------->', objs)
        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]
        otherData = []

        if objs:
            for obj in objs:
                tuikuan = ''
                if obj.tuiKuanDateTime:
                    tuikuan = obj.tuiKuanDateTime.strftime('%Y-%m-%d %H:%M:%S')

                orderNumber_id =  obj.orderNumber_id
                topLunBoTu = ''
                if orderNumber_id:
                    _obj = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli', 'yewuUser').get(id=orderNumber_id)

                    topLunBoTu = []
                    if _obj.shangpinguanli_id:
                        topLunBoTu = _obj.shangpinguanli.topLunBoTu
                        # [{"url":"statics/zhugeleida/imgs/admin/goods/1545614722212.jpg"}]

                    else:
                        topLunBoTu = _obj.topLunBoTu


                    topLunBoTu = json.loads(topLunBoTu)
                    url = topLunBoTu[0].get('data')
                    if url:
                        url = url[0]

                    topLunBoTu = [{"url": url}]


                otherData.append({
                    'id': obj.id,
                    'orderNumber_id': orderNumber_id,
                    'orderNumber': obj.orderNumber.orderNumber,
                    'tuiKuanYuanYin': obj.get_tuiKuanYuanYin_display(),
                    'tuiKuanYuanYinId': obj.tuiKuanYuanYin,
                    'shengChengDateTime': obj.shengChengDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                    'tuiKuanDateTime': tuikuan,
                    'tuiKuanStatus': obj.orderNumber.get_theOrderStatus_display(),
                    'tuiKuanStatusId': obj.orderNumber.theOrderStatus,
                    'goodsName':obj.orderNumber.goodsName,

                    'tuiKuanPrice':obj.orderNumber.yingFuKuan,
                    'detailePicture':topLunBoTu,
                    'goodsNum':obj.orderNumber.unitRiceNum,
                    'goodsPrice':obj.orderNumber.goodsPrice

                })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'otherData':otherData,
                    'objsCount':objsCount,
                }

        else:

            objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli').filter(
                id=orderNumber_id,logicDelete=0).order_by('-createDate')  # 小程序用户只能查看自己的订单

            if objs:
                obj = objs[0]

                # 轮播图
                topLunBoTu = []
                if obj.shangpinguanli_id:
                    topLunBoTu = obj.shangpinguanli.topLunBoTu

                    # [{"url":"statics/zhugeleida/imgs/admin/goods/1545614722212.jpg"}]
                else:
                    topLunBoTu = obj.topLunBoTu

                topLunBoTu = json.loads(topLunBoTu)
                url = topLunBoTu[0].get('data')
                if url:
                    url = url[0]

                topLunBoTu = [{"url": url}]

                otherData.append({

                    'orderNumber_id': orderNumber_id,
                    'orderNumber': obj.orderNumber,
                    'tuiKuanYuanYin': '',
                    'tuiKuanYuanYinId': '',
                    'tuiKuanDateTime': '',
                    'shengChengDateTime': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),

                    'tuiKuanStatus': obj.get_theOrderStatus_display(),
                    'tuiKuanStatusId': obj.theOrderStatus,
                    'goodsName': obj.goodsName,

                    'tuiKuanPrice': obj.yingFuKuan,
                    'detailePicture': topLunBoTu,
                    'goodsNum': obj.unitRiceNum,
                    'goodsPrice': obj.goodsPrice

                })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'otherData': otherData,
                    'objsCount': objsCount,
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
                    tuikuandanhao = tuikuandanhao,
                )
                models.zgld_shangcheng_dingdan_guanli.objects.filter(
                    id=formObjs.get('orderNumber')
                ).update(
                    theOrderStatus=4
                )
                response.code = 200
                response.msg = '添加退款订单成功！'
                response.data = ''
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        if oper_type == 'selectYuanYin':
            objs = models.zgld_shangcheng_tuikuan_dingdan_management
            otherData = []
            for yuanyin in objs.tuikuanyuanyin_status:
                otherData.append({
                    'id':yuanyin[0],
                    'name':yuanyin[1]
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = otherData

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)




