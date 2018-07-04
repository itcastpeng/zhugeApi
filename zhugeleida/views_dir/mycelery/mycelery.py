
from django.http import HttpResponse
from zhugeleida import models
from zhugeleida.views_dir.conf import Conf
from django.views.decorators.csrf import csrf_exempt

import requests
import json
from publicFunc.Response import ResponseObj
from django.http import JsonResponse

#小程序访问动作日志的发送到企业微信
@csrf_exempt
def user_send_action_log(request):
    response = ResponseObj()
    print('request.POST ==>', request.POST)
    data = json.loads(request.POST.get('data'))
    print('data ===>', data)

    customer_id = data.get('customer_id', '')
    user_id = data.get('uid')
    content = data.get('content')
    agentid = data.get('agentid')

    get_token_data = {}
    send_token_data = {}

    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
    print('---------->>>',user_obj.company.corp_id,user_obj.company.tongxunlu_secret)
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
        print('----weixin_ret_data--->',weixin_ret_data)

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
    post_send_data =  {
       "touser" : userid,
       # "toparty" : "PartyID1|PartyID2",
       # "totag" : "TagID1 | TagID2",
       "msgtype" : "text",
       "agentid" :  int(agentid),
       "text" : {
           "content" : content,
       },
       "safe":0
    }

    inter_ret = requests.post(Conf['send_msg_url'], params=send_token_data,data=json.dumps(post_send_data))

    weixin_ret_data = json.loads(inter_ret.text)
    print('---- access_token --->>', weixin_ret_data)

    if weixin_ret_data['errcode'] == 0:
        response.code = 200
        response.msg = '发送成功'

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"


    return JsonResponse(response.__dict__)


