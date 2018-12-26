
from zhugeleida import models
from publicFunc import Response

import json
from zhugeapi_celery_project import tasks
import base64
import qrcode
from django.conf import settings
import os,datetime
import redis
import requests
from django.http import JsonResponse, HttpResponse
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import create_authorizer_access_token as create_gongzhonghao_authorizer_access_token

from publicFunc import account

def action_record(data,remark):
    #response = Response.ResponseObj()
    # user_id = data.get('uid')  # 用户 id
    # customer_id = data.get('user_id')  # 客户 id
    # article_id = data.get('article_id')  # 客户 id
    # action = data.get('action')
    data['remark'] = remark
    tasks.user_send_action_log.delay(data)


def create_qrcode(data):
    url = data.get('url')
    article_id = data.get('article_id')
    type = data.get('type')


    response = Response.ResponseObj()
    qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.show()

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')

    qr_url = ''
    if type == 'web_scan_authorize_qrcode':

        BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'webLogin')
        qr_code_name = '/uid_%s_qrCode.jpg' % (now_time)
        path_qr_code_name = BASE_DIR + qr_code_name
        qr_url = 'statics/zhugeleida/imgs/qiyeweixin/webLogin%s' % (qr_code_name)
        img.save(path_qr_code_name)
        qr_url_dict = {'pre_qrcode_url': qr_url}
        return qr_url_dict

    else:
        article_objs = models.zgld_article.objects.filter(id=article_id)
        qr_url = ''
        if article_objs:
            qr_url = article_objs[0].qrcode_url

        if not qr_url:

            BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'gongzhonghao', 'article')
            qr_code_name = '/article_%s_%s_qrCode.jpg' % (article_id, now_time)
            path_qr_code_name = BASE_DIR + qr_code_name
            qr_url = 'statics/zhugeleida/imgs/gongzhonghao/article%s' % (qr_code_name)
            img.save(path_qr_code_name)
            article_objs.update(
                qrcode_url=qr_url
            )

    response.data = {'pre_qrcode_url': qr_url}
    response.code = 200
    response.msg = '生成文章体验二维码成功'
    print('---------生成文章体验二维码成功--------->>', qr_url)

    return response

def create_scan_code_userinfo_qrcode(data):
    url = data.get('url')
    admin_uid = data.get('admin_uid')

    response = Response.ResponseObj()
    qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.show()

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'admin', 'qr_code')

    qr_code_name = '/admin_uid_%s_%s_qrCode.jpg' % (admin_uid, now_time)
    path_qr_code_name = BASE_DIR + qr_code_name
    qr_url = 'statics/zhugeleida/imgs/admin/qr_code%s' % (qr_code_name)

    img.save(path_qr_code_name)
    response.data = {'qrcode_url': qr_url}
    response.code = 200
    response.msg = '生成文章体验二维码成功'
    print('---------生成文章体验二维码成功--------->>', qr_url)


    return response

def conversion_base64_customer_username_base64(customer_name,customer_id):
    try:
        username = base64.b64decode(customer_name)
        customer_name = str(username, 'utf-8')
        print('----- 解密b64decode username----->', username)
    except Exception as e:
        print('----- b64decode解密失败的 customer_id 是 | e ----->',customer_id, "|", e)
        customer_name = '客户ID%s' % (customer_id)
    return  customer_name


## 把秒数换换成 时|分|秒
def conversion_seconds_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time = 0
    print('---h m s-->>', h, m, s)

    if not h and not m and s:
        print("%s秒" % (s))
        time = "%s秒" % (s)
    elif not h and m and s:
        print("%s分%s秒" % (m, s))
        time = "%s分%s秒" % (m, s)

    elif not h and m and not s:
        print("%s分钟" % (m))
        time = "%s分钟" % (m)

    elif h and m and s:
        print("%s小时%s分%s秒" % (h, m, s))
        time = "%s小时%s分%s秒" % (h, m, s)
    elif h and m and not s:
        print("%s小时%s分钟" % (h, m))
        time = "%s小时%s分钟" % (h, m)

    elif h and not m and not s:
        print("%s小时" % (h))
        time = "%s小时" % (h)

    return time


## 生成请 第三方平台自己的 suite_access_token
def  create_suite_access_token(data):
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    response = Response.ResponseObj()
    SuiteId = data.get('SuiteId')

    post_component_data = ''
    suite_secret = ''
    SuiteTicket = ''
    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        qywx_config_dict = three_service_obj.config
        if qywx_config_dict:
            qywx_config_dict = json.loads(qywx_config_dict)

        if SuiteId ==  qywx_config_dict['leida'].get('sCorpID'): #'wx5d26a7a856b22bec':
            key_name = 'SuiteTicket_%s' % (SuiteId)
            SuiteTicket = rc.get(key_name)
            suite_secret = 'vHBmQNLTkm2FF61pj7gqoQVNFP5fr5J0avEzYRdzr2k'

        elif SuiteId == qywx_config_dict['boss'].get('sCorpID'): # 'wx36c67dd53366b6f0':

            key_name = 'SuiteTicket_%s' % (SuiteId)
            SuiteTicket = rc.get(key_name)
            suite_secret = 'dr7UT0zmMW1Dh7XABacmGieqLefoAhyrabAy74yI8rM'

        elif SuiteId == qywx_config_dict['address_book'].get('sCorpID'): #'wx1cbe3089128fda03':
            key_name = 'SuiteTicket_%s' % (SuiteId)
            SuiteTicket = rc.get(key_name)
            suite_secret = 'xA9Z8lcsTCc7eW8vaKQD0hTmamfjKn1Dnph3TcfdY-8'


        post_component_data = {
            "suite_id": SuiteId,
            "suite_secret": suite_secret,
            "suite_ticket": SuiteTicket
        }

        suite_access_token_key_name = 'suite_access_token_%s' % (SuiteId)
        token_ret = rc.get(suite_access_token_key_name)
        print('--- Redis里存储的 suite_access_token---->>', token_ret)

        if not token_ret:
            post_component_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_suite_token'

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            component_token_ret = s.post(post_component_url, data=json.dumps(post_component_data))
            # component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))

            print('--------- [企业微信]获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
            component_token_ret = component_token_ret.json()
            access_token = component_token_ret.get('suite_access_token')

            if access_token:
                token_ret = access_token
                rc.set(suite_access_token_key_name, access_token, 7000)
            else:
                response.code = 400
                response.msg = "-------- [企业微信] 获取第三方平台 component_token_ret 返回错误 ------->"
                return JsonResponse(response.__dict__)

        response.data = {
            'suite_access_token': token_ret
        }
        response.code = 200

    else:

        response.code = 301
        response.msg = '企业微信第三方-无配置信息'
        print('------ 【企业微信第三方-无配置信息】 create_suite_access_token ------>>')

    return response

## 企业微信 生成 预授权码 + suite_access_token
def create_pre_auth_code(data):
    # app_type =  data.get('app_type')
    SuiteId = data.get('SuiteId')

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    response = Response.ResponseObj()

    pre_auth_code_key_name = 'pre_auth_code_qiyeweixin_%s' % (SuiteId)
    exist_pre_auth_code = rc.get(pre_auth_code_key_name)


    _data = {
        'SuiteId' : SuiteId
    }
    suite_access_token_ret = create_suite_access_token(_data)
    suite_access_token = suite_access_token_ret.data.get('suite_access_token')

    if not exist_pre_auth_code:
        get_pre_auth_data = {
            'suite_access_token': suite_access_token
        }
        pre_auth_code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_pre_auth_code'

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        pre_auth_code_ret = s.get(pre_auth_code_url, params=get_pre_auth_data)
        # pre_auth_code_ret = requests.get(pre_auth_code_url, params=get_pre_auth_data)

        pre_auth_code_ret = pre_auth_code_ret.json()
        pre_auth_code = pre_auth_code_ret.get('pre_auth_code')
        print('------ [企业微信] 获取第三方平台 pre_auth_code 预授权码 ----->', pre_auth_code_ret)
        if pre_auth_code:
            rc.set(pre_auth_code_key_name, pre_auth_code, 1600)
        else:
            response.code = 400
            response.msg = "--------- [企业微信] 获取第三方平台 pre_auth_code预授权码 返回错误 ------->"
            return JsonResponse(response.__dict__)
    else:
        pre_auth_code = exist_pre_auth_code

    response.data = {
        'pre_auth_code': pre_auth_code,
        'suite_access_token': suite_access_token
    }
    response.code = 200

    return response


def create_qiyeweixin_access_token(data):
    response = Response.ResponseObj()

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    SuiteId = data.get('SuiteId')                # 三方应用IP 。
    auth_corpid = data.get('corp_id')            # 授权方企业corpid
    permanent_code = data.get('permanent_code')  # 企业微信永久授权码

    _data = {
        'SuiteId': SuiteId
    }

    suite_access_token_ret = create_suite_access_token(_data)

    suite_access_token = suite_access_token_ret.data.get('suite_access_token')

    get_code_data = {
        'suite_access_token': suite_access_token
    }
    post_code_data = {
        'auth_corpid': auth_corpid,
        'permanent_code' : permanent_code
    }

    key_name = 'access_token_qiyeweixin_%s_%s' % (auth_corpid,SuiteId)
    access_token = rc.get(key_name)

    if not access_token:

        get_corp_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token'

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        get_corp_token_ret = s.post(get_corp_token_url, params=get_code_data,data=json.dumps(post_code_data))
        # get_corp_token_ret = requests.post(get_corp_token_url, params=get_code_data,data=json.dumps(post_code_data))

        get_corp_token_ret = get_corp_token_ret.json()
        print('===========【企业微信】获取企业access_token 返回:==========>', json.dumps(get_corp_token_ret))

        access_token = get_corp_token_ret.get('access_token')
        if access_token:
            rc.set(key_name, access_token, 7000)
            print('===========【企业微信】获取企业access_token【成功】 得到 access_token | 使用 suite_access_token ==========>',access_token,"|" ,suite_access_token,)

        else:
            print('===========【企业微信】获取企业access_token【失败】')

    response.data = {
        'access_token': access_token,
        'suite_access_token': suite_access_token
    }
    response.code = 200

    return response


## 兼容创建企业微信的token
def  jianrong_create_qiyeweixin_access_token(company_id):

    app_objs = models.zgld_app.objects.filter(company_id=company_id, app_type=3)
    permanent_code = ''
    if app_objs:
        permanent_code = app_objs[0].permanent_code
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    company_obj = models.zgld_company.objects.get(id=company_id)
    corp_id = company_obj.corp_id
    tongxunlu_secret = company_obj.tongxunlu_secret


    if not  permanent_code:
        get_token_data = {
            'corpid': corp_id,
            'corpsecret': tongxunlu_secret
        }

        key_name = "company_%s_tongxunlu_token" % (company_id)
        access_token = rc.get(key_name)

        print('---token_ret---->>', access_token)

        if not access_token:
            tongxunlu_token_url =  "https://qyapi.weixin.qq.com/cgi-bin/gettoken"

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            ret = s.get(tongxunlu_token_url, params=get_token_data)

            # ret = requests.get(tongxunlu_token_url, params=get_token_data)

            ret_json = ret.json()
            print('--------【企业微信】使用秘钥生成 access_token 返回-->>', ret_json)
            access_token = ret_json['access_token']
            rc.set(key_name, access_token, 7000)

    else:
        SuiteId = 'wx1cbe3089128fda03'  # 通讯录
        _data = {
            'SuiteId': SuiteId,  # 通讯录 。
            'corp_id': corp_id,  # 授权方企业corpid
            'permanent_code': permanent_code
        }
        access_token_ret = create_qiyeweixin_access_token(_data)
        access_token = access_token_ret.data.get('access_token')

    return  access_token



## 生成公众号token 并获取公众号用户的信息
class get_customer_gongzhonghao_userinfo(object):

    def __init__(self,data):

        self.authorizer_appid = data.get('authorizer_appid')
        self.openid = data.get('openid')
        self.company_id = data.get('company_id')

    def create_token(self):

        three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
        qywx_config_dict = ''
        if three_service_objs:
            three_service_obj = three_service_objs[0]
            qywx_config_dict = three_service_obj.config
            if qywx_config_dict:
                qywx_config_dict = json.loads(qywx_config_dict)

        app_id = qywx_config_dict.get('app_id')
        app_secret = qywx_config_dict.get('app_secret')


        objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=self.authorizer_appid)
        authorizer_refresh_token = ''
        if objs:
            authorizer_refresh_token = objs[0].authorizer_refresh_token

        key_name = 'authorizer_access_token_%s' % (self.authorizer_appid)

        _data = {
            'authorizer_appid': self.authorizer_appid,
            'authorizer_refresh_token': authorizer_refresh_token,
            'key_name': key_name,
            'app_id':  app_id, #'wx6ba07e6ddcdc69b3',  # 查看诸葛雷达_公众号的 appid
            'app_secret': app_secret ,#'0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
        }

        authorizer_access_token_ret = create_gongzhonghao_authorizer_access_token(_data)
        authorizer_access_token = authorizer_access_token_ret.data

        return  authorizer_access_token


    def get_gzh_user_whole_info(self):
        response = Response.ResponseObj()
        authorizer_access_token = self.create_token()
        get_user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
        # get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        get_user_info_data = {
            'access_token': authorizer_access_token,
            'openid': self.openid,
            'lang': 'zh_CN',
        }

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        ret = s.get(get_user_info_url, params=get_user_info_data)

        # ret = requests.get(get_user_info_url, params=get_user_info_data)

        ret.encoding = 'utf-8'
        ret_json = ret.json()
        print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', ret_json)

        if 'errcode' not in ret_json:
            openid = ret_json['openid']  # 用户唯一标识
            nickname = ret_json['nickname']  # 会话密钥

            encodestr = base64.b64encode(nickname.encode('utf-8'))
            customer_name = str(encodestr, 'utf-8')

            sex = ret_json['sex']  #
            province = ret_json['province']  #
            city = ret_json['city']  #
            country = ret_json['country']  #
            headimgurl = ret_json['headimgurl']  #
            token = account.get_token(account.str_encrypt(openid))
            obj = models.zgld_customer.objects.create(
                company_id=self.company_id,
                token=token,
                openid=openid,
                user_type=1,  # (1 代表'微信公众号'),  (2 代表'微信小程序'),
                username=customer_name,
                sex=sex,
                province=province,
                city=city,
                country=country,
                headimgurl=headimgurl,
            )
            print('---------- 公众号-新用户创建成功 crete successful ---->')
            response.code = 200
        else:
            errcode = ret_json.get('errcode')
            errmsg = ret_json.get('errmsg')
            response.code = errcode
            print('---------【公众号】拉取用户信息 报错：errcode | errmsg----------->>', errcode, "|", errmsg)

        return response

    def get_gzh_customer_is_focus_info(self):
        response = Response.ResponseObj()
        authorizer_access_token = self.create_token()

        get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        get_user_info_data = {
            'access_token': authorizer_access_token,
            'openid': self.openid,
            'lang': 'zh_CN',
        }

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        ret = s.get(get_user_info_url, params=get_user_info_data)
        # ret = requests.get(get_user_info_url, params=get_user_info_data)

        ret.encoding = 'utf-8'
        ret_json = ret.json()
        print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', json.dumps(ret_json))

        customer_objs = models.zgld_customer.objects.filter(openid=self.openid)

        customer_id = ''
        if customer_objs:
            customer_id = customer_objs[0].id

        if 'errcode' not in ret_json:
            openid = ret_json['openid']        # 用户唯一标
            subscribe = ret_json['subscribe']  # 值为0时，代表此用户没有关注该公众号

            customer_objs.update(
                is_subscribe=subscribe
            )
            print('---------- 公众号客户ID：%s 修改关注的状态成功| openid | subscribe ---->' % (customer_id), openid, "|", subscribe)
            response.code = 200

        else:
            errcode = ret_json.get('errcode')
            errmsg = ret_json.get('errmsg')
            response.code = errcode

            print('---------【公众号】拉取用户 关注的信息 报错：errcode | errmsg----------->>', errcode, "|", errmsg)


        return response







