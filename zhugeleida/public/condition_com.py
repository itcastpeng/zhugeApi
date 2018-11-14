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
from publicFunc import account


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
    company_id = data.get('company_id')
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
        print('------- Agent_list_ret ----------->>',agent_list_ret)

        agentlist = agent_list_ret.get('agentlist')
        # {'agentlist': [{'square_logo_url': 'http://p.qlogo.cn/bizmail/VJkoqXfNQ0SPj0HLc6qyiabnOibyOcBX208OTW7pB26LGvYW3nfmPDOw/0', 'name': '医美咨询雷达', 'agentid': 1000002}], 'errcode': 0, 'errmsg': 'ok'}

        for agent_dict in agentlist:
            agentid = agent_dict.get('agentid')
            name = agent_dict.get('name')
            square_logo_url = agent_dict.get('square_logo_url')

            if int(agentid) == int(agent_id):
                response.data = {
                    'agentid' : agentid,
                    'name' :    name,
                    'square_logo_url' : square_logo_url
                }

                #设置应用
                set_agent_url = 'https://qyapi.weixin.qq.com/cgi-bin/agent/set'
                home_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?redirect_uri=http://zhugeleida.zhugeyingxiao.com/zhugeleida/qiyeweixin/work_weixin_auth/%s&appid=%s&agentid=%s&scope=snsapi_userinfo&response_type=code#wechat_redirect' % (company_id,corp_id,agentid)

                get_agent_data = {
                    'access_token': access_token
                }
                post_agent_data = {
                    "agentid": agentid,
                    # "name": "NAME",
                    # "description": "DESC",  #企业应用详情
                    "redirect_domain": "zhugeleida.zhugeyingxiao.com",
                    "home_url": home_url

                }
                print('---------- 修改home_url get_agent_data + post_agent_data ------------------>>',json.dumps(get_agent_data),'|',json.dumps(post_agent_data))

                set_agent_ret = requests.post(set_agent_url, params=get_agent_data,data=json.dumps(post_agent_data))
                set_agent_ret = set_agent_ret.json()
                print('--------- 设置应用 set_agent_ret 返回 ----------->>', set_agent_ret)
                errmsg = set_agent_ret.get('errmsg')
                if errmsg == 'ok':
                    print('--------- 设置应用 set_agent_ret 成功 ----------->>')
                else:
                    response.code = weixin_ret_data['errcode']
                    response.msg = "设置应用报错:%s" % (errmsg)
                    print('--------- 设置应用 set_agent_ret 失败 ----------->>')
                    return response



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
    company_id = data.get('company_id')

    get_token_data['corpid'] = corp_id
    get_token_data['corpsecret'] = tongxunlu_secret

    # ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
    # ret_json = ret.json()

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    ret = s.get(Conf['tongxunlu_token_url'], params=get_token_data)  # 你需要的网址
    ret_json = ret.json()

    print('---- 企业微信验证 通讯录同步应用的secret  --->', ret_json)
    if ret_json['errcode'] == 0:

        company_obj = models.zgld_company.objects.filter(id=company_id)
        if company_obj:
            get_token_data = {}
            post_user_data = {}
            get_user_data = {}
            get_token_data['corpid'] = corp_id
            get_token_data['corpsecret'] = tongxunlu_secret

            import redis
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            key_name = "company_%s_tongxunlu_token" % (company_id)
            token_ret = rc.get(key_name)

            print('---token_ret---->>', token_ret)

            if not token_ret:
                # ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                # ret_json = ret.json()

                s.keep_alive = False  # 关闭多余连接
                ret = s.get(Conf['tongxunlu_token_url'], params=get_token_data) # 你需要的网址
                ret_json = ret.json()

                print('--------ret_json-->>', ret_json)

                access_token = ret_json['access_token']
                get_user_data['access_token'] = access_token

                rc.set(key_name, access_token, 7000)

            else:
                get_user_data['access_token'] = token_ret

            department_list_url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list'
            # department_list_ret = requests.get(department_list_url, params=get_user_data)
            # department_list_ret = department_list_ret.json()

            s.keep_alive = False  # 关闭多余连接
            department_list_ret = s.get(department_list_url, params=get_user_data)  # 你需要的网址
            department_list_ret = department_list_ret.json()

            errcode = department_list_ret.get('errcode')
            errmsg = department_list_ret.get('errmsg')
            department_list = department_list_ret.get('department')


            print('-------- 获取部门列表 接口返回----------->>', json.dumps(department_list_ret))

            if department_list:
                for dep_dict in department_list:
                    department_id = dep_dict.get('id')

                    department_liebiao = dep_dict.get('department')  # 已经存在的部门列表

                    user_simplelist_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist'
                    # get_user_data['department_id'] = department_id
                    # user_simplelist_ret = requests.get(user_simplelist_url, params=get_user_data)

                    get_user_data['department_id'] = department_id
                    s.keep_alive = False  # 关闭多余连接
                    user_simplelist_ret = s.get(user_simplelist_url, params=get_user_data)  # 你需要的网址

                    user_simplelist_ret = user_simplelist_ret.json()

                    print('----- 获取部门成员 返回接口信息----->>', json.dumps(user_simplelist_ret))

                    errcode = user_simplelist_ret.get('errcode')
                    errmsg = user_simplelist_ret.get('errmsg')
                    userlist = user_simplelist_ret.get('userlist')

                    if userlist:
                        print('------- 获取-客户信息【成功】 ------->>', user_simplelist_ret)

                        for user_dict in userlist:
                            username = user_dict.get('name')
                            userid = user_dict.get('userid')
                            department_list = user_dict.get('department')
                            password = '123456'
                            token = account.get_token(account.str_encrypt(password))
                            objs = models.zgld_userprofile.objects.filter(userid=userid, company_id=company_id)

                            if objs:
                                print('-------- 用户数据成功已存在 username | userid | user_id -------->>', username, userid,
                                      objs[0].id)
                            else:
                                obj = models.zgld_userprofile.objects.create(
                                    userid=userid,
                                    username=username,
                                    password=account.str_encrypt(password),
                                    # role_id=role_id,
                                    company_id=company_id,
                                    # position='',
                                    # wechat_phone='',
                                    # mingpian_phone= '',
                                    token=token
                                )

                                print('-------- 同步用户数据成功 user_id：-------->>', obj.id)

                                # if department_list:
                                #     obj.department = department_list

                                # 生成企业用户二维码
                                # data_dict = {'user_id': obj.id, 'customer_id': ''}
                                # tasks.create_user_or_customer_small_program_qr_code.delay(json.dumps(data_dict))
                                # print('------- 同步成功并生成用户二维码成功 json.dumps(data_dict) -------->>',json.dumps(data_dict))

                        response.code = 0
                        response.msg = "同步成功并生成用户二维码成功"

                    else:
                        response.code = errcode
                        response.msg =  errmsg

                        print('---- 获取部门成员 [报错]：------>', errcode, "|", errmsg)

            else:
                response.code =  errcode
                response.msg = errmsg

        print("=========企业微信验证 通讯录同步应用的secret-通过======>",corp_id,'|',tongxunlu_secret)

    else:
        response.code = ret_json['errcode']
        response.msg = "企业微信验证未能通过"
        print("=========企业微信验证 通讯录同步应用的secret -未能通过======>",corp_id,'|',tongxunlu_secret)


    return response

