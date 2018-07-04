# 构造搜索条件 q
from django.db.models import Q
from zhugeleida import models
import datetime
from publicFunc import Response
import os,json
import requests
from zhugeleida.views_dir.conf import *

def conditionCom(request, field_dict):
    q = Q()
    for k, v in field_dict.items():
        value = request.GET.get(k)
        print('value ---->', value)
        if value:
            if v == '__contains':
                # 模糊查询
                q.add(Q(**{k + '__contains': value}), Q.AND)
            elif value == '__in':
                # 模糊查询
                q.add(Q(**{k + '__in': value}), Q.AND)
            else:
                q.add(Q(**{k: value}), Q.AND)

    return q


def action_record(data,remark):
    response = Response.ResponseObj()
    user_id = data.get('uid')  # 用户 id
    customer_id = data.get('user_id')  # 客户 id
    action = data.get('action')

    obj = models.zgld_accesslog.objects.create(
        user_id=user_id,
        customer_id=customer_id,
        remark=remark,
        action=action
    )

    follow_objs = models.zgld_user_customer_flowup.objects.filter(user_id=user_id, customer_id=customer_id)
    if follow_objs.count() == 1:
        obj.activity_time_id = follow_objs[0].id
        follow_objs.update(last_activity_time=datetime.datetime.now())
        obj.save()
        follow_objs[0].save()
        response.code = 200
        response.msg = '记录日志成功'


    elif follow_objs.count() == 0:
        flowup_create_obj = models.zgld_user_customer_flowup.objects.create(user_id=user_id,
                                                                            customer_id=customer_id,
                                                                            last_activity_time=datetime.datetime.now())
        obj.activity_time_id = flowup_create_obj.id
        obj.save()
        response.code = 200
        response.msg = '记录日志成功'



    else:
        response.code = 301
        response.msg = '用户-客户跟进信息-关系绑定表数据重复'

    company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id
    customer_name = models.zgld_customer.objects.filter(id=customer_id)[0].username

    data['content'] = customer_name + remark
    data['agentid'] = models.zgld_app.objects.filter(id=company_id,name='AI雷达')[0].agent_id
    user_send_action_log(data)  #发送企业微信的消息提醒




    return response


#小程序访问动作日志的发送到企业微信
def user_send_action_log(data):
    response = Response.ResponseObj()

    customer_id = data.get('customer_id') or ''
    user_id = data.get('uid')
    content = data.get('content')
    agentid = data.get('agentid')

    get_token_data = {}
    send_token_data = {}

    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
    print('---------->>>',user_obj.company.corp_id,user_obj.company.tongxunlu_secret)
    corp_id = user_obj.company.corp_id

    get_token_data['corpid'] = corp_id
    app_secret = models.zgld_app.objects.filter(id=user_obj.company_id, name='AI雷达')
    if not app_secret:
        response.code = 404
        response.msg = "数据库不存在corpsecret"
        return response

    get_token_data['corpsecret'] = app_secret[0]

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
            response.code = weixin_ret_data['errcode']
            response.msg = "企业微信验证未能通过"
            return response

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


    return response



