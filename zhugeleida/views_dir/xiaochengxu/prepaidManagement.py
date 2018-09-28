import random
import hashlib
import requests
import xml.dom.minidom as xmldom
import qrcode
import uuid, time, json
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
import requests
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt, csrf_protect

response = Response.ResponseObj()
def md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf8'))
    return m.hexdigest()

# 返回 xml
def toXml(params):
    xml = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if k == 'detail' and not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)
        xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(xml))

# 返回32为 时间戳
def generateRandomStamping():
    return str(uuid.uuid4()).replace('-', '')

# 生成二维码
# def create_qrcode(url):
#     img = qrcode.make(url)
#     img.get_image().show()
#     img.save('hello.png')

# 生成 签名
def shengchengsign(result_data, KEY):
    ret = []
    for k in sorted(result_data.keys()):
        if (k != 'sign') and (k != '') and (result_data[k] is not None):
            ret.append('%s=%s' % (k, result_data[k]))

    stringA = '&'.join(ret)
    stringSignTemp = '{stringA}&key={key}'.format(
        stringA=stringA,
        key=KEY
    )
    return stringSignTemp


@csrf_exempt
def payback(request):
    print('回调=--GET--回调回调回调回调回GETGETGET调回调回GETGETGET调回调GETGET回调-> ',request.GET)
    print('回调=--POST--==========================================-> ',request.POST)
    response.code = 200
    response.data = ''
    response.msg = ''
    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_customer)
def yuZhiFu(request):
    if request.method == 'POST':
        # spbillIp = request.POST.get('spbillIp')             # 终端ip
        # u_id = request.POST.get('u_id')
        url =  'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接口
        #  参数
        goodsId = request.POST.get('goodsId')                 # 商品ID
        user_id = request.GET.get('user_id')
        xiaochengxu_id = request.POST.get('xiaochengxu_id')


        userObjs = models.zgld_customer.objects.filter(id=user_id)  # 客户
        xiaochengxu_app = models.zgld_xiaochengxu_app.objects.filter(company_id=xiaochengxu_id)
        appid = xiaochengxu_app[0].authorization_appid

        jiChuSheZhiObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu_id)

        # ==========商户KEY============
        KEY = 'dNe089PsAVjQZPEL7ciETtj0DNX5W2RA'            # 商户秘钥KEY
        # KEY = jiChuSheZhiObjs[0].shangHuMiYao             # 商户秘钥真实数据KEY
        # goodsObjs = models.zgld_goods_management.objects.filter(id=goodsId)
        # total_fee = goodsObjs[0].goodsPrice * 100
        total_fee = int(0.01 * 100)
        print('total_fee=========> ',total_fee)
        dingdanhao = str(int(time.time())) + str(random.randint(10, 99)) + '0000' + str(xiaochengxu_id) + str(goodsId)
        print('订单号 ------------------------ > ', dingdanhao)
        getWxPayOrderId =  str(int(time.time()))# 订单号

        client_ip = '0.0.0.0'
        print('client_ip, port--------> ',client_ip)
        result_data = {
            'appid': 'wx1add8692a23b5976',                  # appid
            # 'appid': appid,                                 # 真实数据appid
            'mch_id': '1513325051',                         # 商户号
            # 'mch_id': jiChuSheZhiObjs[0].shangHuHao,      # 商户号真实数据
            'nonce_str': generateRandomStamping(),          # 32位随机值
            'openid': userObjs[0].openid,
            'body': 'zhuge-vip',                            # 描述
            'out_trade_no': getWxPayOrderId,                # 订单号
            'total_fee': total_fee,                            # 金额
            'spbill_create_ip': client_ip,                   # 终端IP
            'notify_url': 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/payback',
            'trade_type': 'JSAPI'
            }
        print('result_data-------> ',result_data)
        stringSignTemp = shengchengsign(result_data, KEY)
        result_data['sign'] = md5(stringSignTemp).upper()
        xml_data = toXml(result_data)

        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'
        DOMTree = xmldom.parseString(ret.text)
        collection = DOMTree.documentElement
        return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
        print('return_code----------> ',return_code)
        if return_code == 'SUCCESS':        # 判断预支付返回参数 是否正确
            # code_url = collection.getElementsByTagName("code_url")[0].childNodes[0].data  # 二维码
            prepay_id = collection.getElementsByTagName("prepay_id")[0].childNodes[0].data  # 直接支付
            data_dict = {
                'appId' : 'wx1add8692a23b5976',
                'timeStamp': int(time.time()),
                'nonceStr':generateRandomStamping(),
                'package': 'prepay_id=' + prepay_id,
                'signType': 'MD5'
            }
            stringSignTemp = shengchengsign(data_dict, KEY)
            data_dict['paySign'] = md5(stringSignTemp).upper() # upper转换为大写
            response.code = 200
            response.msg = '请求成功'
            response.data = data_dict
            return JsonResponse(response.__dict__)
        else:
            response.code = 500
            response.msg = '支付失败'
            response.data = ''
            return JsonResponse(response.__dict__)
    else:
        response.code = 402
        response.msg = '请求异常'
        response.data = ''
        return JsonResponse(response.__dict__)

