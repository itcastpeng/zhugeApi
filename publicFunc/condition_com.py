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

    return response

def user_send_action_log(data):
    response = Response.ResponseObj()
    user_id = data.get('uid')
    customer_id = data.get('customer_id') or ''

    get_token_data = {}
    get_user_data = {}
    user_id = data.get('uid')

    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
    print('---------->>>',user_obj.company.corp_id,user_obj.company.tongxunlu_secret)
    corp_id = user_obj.company.corp_id
    tongxunlu_secret = user_obj.company.tongxunlu_secret

    get_token_data['corpid'] = corp_id
    get_token_data['corpsecret'] = tongxunlu_secret

    # get 传参 corpid = ID & corpsecret = SECRECT
    ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
    weixin_ret_data = json.loads(ret.text)
    print('---- access_token --->>', weixin_ret_data)

    if  weixin_ret_data['errcode'] ==  0 :
        print('---- access_token --->>', weixin_ret_data)
        token_ret_json = ret.json()
        access_token = token_ret_json['access_token']

        url  = "https://qyapi.weixin.qq.com/cgi-bin/department/list"
        ret = requests.get(url, params={'access_token': access_token })
        print(ret.json())

        return 'ok'

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"
        return  response


    userid = user_obj.userid
    post_send_data =  {
       "touser" :userid,
       # "toparty" : "PartyID1|PartyID2",
       # "totag" : "TagID1 | TagID2",
       "msgtype" : "text",
       "agentid" : 1000002,
       "text" : {
           "content" : "你的快递已到，请携带工卡前往邮件中心领取。\n出发前可查看<a href=\"http://work.weixin.qq.com\">邮件中心视频实况</a>，聪明避开排队。"
       },
       "safe":0
    }
    get_token_data = {'access_token': access_token}
    print('---------->>',get_token_data)
    inter_ret = requests.post(Conf['send_msg_url'], params=get_token_data,data=json.dumps(post_send_data))

    weixin_ret_data = json.loads(inter_ret.text)
    print('---- access_token --->>', weixin_ret_data)

    if weixin_ret_data['errcode'] == 0:
        response.code = 200
        response.msg = '发送成功'

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"


    return response



