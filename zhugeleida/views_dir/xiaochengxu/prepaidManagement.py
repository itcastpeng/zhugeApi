import qrcode, re, requests, hashlib, random, uuid, time, json, xml.dom.minidom as xmldom, base64, datetime
from zhugeleida import models
from publicFunc import Response
from publicFunc import account, xmldom_parsing
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu import yuzhifu_verify



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
def shengchengsign(result_data, KEY=None):
    ret = []
    for k in sorted(result_data.keys()):
        if (k != 'sign') and (k != '') and (result_data[k] is not None):
            ret.append('%s=%s' % (k, result_data[k]))
    stringA = '&'.join(ret)
    stringSignTemp = stringA
    if KEY:
        stringSignTemp = '{stringA}&key={key}'.format(
            stringA=stringA,
            key=KEY
        )
    return stringSignTemp



@csrf_exempt
def payback(request):
    resultBody = request.body
    print('resultBody------------------> ',resultBody)
    DOMTree = xmldom.parseString(resultBody)
    collection = DOMTree.documentElement
    data = ['mch_id', 'return_code', 'appid', 'openid', 'cash_fee', 'out_trade_no']
    resultData = xmldom_parsing.xmldom(collection, data)

    # mch_id = collection.getElementsByTagName("mch_id")[0].childNodes[0].data            # 商户号
    # return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data  # 状态
    # appid = collection.getElementsByTagName("appid")[0].childNodes[0].data              # 小程序appid
    # openid = collection.getElementsByTagName("openid")[0].childNodes[0].data            # 用户openid
    # cash_fee = collection.getElementsByTagName("cash_fee")[0].childNodes[0].data        # 钱数
    # out_trade_no = collection.getElementsByTagName("out_trade_no")[0].childNodes[0].data# 订单号

    theOrderStatus = 9
    dingDanobjs = models.zgld_shangcheng_dingdan_guanli.objects.filter(orderNumber=resultData['out_trade_no'])
    nowDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if resultData['return_code'] == 'SUCCESS':
        if dingDanobjs:
            # 二次 查询是否付款成功
            result_data = {
                'appid': resultData['appid'],                 # appid
                'mch_id': resultData['mch_id'],               # 商户号
                'out_trade_no': resultData['out_trade_no'],   # 订单号
                'nonce_str': generateRandomStamping(),  # 32位随机值
            }
            url = 'https://api.mch.weixin.qq.com/pay/orderquery'
            objs = models.zgld_shangcheng_jichushezhi.objects.select_related('xiaochengxuApp').filter(xiaochengxuApp__authorization_appid=resultData['appid'])
            SHANGHUKEY = objs[0].shangHuMiYao
            stringSignTemp = shengchengsign(result_data, SHANGHUKEY)
            result_data['sign'] = md5(stringSignTemp).upper()
            xml_data = toXml(result_data)
            ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
            ret.encoding = 'utf8'
            DOMTree = xmldom.parseString(ret.text)
            collection = DOMTree.documentElement
            return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
            if return_code == 'SUCCESS':
                    theOrderStatus=8,        # 支付成功 改订单状态成功
    dingDanobjs.update(
        theOrderStatus=theOrderStatus,  # 支付失败 改订单状态失败
        stopDateTime=nowDate
    )
    response.code = 200
    response.data = ''
    response.msg = ''
    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_customer)
def yuZhiFu(request):
    if request.method == 'POST':
        url =  'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接口
        # 无订单情况 必传 4个参数
        goodsNum = request.POST.get('goodsNum', 1)               # 商品数量
        goodsId = request.POST.get('goodsId')                 # 商品ID
        user_id = request.GET.get('user_id')
        u_id = request.POST.get('u_id')
        # 传 订单 ID
        fukuan = request.POST.get('fukuan')                 # 订单已存在 原有订单
        phoneNumber = request.POST.get('phoneNumber')  # 电话号码
        forms_obj = yuzhifu_verify.yuZhiFu(request.POST)
        if forms_obj.is_valid():
            print('=======================================userid================userid-------------------> ', user_id, u_id)
            userObjs = models.zgld_customer.objects.filter(id=user_id)  # 客户
            openid = userObjs[0].openid                                 # openid  用户标识
            if not fukuan:
                u_idObjs = models.zgld_userprofile.objects.filter(id=u_id)
                if not u_idObjs[0].company_id:
                    response.code = 301
                    response.msg = '该用户没有公司!'
                    return JsonResponse(response.__dict__)
                xiaochengxu_app = models.zgld_xiaochengxu_app.objects.filter(company_id=u_idObjs[0].company_id)  # 真实数据appid
                if not xiaochengxu_app:
                    response.code = 301
                    response.msg = '该用户没有小程序app'
                    return JsonResponse(response.__dict__)
                goodsObjs = models.zgld_goods_management.objects.filter(id=goodsId)  # 真实单价
                if not goodsObjs:
                    response.code = 301
                    response.msg = '该商品不存在'
                    return JsonResponse(response.__dict__)
                print(xiaochengxu_app)
                jiChuSheZhiObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu_app[0].id)
                print('jiChuSheZhiObjs=========================> ',jiChuSheZhiObjs)
                SHANGHUKEY = jiChuSheZhiObjs[0].shangHuMiYao                    # 商户秘钥真实数据KEY dNe089PsAVjQZPEL7ciETtj0DNX5W2RA

                print('SHANGHUKEY==============> ',goodsObjs)

                total_fee = int(goodsObjs[0].goodsPrice * 100) * int(goodsNum)  # 1:100 0.1*100
                ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())        # 年月日时分秒
                shijianchuoafter5 = str(int(time.time() * 1000))[8:]            # 时间戳 后五位
                dingdanhao = str(ymdhms) + shijianchuoafter5 + str(random.randint(10, 99)) + str(goodsId)
                getWxPayOrderId =  dingdanhao                               # 订单号
                appid = xiaochengxu_app[0].authorization_appid              # 预支付 appid
                mch_id = jiChuSheZhiObjs[0].shangHuHao
            else:# 存在订单的
                orderObjs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=fukuan)
                getWxPayOrderId = orderObjs[0].orderNumber  #订单号
                goodNum = 1
                if orderObjs[0].unitRiceNum:
                    goodNum = orderObjs[0].unitRiceNum
                    phoneNumber = orderObjs[0].phone
                total_fee = int(orderObjs[0].yingFuKuan * 100) * int(goodNum)
                obj = orderObjs[0].shangpinguanli.parentName.mallSetting
                appid = obj.xiaochengxuApp.authorization_appid
                mch_id =obj.shangHuHao
                SHANGHUKEY = obj.shangHuMiYao
            print('mch_id===============> ',mch_id)
            result_data = {
                # 'appid': 'wx1add8692a23b5976',              # appid
                'appid': appid,                               # 真实数据appid 商户号
                # 'mch_id': '1513325051',                     # 商户号
                'mch_id': mch_id,                             # 商户号真实数据
                'nonce_str': generateRandomStamping(),        # 32位随机值a
                'openid': openid,
                'body': 'zhuge-vip',                          # 描述
                'out_trade_no': getWxPayOrderId,              # 订单号
                'total_fee': total_fee,                       # 金额
                'spbill_create_ip': '0.0.0.0',                # 终端IP
                'notify_url': 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/payback',
                'trade_type': 'JSAPI'
                }
            # print('result_data========> ',result_data)
            stringSignTemp = shengchengsign(result_data, SHANGHUKEY)
            result_data['sign'] = md5(stringSignTemp).upper()
            xml_data = toXml(result_data)
            # print('xml_data----------------> ',xml_data)
            ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
            ret.encoding = 'utf8'
            DOMTree = xmldom.parseString(ret.text)
            collection = DOMTree.documentElement
            data = ['return_code', 'return_msg']
            resultData = xmldom_parsing.xmldom(collection, data)
            # print('return_code-------------------> ',return_code)
            if resultData['return_code'] == 'SUCCESS':        # 判断预支付返回参数 是否正确
                data = ['prepay_id']
                resultData = xmldom_parsing.xmldom(collection, data)
                response.code = 200
                response.msg = '预支付请求成功'
                # 预支付成功 创建订单
                if not fukuan: # 判断是否已经存在订单
                    dingDanObjs = models.zgld_shangcheng_dingdan_guanli.objects
                    date_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    commissionFee = 0
                    if goodsObjs[0].commissionFee:
                        commissionFee = goodsObjs[0].commissionFee
                    company_id = xiaochengxu_app[0].company_id
                    dingDanObjs.create(
                        shangpinguanli_id = goodsId,            # 商品ID
                        orderNumber = int(getWxPayOrderId),     # 订单号
                        yingFuKuan = float(total_fee)/100,      # 应付款
                        goodsPrice = goodsObjs[0].goodsPrice,   # 商品单价
                        youHui = 0,                             # 优惠
                        unitRiceNum=int(goodsNum),              # 数量
                        yewuUser_id = u_id,                     # 业务
                        gongsimingcheng_id = company_id,        # 公司
                        yongJin = commissionFee,                # 佣金
                        shouHuoRen_id = user_id,                # 收货人
                        theOrderStatus = 1,                     # 订单状态
                        createDate=date_time,
                        goodsName=goodsObjs[0].goodsName,
                        detailePicture=goodsObjs[0].detailePicture,
                        phone=phoneNumber
                    )
                    # code_url = collection.getElementsByTagName("code_url")[0].childNodes[0].data # 二维码
                    prepay_id = resultData['prepay_id'] # 直接支付
                    data_dict = {
                        # 'appId' : 'wx1add8692a23b5976',
                        'appId' : appid,
                        'timeStamp': int(time.time()),
                        'nonceStr':generateRandomStamping(),
                        'package': 'prepay_id=' + prepay_id,
                        'signType': 'MD5'
                    }
                    stringSignTemp = shengchengsign(data_dict, SHANGHUKEY)
                    data_dict['paySign'] = md5(stringSignTemp).upper() # upper转换为大写
                    response.data = data_dict
                return JsonResponse(response.__dict__)
            else:
                if not fukuan:
                    response.msg = '预支付失败, 原因:{}'.format(resultData['return_msg'])
                else:
                    response.msg = '支付失败, 原因:{}'.format(resultData['return_msg'])
                response.code = 301
                response.data = ''
                return JsonResponse(response.__dict__)
        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
            return JsonResponse(response.__dict__)
    else:
        response.code = 402
        response.msg = '请求异常'
        response.data = ''
        return JsonResponse(response.__dict__)