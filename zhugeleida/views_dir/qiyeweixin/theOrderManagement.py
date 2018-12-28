from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import UpdateForm, SelectForm
import json, base64, datetime
from django.db.models import Q


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def theOrder(request):
    response = Response.ResponseObj()

    if request.method == 'GET':

        user_id = request.GET.get('user_id')
        # u_id = request.GET.get('u_id')
        # company_id = request.GET.get('company_id')
        forms_obj = SelectForm(request.GET)

        if forms_obj.is_valid():
            q = Q()
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            # detailId = request.GET.get('detailId')
            time_section = request.GET.get('time_section')
            orderStatus = request.GET.get('orderStatus')
            if orderStatus:
                if int(orderStatus) == 0:
                    q.add(Q(theOrderStatus__in=[1,3,4,5,9,10]), Q.AND)

                elif int(orderStatus) == 1:
                    q.add(Q(theOrderStatus__in=[2,8]), Q.AND)


            if time_section: # 2018-12
                year = int(time_section.split('-')[0])
                month = int(time_section.split('-')[1]) + 1
                start_time = time_section + '-01'
                if month == 13:
                    month = '01'
                    year = year + 1

                end_time = str(year) + "-"+ str(month) + '-' + '01'
                print('------ 开始时间 | 结束时间 ---->>',start_time,end_time)

                q.add(Q(**{'createDate__gte': start_time}), Q.AND)
                q.add(Q(**{'createDate__lt': end_time}), Q.AND)


            print('q=============> ', q)

            objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli').filter(q).filter(
                yewuUser_id=user_id, logicDelete=0).filter(q).order_by('-createDate')  #

            if objs:

                objsCount = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                otherData = []
                for obj in objs:
                    # tuikuanObj = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=obj.id, logicDelete=0)
                    username = ''
                    yewu = ''
                    if obj.yewuUser:
                        username = obj.yewuUser.username
                        yewu = obj.yewuUser_id

                    # 轮播图
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


                    shouhuoren = ''  # 收货人
                    shouHuoRen_id = ''  # 收货人ID
                    if obj.shouHuoRen_id:
                        shouHuoRen_id = obj.shouHuoRen_id
                        decode_username = base64.b64decode(obj.shouHuoRen.username)
                        shouhuoren = str(decode_username, 'utf-8')
                    countPrice = 0
                    if obj.goodsPrice:
                        countPrice = obj.goodsPrice * obj.unitRiceNum

                    detailePicture = ''
                    if objs[0].detailePicture:
                        detailePicture = json.loads(objs[0].detailePicture)

                    goodsId = obj.shangpinguanli_id
                    if not goodsId:
                        goodsId = obj.goods_id


                    otherData.append({
                        'goodsPicture': topLunBoTu,
                        'id': obj.id,
                        # 'unitRiceNum':obj.unitRiceNum,
                        'goodsId': goodsId,
                        'goodsName': obj.goodsName,
                        'goodsPrice': obj.goodsPrice,
                        'countPrice': countPrice,
                        'yingFuKuan': obj.yingFuKuan,
                        'youhui': obj.yongJin,
                        'yewuyuan_id': yewu,
                        'yewuyuan': username,
                        'yongjin': obj.yongJin,
                        # 'peiSong':obj.peiSong,
                        'shouHuoRen_id': shouHuoRen_id,
                        'shouHuoRen': shouhuoren,
                        'status': obj.get_theOrderStatus_display(),
                        'statusId': obj.theOrderStatus,
                        'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                        # 'tuikuan':tuikuan,         # 0为无退款   1为退款
                        # 'tuikuan_status':tuiKuanStatus,
                        'detailePicture': detailePicture,
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'otherData': otherData,
                    'objsCount': objsCount,
                }

            else:
                response.code = 302
                response.msg = '无数据'


        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_userprofile)
def theOrderOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':

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

            orderObjs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=o_id)
            if orderObjs:
                status = int(orderObjs[0].theOrderStatus)
                print('status=============>', status)
                if status in [1, 10]:
                    orderObjs.update(logicDelete=1)
                    response.code = 200
                    response.msg = '删除成功'
                elif status in [2, 3, 8, 9]:
                    tuiKuanObjs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=o_id)
                    if tuiKuanObjs:
                        orderObjs.update(logicDelete=1)
                        tuiKuanObjs.update(logicDelete=1)

                    else:
                        orderObjs.update(logicDelete=1)

                    response.code = 200
                    response.msg = '删除成功'

                else:
                    response.code = 301
                    response.msg = '删除失败,当前状态不可删除'
            else:
                response.code = 301
                response.msg = '无此订单'

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
