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


def action_record(data):
    response = Response.ResponseObj()
    user_id = data.get('uid')  # 用户 id
    customer_id = data.get('customer_id')  # 客户 id
    article_id = data.get('article_id')  # 客户 id
    action = data.get('action')
    if action:
        action = int(action)

    remark = data.get('remark')
    agent_id = data.get('agent_id')

    customer_name = models.zgld_customer.objects.get(id=customer_id).username
    customer_name = base64.b64decode(customer_name)
    customer_name = str(customer_name, 'utf-8')

    if action in [0]:  # 只发消息，不用记录日志。

        # data['content'] = '%s%s' % (customer_name, remark)
        # data['agentid'] = agent_id
        # tasks.user_send_action_log.delay(json.dumps(data))
        content = '%s%s' % (customer_name, remark)
        response.data = {
            'content': content,
            'agentid': agent_id
        }
        response.code = 200
        response.msg = '发送消息提示成功'

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
        response.data = {
            'content': content,
            'agentid': agent_id
        }
        response.code = 200
        response.msg = '发送消息提示成功'

    else:
        # 创建访问日志
        models.zgld_accesslog.objects.create(
            user_id=user_id,
            customer_id=customer_id,
            remark=remark,
            action=action
        )

        # 查询客户与用户是否已经建立关系
        follow_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(
            user_id=user_id,
            customer_id=customer_id
        )
        now_time = datetime.datetime.now()
        if follow_objs:  # 已经有关系了
            follow_objs.update(
                last_activity_time=now_time
            )
            content = '%s%s' % (customer_name, remark)
            print('------ 客户姓名 + 访问日志信息------->>', customer_name, '+', 'action:', action, content)

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

    userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
    company_id = userprofile_obj.company_id
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid

    component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
    key_name = '%s_authorizer_access_token' % (authorizer_appid)

    authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

    if not authorizer_access_token:
        data = {
            'key_name': key_name,
            'authorizer_refresh_token': authorizer_refresh_token,
            'authorizer_appid': authorizer_appid,

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
        print('----celery生成用户-客户对应的小程序二维码成功-->>', 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

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


#定时器生成海报或二维码
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
                    #生成小程序和企业用户对应的小程序二维码
                    url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
                    get_data = {
                        'data': json.dumps(data_dict)
                    }
                    print('---【定时器生成】 小程序二维码: data_dict-->',data_dict)

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    s.get(url, params=get_data)

                    qr_code = obj.qr_code

                if  not poster_url and qr_code:
                    print('---【定时器生成】 小程序海报: data_dict-->', data_dict)
                    tasks.create_user_or_customer_small_program_poster.delay(json.dumps(data_dict))

        else:
            print('------ 没有符合条件的【定时器刷新】生成二维码或海报 ------->>>')

    return  HttpResponse('执行_定时器生成海报')


# 生成小程序的海报
@csrf_exempt
def create_user_or_customer_poster(request):
    response = ResponseObj()
    # customer_id = request.GET.get('customer_id')
    # user_id = request.GET.get('user_id')

    print(' create_user_or_customer_poster ---- 【生成海报celery】 request.GET | data 数据 -->', request.GET, '|', request.GET.get('data'))

    data = json.loads(request.GET.get('data'))
    user_id = data.get('user_id')
    customer_id = data.get('customer_id', '')
    print(' create_user_or_customer_poster --- [生成海报]customer_id | user_id --------->>', customer_id, user_id)

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
        # driver.implicitly_wait(10)

        url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/mingpian/poster_html?user_id=%s&uid=%s' % (customer_id, user_id)

        print('--- create_user_or_customer_poster ---- url -->', url)

        try:
            driver.get(url)
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

            poster_url = 'statics/zhugeleida/imgs/xiaochengxu/user_poster%s' % user_poster_file
            if os.path.exists(BASE_DIR + user_poster_file_temp): os.remove(BASE_DIR + user_poster_file_temp)
            print('"create_user_or_customer_poster -->", --------- 生成海报URL -------->', poster_url)
            objs.update(
                poster_url=poster_url
            )

            ret_data = {
                'user_id': user_id,
                'poster_url': poster_url,
            }
            print('"create_user_or_customer_poster -->", -----save_poster ret_data --->>', ret_data)
            response.data = ret_data
            response.msg = "请求成功"
            response.code = 200

        except Exception as e:
            response.msg = "PhantomJS截图失败"
            response.code = 400
            driver.quit()
    return JsonResponse(response.__dict__)


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
    while flag:

        post_template_data = {}
        # get_token_data['appid'] = authorization_appid
        # get_token_data['secret'] = authorization_secret
        # get_token_data['grant_type'] = 'client_credential'

        component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
        key_name = '%s_authorizer_access_token' % (authorizer_appid)
        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            data = {
                'key_name': key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,

            }
            authorizer_access_token = create_authorizer_access_token(data)

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
            template_ret = s.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))

            # template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()

            print('--------企业用户 send to 小程序 Template 接口返回数据--------->', template_ret)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"
                flag = False

            elif template_ret.get('errcode') == 40001:
                rc.delete(key_name)

            else:
                print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"
            i = i + 1
            if i  == 10:  # 限制最多重试十次。
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

        activity_redPacket_objs =  models.zgld_activity_redPacket.objects.filter(customer_id=customer_id,customer_parent_id=parent_id,activity_id=activity_id)
        if not activity_redPacket_objs:
            print('------ 【转发后查看 * 不发消息公众号模板消息提示】customer_id | parent_id | activity_id-------->>',customer_id,"|",parent_id,"|",activity_id)

            return  HttpResponse('Dont send message')


    userprofile_obj = models.zgld_userprofile.objects.select_related('company').get(id=user_id)
    company_id = userprofile_obj.company_id
    company_name = userprofile_obj.company.name

    obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    objs = models.zgld_user_customer_belonger.objects.select_related('user','customer').filter(
        customer_id=customer_id,
        user_id=user_id
    )

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

    if not authorizer_access_token:
        authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)
        authorizer_access_token = rc.get(authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            data = {
                'key_name': authorizer_access_token_key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,
                'app_id': 'wx6ba07e6ddcdc69b3',
                'app_secret': '0bbed534062ceca2ec25133abe1eecba'
            }

            authorizer_access_token_result = create_gongzhonghao_authorizer_access_token(data)
            if authorizer_access_token_result.code == 200:
                authorizer_access_token = authorizer_access_token_result.data

    get_template_data = {
        'access_token': authorizer_access_token  # 授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
    }

    if customer_obj and objs:
        openid = customer_obj[0].openid

        # 发送公众号模板消息聊天消息 和 公众号客户查看文章后的红包活动提示

        if _type == 'gongzhonghao_template_tishi' or _type == 'forward_look_article_tishi':

            # path = 'pages/mingpian/msg?source=template_msg&uid=%s&pid=' % (user_id)
            # xiaochengxu_app_obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
            # appid = xiaochengxu_app_obj.authorization_appid

            # 留言回复通知
            '''
            您好，您咨询商家的问题已回复
            咨询名称：孕儿美摄影工作室-张炬
            消息回复：您有未读消息哦
            点击进入咨询页面
            '''
            data = ''
            if _type == 'gongzhonghao_template_tishi':
                _content = json.loads(content)
                info_type = _content.get('info_type')
                msg = ''
                if info_type:
                    info_type = int(info_type)
                    if info_type == 1:
                        msg = _content.get('msg')

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


            elif _type == 'forward_look_article_tishi':
                activity_obj = models.zgld_article_activity.objects.get(id=activity_id)

                activity_name = activity_obj.activity_name
                reach_forward_num = activity_obj.reach_forward_num
                activity_single_money = activity_obj.activity_single_money
                start_time = activity_obj.start_time.strftime('%Y-%m-%d %H:%M')
                end_time = activity_obj.end_time.strftime('%Y-%m-%d %H:%M')
                if not position:
                    position = ''
                remark = '活动规则: 关注公众号并分享文章给朋友/朋友圈,每满足%s人查看,立返现金红包%s元。 分享不停,红包不停,上不封顶。活动日期: %s 至 %s' % (
                reach_forward_num, activity_single_money,start_time,end_time)
                data = {
                    'first': {
                        'value': ('        您好,我是%s的%s%s,很高兴为您服务, 欢迎您参加【分享文章 赚现金活动】\n' % (
                        company_name, position, user_name))  # 回复者
                    },
                    'keyword1': {
                        'value': '您的好友【%s】查看了您转发的活动文章《%s》\n' % (customer_name, activity_name),
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

            print('=========== 发送出去的【模板消息】请求数据 =======>>', json.dumps(post_template_data))

            # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考
            template_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            template_ret = s.post(template_msg_url, params=get_template_data, data=json.dumps(post_template_data))
            # template_ret = requests.post(template_msg_url, params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()


            print('--------企业用户 send to 小程序 Template 接口返回数据--------->', template_ret)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"


            elif template_ret.get('errcode') == 40001:
                rc.delete(key_name)

            else:
                print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"


        # 企业微信-发送公众号的客服聊天消息
        elif _type == 'gongzhonghao_send_kefu_msg':

            kefu_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send'
            kefu_msg_get_data = {
                'access_token': authorizer_access_token,
            }
            _content = json.loads(content)
            info_type = _content.get('info_type')
            msg = ''
            if info_type:
                info_type = int(info_type)
                if info_type == 1:
                    msg = _content.get('msg')

            _content  = '%s:\n        %s' % (user_name,msg)
            kefu_msg_post_data ={
                "touser": openid,
                "msgtype": "text",
                "text":
                {
                     "content": _content
                }
            }


            objs.update(
                last_follow_time=datetime.datetime.now()
            )


            kefu_msg_post_data =  json.dumps(kefu_msg_post_data, ensure_ascii=False)

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            kefu_ret = s.post(kefu_msg_url, params=kefu_msg_get_data,data=kefu_msg_post_data.encode('utf-8'))
            # kefu_ret = requests.post(kefu_msg_url, params=kefu_msg_get_data,data=kefu_msg_post_data.encode('utf-8'))

            kefu_ret = kefu_ret.json()

            print('--------企业用户 send to 小程序 kefu_客服接口 - 返回数据--------->', kefu_ret)

            if kefu_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 kefu_客服消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送客服消息成功"


            elif kefu_ret.get('errcode') == 40001:
                rc.delete(key_name)

            else:
                print('-----企业用户 发送【小程序_客服消息】失败 json.dumps(kefu_msg_post_data)---->>',kefu_msg_post_data)
                a_data = {}
                a_data['customer_id'] = customer_id
                a_data['user_id'] = user_id
                a_data['type'] = 'gongzhonghao_template_tishi'
                a_data['content'] = content
                tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】
                print('-----企业用户 再次发送【小程序_模板消息】 json.dumps(a_data)---->>',json.dumps(a_data))
                response.code = 301
                response.msg = "企业用户发送客服消息成功失败"


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
                customer_parent_id=parent_id, activity_id=activity_id,create_date__lte=end_time,create_date__gte=start_time).values_list('customer_id').distinct().count()

            forward_stay_time_dict = models.zgld_article_to_customer_belonger.objects.filter(
                customer_parent_id=parent_id, article_id=article_id,create_date__lte=end_time,create_date__gte=start_time).aggregate(forward_stay_time=Sum('stay_time'))

            forward_stay_time = forward_stay_time_dict.get('forward_stay_time')
            if not forward_stay_time:
                forward_stay_time = 0

            activity_redPacket_objs.update(
                forward_read_count=forward_read_num,
                forward_stay_time=forward_stay_time
            )


            reach_forward_num = activity_obj.reach_forward_num  # 达到多少次发红包(转发阅读后次数))
            already_send_redPacket_num = activity_redPacket_obj.already_send_redPacket_num  # 已发放次数
            # already_send_redPacket_money = activity_redPacket_obj.already_send_redPacket_money        #已发红包金额

            if reach_forward_num != 0:  # 不能为0
                forward_read_num = int(forward_read_num)
                if forward_read_num >= reach_forward_num:  # 转发大于 阈值,达到可以条件

                    divmod_ret = divmod(forward_read_num, reach_forward_num)

                    shoudle_send_num = divmod_ret[0]
                    yushu = divmod_ret[1]

                    if shoudle_send_num > already_send_redPacket_num:


                        print('---- 【满足发红包条件】forward_read_num[转发被查看数] | reach_forward_num[需满足的阈值] ----->>',
                              forward_read_num, "|", reach_forward_num)
                        print('---- 【满足发红包条件】shoudle_send_num[实发数] | already_send_redPacket_num[已发数] ----->>',
                              shoudle_send_num, "|", already_send_redPacket_num)
                        app_objs = models.zgld_gongzhonghao_app.objects.select_related('company').filter(
                            company_id=company_id)
                        activity_single_money = activity_obj.activity_single_money
                        activity_name = activity_obj.activity_name

                        customer_obj = models.zgld_customer.objects.get(id=parent_id)
                        openid = customer_obj.openid

                        authorization_appid = ''
                        gongzhonghao_name = ''
                        if app_objs:
                            # company_name = '%s' % (app_objs[0].company.name)
                            gongzhonghao_name = '%s' % (app_objs[0].name)
                            authorization_appid = app_objs[0].authorization_appid

                        shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.filter(
                            xiaochengxucompany_id=company_id)

                        shangHuHao = ''
                        shangHuMiYao = ''
                        if shangcheng_objs:
                            shangcheng_obj = shangcheng_objs[0]
                            shangHuHao = shangcheng_obj.shangHuHao
                            # send_name = shangcheng_obj.shangChengName
                            shangHuMiYao = shangcheng_obj.shangHuMiYao

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
                        print('------[调用转发后满足条件,发红包的接口 data 数据]------>>', json.dumps(_data))

                        response_ret = focusOnIssuedRedEnvelope(_data)
                        if response_ret.code == 200:
                            now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('---- 调用发红包成功[转发得现金] 状态值:200  parent_id | openid --->>',parent_id,'|',openid)

                            _send_log_dict = {
                                'type': '自动发送',
                                'activity_single_money': activity_single_money,
                                'send_time': now_time,
                            }
                            activity_redPacket_obj = activity_redPacket_objs[0]
                            send_log_list =activity_redPacket_obj.send_log
                            _send_log_list = json.loads(send_log_list)
                            _send_log_list.append(_send_log_dict)
                            send_log_list = json.dumps(_send_log_list)


                            bufa_send_activity_redPacket = shoudle_send_num - already_send_redPacket_num

                            status = 1
                            if bufa_send_activity_redPacket > 1:
                                status = 4 # 补发状态


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

                        else:  # 余额不足后者其他原因,记录下日志
                            activity_redPacket_objs.update(
                                should_send_redPacket_num=shoudle_send_num,  # 应该发放的次数 [应发]
                                status=3  # (2,'未发'),  改为未发状态
                            )
                            activity_objs.update(
                                reason=response_ret.msg
                            )

                            if response_ret.code == 199:

                                a_data = {}
                                a_data['customer_id'] = parent_id
                                a_data['user_id'] = user_id
                                a_data['type'] = 'gongzhonghao_template_tishi'
                                a_data['content'] = json.dumps({'msg': '您好,活动过于火爆,账户被刷爆,已联系管理员进行充值', 'info_type': 1})

                                print('-----企业用户 公众号_模板消息【余额不足提示】 json.dumps(a_data)---->>', json.dumps(a_data))
                                tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】

                            response.code = response_ret.code
                            response.msg = response_ret.msg


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

        activity_redPacket_objs = models.zgld_activity_redPacket.objects.select_related('company','activity','article','customer').filter(status__in=[3,4])

        if activity_redPacket_objs:


            for activity_redPacket_obj in  activity_redPacket_objs:

                should_send_redPacket_num =activity_redPacket_obj.should_send_redPacket_num
                already_send_redPacket_num =activity_redPacket_obj.already_send_redPacket_num
                activity_id = activity_redPacket_obj.activity_id
                activity_objs = models.zgld_article_activity.objects.filter(id=activity_id).order_by('-create_date')

                if should_send_redPacket_num > already_send_redPacket_num and activity_objs:

                    company_id = activity_redPacket_objs[0].company_id
                    customer_id = activity_redPacket_obj.customer_id
                    article_id = activity_redPacket_obj.article_id

                    activity_single_money = activity_redPacket_obj.activity.activity_single_money
                    activity_name = activity_redPacket_obj.activity.activity_name


                    bufa_redPacket_num = should_send_redPacket_num -  already_send_redPacket_num
                    app_objs = models.zgld_gongzhonghao_app.objects.select_related('company').filter(
                        company_id=company_id)

                    customer_obj = models.zgld_customer.objects.get(id=customer_id)
                    openid = customer_obj.openid

                    authorization_appid = ''
                    gongzhonghao_name = ''
                    if app_objs:
                        # company_name = '%s' % (app_objs[0].company.name)
                        gongzhonghao_name = '%s' % (app_objs[0].name)
                        authorization_appid = app_objs[0].authorization_appid

                    shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.filter(
                        xiaochengxucompany_id=company_id)

                    shangHuHao = ''
                    shangHuMiYao = ''
                    if shangcheng_objs:
                        shangcheng_obj = shangcheng_objs[0]
                        shangHuHao = shangcheng_obj.shangHuHao
                        # send_name = shangcheng_obj.shangChengName
                        shangHuMiYao = shangcheng_obj.shangHuMiYao

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
                            print('---- 调用发红包成功[转发得现金] 状态值:200  customer_id | openid --->>',customer_id,'|',openid)

                            _send_log_dict = {
                                'type': '自动补发',
                                'activity_single_money': activity_single_money,
                                'send_time': now_time,
                            }
                            activity_redPacket_obj = activity_redPacket_objs[0]
                            send_log_list =activity_redPacket_obj.send_log
                            _send_log_list = json.loads(send_log_list)
                            _send_log_list.append(_send_log_dict)
                            send_log_list = json.dumps(_send_log_list)


                            activity_redPacket_objs.update(
                                already_send_redPacket_num=F('already_send_redPacket_num') + 1,
                                already_send_redPacket_money=F('already_send_redPacket_money') + activity_single_money,
                                # 已发红包金额 [累加发送金额]
                                # should_send_redPacket_num=shoudle_send_num,  # 应该发放的次数 [应发]
                                status=1,  # (1,'已发'),
                                send_log=send_log_list  # (1,'已发'),
                            )
                            activity_objs.update(
                                reason='发放成功',
                                already_send_redPacket_num=F('already_send_redPacket_num') + 1,
                                already_send_redPacket_money=F('already_send_redPacket_money') + activity_single_money,
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
                            activity_redPacket_objs.update(
                                status=3,
                            )
                            activity_objs.update(
                                reason=response_ret.msg
                            )
                            break





                else:
                    response.code = 301
                    response.msg = '实发数<=已发数'
                    print('------ 【实发数<=已发数】 should_send_redPacket_num | already_send_redPacket_num ----->>', should_send_redPacket_num,
                          '|', already_send_redPacket_num)

        else:
            response.code = 301
            response.msg = '[无补发用户]'
            print('------【无补发用户】红包记录表里没有要补发的客户 ----->>')

    return JsonResponse(response.__dict__)




# 关注发红包和转发文章满足就发红包
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

                        focus_get_money = gongzhonghao_app_obj.focus_get_money  # 关注领取的红包金额
                        focus_total_money = gongzhonghao_app_obj.focus_total_money

                        app_objs = models.zgld_gongzhonghao_app.objects.select_related('company').filter(company_id=company_id)

                        authorization_appid = ''
                        gongzhonghao_name = ''
                        if app_objs:
                            authorization_appid = app_objs[0].authorization_appid
                            # company_name = '【%s】' % (app_objs[0].company.name)
                            gongzhonghao_name = app_objs[0].name

                        shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.filter(
                            xiaochengxucompany_id=company_id)
                        send_name = ''
                        shangHuHao = ''
                        shangHuMiYao = ''
                        if shangcheng_objs:
                            shangcheng_obj = shangcheng_objs[0]
                            shangHuHao = shangcheng_obj.shangHuHao
                            # send_name = shangcheng_obj.shangChengName
                            shangHuMiYao = shangcheng_obj.shangHuMiYao

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
                        if response_ret.code == 200:
                            print('---- 调发红包成功 状态值:200 --->>')
                            objs.update(
                                is_receive_redPacket=1
                            )
                            app_objs.update(
                                reason='发放成功'
                            )
                        else:
                            app_objs.update(
                                reason=response_ret.msg
                            )
                    else:
                        response.code = 302
                        response.msg = '没有订阅公众号或者应发过红包'
                        print('------没有订阅公众号或者应发过红包 customer_id | openid ----->>', customer_id, "|", openid)
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
    openid = request.GET.get('openid')

    objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=authorizer_appid)
    authorizer_refresh_token = ''
    if objs:
        authorizer_refresh_token = objs[0].authorizer_refresh_token

    key_name = 'authorizer_access_token_%s' % (authorizer_appid)
    _data = {
        'authorizer_appid': authorizer_appid,
        'authorizer_refresh_token': authorizer_refresh_token,
        'key_name': key_name,
        'app_id': 'wx6ba07e6ddcdc69b3',  # 查看诸葛雷达_公众号的 appid
        'app_secret': '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
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

        objs = models.zgld_customer.objects.filter(openid=openid)
        if objs:
            customer_id = objs[0].id
            objs.update(
                is_subscribe=subscribe
            )
            print('---------- 公众号客户ID：%s 修改关注的状态成功| openid | subscribe ---->' % (customer_id), openid, "|", subscribe)

    return JsonResponse(response.__dict__)


## 绑定客户和文章的关系
@csrf_exempt
def binding_article_customer_relate(request):
    response = Response.ResponseObj()
    article_id = request.GET.get('article_id')  # 公众号文章ID
    customer_id = request.GET.get('customer_id')  # 公众号客户ID
    user_id = request.GET.get('user_id')  # 由哪个雷达用户转发出来,Ta的用户的ID
    level = request.GET.get('level')     # 公众号层级
    parent_id = request.GET.get('pid')   # 所属的父级的客户ID。为空代表第一级。
    company_id = request.GET.get('company_id')  # 所属的父级的客户ID。为空代表第一级。

    q = Q()
    q.add(Q(**{'article_id': article_id}), Q.AND)
    q.add(Q(**{'customer_id': customer_id}), Q.AND)
    q.add(Q(**{'user_id': user_id}), Q.AND)
    q.add(Q(**{'level': level}), Q.AND)

    if parent_id:
        q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
    else:
        q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

    data = request.GET.copy()
    print('------ 绑定文章客户关系 json.dumps(data) ------>>', json.dumps(data))

    article_to_customer_belonger_obj = models.zgld_article_to_customer_belonger.objects.filter(q)

    if article_to_customer_belonger_obj:
        print('------ 文章和客户\雷达用户-关系存在 [zgld_article_to_customer_belonger] ------>>')
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
        print('------- [通讯录]关系存在 [zgld_user_customer_belonger]:customer_id|user_id  ------>>', customer_id, "|",
              user_id)
        # response.code = 302
        # response.msg = "关系存在"

    else:
        print('------- 创建[通讯录]关系 [zgld_user_customer_belonger]:customer_id|user_id  ------>>', customer_id, "|",
              user_id)
        models.zgld_user_customer_belonger.objects.create(customer_id=customer_id, user_id=user_id, source=4)

    activity_objs = models.zgld_article_activity.objects.filter(article_id=article_id, status__in=[1,2,4])
    # 活动并且
    if activity_objs:
        activity_id = activity_objs[0].id
        print('------ 此文章有活动 article_id：----->', article_id)
        redPacket_objs = models.zgld_activity_redPacket.objects.filter(article_id=article_id, activity_id=activity_id,
                                                                       customer_id=customer_id)

        if redPacket_objs:
            print('----- 活动发红包表数据【存在】 article_id:%s | activity_id:%s | customer_id: %s ----->>' % (
            article_id, activity_id, customer_id))
            # response.code = 302
            # response.msg = "关系存在"

        else:
            print('----- 活动发红包表数据【不存在并创建】 article_id:%s | activity_id:%s | customer_id: %s | company_id: %s ----->>' % (
                article_id, activity_id, customer_id, company_id))

            models.zgld_activity_redPacket.objects.create(article_id=article_id,
                                                          activity_id=activity_id,
                                                          customer_id=customer_id,
                                                          customer_parent_id=parent_id,
                                                          company_id=company_id,
                                                          )
            response.code = 200
            response.msg = "绑定成功"
    #
    return JsonResponse(response.__dict__)
