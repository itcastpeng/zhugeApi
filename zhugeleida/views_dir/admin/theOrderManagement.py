from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import UpdateForm, SelectForm 
import json, base64, datetime, time
from django.db.models import Q
import xlwt,os

# 后台订单查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def theOrder(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        q = Q()
        yewuyuan = request.GET.get('yewuyuan')                          # 业务员模糊匹配
        dingdanbianhao = request.GET.get('dingdanbianhao')              # 订单编号
        goodsName = request.GET.get('goodsName')                        # 商品名称模糊匹配
        start_createDate = request.GET.get('start_createDate')          # 开始创建时间
        stop_createDate = request.GET.get('stop_createDate')            # 结束创建时间
        theOrderStatus = request.GET.get('theOrderStatus')              # 订单状态
        startCompletionTime = request.GET.get('startCompletionTime')    # 开始完成时间
        stopCompletionTime = request.GET.get('stopCompletionTime')      # 结束完成时间

        if start_createDate and stop_createDate:
            q.add(Q(createDate__gte=start_createDate) & Q(createDate__lte=stop_createDate), Q.AND)
        if startCompletionTime and stopCompletionTime:
            q.add(Q(stopDateTime__gte=startCompletionTime) & Q(stopDateTime__lte=stopCompletionTime), Q.AND)
        if theOrderStatus:
            q.add(Q(theOrderStatus=theOrderStatus), Q.AND)
        if yewuyuan:
            q.add(Q(yewuUser_id=yewuyuan), Q.AND)
        if dingdanbianhao:
            q.add(Q(orderNumber__contains=dingdanbianhao), Q.AND)
        if goodsName:
            q.add(Q(goodsName__contains=goodsName), Q.AND)
        print('q)------------> ',q)

        u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
        company_id = u_idObjs[0].company_id


        objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli', 'yewuUser').filter(
            gongsimingcheng_id=company_id
        ).filter(q).order_by('-createDate')

        objsCount = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        otherData = []
        for obj in objs:

            yewuUser = ''
            yewu = ''
            if obj.yewuUser:
                yewuUser = obj.yewuUser.username
                yewu = obj.yewuUser_id
            shouhuoren = ''
            if obj.shouHuoRen:
                decode_username = base64.b64decode(obj.shouHuoRen.username)
                shouhuoren = str(decode_username, 'utf-8')
            # topLunBoTu = ''
            # if obj.shangpinguanli.topLunBoTu:
            #     topLunBoTu = json.loads(obj.shangpinguanli.topLunBoTu)

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


            # topLunBoTu = json.loads(topLunBoTu)

            detailePicture = ''
            if objs[0].detailePicture:
                detailePicture = json.loads(objs[0].detailePicture)

            countPrice = 0
            if obj.goodsPrice:
                countPrice = obj.goodsPrice * obj.unitRiceNum
            otherData.append({
                'id':obj.id,
                'goodsName' : obj.goodsName,
                'goodsPrice':obj.goodsPrice,
                'countPrice':countPrice,
                'yingFuKuan':obj.yingFuKuan,
                'youhui':obj.yongJin,
                'yewuyuan_id':yewu,
                'yewuyuan':yewuUser,
                'unitRiceNum':obj.unitRiceNum,
                'yongjin':obj.yongJin,
                'orderNumber':obj.orderNumber,
                'shouHuoRen_id':obj.shouHuoRen_id,
                'shouHuoRen':shouhuoren,
                'status':obj.get_theOrderStatus_display(),
                'createDate':obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                'lunbotu':topLunBoTu,
                'detailePicture':detailePicture,
                'phoneNumber':obj.phone
            })
        response.data = {
            'otherData':otherData,
            'objsCount':objsCount,
        }
        response.msg = '查询成功'
        response.code = 200

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 后台订单操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def theOrderOper(request, oper_type, o_id):         # 修改订单基本信息
    response = Response.ResponseObj()
    if request.method == 'POST':
        # 修改订单状态
        if oper_type == 'update':
            otherData = {
                'o_id': o_id,
                # 'countPrice': obj.countPrice,
                'yingFuKuan': request.POST.get('yingFuKuan'),
                'youhui': request.POST.get('youhui'),
                'yewuyuan_id': request.POST.get('yewuyuan_id'),
                'yongjin': request.POST.get('yongjin'),
                # 'peiSong': request.POST.get('peiSong'),
                'shouHuoRen_id': request.POST.get('shouHuoRen_id'),
                'phoneNumber': request.POST.get('phoneNumber')    # 电话
            }
            forms_obj = UpdateForm(otherData)
            if forms_obj.is_valid():
                print('验证通过')
                print(forms_obj.cleaned_data)
                dingDanId = forms_obj.cleaned_data.get('o_id')
                yongjin = 0
                if otherData.get('yongjin'):
                    yongjin = otherData.get('yongjin')
                youhui = 0
                if otherData.get('youhui'):
                    youhui = otherData.get('youhui')
                models.zgld_shangcheng_dingdan_guanli.objects.filter(
                    id=dingDanId
                ).update(
                    yingFuKuan=otherData.get('yingFuKuan'),
                    youHui=youhui,
                    yewuUser_id=otherData.get('yewuyuan_id'),
                    yongJin=yongjin,
                    # peiSong=otherData.get('peiSong'),
                    shouHuoRen_id=otherData.get('shouHuoRen_id'),
                    phone=otherData.get('phoneNumber')
                )
                response.code = 200
                response.msg = '修改成功'
                response.data = ''
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 查询所有状态
        if oper_type == 'selectStatus':
            objs = models.zgld_shangcheng_dingdan_guanli
            statusData = []
            for i in objs.order_status:
                statusData.append({
                    'value':i[0],
                    'lable':i[1]
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = statusData

        # 修改时查询所有 订单业务员
        elif oper_type == 'selectYeWu':
            user_id = request.GET.get('user_id')
            company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            # companyObjs = models.zgld_company.objects.filter(id=company_id)
            yewuObjs = models.zgld_admin_userprofile.objects.filter(company_id=company_id)
            otherData = []
            for yewuObj in yewuObjs:
                otherData.append({
                    'value': yewuObj.id,
                    'lable':yewuObj.login_user
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = otherData


        # 生成资金记录Excel表格
        elif oper_type == 'generate_theOrder_excel':
            company_id = request.GET.get('company_id')

            ## 搜索条件
            start_time = request.GET.get('start_time')
            end_time = request.GET.get('end_time')

            q1 = Q()
            q1.connector = 'and'
            q1.children.append(('gongsimingcheng_id', company_id))

            if start_time:
                q1.add(Q(**{'createDate__gte': start_time}), Q.AND)
            if end_time:
                q1.add(Q(**{'createDate__lte': end_time}), Q.AND)

            data_list = [['编号', '订单号', '商品名称', '单价/数量', '总价','应付','业务员','手机号','收货人','状态','创建时间']]
            book = xlwt.Workbook()  # 新建一个excel

            objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli', 'yewuUser').filter(q1).order_by('-createDate')

            index = 0
            for obj in objs:
                index = index + 1
                yewuUser = ''
                yewu = ''
                if obj.yewuUser:
                    yewuUser = obj.yewuUser.username
                    yewu = obj.yewuUser_id
                shouhuoren = ''
                if obj.shouHuoRen:
                    decode_username = base64.b64decode(obj.shouHuoRen.username)
                    shouhuoren = str(decode_username, 'utf-8')


                if obj.goodsPrice:
                    countPrice = obj.goodsPrice * obj.unitRiceNum
                    data_list.append([
                        index,
                        obj.orderNumber,  # 订单号
                        obj.goodsName,      #商品名称
                        obj.goodsPrice + '/'+ obj.unitRiceNum,   #单价/数量
                        countPrice,       # 总价
                        obj.yingFuKuan,   # 应付
                        yewuUser,         # 业务员
                        obj.phone,        # 手机号
                        shouhuoren, #收货人
                        obj.get_theOrderStatus_display(),
                        obj.createDate.strftime('%Y-%m-%d %H:%M:%S')
                    ])

            print('----data_list -->>', data_list)

            sheet = book.add_sheet('sheet1')  # 添加一个sheet页
            row = 0  # 控制行
            for stu in data_list:
                col = 0  # 控制列
                for s in stu:  # 再循环里面list的值，每一列
                    sheet.write(row, col, s)
                    col += 1
                row += 1

            excel_name = '订单记录_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            download_excel_path = 'http://api.zhugeyingxiao.com/' + os.path.join('statics', 'zhugeleida', 'fild_upload',
                                                                                 '{}.xlsx'.format(excel_name))
            book.save(os.path.join(os.getcwd(), 'statics', 'zhugeleida', 'fild_upload', '{}.xlsx'.format(excel_name)))
            response.data = {'download_excel_path': download_excel_path}
            response.code = 200
            response.msg = '生成成功'


        else:
                response.code = 402
                response.msg = "请求异常"

    return JsonResponse(response.__dict__)




