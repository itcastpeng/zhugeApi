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
            orderNumber__shangpinguanli__parentName__mallSetting__xiaochengxuApp_id=xiaochengxu_id
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
                'tuiKuanYuanYinId':obj.tuiKuanYuanYin,
                'tuiKuanYuanYin':obj.get_tuiKuanYuanYin_display(),
                'shengChengDateTime':obj.shengChengDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                'tuiKuanDateTime':tuikuan,
                'tuiKuanStatus':obj.tuiKuanStatus,
                'tuikuanzhanghao':'123456',
                'tuikuanjine': obj.orderNumber.yingFuKuan,
                'statusNameId':obj.tuiKuanStatus,
                'statusName':obj.get_tuiKuanStatus_display(),
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
        elif oper_type == 'updateStatus':
            status = request.POST.get('status')
            user_id = request.GET.get('user_id')
            objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(id=o_id)
            if status:
                # if int(status) == 1:
                #     objs.update(tuiKuanStatus=2)
                #     response.msg = '修改成功'
                # 调用微信接口 申请退款
                other = []
                if int(status) == 2:
                    objs.update(tuiKuanStatus=4) # 更新状态 退款中
                    # 获取appid
                    u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
                    xiaochengxu_app = models.zgld_xiaochengxu_app.objects.filter(
                        company_id=u_idObjs[0].company_id)
                    appid = xiaochengxu_app[0].authorization_appid   # 真实数据appid
                    jiChuSheZhiObjs = models.zgld_shangcheng_jichushezhi.objects.filter(
                        xiaochengxuApp_id=xiaochengxu_app[0].id)

                    SHANGHUKEY = 'dNe089PsAVjQZPEL7ciETtj0DNX5W2RA'
                    url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
                    jine = 0
                    if objs[0].orderNumber.yingFuKuan:
                        jine = int((objs[0].orderNumber.yingFuKuan) *100)
                    dingdan = ''
                    if objs[0].orderNumber.orderNumber:
                        dingdan = objs[0].orderNumber.orderNumber
                    if objs[0].tuikuandanhao:
                        TUIKUANDANHAO = objs[0].tuikuandanhao
                        result_data = {
                            # 'appid': 'wx1add8692a23b5976',                             # appid
                            'appid': appid,                                              # 真实数据appid
                            'mch_id': '1513325051',                                      # 商户号
                            # 'mch_id': jiChuSheZhiObjs[0].shangHuHao,                   # 商户号真实数据
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

                        if return_code == 'SUCCESS':
                            if collection.getElementsByTagName("err_code_des"):
                                err_code_des = collection.getElementsByTagName("err_code_des")[0].childNodes[0].data
                                response.msg = err_code_des
                                return JsonResponse(response.__dict__)
                            else:
                                nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                objs.update(tuiKuanStatus=2, tuiKuanDateTime=nowTime)
                                response.msg = '退款成功'
                        else:
                            response.msg = '退款失败'
                            objs.update(tuiKuanStatus=3)
                    else:
                        response.msg = '无退款单号'
                else:
                    objs.update(tuiKuanStatus=3)
                    response.msg = '卖家拒绝退款'
                response.code = 200
                response.data = {'other':other}
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)




