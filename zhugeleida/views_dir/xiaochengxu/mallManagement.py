import random
import hashlib
import requests


# ==========商户KEY============
KEY = 'dNe089PsAVjQZPEL7ciETtj0DNX5W2RA'


def md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf8'))
    return m.hexdigest()


def toXml(params):
    xml = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if k == 'detail' and not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)

        # if k == 'body':
        #     # v = v.encode('utf8')
        #     v = parse.quote(v)
        xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(xml))


def yuZhiFu():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(32):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    url =  'https://api.mch.weixin.qq.com/pay/unifiedorder',
    result_data = {
        'appid': 'wx202b03ae2fbf636f', # appid
        'mch_id': '1513325051', # 商户号
        'nonce_str': salt,      # 32位随机值
        # 'sign': '',             # 签名
        'body': 'zhuge-vip',
        'out_trade_no': '20180925142130',
        'total_fee': '100',
        'spbill_create_ip': '192.168.0.0',
        'notify_url': 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/pay',
        'trade_type': 'NATIVE'
        }
    ret = []
    for k in sorted(result_data.keys()):
        if (k != 'sign') and (k != '') and (result_data[k] is not None):
            ret.append('%s=%s' % (k, result_data[k]))

    stringA = '&'.join(ret)
    stringSignTemp = '{stringA}&key={key}'.format(
        stringA=stringA,
        key=KEY
    )
    # print('md5(stringSignTemp) -->', md5(stringSignTemp))
    result_data['sign'] = md5(stringSignTemp).upper()
    print(result_data)
    xml_data = toXml(result_data)
    ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
    ret.encoding = 'utf8'
    print(ret.text)
