from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.views_dir.xiaochengxu import prepaidManagement
from django import forms
import hashlib, random, xml.dom.minidom as xmldom, qrcode, uuid, time, json, requests, base64, datetime, os, zipfile

response = Response.ResponseObj()
yuzhifu = prepaidManagement


# 订单号生成
def dingdanhaoshengcheng():   # 规则： 当前年月日时分秒 + 当前时间戳后五位 + 10-99随机值
    ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
    shijianchuoafter5 = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
    dingdanhao = str(ymdhms) + shijianchuoafter5 + str(random.randint(10, 99))
    return dingdanhao

# 关注发放红包 form验证
class guanZhuForm(forms.Form):
    SHANGHUKEY = forms.CharField(
        required=True,
        error_messages={
            'required': "商户KEY不能为空"
        }
    )
    total_fee = forms.CharField(
        required=True,
        error_messages={
            'required': "钱数不能为空"
        }
    )
    appid = forms.CharField(
        required=True,
        error_messages={
            'required': "小程序id不能为空"
        }
    )
    mch_id = forms.CharField(
        required=True,
        error_messages={
            'required': "商户号不能为空"
        }
    )
    openid = forms.CharField(
        required=True,
        error_messages={
            'required': "微信标识openid不能为空"
        }
    )
    send_name = forms.CharField(
        required=True,
        error_messages={
            'required': "商户名称不能为空"
        }
    )
    act_name = forms.CharField(
        required=True,
        error_messages={
            'required': "活动名称不能为空"
        }
    )
    remark = forms.CharField(
        required=True,
        error_messages={
            'required': "备注不能为空"
        }
    )
    wishing = forms.CharField(
        required=True,
        error_messages={
            'required': "红包祝福语不能为空"
        }
    )
    def clean_total_fee(self):
        total_fee = self.data.get('total_fee')
        if float(total_fee) >= 1:
            total_fee = int(float(total_fee) * 100)
            return total_fee
        else:
            self.add_error('total_fee', '钱数不能小于1元！')
    def clean_mch_id(self):
        mch_id = self.data.get('mch_id')
        if len(mch_id) > 32:
            self.add_error('mch_id', '商户号不能超过32位！')
        else:
            return mch_id
    def clean_appid(self):
        appid = self.data.get('appid')
        if len(appid) > 32:
            self.add_error('appid', '公众号appid不能超过32位！')
        else:
            return appid
    def clean_send_name(self):
        send_name = self.data.get('send_name')
        if len(send_name) > 32:
            self.add_error('send_name', '发送者名称不能超过32位！')
        else:
            return send_name
    def clean_openid(self):
        openid = self.data.get('openid')
        if len(openid) > 32:
            self.add_error('openid', '用户唯一标识openid不能超过32位！')
        else:
            return openid
    def clean_wishing(self):
        wishing = self.data.get('wishing')
        if len(wishing) > 128:
            self.add_error('wishing', '红包祝福语不能超过128位！')
        else:
            return wishing
    def clean_act_name(self):
        act_name = self.data.get('act_name')
        if len(act_name) > 32:
            self.add_error('act_name', '活动名称不能超过32位！')
        else:
            return act_name
    def clean_remark(self):
        remark = self.data.get('remark')
        if len(remark) > 256:
            self.add_error('remark', '备注不能超过256位！')
        else:
            return remark

# 关注发放红包(实时发送)
# @csrf_exempt
# @account.is_token(models.zgld_customer)
def focusOnIssuedRedEnvelope(resultDict):
    # if request.method == 'POST':
    url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'  # 微信支付接口
        # 获取IP
        # if request.META.get('HTTP_X_FORWARDED_FOR'):
        #     ip = request.META.get('HTTP_X_FORWARDED_FOR')
        # elif request.META.get('REMOTE_ADDR'):
        #     ip = request.META.get('REMOTE_ADDR')
        # else:
        #     ip = '0.0.0.0'
        # client_ip = ip
        # dataDict = {
        #     'SHANGHUKEY' : request.POST.get('shanghukey'),       # 商户秘钥KEY
        #     'total_fee' : request.POST.get('total_fee'),         # 钱数
        #     'appid' : request.POST.get('appid'),                 # 小程序ID
        #     'mch_id' : request.POST.get('mch_id'),               # 商户号
        #     'openid' : request.POST.get('openid'),               # 微信用户唯一标识
        #     'send_name' : request.POST.get('send_name'),         # 商户名称 中文32
        #     'act_name' : request.POST.get('act_name'),           # 动名称 32长度
        #     'remark' : request.POST.get('remark'),               # 备注信息 256长度
        #     'wishing' : request.POST.get('wishing'),             # 红包祝福语 128长度
        # }
    client_ip = resultDict.get('client_ip'),  # 用户IP
    dataDict = {
        'SHANGHUKEY': resultDict.get('shanghukey'), # 商户秘钥KEY
        'total_fee': resultDict.get('total_fee'),   # 钱数
        'appid': resultDict.get('appid'),           # 小程序ID
        'mch_id': resultDict.get('mch_id'),         # 商户号
        'openid': resultDict.get('openid'),         # 微信用户唯一标识
        'send_name': resultDict.get('send_name'),   # 商户名称 中文32
        'act_name': resultDict.get('act_name'),     # 动名称 32长度
        'remark': resultDict.get('remark'),         # 备注信息 256长度
        'wishing': resultDict.get('wishing'),       # 红包祝福语 128长度
    }
    forms_obj = guanZhuForm(dataDict)
    if forms_obj.is_valid():
        print('------ forms_obj 验证后的数据----->>',json.dumps(forms_obj.cleaned_data))

        objsForm = forms_obj.cleaned_data
        redEnvelope = models.zgld_red_envelope_to_issue.objects.filter(articleId__isnull=True)

        cunzaiObjs = redEnvelope.filter(mch_id=objsForm.get('mch_id'), re_openid=objsForm.get('openid'))
        if cunzaiObjs:
            print('-------重复关注公众号---->>')
            response.code = 500
            response.msg = '重复关注公众号'
            return JsonResponse(response.__dict__)
        else:
            print('---- cunzaiObjs ! --->>',cunzaiObjs)
            nowDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            redEnvelopeObjs = redEnvelope.create(
                wxappid = objsForm.get('appid'),                        # appid
                mch_id = objsForm.get('mch_id'),                        # 商户号
                re_openid = objsForm.get('openid'),                 # 用户唯一标识
                total_amount = int(objsForm.get('total_fee')) / 100,  # 付款金额 1:100
                mch_billno = dingdanhaoshengcheng(),                  # 订单号
                send_name = objsForm.get('send_name'),                  # 商户名称 中文
                act_name = objsForm.get('act_name'),                    # 活动名称 32长度
                remark = objsForm.get('remark'),                        # 备注信息 256长度
                client_ip = client_ip,                                  # 终端IP
                wishing = objsForm.get('wishing'),                      # 红包祝福语 128长度
                createDate=nowDateTime
            )
            SHANGHUKEY = objsForm.get('SHANGHUKEY')
            result_data = {
                'nonce_str': yuzhifu.generateRandomStamping(),              # 32位随机值a
                'wxappid': objsForm.get('appid'),                           # appid
                'mch_id':objsForm.get('mch_id'),                            # 商户号
                're_openid': objsForm.get('openid'),                        # 用户唯一标识
                'total_amount': objsForm.get('total_fee'),                  # 付款金额 1:100
                'mch_billno': dingdanhaoshengcheng(),                       # 订单号
                'client_ip' : client_ip,                                    # 终端IP
                'total_num':1,                                              # 红包发放总人数
                'send_name':objsForm.get('send_name'),                      # 商户名称 中文
                'act_name':objsForm.get('act_name'),                        # 活动名称 32长度
                'remark':objsForm.get('remark'),                            # 备注信息 256长度
                'wishing':objsForm.get('wishing'),                          # 红包祝福语 128长度
                }
            print('---- 支付的 result_data ------>>',json.dumps(result_data))

            stringSignTemp = yuzhifu.shengchengsign(result_data, SHANGHUKEY)
            result_data['sign'] = yuzhifu.md5(stringSignTemp).upper()
            xml_data = yuzhifu.toXml(result_data).encode('utf8')
            # 获取商户证书
            shangHuObjs = models.zgld_shangcheng_jichushezhi.objects.filter(shangHuHao=objsForm.get('mch_id'))
            if shangHuObjs:
                path = shangHuObjs[0].zhengshu
                zhengshupath = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                file_dir = zhengshupath + '/' + path
                cret = os.path.join(file_dir, 'apiclient_cert.pem')
                key = os.path.join(file_dir, 'apiclient_key.pem')
                ret = requests.post(url, data=xml_data, cert=(cret, key))
                print(ret.text)
                DOMTree = xmldom.parseString(ret.text)
                collection = DOMTree.documentElement
                return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
                print('---------  发放红包 解析后的xml内容 ------------> ',return_code,collection)
                if return_code == 'SUCCESS':        # 判断预支付返回参数 是否正确
                    redEnvelope.filter(id=redEnvelopeObjs.id).update(issuingState=1)
                    response.code = 200
                    response.msg = '发放红包成功'
                else:
                    print('----- 发放红包失败 ----->>')
                    redEnvelope.filter(id=redEnvelopeObjs.id).update(issuingState=2)
                    response.code = 500
                    response.msg = '发放红包失败'

            else:
                print('---- 没有商户证书, 请前往商城设置册证书！--->')
                response.code = 500
                response.msg = '没有商户证书, 请前往商城设置册证书！'
    else:
        print('---- [关注领红包form报错]---->>',json.loads(forms_obj.errors.as_json()))
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)

# 文章转发发放红包
# @csrf_exempt
# @account.is_token(models.zgld_customer)
def articleForwardingRedEnvelope(resultDict):
    # if request.method == 'POST':
    url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'  # 微信支付接口
        # 获取IP
        # if request.META.get('HTTP_X_FORWARDED_FOR'):
        #     ip = request.META.get('HTTP_X_FORWARDED_FOR')
        # elif request.META.get('REMOTE_ADDR'):
        #     ip = request.META.get('REMOTE_ADDR')
        # else:
        #     ip = '0.0.0.0'
        # client_ip = ip
        # articleId = request.POST.get('articleId')         # 文章ID
        # dataDict = {
        #     'SHANGHUKEY' : request.POST.get('shanghukey'),       # 商户秘钥KEY
        #     'total_fee' : request.POST.get('total_fee'),         # 钱数
        #     'appid' : request.POST.get('appid'),                 # 小程序ID
        #     'mch_id' : request.POST.get('mch_id'),               # 商户号
        #     'openid' : request.POST.get('openid'),               # 微信用户唯一标识
        #     'send_name' : request.POST.get('send_name'),         # 商户名称 中文
        #     'act_name' : request.POST.get('act_name'),           # 动名称 32长度
        #     'remark' : request.POST.get('remark'),               # 备注信息 256长度
        #     'wishing' : request.POST.get('wishing'),             # 红包祝福语 128长度
        # }
    client_ip = resultDict.get('client_ip')
    articleId = resultDict.get('articleId')  # 文章ID
    dataDict = {
        'SHANGHUKEY' : resultDict.get('shanghukey'),       # 商户秘钥KEY
        'total_fee' : resultDict.get('total_fee'),         # 钱数
        'appid' : resultDict.get('appid'),                 # 小程序ID
        'mch_id' : resultDict.get('mch_id'),               # 商户号
        'openid' : resultDict.get('openid'),               # 微信用户唯一标识
        'send_name' : resultDict.get('send_name'),         # 商户名称 中文
        'act_name' : resultDict.get('act_name'),           # 动名称 32长度
        'remark' : resultDict.get('remark'),               # 备注信息 256长度
        'wishing' : resultDict.get('wishing'),             # 红包祝福语 128长度
    }
    forms_obj = guanZhuForm(dataDict)
    if forms_obj.is_valid():
        objsForm = forms_obj.cleaned_data
        redEnvelope = models.zgld_red_envelope_to_issue.objects.filter(articleId__isnull=False)

        cunzaiObjs = redEnvelope.filter(articleId=articleId, mch_id=objsForm.get('mch_id'), re_openid=objsForm.get('openid'))
        if cunzaiObjs:
            response.code = 500
            response.msg = '本文章该用户已领取红包'
            return JsonResponse(response.__dict__)
        else:
            nowDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            redEnvelopeObjs = redEnvelope.create(
                wxappid = objsForm.get('appid'),                        # appid
                mch_id = objsForm.get('mch_id'),                        # 商户号
                re_openid = objsForm.get('openid'),                 # 用户唯一标识
                total_amount = int(objsForm.get('total_fee')) / 100,  # 付款金额 1:100
                mch_billno = dingdanhaoshengcheng(),                  # 订单号
                send_name = objsForm.get('send_name'),                  # 商户名称 中文
                act_name = objsForm.get('act_name'),                    # 活动名称 32长度
                remark = objsForm.get('remark'),                        # 备注信息 256长度
                client_ip = client_ip,                                  # 终端IP
                wishing = objsForm.get('wishing'),                      # 红包祝福语 128长度
                createDate=nowDateTime
            )
            SHANGHUKEY = objsForm.get('SHANGHUKEY')
            result_data = {
                'nonce_str': yuzhifu.generateRandomStamping(),              # 32位随机值a
                'wxappid': objsForm.get('appid'),                           # appid
                'mch_id':objsForm.get('mch_id'),                            # 商户号
                're_openid': objsForm.get('openid'),                        # 用户唯一标识
                'total_amount': objsForm.get('total_fee'),                  # 付款金额 1:100
                'mch_billno': dingdanhaoshengcheng(),                       # 订单号
                'client_ip': client_ip,                                     # 终端IP
                'total_num':1,                                              # 红包发放总人数
                'send_name':objsForm.get('send_name'),                      # 商户名称 中文
                'act_name':objsForm.get('act_name'),                        # 活动名称 32长度
                'remark':objsForm.get('remark'),                            # 备注信息 256长度
                'wishing':objsForm.get('wishing'),                          # 红包祝福语 128长度
                'articleId':articleId                                       # 文章ID
                }
            stringSignTemp = yuzhifu.shengchengsign(result_data, SHANGHUKEY)
            result_data['sign'] = yuzhifu.md5(stringSignTemp).upper()
            xml_data = yuzhifu.toXml(result_data).encode('utf8')
            # 获取商户证书
            shangHuObjs = models.zgld_shangcheng_jichushezhi.objects.filter(shangHuHao=objsForm.get('mch_id'))
            if shangHuObjs:
                path = shangHuObjs[0].zhengshu
                zhengshupath = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                file_dir = zhengshupath + '/' + path
                cret = os.path.join(file_dir, 'apiclient_cert.pem')
                key = os.path.join(file_dir, 'apiclient_key.pem')
                ret = requests.post(url, data=xml_data, cert=(cret, key))
                print(ret.text)
                DOMTree = xmldom.parseString(ret.text)
                collection = DOMTree.documentElement
                return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
                print('return_code-------------------> ',return_code)
                if return_code == 'SUCCESS':        # 判断预支付返回参数 是否正确
                    redEnvelope.filter(id=redEnvelopeObjs.id).update(issuingState=1)
                    response.code = 200
                    response.msg = '发放红包成功'
                else:
                    redEnvelope.filter(id=redEnvelopeObjs.id).update(issuingState=2)
                    response.code = 500
                    response.msg = '发放红包失败'
            else:
                response.code = 500
                response.msg = '没有商户证书, 请前往商城设置册证书！'
    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)