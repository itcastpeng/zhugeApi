from django.http import HttpResponse
from zhugeleida import models
from zhugeleida.views_dir.conf import Conf
from django.views.decorators.csrf import csrf_exempt

from publicFunc import Response
import json
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
import os
import datetime
import redis
from collections import OrderedDict
from zhugeleida.views_dir.admin.dai_xcx import create_authorizer_access_token
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import \
    create_authorizer_access_token as create_gongzhonghao_authorizer_access_token

import sys
from django.conf import settings
from selenium import webdriver
import requests
from PIL import Image
from zhugeapi_celery_project import tasks
from zhugeleida.public import common
from django.db.models import Sum
from zhugeleida.views_dir.admin.redEnvelopeToIssue import focusOnIssuedRedEnvelope
from django.db.models import Q, F
import base64
from zhugeleida.public.common import create_qiyeweixin_access_token
import random


def action_record(data):
    response = Response.ResponseObj()
    user_id = data.get('uid')  # 用户 id
    customer_id = data.get('customer_id', '')  # 客户 id
    article_id = data.get('article_id')  # 客户 id
    action = data.get('action')
    if action:
        action = int(action)

    remark = data.get('remark')
    agent_id = data.get('agent_id')

    if action in [666]:  # 只做消息【温馨提示】。

        response.data = {
            'content': remark,
            'agentid': agent_id
        }

        _content = {'info_type': 1}
        encodestr = base64.b64encode(remark.encode('utf-8'))
        msg = str(encodestr, 'utf-8')
        _content['msg'] = msg
        content = json.dumps(_content)

        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

        models.zgld_chatinfo.objects.filter(send_type=2, userprofile_id=user_id, customer_id=customer_id,
                                            is_last_msg=True).update(is_last_msg=False)
        models.zgld_chatinfo.objects.create(send_type=2, userprofile_id=user_id, customer_id=customer_id,
                                            content=content)

        redis_user_query_info_key = 'message_user_id_{uid}_info_num'.format(
            uid=user_id)  # 客户发过去消息,雷达用户的key 消息数量发生变化
        redis_user_query_contact_key = 'message_user_id_{uid}_contact_list'.format(
            uid=user_id)  # 客户发过去消息,雷达用户的key 消息列表发生变化
        rc.set(redis_user_query_info_key, True)  # 代表 雷达用户 消息数量发生了变化
        rc.set(redis_user_query_contact_key, True)  # 代表 雷达用户 消息列表的数量发生了变化

        response.code = 200
        response.msg = '发送消息提示成功'
        return response

    customer_name = models.zgld_customer.objects.get(id=customer_id).username
    customer_name = base64.b64decode(customer_name)
    customer_name = str(customer_name, 'utf-8')

    if action in [0]:  # 发消息记录客户 最后活动时间。

        # data['content'] = '%s%s' % (customer_name, remark)
        # data['agentid'] = agent_id
        # tasks.user_send_action_log.delay(json.dumps(data))
        _remark = ':发送给您一条新消息，请点击查看!'
        content = '【%s】%s' % (customer_name, _remark)

        flow_up_objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id,
                                                                         customer_id=customer_id)
        if flow_up_objs:  # 用戶發消息給客戶，修改最後跟進-時間
            flow_up_objs.update(
                is_customer_msg_num=F('is_customer_msg_num') + 1,  # 说明用户发过消息给雷达用户。
                last_activity_time=datetime.datetime.now()  # 用户的最后活动时间。
            )
        response.data = {
            'content': content,
            'agentid': agent_id
        }
        response.code = 200
        response.msg = '发送消息提示成功'

        return response

    elif action in [14, 15, 16, 17]:  # (14,'查看文章'),  (15,'转发文章到朋友'), (16,'转发文章到朋友圈')
        # 创建访问日志
        models.zgld_accesslog.objects.create(
            user_id=user_id,
            article_id=article_id,
            customer_id=customer_id,
            remark=remark,
            action=action
        )
        content = '%s%s' % (customer_name, remark)
        print('------ 客户姓名 + 访问日志信息------->>', customer_name, 'action:', action, content)

        # follow_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(
        #     user_id=user_id,
        #     customer_id=customer_id
        # )
        # now_time = datetime.datetime.now()
        # if follow_objs:  # 已经有关系了
        #     follow_objs.update(
        #         last_activity_time=now_time
        #     )
        #
        # content = '%s%s' % (customer_name, remark)
        # print('------ 客户姓名 + 访问日志信息------->>', customer_name, 'action:', action, content)
        # response.data = {
        #     'content': content,
        #     'agentid': agent_id
        # }
        # response.code = 200
        # response.msg = '发送消息提示成功'

    else:
        # 创建访问日志
        models.zgld_accesslog.objects.create(
            user_id=user_id,
            customer_id=customer_id,
            remark=remark,
            action=action
        )
        content = '%s%s' % (customer_name, remark)
        print('------ 客户姓名 + 访问日志信息------->>', customer_name, '+', 'action:', action, content)

    # 查询客户与用户是否已经建立关系
    follow_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(
        user_id=user_id,
        customer_id=customer_id
    )
    now_time = datetime.datetime.now()
    if follow_objs:  # 记录 最后活动时间
        follow_objs.update(
            last_activity_time=now_time
        )

    response.data = {
        'content': content,
        'agentid': agent_id
    }
    response.code = 200
    response.msg = '记录日志成功'

    return response


# 小程序访问动作日志的发送到企业微信
@csrf_exempt
def user_send_action_log(request):
    response = ResponseObj()
    customer_id = request.GET.get('user_id')  # 客户 id
    user_id = request.GET.get('uid')
    article_id = request.GET.get('article_id')  # 客户 id
    action = request.GET.get('action')
    remark = request.GET.get('remark')

    # objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
    #     customer_id=customer_id,user_id=user_id).order_by('create_date')
    # user_id = objs[0].user_id
    # objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
    #     customer_id=customer_id).order_by('create_date')
    #
    # user_id = objs[0].user_id  # 找到那个建立唯一关系的人。

    send_token_data = {}
    user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)[0]

    corp_id = user_obj.company.corp_id
    company_id = user_obj.company_id

    print('------ 企业通讯录corp_id | 通讯录秘钥  ---->>>', corp_id)

    app_obj = models.zgld_app.objects.get(company_id=company_id, app_type=1)
    agent_id = app_obj.agent_id
    permanent_code = app_obj.permanent_code

    company_obj = models.zgld_company.objects.get(id=company_id)
    account_expired_time = company_obj.account_expired_time
    company_name = company_obj.name

    if datetime.datetime.now() <= account_expired_time:
        _data = {
            'uid': user_id,  # 用户 id
            'customer_id': customer_id,  # 客户 id
            'article_id': article_id,  # 客户 id
            'action': action,
            'remark': remark,
            'agent_id': agent_id,
        }
        response_ret = action_record(_data)
        content = response_ret.data.get('content')

        if not permanent_code:

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            key_name = "company_%s_leida_app_token" % (user_obj.company_id)
            token_ret = rc.get(key_name)

            print('-------  Redis缓存的 keyname |value -------->>', key_name, "|", token_ret)

            app_secret = app_obj.app_secret
            get_token_data = {
                'corpid': corp_id,
                'corpsecret': app_secret
            }

            print('-------- 企业ID | 应用的凭证密钥  get_token_data数据 ------->', get_token_data)

            if not token_ret:

                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                ret = s.get(Conf['token_url'], params=get_token_data)
                # ret = requests.get(Conf['token_url'], params=get_token_data)

                weixin_ret_data = ret.json()
                errcode = weixin_ret_data.get('errcode')
                errmsg = weixin_ret_data.get('errmsg')
                access_token = weixin_ret_data.get('access_token')
                print('--------- 从【企业微信】接口, 获取access_token 返回 -------->>', weixin_ret_data)

                if errcode == 0:
                    rc.set(key_name, access_token, 7000)
                    send_token_data['access_token'] = access_token

                else:
                    response.code = errcode
                    response.msg = "企业微信验证未能通过"
                    print('----------- 获取 access_token 失败 : errcode | errmsg  -------->>', errcode, "|", errmsg)
                    return JsonResponse(response.__dict__)

            else:
                send_token_data['access_token'] = token_ret

        else:

            SuiteId = 'wx5d26a7a856b22bec'  # '雷达AI | 三方应用id'
            _data = {
                'SuiteId': SuiteId,  # 三方应用IP 。
                'corp_id': corp_id,  # 授权方企业corpid
                'permanent_code': permanent_code
            }
            access_token_ret = common.create_qiyeweixin_access_token(_data)
            access_token = access_token_ret.data.get('access_token')
            send_token_data['access_token'] = access_token

        userid = user_obj.userid
        post_send_data = {
            "touser": userid,
            # "toparty" : "PartyID1|PartyID2",
            # "totag" : "TagID1 | TagID2",
            "msgtype": "text",
            "agentid": int(agent_id),
            "text": {
                "content": content,
            },
            "safe": 0
        }
        print('-------- 发送应用消息 POST json.dumps 格式数据:  ---------->>', json.dumps(post_send_data))

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        inter_ret = s.post(Conf['send_msg_url'], params=send_token_data, data=json.dumps(post_send_data))
        # inter_ret = requests.post(Conf['send_msg_url'], params=send_token_data, data=json.dumps(post_send_data))

        weixin_ret_data = inter_ret.json()
        errcode = weixin_ret_data.get('errcode')
        errmsg = weixin_ret_data.get('errmsg')

        print('---- 发送应用消息 【接口返回】 --->>', weixin_ret_data)

        if errmsg == "ok":
            response.code = 200
            response.msg = '发送成功'
            print('--------- 发送应用消息 【成功】----------->')

        else:
            response.code = errcode
            response.msg = "企业微信验证未能通过"
            print('---------- 发送应用消息 【失败】 : errcode | errmsg ----------->', errcode, '|', errmsg)

    else:

        response.code = 403
        response.msg = '账户过期'
        print('-------- 雷达账户过期: %s-%s | 过期时间:%s ------->>' % (company_id, company_name, account_expired_time))

    return JsonResponse(response.__dict__)


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@csrf_exempt
def create_user_or_customer_qr_code(request):
    response = ResponseObj()
    print('---- 【生成小程序二维码 celery】 request.GET | data 数据 -->', request.GET, '|', request.GET.get('data'))

    data = request.GET.get('data')
    if data:
        data = json.loads(request.GET.get('data'))
        user_id = data.get('user_id')
        customer_id = data.get('customer_id', '')

    else:
        # data = request.POST.get('user_id')
        print('---- celery request.POST | data 数据 -->', request.POST, '|')
        user_id = request.POST.get('user_id')
        customer_id = request.POST.get('customer_id', '')

    company_id = ''
    product_function_type = ''
    userprofile_objs = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
    if userprofile_objs:
        company_id = userprofile_objs[0].company_id
        product_function_type = userprofile_objs[0].company.product_function_type

    if product_function_type != 3:
        xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)

        if xiaochengxu_app_objs:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            if not customer_id:
                path = '/pages/mingpian/index?uid=%s&source=1' % (user_id)
                user_qr_code = '/%s_%s_qrcode.jpg' % (user_id, now_time)

            else:
                path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
                user_qr_code = '/%s_%s_%s_qrcode.jpg' % (user_id, customer_id, now_time)

            get_qr_data = {}
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            # userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
            # company_id = userprofile_obj.company_id

            authorizer_refresh_token = xiaochengxu_app_objs[0].authorizer_refresh_token
            authorizer_appid = xiaochengxu_app_objs[0].authorization_appid

            key_name = '%s_authorizer_access_token' % (authorizer_appid)

            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

            if not authorizer_access_token:
                data = {
                    'key_name': key_name,
                    'authorizer_refresh_token': authorizer_refresh_token,
                    'authorizer_appid': authorizer_appid,
                    'company_id': company_id
                }
                authorizer_access_token_ret = create_authorizer_access_token(data)
                authorizer_access_token = authorizer_access_token_ret.data  # 调用生成 authorizer_access_token 授权方接口调用凭据, 也简称为令牌。

            get_qr_data['access_token'] = authorizer_access_token

            post_qr_data = {'path': path, 'width': 430}

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            qr_ret = s.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

            # qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

            if not qr_ret.content:
                rc.delete('xiaochengxu_token')
                response.msg = "生成小程序二维码未验证通过"

                return response

            # print('-------qr_ret---->', qr_ret.text)

            IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'qr_code') + user_qr_code
            with open('%s' % (IMG_PATH), 'wb') as f:
                f.write(qr_ret.content)

            if customer_id:
                user_obj = models.zgld_user_customer_belonger.objects.get(user_id=user_id, customer_id=customer_id)
                user_qr_code_path = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
                user_obj.qr_code = user_qr_code_path
                user_obj.save()
                print('----celery生成用户-客户对应的小程序二维码成功-->>',
                      'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

                # 一并生成海报
                data_dict = {'user_id': user_id, 'customer_id': customer_id}
                tasks.create_user_or_customer_small_program_poster.delay(json.dumps(data_dict))

            else:  # 没有 customer_id 说明不是在小程序中生成
                user_obj = models.zgld_userprofile.objects.get(id=user_id)
                user_obj.qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
                user_obj.save()
                print('----celery生成企业用户对应的小程序二维码成功-->>', 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

            response.data = {'qr_code': user_obj.qr_code}
            response.code = 200
            response.msg = "生成小程序二维码成功"

    return JsonResponse(response.__dict__)


# 获取企业用户信息
def qiyeweixin_user_get_userinfo(request):
    response = ResponseObj()
    company_id = request.GET.get('company_id')
    userid = request.GET.get('userid')

    company_objs = models.zgld_company.objects.filter(id=company_id)
    corp_id = company_objs[0].corp_id

    app_objs = models.zgld_app.objects.filter(company_id=company_id, app_type=3)
    if app_objs:
        app_obj = app_objs[0]
        permanent_code = app_obj.permanent_code
        if permanent_code:
            SuiteId = 'wx1cbe3089128fda03'  # '雷达AI | 三方应用id'
            _data = {
                'SuiteId': SuiteId,  # 三方应用IP 。
                'corp_id': corp_id,  # 授权方企业corpid
                'permanent_code': permanent_code,
            }
            access_token_ret = create_qiyeweixin_access_token(_data)
            access_token = access_token_ret.data.get('access_token')

            get_code_data = {
                'access_token': access_token,
                'userid': userid
            }
            code_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            user_list_ret = s.get(code_url, params=get_code_data)
            # user_list_ret = requests.get(code_url, params=get_code_data)

            user_list_ret_json = user_list_ret.json()
            print('===========【celery 企业微信】 获取 user_ticket 返回:==========>', json.dumps(user_list_ret_json))

            # userid = user_list_ret_json.get('userid')
            corpid = user_list_ret_json.get('corpid')
            avatar = user_list_ret_json.get('avatar')  # 加上100 获取小图
            mobile = user_list_ret_json.get('mobile')  # 加上100 获取小图
            gender = user_list_ret_json.get('gender')
            errmsg = user_list_ret_json.get('errmsg')
            if not avatar:
                avatar = 'statics/imgs/setAvator.jpg'

            if errmsg == 'ok':
                print('----------【celery 企业微信】获取 《用户基本信息》 返回 | userid---->', json.dumps(user_list_ret_json), "|",
                      userid)

                user_profile_objs = models.zgld_userprofile.objects.select_related('company').filter(
                    userid=userid,
                    company_id=company_id
                )
                user_profile_objs.update(
                    avatar=avatar,
                    gender=gender,
                    wechat_phone=mobile,  # 微信绑定的手机号
                )
                response.msg = '【celery企业微信】获取成员信息成功'
                response.code = 200
            else:
                print('----------【celery 企业微信】获取 《用户基本信息》报错 ------>')

    return JsonResponse(response.__dict__)


# 定时器生成海报或二维码
@csrf_exempt
def crontab_create_user_to_customer_qrCode_poster(request):
    if request.method == "GET":
        objs = models.zgld_user_customer_belonger.objects.filter(Q(poster_url__isnull=True) | Q(qr_code__isnull=True))

        if objs:
            for obj in objs:
                qr_code = obj.qr_code
                poster_url = obj.poster_url
                user_id = obj.user_id
                customer_id = obj.customer_id

                data_dict = {'user_id': user_id, 'customer_id': customer_id}
                if not qr_code:
                    # 生成小程序和企业用户对应的小程序二维码
                    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
                    get_data = {
                        'data': json.dumps(data_dict)
                    }
                    print('---【定时器生成】 小程序二维码: data_dict-->', data_dict)

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    s.get(url, params=get_data)

                    qr_code = obj.qr_code

                if not poster_url and qr_code:
                    print('---【定时器生成】 小程序海报: data_dict-->', data_dict)
                    tasks.create_user_or_customer_small_program_poster.delay(json.dumps(data_dict))

        else:
            print('------ 没有符合条件的【定时器刷新】生成二维码或海报 ------->>>')

        u_objs = models.zgld_userprofile.objects.filter(status=1, qr_code__isnull=True)
        if u_objs:
            user_id = u_objs[0].id
            data_dict = {'user_id': user_id, 'customer_id': ''}

            # 生成小程序和企业用户对应的小程序二维码
            url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
            get_data = {
                'data': json.dumps(data_dict)
            }
            print('---【定时器生成】 小程序二维码: data_dict-->', data_dict)

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            s.get(url, params=get_data)

    return HttpResponse('执行_定时器生成海报')


# 生成小程序的海报
@csrf_exempt
def create_user_or_customer_poster(request):
    response = ResponseObj()
    # customer_id = request.GET.get('customer_id')
    # user_id = request.GET.get('user_id')

    print(' create_user_or_customer_poster ---- 【生成海报celery】 request.GET | data 数据 -->', request.GET.get('data'))

    data = json.loads(request.GET.get('data'))
    user_id = data.get('user_id')
    customer_id = data.get('customer_id', '')
    poster_url = data.get('poster_url', '')
    print(' create_user_or_customer_poster --- [生成海报]customer_id | user_id --------->>', customer_id, user_id)

    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/mingpian/poster_html?user_id=%s&uid=%s' % (customer_id, user_id)
    if poster_url:
        url = poster_url

    _data = {
        'user_id': user_id,
        'customer_id' : customer_id,
        'poster_url' : url
    }
    create_poster_process(_data)

    return JsonResponse(response.__dict__)


def create_poster_process(data):
    response = ResponseObj()


    user_id = data.get('user_id')
    customer_id = data.get('customer_id', '')
    poster_url = data.get('poster_url')

    user_customer_belonger_id = data.get('user_customer_belonger_id')
    case_id = data.get('case_id')

    print('create_poster_process 传递的值 -------------->>',data)

    objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id, customer_id=customer_id)
    if not objs:  # 如果没有找到则表示异常
        response.code = 500
        response.msg = "传参异常"

    else:
        BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'user_poster', )
        print(' create_user_or_customer_poster ---->', BASE_DIR)

        platform = sys.platform  # 获取平台
        phantomjs_path = os.path.join(settings.BASE_DIR, 'zhugeleida', 'views_dir', 'tools')

        if 'linux' in platform:
            phantomjs_path = phantomjs_path + '/phantomjs'

        else:
            phantomjs_path = phantomjs_path + '/phantomjs.exe'

        print('create_user_or_customer_poster ----- phantomjs_path ----->>', phantomjs_path)

        driver = webdriver.PhantomJS(executable_path=phantomjs_path)
        driver.implicitly_wait(10)


        print('--- create_user_or_customer_poster ---- url -->', poster_url)

        try:
            driver.get(poster_url)
            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            if customer_id:
                user_poster_file_temp = '/%s_%s_poster_temp.png' % (user_id, customer_id)
                user_poster_file = '/%s_%s_%s_poster.png' % (user_id, customer_id, now_time)
            else:
                user_poster_file_temp = '/%s_poster_temp.png' % (user_id)
                user_poster_file = '/%s_%s_poster.png' % (user_id, now_time)

            driver.save_screenshot(BASE_DIR + user_poster_file_temp)
            driver.get_screenshot_as_file(BASE_DIR + user_poster_file_temp)

            element = driver.find_element_by_id("jietu")
            print("create_user_or_customer_poster -->", element.location)  # 打印元素坐标
            print("create_user_or_customer_poster -->", element.size)  # 打印元素大小

            left = element.location['x']
            top = element.location['y']
            right = element.location['x'] + element.size['width']
            bottom = element.location['y'] + element.size['height']

            im = Image.open(BASE_DIR + user_poster_file_temp)
            im = im.crop((left, top, right, bottom))

            print("create_user_or_customer_poster -->", len(im.split()))  # test
            if len(im.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = im.split()
                im = Image.merge("RGB", (r, g, b))
                im.save(BASE_DIR + user_poster_file)
            else:
                im.save(BASE_DIR + user_poster_file)

            print('page_source -->', driver.page_source)

            _poster_url = 'statics/zhugeleida/imgs/xiaochengxu/user_poster%s' % user_poster_file
            if os.path.exists(BASE_DIR + user_poster_file_temp): os.remove(BASE_DIR + user_poster_file_temp)
            print('"create_user_or_customer_poster -->", --------- 生成海报URL -------->', poster_url)

            if poster_url:

                    case_poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                        user_customer_belonger_id=user_customer_belonger_id,
                        case_id=case_id
                    )
                    if case_poster_belonger_objs:
                        case_poster_belonger_objs.update(
                            poster_url=_poster_url
                        )

                    else:
                        models.zgld_customer_case_poster_belonger.objects.create(
                            user_customer_belonger_id=user_customer_belonger_id,
                            case_id=case_id,
                            poster_url=_poster_url
                        )


            else:
                objs.update(
                    poster_url=_poster_url
                )

            ret_data = {
                'user_id': user_id,
                'poster_url': _poster_url,
            }

            print('结果 ret_data --->>', ret_data)
            response.data = ret_data
            response.msg = "请求成功"
            response.code = 200

        except Exception as e:
            response.msg = "PhantomJS截图失败"
            response.code = 400
            driver.quit()

    return  response




# 小程序生成token，并然后发送模板消息
@csrf_exempt
def user_send_template_msg(request):
    response = ResponseObj()

    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id')
    userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
    company_id = userprofile_obj.company_id
    print('company_id -->', company_id)
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    customer_obj = models.zgld_customer.objects.filter(id=customer_id)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
        customer_id=customer_id,
        user_id=user_id
    )
    exist_formid_json = json.loads(objs[0].customer.formid)
    user_name = objs[0].user.username
    flag = True
    i = 0
    j = 0
    while flag:

        post_template_data = {}
        key_name = '%s_authorizer_access_token' % (authorizer_appid)
        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。
        # print('------- [1] redis取出的 authorizer_access_token ------>>', authorizer_access_token)

        if not authorizer_access_token:
            data = {
                'key_name': key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,
                'company_id': company_id
            }
            # print('------ 使用的 data ------>>',data)
            authorizer_access_token_ret = create_authorizer_access_token(data)
            authorizer_access_token = authorizer_access_token_ret.data

            # print('------- [3] 新出锅的 authorizer_access_token ------>>', authorizer_access_token)

        print('------- [3] 最后的 authorizer_access_token ------>>', authorizer_access_token)
        get_template_data = {
            'access_token': authorizer_access_token  # 授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
        }
        # global openid,form_id
        if customer_obj and objs:
            openid = customer_obj[0].openid
            post_template_data['touser'] = openid

            # post_template_data['template_id'] = 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE'
            post_template_data['template_id'] = template_id

            # path = 'pages/mingpian/index' % (user_id)
            path = 'pages/mingpian/msg?source=template_msg&uid=%s&pid=' % (user_id)
            post_template_data['page'] = path

            if len(exist_formid_json) == 0:
                response.msg = "没有formID"
                response.code = 301
                print('------- 没有消费的formID -------->>')
                break

            print('---------formId 消费前数据----------->>', exist_formid_json)
            form_id = exist_formid_json.pop(-1)
            obj = models.zgld_customer.objects.filter(id=customer_id)

            obj.update(formid=json.dumps(exist_formid_json))
            print('---------formId 消费了哪个 ----------->>', form_id)
            post_template_data['form_id'] = form_id

            # 留言回复通知
            data = {
                'keyword1': {
                    'value': user_name  # 回复者
                },
                'keyword2': {
                    'value': now_time  # 回复时间
                },
                'keyword3': {
                    'value': '您有未读消息,点击小程序查看哦'  # 回复内容
                }
            }
            post_template_data['data'] = data
            # post_template_data['emphasis_keyword'] = 'keyword1.DATA'
            print('===========post_template_data=======>>', post_template_data)

            # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            template_ret = s.post(Conf['template_msg_url'], params=get_template_data,
                                  data=json.dumps(post_template_data))

            # template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()

            print('--------企业用户 send to 小程序 Template 接口返回数据--------->', template_ret)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"
                flag = False

            elif template_ret.get('errcode') == 40001:
                # 如果是token不对的话,只重试3次
                j = j + 1
                rc.delete(key_name)
                authorizer_access_token = ''
                if j == 3:
                    flag = False

                continue

            else:
                print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"

            i = i + 1
            if i == 10:  # 限制最多重试十次。
                print('---- 限制最多重试十次 ---->>')
                flag = False
                obj.update(formid='[]')

        else:
            response.msg = "客户不存在"
            response.code = 301
            print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)


## 发送公众号模板消息
@csrf_exempt
def user_send_gongzhonghao_template_msg(request):
    response = ResponseObj()

    print('---发送公众号模板消息request.GET -->', request.GET)

    user_id = request.GET.get('user_id')
    customer_id = request.GET.get('customer_id')
    parent_id = request.GET.get('parent_id')
    _type = request.GET.get('type')
    activity_id = request.GET.get('activity_id')
    content = request.GET.get('content')

    if _type == 'forward_look_article_tishi':

        activity_redPacket_objs = models.zgld_activity_redPacket.objects.filter(customer_id=customer_id,
                                                                                customer_parent_id=parent_id,
                                                                                activity_id=activity_id)
        if not activity_redPacket_objs:
            print('------ 【转发后查看 * 不发消息公众号模板消息提示】customer_id | parent_id | activity_id-------->>', customer_id, "|",
                  parent_id, "|", activity_id)

            return HttpResponse('Dont send message')

    userprofile_obj = models.zgld_userprofile.objects.select_related('company').get(id=user_id)
    company_id = userprofile_obj.company_id
    company_name = userprofile_obj.company.name

    obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    # objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(
    #     customer_id=customer_id,
    #     user_id=user_id
    # )

    objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
        customer_id=customer_id,
        user_id=user_id,
        user__company_id=company_id)

    # user_id = objs[0].user_id # 找到那个建立关系的人。

    customer_name = ''
    if parent_id:
        customer_obj = models.zgld_customer.objects.filter(id=parent_id)
        customer_name = objs[0].customer.username
        customer_name = common.conversion_base64_customer_username_base64(customer_name, customer_id)

    else:
        customer_obj = models.zgld_customer.objects.filter(id=customer_id)

    user_name = objs[0].user.username
    position = objs[0].user.position

    key_name = 'authorizer_access_token_%s' % (authorizer_appid)
    authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
    qywx_config_dict = ''
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        qywx_config_dict = three_service_obj.config
        if qywx_config_dict:
            qywx_config_dict = json.loads(qywx_config_dict)

    app_id = qywx_config_dict.get('app_id')
    app_secret = qywx_config_dict.get('app_secret')

    if not authorizer_access_token:
        authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)
        authorizer_access_token = rc.get(
            authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            data = {
                'key_name': authorizer_access_token_key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,
                'app_id': app_id,  # 'wx6ba07e6ddcdc69b3',
                'app_secret': app_secret,  # '0bbed534062ceca2ec25133abe1eecba'
            }

            authorizer_access_token_result = create_gongzhonghao_authorizer_access_token(data)
            if authorizer_access_token_result.code == 200:
                authorizer_access_token = authorizer_access_token_result.data

    get_template_data = {
        'access_token': authorizer_access_token  # 授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
    }

    if customer_obj and objs:
        openid = customer_obj[0].openid

        # 企业微信-发送公众号的客服聊天消息
        if _type == 'gongzhonghao_send_kefu_msg':

            kefu_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send'
            kefu_msg_get_data = {
                'access_token': authorizer_access_token
            }
            _content = json.loads(content)
            info_type = _content.get('info_type')
            msg = ''
            media_id = ''

            if info_type:
                info_type = int(info_type)
                if info_type == 1:
                    msg = _content.get('msg')

                elif info_type == 4:
                    url = _content.get('url')

                    add_news_url = 'https://api.weixin.qq.com/cgi-bin/media/upload'
                    add_new_data = {
                        'access_token': authorizer_access_token,
                        'type': 'image'
                    }

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接

                    files = {"media": open(url, "rb")}
                    add_news_ret = s.post(add_news_url, params=add_new_data, files=files)
                    add_news_ret = add_news_ret.json()

                    print('--------企业用户 公众号客服接口 微信公众号上临时素 返回数据--------->', add_news_ret)
                    media_id = add_news_ret.get('media_id')
                    if media_id:
                        print('-----  企业用户 公众号客服接口 微信公众号上临时素材 media_id ---->>', media_id)

                    else:
                        print('----   企业用户 公众号客服接口 微信公众号上临时素材 media_id[获取失败] -------->>')

            _content = '%s' % (msg)

            kefu_msg_post_data = {}
            if info_type == 1:

                kefu_msg_post_data = {
                    "touser": openid,
                    "msgtype": "text",
                    "text":
                        {
                            "content": _content
                        }
                }

            elif info_type == 4:

                kefu_msg_post_data = {
                    "touser": openid,
                    "msgtype": "image",
                    "image":
                        {
                            "media_id": media_id
                        }
                }

            objs.update(
                last_follow_time=datetime.datetime.now()
            )

            kefu_msg_post_data = json.dumps(kefu_msg_post_data, ensure_ascii=False)
            print('--- 数据 kefu_msg_post_data --->>', kefu_msg_post_data)

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            kefu_ret = s.post(kefu_msg_url, params=kefu_msg_get_data, data=kefu_msg_post_data.encode('utf-8'))
            # kefu_ret = requests.post(kefu_msg_url, params=kefu_msg_get_data,data=kefu_msg_post_data.encode('utf-8'))

            kefu_ret = kefu_ret.json()

            print('--------企业用户 send to 公众号 kefu_客服接口 - 返回数据--------->', kefu_ret)

            if info_type == 4 and kefu_ret.get('errmsg') != "ok":  # 满足 发送图片并且发送失败,记录下日志的素材ID
                print('-----企业用户 发送【小程序_客服消息】失败 json.dumps(kefu_msg_post_data)---->>', kefu_msg_post_data)
                msg = {
                    "msgtype": "image",
                    "image":
                        {
                            "media_id": media_id
                        }
                }

                models.zgld_chatinfo.objects.create(
                    msg=json.dumps(msg),
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=4,
                    is_customer_new_msg=False,  # 公众号客户不需要获取此提示消息
                    is_user_new_msg=False,
                    is_last_msg=False
                )

            if kefu_ret.get('errcode') == 40001:
                rc.delete(key_name)

            if kefu_ret.get('errmsg') == "ok":  # 发送成功
                print('-----企业用户 send to 公众号 kefu_客服消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送客服消息成功"

            else:  # 发送失败发送模板消息
                a_data = {}
                a_data['customer_id'] = customer_id
                a_data['user_id'] = user_id
                a_data['type'] = 'gongzhonghao_template_tishi'
                a_data['content'] = content
                tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】
                print('-----企业用户 再次发送【公众号_模板消息】 json.dumps(a_data)---->>', json.dumps(a_data))
                response.code = 301
                response.msg = "企业用户发送客服消息成功失败"




        # 发送公众号模板消息聊天消息 or  公众号客户查看文章后的红包活动提示
        else:

            # 留言回复通知
            '''
            您好，您咨询商家的问题已回复
            咨询名称：孕儿美摄影工作室-张炬
            消息回复：您有未读消息哦
            点击进入咨询页面
            '''
            info_type = ''
            post_template_data = {}

            ## 言简意赅的模板消息提示消息
            if _type == 'gongzhonghao_template_tishi':
                _content = json.loads(content)
                info_type = _content.get('info_type')
                msg = ''
                if info_type:
                    info_type = int(info_type)
                    if info_type == 1:
                        msg = _content.get('msg')

                    elif info_type == 4:  # 图片
                        msg = '您的专属客服发来一张图片,回复【A】查看哦'

                _content = '%s' % (msg)

                if position:
                    consult_info = ('%s - %s【%s】') % (company_name, user_name, position)
                else:
                    consult_info = ('%s - %s') % (company_name, user_name)

                data = {
                    'first': {
                        'value': ''  # 回复者
                    },
                    'keyword1': {
                        'value': consult_info + '\n',
                        "color": "#0000EE"
                    },
                    'keyword2': {
                        'value': _content + '\n',
                        "color": "#FF0000"
                    },
                    'remark': {
                        'value': '如需沟通,可在此公众号进行回复'  # 回复内容
                    }
                }

                post_template_data = {
                    'touser': openid,
                    'template_id': template_id,
                    # "miniprogram": {
                    #     "appid": appid,
                    #     "pagepath": path,
                    # },
                    'data': data
                }

            ## 参加活动后模板消息提示[活动规则]
            elif _type == 'forward_look_article_tishi':
                activity_obj = models.zgld_article_activity.objects.get(id=activity_id)

                activity_name = activity_obj.activity_name
                title = activity_obj.article.title
                reach_forward_num = activity_obj.reach_forward_num
                # activity_single_money = activity_obj.activity_single_money
                start_time = activity_obj.start_time.strftime('%Y-%m-%d %H:%M')
                end_time = activity_obj.end_time.strftime('%Y-%m-%d %H:%M')
                if not position:
                    position = ''
                remark = '活动规则: 关注公众号并分享文章给朋友/朋友圈,每满足%s人查看,立返现金红包。分享不停,红包不停,上不封顶。活动日期: %s 至 %s' % (
                    reach_forward_num, start_time, end_time)
                data = {
                    'first': {
                        'value': ('        您好,我是%s的%s%s,很高兴为您服务, 欢迎您参加【分享文章 赚现金活动】\n' % (
                            company_name, position, user_name))  # 回复者
                    },
                    'keyword1': {
                        'value': '您的好友【%s】查看了您转发的活动文章《%s》\n' % (customer_name, title),
                        "color": "#0000EE"
                    },
                    'keyword2': {
                        'value': '【回复 T%s】查看红包活动进度、具体人员详情\n' % (activity_id),
                        "color": "#FF0000"

                    },
                    'remark': {
                        'value': remark  # 回复内容
                    }
                }

                post_template_data = {
                    'touser': openid,
                    'template_id': template_id,
                    # "miniprogram": {
                    #     "appid": appid,
                    #     "pagepath": path,
                    # },
                    'data': data
                }

            # 发送商城的消息
            elif _type == 'gongzhonghao_template_shopping_mall':

                _content = json.loads(content)
                info_type = _content.get('info_type')

                if info_type:
                    info_type = int(info_type)
                    if info_type == 6:
                        _content = '点击进入官方商城'

                if position:
                    consult_info = ('%s - %s【%s】') % (company_name, user_name, position)
                else:
                    consult_info = ('%s - %s') % (company_name, user_name)

                data = {
                    'first': {
                        'value': ''  # 回复者
                    },
                    'keyword1': {
                        'value': consult_info + '\n',
                        "color": "#0000EE"
                    },
                    'keyword2': {
                        'value': _content + '\n',
                        "color": "#FF0000"
                    },
                    'remark': {
                        'value': '如需沟通,可在此公众号或小程序内进行回复！玩转名片电商从这里开始 go ~'  # 回复内容
                    }
                }

                xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)

                authorization_appid = ''
                if xiaochengxu_app_objs:
                    authorization_appid = xiaochengxu_app_objs[0].authorization_appid

                path = 'pages/store/store?uid=%s' % (user_id)
                post_template_data = {
                    'touser': openid,
                    'template_id': template_id,
                    "miniprogram": {
                        "appid": authorization_appid,
                        "pagepath": path,
                    },
                    'data': data
                }

            print('=========== 发送出去的【模板消息】请求数据 =======>>', json.dumps(post_template_data))

            # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考
            template_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            template_ret = s.post(template_msg_url, params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()
            errcode = template_ret.get('errcode')

            print('--------企业用户 send to 公众号 Template 接口返回数据--------->', template_ret)

            if errcode == 40001:
                rc.delete(key_name)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 公众号 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"

            elif errcode == 43004 or errcode == 40013:  # {'errcode': 40013, 'errmsg': 'invalid appid hint: [Vc1zrA00434123]'}

                # {'errcode': 43004, 'errmsg': 'require subscribe hint: [_z5Nwa00958672]'}
                # {'errcode': 40003, 'errmsg': 'invalid openid hint: [JUmuwa08163951]'}
                redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)

                _msg = '此客户【未关注】公众号'
                if info_type == 6 and errcode == 40013:
                    _msg = '此公众号未绑定小程序,请联系管理员'  # 【名片商城】未送达

                encodestr = base64.b64encode(_msg.encode('utf-8'))
                msg = str(encodestr, 'utf-8')
                _content = {
                    'msg': msg,
                    'info_type': 1
                }
                content = json.dumps(_content)

                _objs = models.zgld_chatinfo.objects.filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=3,

                )
                if not _objs:
                    models.zgld_chatinfo.objects.create(
                        content=content,
                        userprofile_id=user_id,
                        customer_id=customer_id,
                        send_type=3,
                        is_last_msg=False
                    )

                    rc.set(redis_user_id_key, True)  # 代表雷达用户有新消息 要推送了。


            else:
                print('-----企业用户 send to 公众号 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"


    else:
        response.msg = "客户不存在"
        response.code = 301
        print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)


# 获取查询最新一次提交的审核状态 并提交审核通过的代码上线.
@csrf_exempt
def get_latest_audit_status_and_release_code(request):
    from zhugeleida.views_dir.admin.dai_xcx import batch_get_latest_audit_status
    response = ResponseObj()

    if request.method == "GET":
        objs = models.zgld_xiapchengxu_upload_audit.objects.filter(audit_result=2, auditid__isnull=False).order_by(
            '-audit_commit_date')

        audit_status_data = {
            'upload_audit_objs': objs
        }
        audit_status_response = batch_get_latest_audit_status(audit_status_data)  # 只管查询最后一次上传的代码，

        response.code = 200
        response.msg = '查询最新一次提交的审核状态-执行完成'

    return JsonResponse(response.__dict__)


# 关注发红包和转发文章满足就发红包
@csrf_exempt
def user_forward_send_activity_redPacket(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        print('------- 【转发发送大红包】user_send_activity_redPacket ------>>')

        # ip = ''
        # if request.META.get('HTTP_X_FORWARDED_FOR'):
        #     ip = request.META.get('HTTP_X_FORWARDED_FOR')
        # elif request.META.get('REMOTE_ADDR'):
        #     ip = request.META.get('REMOTE_ADDR')
        # else:
        #     ip = '0.0.0.0'

        ip = '192.168.1.10'

        client_ip = ip
        company_id = request.GET.get('company_id')
        user_id = request.GET.get('user_id')
        parent_id = request.GET.get('parent_id')
        article_id = request.GET.get('article_id')
        activity_id = request.GET.get('activity_id')
        article_access_log_id = request.GET.get('article_access_log_id')

        activity_redPacket_objs = models.zgld_activity_redPacket.objects.filter(customer_id=parent_id,
                                                                                article_id=article_id,
                                                                                activity_id=activity_id
                                                                                )
        if activity_redPacket_objs:
            activity_redPacket_obj = activity_redPacket_objs[0]

            activity_objs = models.zgld_article_activity.objects.filter(id=activity_id).order_by('-create_date')
            activity_obj = activity_objs[0]
            start_time = activity_obj.start_time
            end_time = activity_obj.end_time

            forward_read_num = models.zgld_activity_redPacket.objects.filter(
                customer_parent_id=parent_id, activity_id=activity_id, create_date__lte=end_time,
                create_date__gte=start_time).values_list('customer_id', flat=True).distinct().count()

            forward_stay_time_dict = models.zgld_article_to_customer_belonger.objects.filter(
                customer_parent_id=parent_id, article_id=article_id, create_date__lte=end_time,
                create_date__gte=start_time).aggregate(forward_stay_time=Sum('stay_time'))

            forward_stay_time = forward_stay_time_dict.get('forward_stay_time')
            if not forward_stay_time:
                forward_stay_time = 0

            activity_redPacket_objs.update(
                forward_read_count=forward_read_num,
                forward_stay_time=forward_stay_time
            )

            reach_stay_time = activity_obj.reach_stay_time  # 达到多少时间才能发放
            is_limit_area = activity_obj.is_limit_area  # 是否开启了限制
            limit_area = activity_obj.limit_area  # 限制的区域

            reach_forward_num = activity_obj.reach_forward_num  # 达到多少次发红包(转发阅读后次数))
            already_send_redPacket_num = activity_redPacket_obj.already_send_redPacket_num  # 已发放次数
            # already_send_redPacket_money = activity_redPacket_obj.already_send_redPacket_money        #已发红包金额

            if reach_forward_num != 0:  # 不能为0
                forward_read_num = int(forward_read_num)
                if forward_read_num >= reach_forward_num:  # 转发大于 阈值,达到可以条件

                    divmod_ret = divmod(forward_read_num, reach_forward_num)

                    shoudle_send_num = divmod_ret[0]
                    yushu = divmod_ret[1]
                    _send_log_dict = {}
                    if shoudle_send_num > already_send_redPacket_num:  # 应发数量 > 已发放的数量（数据库中记录值）

                        customer_obj = models.zgld_customer.objects.get(id=parent_id)
                        openid = customer_obj.openid  # 对应的发放用户openid
                        formatted_address = customer_obj.formatted_address  # 客户具体地址
                        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        area_Flag = False
                        if is_limit_area:  # True 地域限制条件开启了 并且 获取到了用户的具体位置

                            limit_area = json.loads(limit_area)
                            for area in limit_area.get('limit_area_list'):
                                if area in formatted_address:  # 如果本区域满足发放
                                    area_Flag = True
                                    _send_log_dict = {
                                        'type': '数量满足|有地域限制【在发放范围内】',
                                        'activity_single_money': '发送的地域area: %s | 客户具体地址: formatted_address: %s' % (
                                        area, formatted_address),
                                        'send_time': now_time,
                                    }

                            if not area_Flag:
                                _send_log_dict = {
                                    'type': '数量满足|有地域限制【没有在发放范围内】',
                                    'activity_single_money': '客户具体地址: formatted_address: %s' % (formatted_address),
                                    'send_time': now_time,
                                }


                        else:  # 没有开启限制
                            area_Flag = True

                        time_Flag = False
                        if reach_stay_time == 0:  # 代表没有时间秒数的限制,立即发放这个用户的红包
                            time_Flag = True

                        else:
                            time_Flag = False
                            if article_access_log_id:
                                objs = models.zgld_article_access_log.objects.filter(id=article_access_log_id)
                                stay_time = None
                                if objs:
                                    obj = objs[0]
                                    stay_time = obj.stay_time
                                    if stay_time >= reach_stay_time:  # 单次查看时间大于 时间限制
                                        time_Flag = True

                                _send_log_dict = {
                                    'type': '数量满足|有时间限制|Time_Flag: %s' % (time_Flag),
                                    'activity_single_money': 'Log_id:%s | 单次查看时间:%s | 时间限制: %s' % (
                                    article_access_log_id, stay_time, reach_stay_time),
                                    'send_time': now_time,
                                }

                            else:
                                _send_log_dict = {
                                    'type': '数量满足|有时间限制|Time_Flag: %s' % (time_Flag),
                                    'activity_single_money': '无log_id | 无统计单次阅读时间 | 时间限制: %s' % (reach_stay_time),
                                    'send_time': now_time,
                                }

                        send_log_list = activity_redPacket_obj.access_log
                        _send_log_list = json.loads(send_log_list)
                        _send_log_list.append(_send_log_dict)
                        send_log_list = json.dumps(_send_log_list)

                        activity_redPacket_objs.update(access_log=send_log_list)

                        if area_Flag and time_Flag:  # 满足发送的时间和地区限制

                            print(
                                '---- 【满足发红包条件-时间和地区限制】forward_read_num[转发被查看数] | reach_forward_num[需满足的阈值] ----->>',
                                forward_read_num, "|", reach_forward_num)
                            print(
                                '---- 【满足发红包条件-时间和地区限制】shoudle_send_num[实发数] | already_send_redPacket_num[已发数] ----->>',
                                shoudle_send_num, "|",
                                already_send_redPacket_num)

                            _data = {
                                'company_id': company_id,
                                'openid': openid,
                                'user_id': user_id,
                                'parent_id': parent_id,
                                'shoudle_send_num': shoudle_send_num,
                                'already_send_redPacket_num': already_send_redPacket_num
                            }
                            Red_Packet_Sending_Process(activity_objs, activity_redPacket_objs, _data)

                    else:
                        response.code = 301
                        response.msg = '应发数<=已发数'
                        print('------ 活动发红包记录表 应发数<=已发数 shoudle_send_num|reach_forward_num ----->>', shoudle_send_num,
                              '|', reach_forward_num)

                else:

                    response.code = 301
                    response.msg = '转发查看数未达到阈值'
                    print('------ 活动发红包记录表 应发数<=已发数 shoudle_send_num|send_redPacket_num ----->>', reach_forward_num,
                          '|', already_send_redPacket_num)

        else:
            response.code = 301
            response.msg = '[无记录]活动发红包记录表'
            print('------[无记录]活动发红包记录表 parent_id | article_id | activity_id ----->>', parent_id, '|', article_id, "|",
                  activity_id)

    return JsonResponse(response.__dict__)


## 红包发送裂变红包过程函数
def Red_Packet_Sending_Process(activity_objs, activity_redPacket_objs, data):
    response = Response.ResponseObj()
    company_id = data.get('company_id')
    openid = data.get('openid')
    user_id = data.get('user_id')
    parent_id = data.get('parent_id')
    shoudle_send_num = data.get('shoudle_send_num')
    already_send_redPacket_num = data.get('already_send_redPacket_num')

    activity_obj = activity_objs[0]

    app_objs = models.zgld_gongzhonghao_app.objects.select_related('company').filter(company_id=company_id)

    activity_single_money = ''
    mode = activity_obj.mode
    if mode == 1:  # 随机金额
        max_single_money = activity_obj.max_single_money
        min_single_money = activity_obj.min_single_money

        rand_num = random.uniform(max_single_money, min_single_money)
        activity_single_money = float(round(rand_num, 2))

    elif mode == 2:  # 固定金额
        activity_single_money = activity_obj.activity_single_money

    activity_name = activity_obj.activity_name

    authorization_appid = ''
    gongzhonghao_name = ''
    is_used_daifa_redPacket = ''
    if app_objs:
        # company_name = '%s' % (app_objs[0].company.name)
        gongzhonghao_name = '%s' % (app_objs[0].name)
        authorization_appid = app_objs[0].authorization_appid
        is_used_daifa_redPacket = app_objs[0].is_used_daifa_redPacket

    _company_id = 1
    if is_used_daifa_redPacket == 2:  # (1, '代发红包'),  (2, '自己商户发红包')
        _company_id = company_id

    shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.select_related('xiaochengxucompany').filter(
        xiaochengxucompany_id=_company_id)  # 使用固定商户账户-发红包。

    shangHuHao = ''
    shangHuMiYao = ''
    code = ''
    msg = ''
    account_balance = ''
    if shangcheng_objs:
        shangcheng_obj = shangcheng_objs[0]
        shangHuHao = shangcheng_obj.shangHuHao
        shangHuMiYao = shangcheng_obj.shangHuMiYao

        if is_used_daifa_redPacket == 1:  # 代发红包，要看自己平台上午有没有钱
            company_obj = models.zgld_company.objects.get(id=company_id)
            account_balance = company_obj.account_balance  # # 账户余额

        elif is_used_daifa_redPacket == 2:
            account_balance = shangcheng_obj.xiaochengxucompany.account_balance  # # 账户余额

        if activity_single_money > account_balance and is_used_daifa_redPacket == 1:  # 当 发送金额大于账户余额
            code = 199  # 余额不足
            msg = '平台账户余额不足'
            activity_redPacket_objs.update(
                should_send_redPacket_num=shoudle_send_num,  # 应该发放的次数 [应发]
                status=3  # (2,'未发'),  改为未发状态
            )
            activity_objs.update(
                reason='平台账户余额不足,请充值'
            )
            objs = models.zgld_customer.objects.filter(session_key='notifier', company_id__in=[int(company_id), 1, 2])
            remark = 'openid: %s | company_id: %s | %s' % (openid, company_id, '')
            for obj in objs:
                data_dict = {
                    'company_id': obj.company_id,
                    'customer_id': obj.id,
                    'type': 'gongzhonghao_template_tishi',
                    'title': '平台账户余额不足提示[文章活动]',
                    'content': '转发文章|发红包-平台账户余额不足，请联系管理员进行充值',
                    'remark': remark
                }
                print('红包发送报错数据 --------->', data_dict)
                tasks.monitor_send_gzh_template_msg.delay(data_dict)

    if code != 199:

        _data = {
            'client_ip': '192.168.1.10',
            'shanghukey': shangHuMiYao,  # 支付钱数
            'total_fee': activity_single_money,  # 支付钱数
            'appid': authorization_appid,  # 小程序ID
            'mch_id': shangHuHao,  # 商户号
            'openid': openid,
            'send_name': gongzhonghao_name,  # 商户名称
            'act_name': activity_name,  # 活动名称
            'remark': '分享不停,红包不停,上不封顶!',  # 备注信息
            'wishing': '感谢您参加【分享文章 赚现金活动】！',  # 祝福语
        }
        print('------[调用转发后满足条件,发红包的接口 data 数据]------>>', json.dumps(_data))

        response_ret = focusOnIssuedRedEnvelope(_data)
        code = response_ret.code
        msg = response_ret.msg
        if code == 200:

            now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('---- 调用发红包成功[转发得现金] 状态值:200  parent_id | openid --->>', parent_id, '|', openid)

            _send_log_dict = {
                'type': '自动发送',
                'activity_single_money': activity_single_money,
                'send_time': now_time,
            }
            activity_redPacket_obj = activity_redPacket_objs[0]
            send_log_list = activity_redPacket_obj.send_log
            _send_log_list = json.loads(send_log_list)
            _send_log_list.append(_send_log_dict)
            send_log_list = json.dumps(_send_log_list)

            bufa_send_activity_redPacket = shoudle_send_num - already_send_redPacket_num

            status = 1
            if bufa_send_activity_redPacket > 1:  # 判断该用户是不是发布状态.应发数量减去已发数量时大于1,说明此用户已经有补发的红包
                status = 4  # 补发状态

            activity_redPacket_objs.update(
                already_send_redPacket_num=F('already_send_redPacket_num') + 1,
                already_send_redPacket_money=F('already_send_redPacket_money') + activity_single_money,
                # 已发红包金额 [累加发送金额]
                should_send_redPacket_num=shoudle_send_num,  # 应该发放的次数 [应发]
                status=status,  # (1,'已发成功'),
                send_log=send_log_list  #
            )
            activity_objs.update(
                reason='发放成功',
                already_send_redPacket_num=F('already_send_redPacket_num') + 1,
                already_send_redPacket_money=F('already_send_redPacket_money') + activity_single_money,
            )

            if is_used_daifa_redPacket == 1:  # 只有代发才记录资金流水
                ### 红包发送之后,记录红包流水
                record_data = {
                    'admin_user_id': '',
                    'user_id': user_id,
                    'company_id': company_id,
                    'customer_id': parent_id,
                    'transaction_amount': activity_single_money,
                    'source': 2,
                    'type': 4
                }
                record_money_process(record_data)




        else:  # 余额不足后者其他原因,记录下日志
            activity_redPacket_objs.update(
                should_send_redPacket_num=shoudle_send_num,  # 应该发放的次数 [应发]
                status=3  # (2,'未发'),  改为未发状态
            )
            activity_objs.update(
                reason=response_ret.msg
            )
            objs = models.zgld_customer.objects.filter(session_key='notifier',
                                                       company_id__in=[1, 2])
            remark = 'openid: %s | company_id: %s | %s' % (openid, company_id, response_ret.msg)
            for obj in objs:
                data_dict = {
                    'company_id': obj.company_id,
                    'customer_id': obj.id,
                    'type': 'gongzhonghao_template_tishi',
                    'title': '商户红包报错提示[文章活动]',
                    'content': '商户发红包发生错误,请及时排查',
                    'remark': remark
                }
                print('红包发送报错数据 --------->', data_dict)
                tasks.monitor_send_gzh_template_msg.delay(data_dict)

    if code == 199:
        a_data = {}
        a_data['customer_id'] = parent_id
        a_data['user_id'] = user_id
        a_data['type'] = 'gongzhonghao_template_tishi'
        a_data['content'] = json.dumps({'msg': '您好,活动过于火爆,账户被刷爆,已联系管理员进行充值，然后再补发哦', 'info_type': 1})

        print('-----企业用户 公众号_模板消息【余额不足提示】 json.dumps(a_data)---->>', json.dumps(a_data))
        tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】

        response.code = code
        response.msg = msg

    return response


## 资金流水记录过程函数
def record_money_process(data):
    response = Response.ResponseObj()

    admin_user_id = data.get('admin_user_id')
    user_id = data.get('user_id')
    company_id = data.get('company_id')
    customer_id = data.get('customer_id')
    transaction_amount = data.get('transaction_amount')
    source = data.get('source')
    type = data.get('type')

    print('admin_user_id----->>', admin_user_id)
    print('user_id----->>', user_id)
    print('company_id----->>', company_id)
    print('customer_id----->>', customer_id)
    print('transaction_amount----->>', transaction_amount)
    print('source----->>', source)
    print('type----->>', type)

    ## 资金流水记录表
    ''''
       (1,'充值成功'),
       (2,'提现成功'),
       (3,'红包发放(关注公众号)'),
       (4,'红包发放(文章裂变)'),
       (5,'商城入账'),
       (6,'商城退款')
    '''
    company_objs = models.zgld_company.objects.filter(id=company_id)

    if int(type) == 1:  # (1,'充值成功'),
        company_objs.update(
            account_balance=F('account_balance') + transaction_amount,  # 账户余额
            leiji_chongzhi=F('leiji_chongzhi') + transaction_amount,  # 累计充值
        )

    elif int(type) == 2:  # (2,'提现成功'),
        account_balance = company_objs[0].account_balance  # 余额

        if account_balance < int(transaction_amount):
            response.code = 303
            response.msg = '账户余额不足'
            return response

        else:
            company_objs.update(
                account_balance=F('account_balance') - transaction_amount,  # 账户余额
                leiji_zhichu=F('leiji_zhichu') + transaction_amount,  # 累计支出
            )

    elif int(type) in [3, 4]:  # (3,'红包发放(关注公众号)'),  (4,'红包发放(文章裂变)'),

        company_objs.update(
            account_balance=F('account_balance') - transaction_amount,  # 账户余额
            leiji_zhichu=F('leiji_zhichu') + transaction_amount,  # 累计支出
        )

    if not admin_user_id:
        admin_user_id = None

    if not customer_id:
        customer_id = None

    if not user_id:
        user_id = None

    account_balance = company_objs[0].account_balance  # 余额
    print('admin_user_id----->>', admin_user_id)
    print('user_id----->>', user_id)
    print('customer_id----->>', customer_id)
    print('transaction_amount----->>', transaction_amount)
    print('account_balance----->>', account_balance)

    models.zgld_money_record.objects.create(
        company_id=company_id,
        source=source,  # (1,'平台账号'),  (2,'公众号'),    (3,'小程序'),
        type=type,
        admin_user_id=admin_user_id,
        user_id=user_id,
        customer_id=customer_id,
        transaction_amount=transaction_amount,  # 交易金额
        account_balance=account_balance  # 余额
    )

    response.code = 200
    response.msg = '记录成功'

    return response
    # return JsonResponse(response.__dict__)


# [定时器] - 补发红包红包
@csrf_exempt
def bufa_send_activity_redPacket(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        print('------- 【补发红包】 ------>>')

        ip = '192.168.1.10'

        client_ip = ip
        # company_id = request.GET.get('company_id')
        # parent_id = request.GET.get('parent_id')
        # article_id = request.GET.get('article_id')
        # activity_id = request.GET.get('activity_id')

        activity_redPacket_objs = models.zgld_activity_redPacket.objects.select_related('company', 'activity',
                                                                                        'article', 'customer').filter(
            status__in=[3, 4])

        if activity_redPacket_objs:

            for activity_redPacket_obj in activity_redPacket_objs:

                should_send_redPacket_num = activity_redPacket_obj.should_send_redPacket_num
                already_send_redPacket_num = activity_redPacket_obj.already_send_redPacket_num
                activity_id = activity_redPacket_obj.activity_id
                activity_objs = models.zgld_article_activity.objects.filter(id=activity_id).order_by('-create_date')

                if should_send_redPacket_num > already_send_redPacket_num and activity_objs:

                    company_id = activity_redPacket_objs[0].company_id
                    customer_id = activity_redPacket_obj.customer_id
                    article_id = activity_redPacket_obj.article_id

                    activity_single_money = ''
                    mode = activity_redPacket_obj.activity.mode
                    if mode == 1:  # 随机金额
                        max_single_money = activity_redPacket_obj.activity.max_single_money
                        min_single_money = activity_redPacket_obj.activity.min_single_money

                        rand_num = random.uniform(max_single_money, min_single_money)
                        activity_single_money = float(round(rand_num, 2))

                    elif mode == 2:  # 固定金额

                        activity_single_money = activity_redPacket_obj.activity.activity_single_money

                    activity_name = activity_redPacket_obj.activity.activity_name

                    bufa_redPacket_num = should_send_redPacket_num - already_send_redPacket_num
                    app_objs = models.zgld_gongzhonghao_app.objects.select_related('company').filter(
                        company_id=company_id)

                    customer_obj = models.zgld_customer.objects.get(id=customer_id)
                    openid = customer_obj.openid

                    authorization_appid = ''
                    gongzhonghao_name = ''
                    is_used_daifa_redPacket = ''
                    if app_objs:
                        # company_name = '%s' % (app_objs[0].company.name)
                        gongzhonghao_name = '%s' % (app_objs[0].name)
                        authorization_appid = app_objs[0].authorization_appid

                        ###
                        is_used_daifa_redPacket = app_objs[0].is_used_daifa_redPacket

                    _company_id = 1
                    if is_used_daifa_redPacket == 2:  # (1, '代发红包'),  (2, '自己商户发红包')
                        _company_id = company_id

                    shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.select_related(
                        'xiaochengxucompany').filter(xiaochengxucompany_id=_company_id)  # 使用固定商户账户-发红包。

                    shangHuHao = ''
                    shangHuMiYao = ''
                    code = ''
                    msg = ''
                    if shangcheng_objs:
                        shangcheng_obj = shangcheng_objs[0]
                        shangHuHao = shangcheng_obj.shangHuHao
                        shangHuMiYao = shangcheng_obj.shangHuMiYao
                        account_balance = shangcheng_objs[0].xiaochengxucompany.account_balance  # 账户余额

                        if activity_single_money > account_balance and is_used_daifa_redPacket == 1:  # 当 发送金额大于账户余额
                            code = 199  # 余额不足
                            msg = '平台账户余额不足【自动补发】'

                            activity_objs.update(
                                reason=msg
                            )

                    # shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxucompany_id=company_id)
                    # shangHuHao = ''
                    # shangHuMiYao = ''
                    # if shangcheng_objs:
                    #     shangcheng_obj = shangcheng_objs[0]
                    #     shangHuHao = shangcheng_obj.shangHuHao
                    #     # send_name = shangcheng_obj.shangChengName
                    #     shangHuMiYao = shangcheng_obj.shangHuMiYao

                    if code != 199:
                        _data = {
                            'client_ip': client_ip,
                            'shanghukey': shangHuMiYao,  # 支付钱数
                            'total_fee': activity_single_money,  # 支付钱数
                            'appid': authorization_appid,  # 小程序ID
                            'mch_id': shangHuHao,  # 商户号
                            'openid': openid,
                            'send_name': gongzhonghao_name,  # 商户名称
                            'act_name': activity_name,  # 活动名称
                            'remark': '分享不停,红包不停,上不封顶!',  # 备注信息
                            'wishing': '感谢您参加【分享文章 赚现金活动】！',  # 祝福语
                        }
                        print('------[补发后-满足条件,发红包的接口 data 数据]------>>', json.dumps(_data))

                        for i in range(bufa_redPacket_num):
                            response_ret = focusOnIssuedRedEnvelope(_data)

                            if response_ret.code == 200:
                                now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print('---- 调用发红包成功[转发得现金] 状态值:200  customer_id | openid --->>', customer_id, '|',
                                      openid)

                                _send_log_dict = {
                                    'type': '自动补发',
                                    'activity_single_money': activity_single_money,
                                    'send_time': now_time,
                                }
                                activity_redPacket_obj = activity_redPacket_objs[0]
                                send_log_list = activity_redPacket_obj.send_log
                                _send_log_list = json.loads(send_log_list)
                                _send_log_list.append(_send_log_dict)
                                send_log_list = json.dumps(_send_log_list)

                                activity_redPacket_objs.update(
                                    already_send_redPacket_num=F('already_send_redPacket_num') + 1,
                                    already_send_redPacket_money=F(
                                        'already_send_redPacket_money') + activity_single_money,
                                    # 已发红包金额 [累加发送金额]
                                    # should_send_redPacket_num=shoudle_send_num,  # 应该发放的次数 [应发]
                                    status=1,  # (1,'已发'),
                                    send_log=send_log_list  # (1,'已发'),
                                )
                                activity_objs.update(
                                    reason='发放成功',
                                    already_send_redPacket_num=F('already_send_redPacket_num') + 1,
                                    already_send_redPacket_money=F(
                                        'already_send_redPacket_money') + activity_single_money,
                                )

                                _should_send_redPacket_num = activity_redPacket_objs[0].should_send_redPacket_num
                                _already_send_redPacket_num = activity_redPacket_objs[0].already_send_redPacket_num

                                _bufa_redPacket_num = _should_send_redPacket_num - _already_send_redPacket_num
                                if _bufa_redPacket_num + 1 != bufa_redPacket_num:  # 如果补发不相等说明有人在说手动触发了。我们在这停止发放。
                                    if _bufa_redPacket_num > 1:
                                        activity_redPacket_objs.update(
                                            status=4
                                        )
                                    break

                            else:  # 余额不足后者其他原因,记录下日志

                                code = response_ret.code
                                activity_redPacket_objs.update(
                                    status=3,
                                )
                                activity_objs.update(
                                    reason=response_ret.msg
                                )
                                break

                    if code == 199:
                        objs = models.zgld_customer.objects.filter(session_key='notifier', company_id=_company_id)

                        for obj in objs:
                            data_dict = {
                                'company_id': obj.company_id,
                                'customer_id': obj.id,
                                'type': 'gongzhonghao_template_tishi',
                                'title': '红包账户余额不足提示',
                                'content': '系统自动补发红包，余额不足，请联系管理员进行充值',
                                'remark': ''
                            }
                            print('红包发送报错数据 --------->', data_dict)
                            tasks.monitor_send_gzh_template_msg.delay(data_dict)


                else:
                    response.code = 301
                    response.msg = '实发数<=已发数'
                    print('------ 【实发数<=已发数】 should_send_redPacket_num | already_send_redPacket_num ----->>',
                          should_send_redPacket_num,
                          '|', already_send_redPacket_num)

        else:
            response.code = 301
            response.msg = '[无补发用户]'
            print('------【无补发用户】红包记录表里没有要补发的客户 ----->>')

    return JsonResponse(response.__dict__)


# 关注发红包
@csrf_exempt
def user_focus_send_activity_redPacket(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        print('------- 【关注发大红包测试】user_focus_send_activity_redPacket ------>>')

        # ip = ''
        # if request.META.get('HTTP_X_FORWARDED_FOR'):
        #     ip = request.META.get('HTTP_X_FORWARDED_FOR')
        # elif request.META.get('REMOTE_ADDR'):
        #     ip = request.META.get('REMOTE_ADDR')
        # else:
        #     ip = '0.0.0.0'

        ip = '192.168.1.10'

        client_ip = ip
        company_id = request.GET.get('company_id')
        customer_id = request.GET.get('customer_id')
        user_id = request.GET.get('user_id')

        gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
        if gongzhonghao_app_objs:
            gongzhonghao_app_obj = gongzhonghao_app_objs[0]
            is_focus_get_redpacket = gongzhonghao_app_obj.is_focus_get_redpacket

            if is_focus_get_redpacket:  # 开启了-关注领取红包是否开启

                objs = models.zgld_customer.objects.filter(id=customer_id)

                if objs:
                    obj = objs[0]

                    openid = obj.openid
                    is_subscribe = obj.is_subscribe  # 用户是否订阅该公众号   (0, '没有订阅该公众号'),
                    is_receive_redPacket = obj.is_receive_redPacket  # 是否发送过关注红包  (0, '没有发送过关注红包'),

                    if is_subscribe == 1 and is_receive_redPacket == 0:

                        focus_get_money = ''
                        # focus_total_money   =  gongzhonghao_app_obj.focus_get_money
                        mode = gongzhonghao_app_obj.mode
                        if mode == 1:  # 随机金额
                            max_single_money = gongzhonghao_app_obj.max_single_money
                            min_single_money = gongzhonghao_app_obj.min_single_money

                            rand_num = random.uniform(max_single_money, min_single_money)
                            focus_get_money = float(round(rand_num, 2))

                        elif mode == 2:  # 固定金额
                            focus_get_money = gongzhonghao_app_obj.focus_get_money

                        app_objs = models.zgld_gongzhonghao_app.objects.select_related('company').filter(
                            company_id=company_id)

                        authorization_appid = ''
                        gongzhonghao_name = ''
                        is_used_daifa_redPacket = ''

                        if app_objs:
                            authorization_appid = app_objs[0].authorization_appid
                            # company_name = '【%s】' % (app_objs[0].company.name)
                            gongzhonghao_name = app_objs[0].name

                            is_used_daifa_redPacket = app_objs[0].is_used_daifa_redPacket

                        _company_id = 1
                        if is_used_daifa_redPacket == 2:  # (1, '代发红包'),  (2, '自己商户发红包')
                            _company_id = company_id

                        ## 判断使用的商户发红包
                        shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.select_related(
                            'xiaochengxucompany').filter(xiaochengxucompany_id=_company_id)  # 使用固定商户账户-发红包。
                        send_name = ''
                        shangHuHao = ''
                        shangHuMiYao = ''
                        code = ''
                        account_balance = ''
                        if shangcheng_objs:
                            shangcheng_obj = shangcheng_objs[0]
                            shangHuHao = shangcheng_obj.shangHuHao
                            shangHuMiYao = shangcheng_obj.shangHuMiYao

                            if is_used_daifa_redPacket == 1:  # 代发红包，要看自己平台上午有没有钱
                                company_obj = models.zgld_company.objects.get(id=company_id)
                                account_balance = company_obj.account_balance  # # 账户余额

                            elif is_used_daifa_redPacket == 2:
                                account_balance = shangcheng_obj.xiaochengxucompany.account_balance  # # 账户余额

                            if focus_get_money > account_balance and is_used_daifa_redPacket == 1:  # 当 发送金额大于账户余额
                                code = 199  # 余额不足
                                app_objs.update(
                                    reason='平台账户余额不足,请联系管理员充值'
                                )

                                remark = 'openid: %s | company_id: %s | %s' % (openid, company_id, '')
                                objs = models.zgld_customer.objects.filter(session_key='notifier',
                                                                           company_id__in=[int(company_id), 1, 2])
                                for obj in objs:
                                    data_dict = {
                                        'company_id': obj.company_id,
                                        'customer_id': obj.id,
                                        'type': 'gongzhonghao_template_tishi',
                                        'title': '平台账户余额不足提示',
                                        'content': '关注公众号|发红包平台余额不足，请联系管理员进行充值',
                                        'remark': remark
                                    }
                                    print('红包发送报错数据 --------->', data_dict)
                                    tasks.monitor_send_gzh_template_msg.delay(data_dict)

                        ## 说明平台余额充足
                        if code != 199:

                            _data = {
                                'client_ip': client_ip,
                                'shanghukey': shangHuMiYao,  # 支付钱数
                                'total_fee': focus_get_money,  # 支付钱数
                                'appid': authorization_appid,  # 小程序ID
                                'mch_id': shangHuHao,  # 商户号
                                'openid': openid,
                                'send_name': gongzhonghao_name,  # 商户名称
                                'act_name': '关注领现金红包',  # 活动名称
                                'remark': '动动手指,轻松拿现金!',  # 备注信息
                                'wishing': '感谢您的关注我！',  # 祝福语
                            }

                            print('------[调发红包的接口 data 数据]------>>', json.dumps(_data))
                            response_ret = focusOnIssuedRedEnvelope(_data)
                            code = response_ret.code
                            if code == 200:
                                print('---- 调发红包成功 状态值:200 --->>')
                                objs.update(
                                    is_receive_redPacket=1,
                                    redPacket_money=focus_get_money
                                )
                                app_objs.update(
                                    reason='发放成功'
                                )

                                if is_used_daifa_redPacket == 1:  # 只有代发才记录资金流水
                                    ### 红包发送之后,记录红包流水
                                    record_data = {
                                        'admin_user_id': '',
                                        'user_id': user_id,
                                        'company_id': company_id,
                                        'customer_id': customer_id,
                                        'transaction_amount': focus_get_money,
                                        'source': 2,  # (2,'公众号'),
                                        'type': 3  # (3,'红包发放(关注公众号)'),
                                    }
                                    record_money_process(record_data)

                            else:
                                app_objs.update(
                                    reason=response_ret.msg
                                )

                                remark = 'openid: %s | company_id: %s | %s' % (openid, company_id, response_ret.msg)
                                objs = models.zgld_customer.objects.filter(session_key='notifier',
                                                                           company_id__in=[1, 2])

                                for obj in objs:
                                    data_dict = {
                                        'company_id': obj.company_id,
                                        'customer_id': obj.id,
                                        'type': 'gongzhonghao_template_tishi',
                                        'title': '商户发红包报错提示[关注领红包]',
                                        'content': '关注公众号|发送现金红包-发生错误,请及时排查',
                                        'remark': remark
                                    }
                                    print('红包发送报错数据 --------->', data_dict)
                                    tasks.monitor_send_gzh_template_msg.delay(data_dict)

                        ## 无论哪个平台发送失败都要发送消息提醒
                        if code == 199:
                            a_data = {}
                            a_data['customer_id'] = customer_id
                            a_data['user_id'] = user_id
                            a_data['type'] = 'gongzhonghao_template_tishi'
                            a_data['content'] = json.dumps({'msg': '您好,活动过于火爆,账户被刷爆,已联系管理员进行充值后再补发哦', 'info_type': 1})

                            print('-----企业用户 公众号_模板消息【关注红包 | 余额不足提示】 json.dumps(a_data)---->>', json.dumps(a_data))
                            tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】




                    elif is_subscribe == 1 and is_receive_redPacket == 1:

                        a_data = {}
                        # user_objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
                        #     customer_id=customer_id,user__company_id=company_id)
                        # user_id = ''
                        # if user_objs:
                        #     obj = user_objs[0]
                        #     user_id = obj.user_id

                        a_data['customer_id'] = customer_id
                        a_data['user_id'] = user_id
                        a_data['type'] = 'gongzhonghao_template_tishi'  # 简单的公众号模板消息提示。
                        a_data['content'] = json.dumps({'msg': '您好,您已经领取过红包喽,可转发【公众号】给您的好友领取现金红包!', 'info_type': 1})

                        print('-----企业用户 公众号_模板消息没有订阅公众号或者已经发过红包 json.dumps(a_data)---->>', json.dumps(a_data))
                        tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】

                        response.code = 302
                        response.msg = '没有订阅公众号或者应发过红包'
                        print('------没有订阅公众号或者已经发过红包 customer_id | openid ----->>', customer_id, "|", openid)

                else:
                    response.code = 301
                    response.msg = '客户不存在'
                    print('------客户不存在 customer_id ----->>', customer_id)
            else:
                response.code = 301
                response.msg = '此公众号没有开启[关注领红包]'
                print('------此公众号没有开启[关注领红包] company_id ----->>', company_id)
        else:
            response.code = 301
            response.msg = '无此公众号'
            print('------无此公众号 company_id ----->>', company_id)

    return JsonResponse(response.__dict__)


## 异步获取公众号用户信息[用三方平台token]
@csrf_exempt
def get_customer_gongzhonghao_userinfo(request):
    response = Response.ResponseObj()
    authorizer_appid = request.GET.get('authorizer_appid')
    company_id = request.GET.get('company_id')
    type = request.GET.get('type')
    openid = request.GET.get('openid')
    user_id = request.GET.get('user_id')
    client_id = request.GET.get('client_id')

    headimgurl = request.GET.get('headimgurl')

    if type == 'get_gzh_user_whole_info':  ## 获取全部的信息

        __data = {
            'openid': openid,
            'authorizer_appid': authorizer_appid,
            'company_id': company_id,
        }
        from zhugeleida.public.common import \
            get_customer_gongzhonghao_userinfo as get_customer_gongzhonghao_userinfo_cla

        user_obj_cla = get_customer_gongzhonghao_userinfo_cla(__data)
        ret = user_obj_cla.get_gzh_user_whole_info()
        response.code = 200
        response.msg = '获取成功'

        return JsonResponse(response.__dict__)

    customer_objs = models.zgld_customer.objects.filter(openid=openid)
    if customer_objs:
        customer_id = customer_objs[0].id
        formid = customer_objs[0].formid

        three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
        qywx_config_dict = ''
        if three_service_objs:
            three_service_obj = three_service_objs[0]
            qywx_config_dict = three_service_obj.config
            if qywx_config_dict:
                qywx_config_dict = json.loads(qywx_config_dict)

        app_id = qywx_config_dict.get('app_id')
        app_secret = qywx_config_dict.get('app_secret')

        objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=authorizer_appid)
        authorizer_refresh_token = ''
        if objs:
            authorizer_refresh_token = objs[0].authorizer_refresh_token

        key_name = 'authorizer_access_token_%s' % (authorizer_appid)

        _data = {
            'authorizer_appid': authorizer_appid,
            'authorizer_refresh_token': authorizer_refresh_token,
            'key_name': key_name,
            'app_id': app_id,  # 'wx6ba07e6ddcdc69b3',  # 查看诸葛雷达_公众号的 appid
            'app_secret': app_secret,  # '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
        }

        authorizer_access_token_ret = create_gongzhonghao_authorizer_access_token(_data)
        authorizer_access_token = authorizer_access_token_ret.data

        # access_token = "14_8p_bIh8kVgaZpnn_8IQ3y77mhJcSLoLuxnqtrE-mKYuOfXFPnNYhZAOWk8AZ-NeK6-AthHxolrSOJr1HvlV-gSlspaO0YFYbkPrsjJzKxalWQtlBxX4n-v11mqJElbT0gn3WVo9UO5zQpQMmTDGjAEDZJM"
        # openid = 'ob5mL1Q4faFlL2Hv2S43XYKbNO-k'

        get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        get_user_info_data = {
            'access_token': authorizer_access_token,
            'openid': openid,
            'lang': 'zh_CN',
        }

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        ret = s.get(get_user_info_url, params=get_user_info_data)
        # ret = requests.get(get_user_info_url, params=get_user_info_data)

        ret.encoding = 'utf-8'
        ret_json = ret.json()
        print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', json.dumps(ret_json))

        if 'errcode' not in ret_json:
            openid = ret_json['openid']  # 用户唯一标
            subscribe = ret_json['subscribe']  # 值为0时，代表此用户没有关注该公众号

            if formid != '已发':
                company_objs = models.zgld_company.objects.filter(id=company_id)
                user_objs = models.zgld_userprofile.objects.filter(id=user_id)

                # 插入第一条用户和客户的对话信息 终于等到你🌹，感谢您的关注，我是您的专属咨询代表,您现在可以直接给我发消息哦，期待您的回复
                msg = '终于等到你🌹，我是您的专属咨询代表【%s - %s】。   如需沟通，您可在此或扫码关注【公众号】, 并在公众号内进行回复(支持语音、图片、文字)' % (
                    company_objs[0].name, user_objs[0].username)
                # models.zgld_chatinfo.objects.create(send_type=1, userprofile_id=user_id, customer_id=customer_id,
                #                                     msg=msg)
                _content = {'info_type': 1}
                encodestr = base64.b64encode(msg.encode('utf-8'))
                msg = str(encodestr, 'utf-8')
                _content['msg'] = msg
                content = json.dumps(_content)

                models.zgld_chatinfo.objects.create(
                    send_type=1,
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    content=content
                )

                gzh_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                if gzh_objs:
                    gzh_obj = gzh_objs[0]
                    qrcode_url = gzh_obj.qrcode_url
                    _content = {
                        'url': qrcode_url,
                        'info_type': 4  # 图片
                    }
                    content = json.dumps(_content)
                    models.zgld_chatinfo.objects.create(
                        content=content,
                        userprofile_id=user_id,
                        customer_id=customer_id,
                        send_type=1,
                        is_last_msg=False
                    )

                print('---------- 插入 第一条用户和公众号客户的对话信息 successful ---->')
                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

                redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)
                redis_customer_query_info_key = 'message_customer_id_{cid}_info_num'.format(cid=customer_id)
                redis_user_query_info_key = 'message_user_id_{uid}_info_num'.format(
                    uid=user_id)  # 小程序发过去消息,雷达用户的key 消息数量发生变化
                redis_user_query_contact_key = 'message_user_id_{uid}_contact_list'.format(
                    uid=user_id)  # 小程序发过去消息,雷达用户的key 消息列表发生变化

                rc.set(redis_user_id_key, True)
                rc.set(redis_customer_id_key, True)
                rc.set(redis_customer_query_info_key, True)  # 通知公众号文章客户消息数量变化了

                rc.set(redis_user_query_info_key, True)  # 代表 雷达用户 消息数量发生了变化
                rc.set(redis_user_query_contact_key, True)  # 代表 雷达用户 消息列表的数量发生了变化
                customer_objs.update(
                    formid='已发'
                )

            customer_objs.update(
                is_subscribe=subscribe
            )
            print('---------- 公众号客户ID：%s 修改关注的状态成功| openid | subscribe ---->' % (customer_id), openid, "|", subscribe)

        # 保存头像到本地的数据库
        if headimgurl:
            html = s.get(headimgurl)

            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = "/gzh_cid_%s_%s.jpg" % (customer_id, now_time)
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'gongzhonghao', 'headimgurl') + filename
            with open(file_dir, 'wb') as file:
                file.write(html.content)
            print('----- 生成 到本地头像 file_dir ---->>', file_dir)

            customer_objs.update(
                headimgurl=file_dir
            )

    return JsonResponse(response.__dict__)


## 绑定客户和文章的关系
@csrf_exempt
def binding_article_customer_relate(request):
    response = Response.ResponseObj()
    article_id = request.GET.get('article_id')  # 公众号文章ID
    customer_id = request.GET.get('customer_id')  # 公众号客户ID
    user_id = request.GET.get('user_id')  # 由哪个雷达用户转发出来,Ta的用户的ID
    level = request.GET.get('level')  # 公众号层级
    parent_id = request.GET.get('pid')  # 所属的父级的客户ID。为空代表第一级。
    company_id = request.GET.get('company_id')  # 所属的父级的客户ID。为空代表第一级。

    q = Q()
    q.add(Q(**{'article_id': article_id}), Q.AND)
    q.add(Q(**{'customer_id': customer_id}), Q.AND)
    q.add(Q(**{'user_id': user_id}), Q.AND)
    q.add(Q(**{'level': level}), Q.AND)

    if parent_id:
        # 找到这个用户的父级并给它打上一个有[孩子的]的标签

        _level = int(level) - 1
        q1 = Q()
        q1.add(Q(**{'article_id': article_id}), Q.AND)
        q1.add(Q(**{'customer_id': parent_id}), Q.AND)
        q1.add(Q(**{'user_id': user_id}), Q.AND)
        q1.add(Q(**{'level': _level}), Q.AND)
        _objs = models.zgld_article_to_customer_belonger.objects.filter(q1)
        if _objs:
            print('----- 给父级的客户,打上一个有[孩子的]的标签【成功】 |  搜索条件 q1:----->>', q1)
            _objs.update(
                is_have_child=True
            )

        else:
            print('----- [没有找到]父级的客户, 打有[孩子的]的标签【失败】 |  搜索条件 q1:----->>', q1)

        q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)


    else:
        q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

    data = request.GET.copy()
    print('------ 绑定文章客户关系 json.dumps(data) ------>>', json.dumps(data))

    ###
    customer_objs = models.zgld_customer.objects.filter(id=customer_id)

    if customer_objs:

        company_objs = models.zgld_company.objects.filter(id=company_id)
        if company_objs:
            company_obj = company_objs[0]
            is_customer_unique = company_obj.is_customer_unique

            if is_customer_unique:  ## 唯一性
                article_to_customer_belonger_objs = models.zgld_article_to_customer_belonger.objects.filter(
                    article_id=article_id,
                    customer_id=customer_id
                )

                if article_to_customer_belonger_objs:

                    # article_to_customer_belonger_obj = models.zgld_article_to_customer_belonger.objects.filter(q)
                    # if article_to_customer_belonger_obj:
                    print('------ 文章和客户\雷达用户-关系存在 [zgld_article_to_customer_belonger] ------>>')
                    # response.code = 302
                    # response.msg = "文章和客户\雷达用户-关系存在"

                    article_to_customer_belonger_obj = article_to_customer_belonger_objs[0]
                    e_level = article_to_customer_belonger_obj.level
                    e_user_id = article_to_customer_belonger_obj.user_id

                    if e_user_id == user_id and int(level) != e_level:  # 当用户user_id 是同一个用户的时候,并且 层级不同的时候
                        print('------ [创建]文章和客户\雷达用户关系 ------>')
                        models.zgld_article_to_customer_belonger.objects.create(
                            article_id=article_id,
                            customer_id=customer_id,
                            user_id=user_id,
                            customer_parent_id=parent_id,
                            level=level,
                        )

                else:

                    user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.select_related(
                        'user').filter(customer_id=customer_id,
                                       user__company_id=company_id)
                    if user_customer_belonger_objs:  # 如果关系存在的话，说明已经看过文章并建立关系。
                        print('------- [通讯录]关系存在 [zgld_user_customer_belonger]:customer_id|user_id  ------>>',
                              customer_id, "|", user_id)

                        customer_belonger_obj = user_customer_belonger_objs[0]
                        e_user_id = customer_belonger_obj.user_id  # 找到那个建立关系的人。
                        print('------ [创建]文章和客户\雷达用户关系 ------>')

                        if e_user_id == user_id:  # 如果是同一个雷达用户才能够建立关系
                            models.zgld_article_to_customer_belonger.objects.create(
                                article_id=article_id,
                                customer_id=customer_id,
                                user_id=user_id,
                                customer_parent_id=parent_id,
                                level=level,
                            )

                    else:
                        print('------- 创建[通讯录]关系 [zgld_user_customer_belonger]:customer_id|user_id  ------>>',
                              customer_id, "|", user_id)
                        models.zgld_user_customer_belonger.objects.create(customer_id=customer_id, user_id=user_id,
                                                                          source=4)
                        models.zgld_article_to_customer_belonger.objects.create(
                            article_id=article_id,
                            customer_id=customer_id,
                            user_id=user_id,
                            customer_parent_id=parent_id,
                            level=level,
                        )

            else:  # 非唯一性的
                article_to_customer_belonger_obj = models.zgld_article_to_customer_belonger.objects.filter(q)

                if article_to_customer_belonger_obj:
                    print('------ 文章和客户\雷达用户-关系存在 [zgld_article_to_customer_belonger] ------>>', q)
                    # response.code = 302
                    # response.msg = "文章和客户\雷达用户-关系存在"

                else:
                    print('------ [创建]文章和客户\雷达用户关系 ------>')
                    models.zgld_article_to_customer_belonger.objects.create(
                        article_id=article_id,
                        customer_id=customer_id,
                        user_id=user_id,
                        customer_parent_id=parent_id,
                        level=level,
                    )

                user_customer_belonger_obj = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,
                                                                                               user_id=user_id)
                if user_customer_belonger_obj:
                    print('------- [通讯录]关系存在 [zgld_user_customer_belonger]:customer_id|user_id  ------>>', customer_id,
                          "|", user_id)
                    # response.code = 302
                    # response.msg = "关系存在"

                else:
                    print('------- 创建[通讯录]关系 [zgld_user_customer_belonger]:customer_id|user_id  ------>>', customer_id,
                          "|", user_id)
                    models.zgld_user_customer_belonger.objects.create(customer_id=customer_id, user_id=user_id,
                                                                      source=4)

    activity_objs = models.zgld_article_activity.objects.filter(article_id=article_id, status__in=[1, 2, 4]).order_by(
        '-create_date')
    # # 活动并且活动开通中
    if activity_objs:
        activity_obj = activity_objs[0]

        start_time = activity_obj.start_time
        end_time = activity_obj.end_time
        now_date_time = datetime.datetime.now()

        if now_date_time >= start_time and now_date_time <= end_time:  # 活动开启并活动在进行中

            activity_id = activity_objs[0].id
            print('------ 此文章有活动 article_id：----->', article_id)
            redPacket_objs = models.zgld_activity_redPacket.objects.filter(article_id=article_id,
                                                                           activity_id=activity_id,
                                                                           customer_id=customer_id)

            if redPacket_objs:
                print('----- 活动发红包表数据【存在】 article_id:%s | activity_id:%s | customer_id: %s ----->>' % (
                article_id, activity_id, customer_id))


            else:
                print(
                    '----- 活动发红包表数据【不存在并创建】 article_id:%s | activity_id:%s | customer_id: %s | company_id: %s ----->>' % (
                        article_id, activity_id, customer_id, company_id))

                models.zgld_activity_redPacket.objects.create(article_id=article_id,
                                                              activity_id=activity_id,
                                                              customer_id=customer_id,
                                                              customer_parent_id=parent_id,
                                                              company_id=company_id,
                                                              )
                response.code = 200
                response.msg = "绑定成功"

    return JsonResponse(response.__dict__)
