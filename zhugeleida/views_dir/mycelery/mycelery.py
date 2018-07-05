from django.http import HttpResponse
from zhugeleida import models
from zhugeleida.views_dir.conf import Conf
from django.views.decorators.csrf import csrf_exempt

import requests
import json
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
import os

# 小程序访问动作日志的发送到企业微信
@csrf_exempt
def user_send_action_log(request):
    response = ResponseObj()
    data = json.loads(request.POST.get('data'))
    print('data ===>', data)

    customer_id = data.get('customer_id', '')
    user_id = data.get('uid')
    content = data.get('content')
    agentid = data.get('agentid')

    get_token_data = {}
    send_token_data = {}

    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
    print('---------->>>', user_obj.company.corp_id, user_obj.company.tongxunlu_secret)
    corp_id = user_obj.company.corp_id

    get_token_data['corpid'] = corp_id
    app_secret = models.zgld_app.objects.get(id=user_obj.company_id, name='AI雷达').app_secret
    # if not app_secret:
    #     response.code = 404
    #     response.msg = "数据库不存在corpsecret"
    #     return response

    get_token_data['corpsecret'] = app_secret
    print('get_token_data -->', get_token_data)

    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    token_ret = rc.get('leida_app_token')
    print('---token_ret---->>', token_ret)

    if not token_ret:
        ret = requests.get(Conf['token_url'], params=get_token_data)

        weixin_ret_data = ret.json()
        print('----weixin_ret_data--->', weixin_ret_data)

        if weixin_ret_data['errcode'] == 0:
            access_token = weixin_ret_data['access_token']
            send_token_data['access_token'] = access_token
            rc.set('leida_app_token', access_token, 7000)

        else:
            print('企业微信验证未能通过')
            response.code = weixin_ret_data['errcode']
            response.msg = "企业微信验证未能通过"
            return JsonResponse(response.__dict__)

    else:
        send_token_data['access_token'] = token_ret

    userid = user_obj.userid
    post_send_data = {
        "touser": userid,
        # "toparty" : "PartyID1|PartyID2",
        # "totag" : "TagID1 | TagID2",
        "msgtype": "text",
        "agentid": int(agentid),
        "text": {
            "content": content,
        },
        "safe": 0
    }
    print('post_send_data ==>', post_send_data)

    inter_ret = requests.post(Conf['send_msg_url'], params=send_token_data, data=json.dumps(post_send_data))

    weixin_ret_data = json.loads(inter_ret.text)
    print('---- access_token --->>', weixin_ret_data)

    if weixin_ret_data['errcode'] == 0:
        response.code = 200
        response.msg = '发送成功'

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"

    return JsonResponse(response.__dict__)


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@csrf_exempt
def create_user_or_customer_qr_code(request):
    response = ResponseObj()
    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id','')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    get_token_data = {}

    if not customer_id:
        path = '/pages/mingpian/index?uid=%s&source=1&' % (user_id)
        user_qr_code = '/%s_qrcode.jpg' % (user_id)

    else:
        path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
        user_qr_code = '/%s_%s_qrcode.jpg' % (user_id, customer_id)

    get_qr_data = {}

    get_token_data['appid'] = Conf['appid']
    get_token_data['secret'] = Conf['appsecret']
    get_token_data['grant_type'] = 'client_credential'

    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    token_ret = rc.get('xiaochengxu_token')
    print('---token_ret---->>', token_ret)

    if not token_ret:
        # {"errcode": 0, "errmsg": "created"}
        token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
        token_ret_json = token_ret.json()
        print('-----token_ret_json------>', token_ret_json)
        if not token_ret_json.get('access_token'):
            response.code = token_ret_json['errcode']
            response.msg = "生成小程序二维码未验证通过"
            return response

        access_token = token_ret_json['access_token']
        print('---- access_token --->>', token_ret_json)
        get_qr_data['access_token'] = access_token
        rc.set('xiaochengxu_token', access_token, 7000)

    else:

        get_qr_data['access_token'] = token_ret

    post_qr_data = {'path': path, 'width': 430}
    qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

    if not qr_ret.content:
        response.msg = "生成小程序二维码未验证通过"
        return response

    # print('-------qr_ret---->', qr_ret.text)

    IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'qr_code') + user_qr_code
    with open('%s' % (IMG_PATH), 'wb') as f:
        f.write(qr_ret.content)

    user_obj = models.zgld_userprofile.objects.get(id=user_id)
    user_obj.qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code/%s' % user_qr_code
    print('user_obj.qr_code -->', user_obj.qr_code)
    user_obj.save()

    response.code = 200
    response.msg = "生成小程序二维码成功"

    return JsonResponse(response.__dict__)
