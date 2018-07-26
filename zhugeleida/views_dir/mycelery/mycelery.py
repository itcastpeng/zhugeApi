from django.http import HttpResponse
from zhugeleida import models
from zhugeleida.views_dir.conf import Conf
from django.views.decorators.csrf import csrf_exempt

import requests
import json
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
import os
import datetime
import redis
from collections import OrderedDict

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

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    if not customer_id:
        path = '/pages/mingpian/index?uid=%s&source=1' % (user_id)
        user_qr_code = '/%s_%s_qrcode.jpg' % (user_id,now_time)

    else:
        path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
        user_qr_code = '/%s_%s_%s_qrcode.jpg' % (user_id ,customer_id,now_time)

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
        rc.delete('xiaochengxu_token')
        response.msg = "生成小程序二维码未验证通过"

        return response

    # print('-------qr_ret---->', qr_ret.text)

    IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'qr_code') + user_qr_code
    with open('%s' % (IMG_PATH), 'wb') as f:
        f.write(qr_ret.content)


    if  customer_id:
        obj = models.zgld_user_customer_belonger.objects.get(user_id=user_id,customer_id=customer_id)
        user_qr_code_path = 'statics/zhugeleida/imgs/xiaochengxu/qr_code/%s' % user_qr_code
        obj.qr_code=user_qr_code_path
        obj.save()
        print('----celery生成用户-客户对应的小程序二维码成功-->>','statics/zhugeleida/imgs/xiaochengxu/qr_code/%s' % user_qr_code)

    else:
        user_obj = models.zgld_userprofile.objects.get(id=user_id)
        user_obj.qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code/%s' % user_qr_code
        user_obj.save()
        print('----celery生成企业用户对应的小程序二维码成功-->>','statics/zhugeleida/imgs/xiaochengxu/qr_code/%s' % user_qr_code)


    response.code = 200
    response.msg = "生成小程序二维码成功"

    return JsonResponse(response.__dict__)



# 小程序生成token，并然后发送模板消息
@csrf_exempt
def user_send_template_msg(request):
    response = ResponseObj()

    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id')

    get_token_data = {}
    get_template_data = {}
    post_template_data =  {}
    get_token_data['appid'] = Conf['appid']
    get_token_data['secret'] = Conf['appsecret']
    get_token_data['grant_type'] = 'client_credential'


    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    token_ret = rc.get('xiaochengxu_token')
    print('---token_ret---->>', token_ret)

    if not token_ret:
        # {"errcode": 0, "errmsg": "created"}
        token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
        token_ret_json = token_ret.json()
        print('-----生成小程序模板信息用的token：微信接口返回数据------>', token_ret_json)
        if not token_ret_json.get('access_token'):
            response.code = token_ret_json['errcode']
            response.msg = "生成模板信息用的token未通过"
            return response

        access_token = token_ret_json['access_token']
        print('---- access_token --->>', token_ret_json)
        get_template_data['access_token'] = access_token
        rc.set('xiaochengxu_token', access_token, 7000)

    else:
        get_template_data['access_token'] = token_ret

    global openid,form_id
    customer_obj = models.zgld_customer.objects.filter(id=customer_id)
    if customer_obj:
        form_id =  customer_obj[0].formid
        openid =  customer_obj[0].openid
        post_template_data['touser'] = openid

        post_template_data['template_id'] = 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE'

        path = 'pages/mingpian/index?source=2&uid=%s&pid=' % (user_id)
        post_template_data['page'] = path

        objs = models.zgld_user_customer_belonger.objects.filter(
            customer_id=customer_id,user_id=user_id
        )
        print('-------formid----->>', objs)

        user_name = ''
        if objs:
            exist_formid_json = json.loads(objs[0].customer.formid, object_pairs_hook=OrderedDict)
            user_name = objs[0].user.name
            print('===== 1 exist_formid_json 1 ========>>',exist_formid_json,'=====',len(exist_formid_json))
            if len(exist_formid_json) == 0:
                response.msg = "没有formID"
                response.code = 301
                print('------没有消费的formID------>>')
                return JsonResponse(response.__dict__)


            form_id = exist_formid_json.pop(0)
            obj = models.zgld_customer.objects.filter(id=customer_id)
            print('++++++++++ 2 exist_formid_json++++++++++++>>',exist_formid_json)

            obj.update(formid=json.dumps(exist_formid_json))

            post_template_data['form_id'] = form_id


        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 留言回复通知
        data = {
            'keyword1': {
                'value': user_name  # 回复者
            },
            'keyword2': {
                'value': now_time   # 回复时间
            },
            'keyword3': {
                'value': '您有未读消息,点击小程序查看哦。'  #回复内容
            }
        }
        post_template_data['data'] = data
        # post_template_data['emphasis_keyword'] = 'keyword1.DATA'
        print('===========post_template_data=======>>',post_template_data)

        # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html#发送模板消息
        # return  HttpResponse(post_template_data)

        template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
        template_ret = template_ret.json()
        print('--------企业用户 send to 小程序 Template 接口返回数据--------->',template_ret)

        if  template_ret.get('errmsg') == "ok":
            print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
            response.code = 200
            response.msg = "企业用户发送模板消息成功"
        else:
            print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
            response.code = 200
            response.msg = "企业用户发送模板消息成功"
    else:
        response.msg = "客户不存在"
        response.code = 301
        print('---- Template Msg 客户不存在---->>')


    return JsonResponse(response.__dict__)
