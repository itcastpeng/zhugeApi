from zhugeleida.views_dir.conf import *
import requests
from publicFunc import Response
import json


#小程序访问动作日志的发送到企业微信
def user_send_action_log(data):
    response = Response.ResponseObj()

    customer_id = data.get('customer_id') or ''
    user_id = data.get('uid')
    content = data.get('content')
    agentid = data.get('agentid')

    get_token_data = {}
    send_token_data = {}


    corp_id = 'wx81159f52aff62388'
    tongxunlu_secret = '-pkF6u6vdXRbapZNb-fdQc16DXBhGCgDmyfa0OUuOgk'


    get_token_data['corpid'] = corp_id
    get_token_data['corpsecret'] = tongxunlu_secret

    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    token_ret = rc.get('tongxunlu_token')
    print('---token_ret---->>', token_ret)

    if not token_ret:
        ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
        weixin_ret_data = ret.json()
        print('------weixin_ret_data---->>',weixin_ret_data)

        if weixin_ret_data['errcode'] == 0:
           access_token = weixin_ret_data['access_token']
           send_token_data['access_token'] = access_token
           rc.set('tongxunlu_token', access_token, 7000)

        else:
            response.code = weixin_ret_data['errcode']
            response.msg = "企业微信验证未能通过"
            return response

    else:
        send_token_data['access_token'] = token_ret

    userid = '@all'
    post_send_data =  {
       "touser" :userid,
       # "toparty" : "PartyID1|PartyID2",
       # "totag" : "TagID1 | TagID2",
       "msgtype" : "text",
       "agentid" :  agentid,
       "text" : {
           "content" : content,
       },
       "safe":0
    }

    inter_ret = requests.post(Conf['send_msg_url'], params=send_token_data,data= json.dumps(post_send_data))
    import json
    weixin_ret_data = json.loads(inter_ret.text)
    print('---- access_token --->>', weixin_ret_data)

    if weixin_ret_data['errcode'] == 0:
        response.code = 200
        response.msg = '发送成功'

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"


    return response


data = {

    'uid' :  '@all',
    'content': 'hey man !!!!' ,
    'agentid' : 10001,
}
user_send_action_log(data)