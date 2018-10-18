from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import UpdateForm, SelectForm 
import json, base64
from django.db.models import Q


@csrf_exempt
@account.is_token(models.zgld_customer)
def theOrderShow(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    u_id = request.GET.get('u_id')
    if forms_obj.is_valid():
        q = Q()
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        detailId = request.GET.get('detailId')
        orderStatus = request.GET.get('orderStatus')
        if orderStatus:
            if int(orderStatus) == 1:
                q.add(Q(theOrderStatus=1) | Q(theOrderStatus=11), Q.AND)
            elif int(orderStatus) == 2:
                q.add(Q(theOrderStatus=9) | Q(theOrderStatus=10), Q.AND)
            else:
                q.add(Q(theOrderStatus=8), Q.AND)
        if detailId:
            q.add(Q(id=detailId), Q.AND)
        objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli').filter(q).filter(shouHuoRen_id=user_id, logicDelete=0) # 小程序用户只能查看自己的订单
        objsCount = objs.count()
        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]
        otherData = []
        for obj in objs:
            tuikuanObj = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=obj.id, logicDelete=0)
            username = ''
            yewu = ''
            if obj.yewuUser:
                username = obj.yewuUser.username
                yewu = obj.yewuUser_id
            tuikuan = 0
            if tuikuanObj:
                tuikuan = 1
            # 轮播图
            topLunBoTu = ''
            if obj.shangpinguanli.topLunBoTu:
                topLunBoTu = json.loads(obj.shangpinguanli.topLunBoTu)
            shouhuoren = ''         # 收货人
            shouHuoRen_id = ''      # 收货人ID
            if obj.shouHuoRen_id:
                shouHuoRen_id = obj.shouHuoRen_id
                decode_username = base64.b64decode(obj.shouHuoRen.username)
                shouhuoren = str(decode_username, 'utf-8')
            countPrice = 0
            if obj.goodsPrice:
                countPrice =  obj.goodsPrice * obj.unitRiceNum
            detailePicture = ''
            if objs[0].detailePicture:
                detailePicture = json.loads(objs[0].detailePicture)
            otherData.append({
                'goodsPicture':topLunBoTu,
                'id':obj.id,
                # 'unitRiceNum':obj.unitRiceNum,
                'goodsName' : obj.goodsName,
                'goodsPrice':obj.goodsPrice,
                'countPrice':countPrice,
                'yingFuKuan':obj.yingFuKuan,
                'youhui':obj.yongJin,
                'yewuyuan_id':yewu,
                'yewuyuan':username,
                'yongjin':obj.yongJin,
                'peiSong':obj.peiSong,
                'shouHuoRen_id':shouHuoRen_id,
                'shouHuoRen':shouhuoren,
                'status':obj.get_theOrderStatus_display(),
                'statusId': obj.theOrderStatus,
                'createDate':obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                'tuikuan':tuikuan,
                'detailePicture':detailePicture,
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
def theOrderOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':
        # if oper_type == 'update':
        #     otherData = {
        #         'o_id': o_id,
        #         # 'countPrice': obj.countPrice,
        #         'yingFuKuan': request.POST.get('yingFuKuan'),
        #         'youhui': request.POST.get('youhui'),
        #         'yewuyuan_id': request.POST.get('yewuyuan_id'),
        #         'yongjin': request.POST.get('yongjin'),
        #         'peiSong': request.POST.get('peiSong'),
        #         'shouHuoRen_id': request.POST.get('shouHuoRen_id'),
        #     }
        #     forms_obj = UpdateForm(otherData)
        #     if forms_obj.is_valid():
        #         print('验证通过')
        #         print(forms_obj.cleaned_data)
        #         dingDanId = forms_obj.cleaned_data.get('o_id')
        #         models.zgld_shangcheng_dingdan_guanli.objects.filter(
        #             id=dingDanId
        #         ).update(
        #             yingFuKuan=otherData.get('yingFuKuan'),
        #             youHui=otherData.get('youhui'),
        #             yewuUser_id=otherData.get('yewuyuan_id'),
        #             yongJin=otherData.get('yongjin'),
        #             peiSong=otherData.get('peiSong'),
        #             shouHuoRen_id=otherData.get('shouHuoRen_id')
        #         )
        #         response.code = 200
        #         response.msg = '修改成功'
        #         response.data = ''
        #     else:
        #         response.code = 301
        #         response.msg = json.loads(forms_obj.errors.as_json())
        # 确认收货
        if oper_type == 'querenshouhuo':
            tuiKuanId = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=o_id)
            objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=o_id)
            if tuiKuanId:
                response.code = 301
                response.msg = '退款中, 无法确认收货！'
            else:
                otherStatus = objs[0].theOrderStatus
                if int(otherStatus) != 8:
                    response.code = 301
                    response.msg = '交易未成功,无法收货！'
                else:
                    response.msg = '已完成'
                    response.code = 200
                    objs.update(theOrderStatus=7)

        # 取消订单
        elif oper_type == 'CancelTheOrder':
            orderObjs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=o_id)
            status = int(orderObjs[0].theOrderStatus)
            if status and (status == 1 or status == 11):
                orderObjs.update(theOrderStatus=10)
                response.code = 200
                response.msg = '已取消订单'
            else:
                response.code = 301
                response.msg = '订单无法取消'

        elif oper_type == 'deleteOrder':
            print('=-==========================================')
            orderObjs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=o_id)
            if orderObjs:
                status = int(orderObjs[0].theOrderStatus)
                print('status=============>',status)
                if status in [1, 10]:
                    orderObjs.update(logicDelete=1)
                    response.code = 200
                    response.msg = '删除成功'
                elif status in [8, 9]:
                    tuiKuanObjs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=o_id)
                    if tuiKuanObjs:
                        tuikuanstatus = int(tuiKuanObjs[0].tuiKuanStatus)
                        if tuikuanstatus in [2, 3]:
                            orderObjs.update(logicDelete=1)
                            tuiKuanObjs.update(logicDelete=1)
                        else:
                            response.code = 301
                            response.msg = '该订单有退款业务, 不可删除！'
                    else:
                        orderObjs.update(logicDelete=1)
                        response.code = 200
                        response.msg = '删除成功'
                else:
                    response.code = 301
                    response.msg = '删除失败, 当前状态不可删除'
            else:
                response.code = 301
                response.msg = '无此订单'
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)




