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
            u_id = request.POST.get('u_id')
            objs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(id=o_id)
            if status:
                if int(status) == 1:
                    objs.update(tuiKuanStatus=2)
                    response.msg = '修改成功'
                # 调用微信接口 申请退款
                elif int(status) == 2:
                    objs.update(tuiKuanStatus=5) # 更新状态 退款中
                    if u_id:
                        # 获取appid
                        u_idObjs = models.zgld_admin_userprofile.objects.filter(id=u_id)
                        xiaochengxu_app = models.zgld_xiaochengxu_app.objects.filter(
                            company_id=u_idObjs[0].company_id)
                        appid = xiaochengxu_app[0].authorization_appid   # 真实数据appid
                        jiChuSheZhiObjs = models.zgld_shangcheng_jichushezhi.objects.filter(
                            xiaochengxuApp_id=xiaochengxu_app[0].id)

                        SHANGHUKEY = 'dNe089PsAVjQZPEL7ciETtj0DNX5W2RA'
                        TUIKUANDANHAO = 123541116516165156
                        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
                        jine = 0
                        if objs[0].orderNumber.yingFuKuan:
                            jine = int((objs[0].orderNumber.yingFuKuan) *100)
                        print('jine===================> ',jine)
                        result_data = {
                            'appid': 'wx1add8692a23b5976',                               # appid
                            # 'appid': appid,                                            # 真实数据appid
                            'mch_id': '1513325051',                                      # 商户号
                            # 'mch_id': jiChuSheZhiObjs[0].shangHuHao,                   # 商户号真实数据
                            'nonce_str': prepaidManagement.generateRandomStamping(),     # 32位随机值a
                            'out_trade_no': '2018100814582101197912',             # 订单号
                            # 'out_trade_no': objs[0].orderNumber.orderNumber,             # 订单号
                            'out_refund_no': TUIKUANDANHAO,                              # 退款单号
                            'total_fee': jine,                             # 订单金额
                            'refund_fee': jine,                            # 退款金额
                        }

                        stringSignTemp = prepaidManagement.shengchengsign(result_data, SHANGHUKEY)
                        result_data['sign'] = prepaidManagement.md5(stringSignTemp).upper()
                        xml_data = prepaidManagement.toXml(result_data)
                        print('xml_data-----------> ',xml_data)

                        p = 0
                        ret = requests.post(url, data=xml_data, files={'filename':p}, verify='/tmp/test.cert')
                        print(ret.text)


                        # ret.encoding = 'utf8'
                        # DOMTree = xmldom.parseString(ret.text)
                        # collection = DOMTree.documentElement
                        # return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
                        # print('return_code----------> ', return_code)

                        response.msg = '修改成功'

                    else:
                        response.msg = '无u_id'
                else:
                    objs.update(tuiKuanStatus=4)
                    response.msg = '退款失败！'
                response.code = 200
                response.data = ''
    else:
        response.code = 402
        response.msg = "请求异常"
    print('response------------> ',response)
    return JsonResponse(response.__dict__)




