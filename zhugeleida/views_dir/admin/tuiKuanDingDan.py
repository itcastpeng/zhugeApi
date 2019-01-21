from zhugeleida.forms.xiaochengxu.tuiKuanDingDan_verify import AddForm, SelectForm
from django.db.models import Q
from zhugeleida.views_dir.xiaochengxu import prepaidManagement
import uuid, time, json
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
import xml.dom.minidom as xmldom
import os, random, datetime
from zhugeleida.views_dir.mycelery_task.mycelery import record_money_process
import xlwt,os,datetime

# 退款单 查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def tuiKuanDingDan(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        status = request.GET.get('status')

        u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
        company_id =  u_idObjs[0].company_id

        q = Q()
        if status:
            q.add(Q(orderNumber__theOrderStatus=status), Q.AND)

        objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.select_related(
            'orderNumber'
        ).filter(orderNumber__gongsimingcheng_id=company_id).filter(q).order_by('-shengChengDateTime')

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
                'tuiKuanYuanYinId':obj.tuiKuanYuanYin,
                'tuiKuanYuanYin':obj.get_tuiKuanYuanYin_display(),
                'shengChengDateTime':obj.shengChengDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                'tuiKuanDateTime':tuikuan,
                'tuiKuanStatus':obj.orderNumber.theOrderStatus,
                'tuikuanzhanghao':'123456',
                'remark': obj.remark or '',
                'tuikuanjine': obj.orderNumber.yingFuKuan,
                'statusNameId':obj.orderNumber.theOrderStatus,
                'statusName':obj.orderNumber.get_theOrderStatus_display(),
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


# 退款单操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def tuiKuanDingDanOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':
        # 添加退款单
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
                print('tuikuandanhao---------> ',tuikuandanhao)

                formObjs = forms_obj.cleaned_data
                models.zgld_shangcheng_tuikuan_dingdan_management.objects.create(
                    orderNumber_id=formObjs.get('orderNumber'),
                    tuiKuanYuanYin=formObjs.get('tuiKuanYuanYin'),
                    tuikuandanhao=tuikuandanhao
                )
                response.code = 200
                response.msg = '添加退款订单成功！'
                response.data = ''
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改退款单状态
        elif oper_type == 'updateStatus':
            status = request.POST.get('status')
            user_id = request.GET.get('user_id')
            objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(id=o_id)
            if status and objs:

                # 调用微信接口 申请退款
                other = []
                orderNumber_id = objs[0].orderNumber_id
                dingdan_guanli_objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=orderNumber_id)

                if int(status) == 2 and dingdan_guanli_objs:

                    u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
                    xiaochengxu_app = models.zgld_xiaochengxu_app.objects.filter(
                        company_id=u_idObjs[0].company_id)
                    appid = xiaochengxu_app[0].authorization_appid   # 真实数据appid
                    jiChuSheZhiObjs = models.zgld_shangcheng_jichushezhi.objects.filter(
                        xiaochengxuApp_id=xiaochengxu_app[0].id)

                    # SHANGHUKEY = 'dNe089PsAVjQZPEL7ciETtj0DNX5W2RA'
                    SHANGHUKEY = jiChuSheZhiObjs[0].shangHuMiYao
                    company_id = jiChuSheZhiObjs[0].xiaochengxucompany_id
                    url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'

                    jine = 0
                    yingFuKuan = ''
                    if objs[0].orderNumber.yingFuKuan:
                        yingFuKuan = objs[0].orderNumber.yingFuKuan
                        jine = int((objs[0].orderNumber.yingFuKuan) *100)

                    dingdan = ''
                    shouHuoRen_id = ''
                    yewuUser_id = ''
                    if objs[0].orderNumber_id:
                        dingdan = objs[0].orderNumber.orderNumber
                        yewuUser_id = objs[0].orderNumber.yewuUser_id
                        shouHuoRen_id = objs[0].orderNumber.shouHuoRen_id

                    if objs[0].tuikuandanhao:
                        TUIKUANDANHAO = objs[0].tuikuandanhao
                        result_data = {
                            # 'appid': 'wx1add8692a23b5976',                             # appid
                            'appid': appid,                                              # 真实数据appid
                            # 'mch_id': '1513325051',                                      # 商户号
                            'mch_id': jiChuSheZhiObjs[0].shangHuHao,                   # 商户号真实数据
                            'nonce_str': prepaidManagement.generateRandomStamping(),     # 32位随机值a
                            # 'out_trade_no': '2018100814582101197912',                  # 订单号
                            'out_trade_no': dingdan,                                     # 线上订单号
                            'out_refund_no': TUIKUANDANHAO,                              # 退款单号
                            'total_fee': jine,                                           # 订单金额
                            'refund_fee': jine,                                          # 退款金额
                        }
                        other.append(result_data)
                        # print('result_data----------result_data--------------result_data------------->',result_data)
                        stringSignTemp = prepaidManagement.shengchengsign(result_data, SHANGHUKEY)
                        result_data['sign'] = prepaidManagement.md5(stringSignTemp).upper()
                        xml_data = prepaidManagement.toXml(result_data)
                        # print('xml_data-----------> ',xml_data)

                        BASE_DIR = jiChuSheZhiObjs[0].zhengshu
                        cret = os.path.join(BASE_DIR, 'apiclient_cert.pem')
                        key = os.path.join(BASE_DIR, 'apiclient_key.pem')

                        ret = requests.post(url, data=xml_data, cert=(cret, key))
                        ret.encoding = 'utf8'
                        print(ret.text)
                        DOMTree = xmldom.parseString(ret.text)
                        collection = DOMTree.documentElement

                        return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
                        #  通用的<xml><return_code><![CDATA[SUCCESS]]></return_code>

                        result_code = collection.getElementsByTagName("result_code")[0].childNodes[0].data
                        #  <result_code><![CDATA[SUCCESS]]></result_code> 或 <result_code><![CDATA[FAIL]]></result_code>


                        if return_code == 'SUCCESS' and result_code == 'SUCCESS':
                            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            objs.update(
                                tuiKuanDateTime=nowTime
                            )
                            dingdan_guanli_objs.update(
                                theOrderStatus=2, # (2, '退款完成'),
                            )

                            ### 商城退款后,记录流水
                            # record_data = {
                            #     'admin_user_id': user_id,
                            #     'user_id': yewuUser_id, # 业务员
                            #     'company_id': company_id,
                            #     'customer_id': shouHuoRen_id,
                            #     'transaction_amount': yingFuKuan,
                            #     'source': 3,  #  (3,'小程序')
                            #     'type': 6     #  (6,'商城退款')
                            # }
                            # print('record_data----->>',record_data)
                            # record_money_process(record_data)

                            response.code = 200
                            response.msg = '退款成功'

                        elif  return_code == 'SUCCESS' and result_code == 'FAIL':

                            err_msg = collection.getElementsByTagName("err_code_des")[0].childNodes[0].data
                            # <err_code_des><![CDATA[基本账户余额不足，请充值后重新发起]]></err_code_des>
                            # 记录返回的xml日志
                            objs.update(
                                remark=err_msg
                            )

                            dingdan_guanli_objs.update(         # (3, '退款失败'),
                                theOrderStatus=3,

                            )
                            response.code = 301
                            response.msg = '退款失败'

                    else:
                        response.code = 301
                        response.msg = '无退款单号'

                elif int(status) == 5:

                    dingdan_guanli_objs.update( # (5, '拒绝退款'),
                        theOrderStatus=5,
                    )
                    response.msg = '卖家拒绝退款'
                    response.code = 301


            else:
                response.code = 301
                response.msg = "退款订单不存在"



    else:


        ## 生成退款的Excel 表格
        if oper_type == 'generate_tuiKuan_Order_excel':
            company_id = request.GET.get('company_id')

            ## 搜索条件
            start_time = request.GET.get('start_time')
            end_time = request.GET.get('end_time')

            q1 = Q()
            q1.connector = 'and'
            q1.children.append(('orderNumber__gongsimingcheng_id', company_id))

            if start_time:
                q1.add(Q(**{'create_date__gte': start_time}), Q.AND)
            if end_time:
                q1.add(Q(**{'create_date__lte': end_time}), Q.AND)

            data_list = [['编号', '退款原因', '退款金额', '生成时间', '退款时间', '状态',]]
            book = xlwt.Workbook()  # 新建一个excel

            objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.select_related('orderNumber').filter(q1).order_by('-shengChengDateTime')

            index = 0
            for obj in objs:
                index = index + 1
                tuikuan = ''
                if obj.tuiKuanDateTime:
                    tuikuan = obj.tuiKuanDateTime.strftime('%Y-%m-%d %H:%M:%S')


                data_list.append([
                    index,
                    obj.get_tuiKuanYuanYin_display(),                                 # 退款原因
                    obj.orderNumber.yingFuKuan,                                       # 退款金额
                    obj.obj.shengChengDateTime.strftime('%Y-%m-%d %H:%M:%S'),         # 生成时间
                    tuikuan,                                                          # 退款时间
                    obj.orderNumber.get_theOrderStatus_display(),    # 状态
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

            excel_name = '退款订单记录_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            download_excel_path = 'http://api.zhugeyingxiao.com/' + os.path.join('statics', 'zhugeleida', 'fild_upload',
                                                                                 '{}.xlsx'.format(excel_name))
            book.save(os.path.join(os.getcwd(), 'statics', 'zhugeleida', 'fild_upload', '{}.xlsx'.format(excel_name)))
            response.data = {'download_excel_path': download_excel_path}
            response.code = 200
            response.msg = '生成生成'




    return JsonResponse(response.__dict__)




