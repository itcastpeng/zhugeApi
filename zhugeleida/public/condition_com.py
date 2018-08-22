# 构造搜索条件 q
from django.db.models import Q
from zhugeleida import models
import datetime
from publicFunc import Response
import os,json
import requests
from zhugeleida.views_dir.conf import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def conditionCom(data, field_dict):
    q = Q()
    for k, v in field_dict.items():
        value = data.get(k)
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

## 按月增加datetime月份
def datetime_offset_by_month(datetime1, n=1):
        # create a shortcut object for one day
        one_day = datetime.timedelta(days=1)

        # first use div and mod to determine year cycle
        q, r = divmod(datetime1.month + n, 12)

        # create a datetime2
        # to be the last day of the target month
        datetime2 = datetime.datetime(
            datetime1.year + q, r + 1, 1) - one_day

        if datetime1.month != (datetime1 + one_day).month:
            return datetime2

        if datetime1.day >= datetime2.day:
            return datetime2

        return datetime2.replace(day=datetime1.day)



@csrf_exempt
def validate_agent(data):
    response = Response.ResponseObj()

    corp_id = data.get('corp_id')
    app_secret = data.get('app_secret')
    agent_id = data.get('agent_id')
    get_token_data = {}
    send_token_data = {}

    get_token_data['corpid'] = corp_id
    # app_secret = models.zgld_app.objects.get(company_id=company_id, name='AI雷达').app_secret
    get_token_data['corpsecret'] = app_secret
    ret = requests.get(Conf['token_url'], params=get_token_data)

    weixin_ret_data = ret.json()
    print('---- 企业微信agent secret 验证接口返回 --->', weixin_ret_data)
    access_token = weixin_ret_data.get('access_token')

    if weixin_ret_data['errcode'] == 0:
        agent_list_url = 'https://qyapi.weixin.qq.com/cgi-bin/agent/list'
        get_token_data = {
            'access_token' : access_token
        }
        agent_list_ret = requests.get(agent_list_url, params=get_token_data)
        agent_list_ret = agent_list_ret.json()
        agentlist = agent_list_ret.get('agentlist')
        for agent_dict in agentlist:
            agentid = agent_dict.get('agentid')
            name = agent_dict.get('name')
            square_logo_url = agent_dict.get('square_logo_url')

            if agentid == agent_id:
                response.data = {
                    'agentid' : agentid,
                    'name' :    name,
                    'square_logo_url' : square_logo_url
                }


        response.code = 0
        response.msg = '企业微信验证'
        print("=========企业微信agent secret验证-通过======>",corp_id,'|',app_secret)

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"
        print("=========企业微信agent secret验证未能通过======>",corp_id,'|',app_secret)


    return response


@csrf_exempt
def validate_tongxunlu(data):
    response = Response.ResponseObj()
    get_token_data = {}
    corp_id = data.get('corp_id')
    tongxunlu_secret = data.get('tongxunlu_secret')

    get_token_data['corpid'] = corp_id
    get_token_data['corpsecret'] = tongxunlu_secret

    ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
    ret_json = ret.json()

    print('---- 企业微信验证 通讯录同步应用的secret  --->', ret_json)
    if ret_json['errcode'] == 0:
        response.code = 0
        response.msg = '企业微信验证'
        print("=========企业微信验证 通讯录同步应用的secret-通过======>",corp_id,'|',tongxunlu_secret)

    else:
        response.code = ret_json['errcode']
        response.msg = "企业微信验证未能通过"
        print("=========企业微信验证 通讯录同步应用的secret -未能通过======>",corp_id,'|',tongxunlu_secret)


    return response

