from django.shortcuts import render, redirect,HttpResponse
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.gongzhonghao.gongzhonghao_verify import GongzhonghaoAddForm, LoginBindingForm, CreateShareUrl
from zhugeapi_celery_project import tasks
from publicFunc.account import str_sha_encrypt
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import create_authorizer_access_token, \
    create_component_access_token

from urllib.parse import unquote,quote
import base64, random, json, string, redis, requests, time

# 获取用户信息
def get_user_info(access_token, openid):
    get_user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
    # get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
    get_user_info_data = {
        'access_token': access_token,
        'openid': openid,
        'lang': 'zh_CN',
    }
    # s = requests.session()
    # s.keep_alive = False  # 关闭多余连接
    ret = requests.get(get_user_info_url, params=get_user_info_data)
    ret.encoding = 'utf-8'
    print('----------************************************************------> ', ret.json())
    return ret.json()

# 从微信公众号接口中获取openid等信息
def get_openid_info(get_token_data):
    oauth_url = 'https://api.weixin.qq.com/sns/oauth2/component/access_token'

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    ret = s.get(oauth_url, params=get_token_data)

    # ret = requests.get(oauth_url, params=get_token_data)
    ret_json = ret.json()

    print('-------- 通过code换取 access_token、openid信息等  返回 ------->>', ret_json)

    openid = ret_json['openid']  # 授权用户唯一标识
    access_token = ret_json['access_token']  # 接口调用凭证

    ret_data = {
        'openid': openid,
        'access_token': access_token
    }

    return ret_data

# 公众号验证code 展示转发的文章 和 后台预览的文章
@csrf_exempt
def user_gongzhonghao_auth(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        # <QueryDict: {'code': ['071uPB5w1EudCa0g6b5w1ZAt5w1uPB5U'], 'state': ['snsapi_base'], 'relate': ['article_id_2|pid_|level_1'], 'appid': ['wxa77213c591897a13']}>

        print('-------- 公众号-登录验证 request.GET 数据 ----****-->', request.GET)

        js_code = request.GET.get('code')
        code_objs = models.save_code.objects.filter(code=js_code)
        if not code_objs:
            models.save_code.objects.create(
                code=js_code
            )

            state = request.GET.get('state')
            appid = request.GET.get('appid')
            relate = request.GET.get('relate')

            _type = relate.split('|')[0].split('_')[1]
            if _type == 'BindingUserNotify':
                redirect_url = binding_gzh_user_notify(request)
                return redirect(redirect_url)

            article_id = relate.split('|')[0].split('_')[2]
            pid = relate.split('|')[1].split('_')[1]
            level = relate.split('|')[2].split('_')[1]
            uid = relate.split('|')[3].split('_')[1]
            company_id = relate.split('|')[4].split('_')[2]

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
            qywx_config_dict = ''
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

            component_appid = qywx_config_dict.get('app_id')
            app_secret = qywx_config_dict.get('app_secret')

            # component_appid = 'wx6ba07e6ddcdc69b3'

            data_dict = {
                'app_id': component_appid,  # 查看诸葛雷达_公众号的 appid
                'app_secret': app_secret  # 查看诸葛雷达_公众号的AppSecret
            }

            component_access_token_ret = create_component_access_token(data_dict)
            component_access_token = component_access_token_ret.data.get('component_access_token')

            get_token_data = {
                'appid': appid,
                'code': js_code,
                'grant_type': 'authorization_code',
                'component_appid': component_appid,
                'component_access_token': component_access_token
            }

            ret_data = get_openid_info(get_token_data)
            print('ret_data----ret_data----ret_data----ret_data---------------ret_data->< ', ret_data)
            openid = ret_data['openid']
            access_token = ret_data['access_token']
            redirect_url = ''

            # 判断静默和非静默方式
            # 静默方式
            client_id = ''
            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
            qywx_config_dict = ''
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

            url = qywx_config_dict.get('authorization_url')
            api_url = qywx_config_dict.get('api_url')
            headimgurl = ''
            if state == 'snsapi_base':

                customer_objs = models.zgld_customer.objects.filter(
                    openid=openid,
                    user_type=1,  # 公众号
                )
                # 获取用户信息
                ret_json = get_user_info(access_token, openid)
                print('ret_json============ret_json---ret_json---ret_json--ret_json--ret_json--->', ret_json)
                openid = ret_json['openid']  # 用户唯一标识
                nickname = ret_json['nickname']  # 客户名称
                encodestr = base64.b64encode(nickname.encode('utf-8'))  # 加密客户名称
                customer_name = str(encodestr, 'utf-8') # 字符串化
                sex = ret_json['sex']  # 客户性别
                province = ret_json['province']  # 客户
                city = ret_json['city']  #
                country = ret_json['country']  #
                headimgurl = ret_json['headimgurl']  # 客户头像

                if customer_objs:
                    # 更新客户基本信息
                    customer_objs.update(
                        username=customer_name,
                        sex=sex,
                        province=province,
                        city=city,
                        country=country,
                        headimgurl=headimgurl
                    )

                    token = customer_objs[0].token
                    client_id = customer_objs[0].id
                    if not uid:  # 代表预览的后台分享出去的链接
                        article_url = '/gongzhonghao/yulanneirong/'
                    else:  # 代表是雷达用户分享出去的。
                        article_url = '/gongzhonghao/leidawenzhang/'


                    redirect_url = '{url}/zhugeleidaArticleShare#{article_url}{article_id}?token={token}&user_id={client_id}&uid={uid}&level={level}&pid={pid}&company_id={company_id}'.format(
                        url=url,
                        article_url=article_url,
                        article_id=article_id,
                        token=token,
                        client_id=client_id,
                        uid=uid,  # 文章作者-ID
                        level=level,  # 所在层级
                        pid=pid,  # 目前所在的父级ID
                        company_id=company_id,
                    )

                    data = {
                        'article_id': article_id,
                        'user_id': uid,  # 文章作者-ID
                        'customer_id': client_id,
                        'level': level,
                        'pid': pid,
                        'company_id': company_id,
                    }
                    pid = int(pid) if pid else ''
                    customer_id = int(client_id)

                    if uid and pid != customer_id:  # 说明不是从后台预览的,是企业用户分享出去的,要绑定关系的。
                        customer_username = customer_objs[0].username
                        if customer_username:
                            customer_username = base64.b64decode(customer_username)
                            customer_username = str(customer_username, 'utf-8')

                        print('静默--------- 企业雷达用户ID：%s 分享出去的,【已完成注册的公众号ID: %s,customer_name: %s】客户要绑定自己到文章 | json.dumps(data) ---------->' % (
                            uid, client_id, customer_username), '|', json.dumps(data))
                        tasks.binding_article_customer_relate.delay(data)

                else:

                    redirect_uri = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth?relate=article_id_%s|pid_%s|level_%s|uid_%s|company_id_%s' % (
                    api_url, article_id, pid, level, uid, company_id)
                    redirect_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={scope}&component_appid={component_appid}#wechat_redirect'.format(
                        appid=appid,
                        redirect_uri=redirect_uri,
                        scope='snsapi_userinfo',
                        component_appid=component_appid
                    )
                    print('--------- 当认证登录时判断是首次登录, 返回非静默方式 snsapi_userinfo URL 登录------>>', redirect_url)

            # 非静默
            else:
                ret_json = get_user_info(access_token, openid) # 获取用户信息
                print('----------- 【公众号】拉取用户信息 接口返回拉取用户信息 接口返回拉取用户信息 接口返回 ---------->>', ret_json)
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
                    customer_objs = models.zgld_customer.objects.filter(openid=openid)
                    if customer_objs:
                        customer_objs.update(
                            company_id=company_id,
                            user_type=1,  # (1 代表'微信公众号'),  (2 代表'微信小程序'),
                            username=customer_name,
                            sex=sex,
                            province=province,
                            city=city,
                            country=country,
                            headimgurl=headimgurl
                        )
                        client_id = customer_objs[0].id
                        print('---------- 公众号-新用户修改成功 update successful ---->',client_id)

                    else:
                        obj = models.zgld_customer.objects.create(
                            company_id=company_id,
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
                        client_id = obj.id
                        print('---------- 公众号-新用户创建成功 crete successful ---->',client_id)

                    if not uid:  # 代表预览的后台分享出去的链接
                        article_url = '/gongzhonghao/yulanneirong/'
                    else:  # 代表是雷达用户分享出去的。
                        article_url = '/gongzhonghao/leidawenzhang/'


                    redirect_url = '{url}/zhugeleidaArticleShare#{article_url}{article_id}?token={token}&user_id={client_id}&uid={uid}&level={level}&pid={pid}&company_id={company_id}'.format(
                        url=url,
                        article_url=article_url,
                        article_id=article_id,
                        token=token,
                        client_id=client_id,

                        uid=uid,  # 文章作者-ID
                        level=level,  # 所在层级
                        pid=pid,  # 目前所在的父级ID
                        company_id=company_id,
                    )
                    data = {
                        'article_id': article_id,
                        'user_id': uid,  # 文章作者-ID
                        'customer_id': client_id,
                        'level': level,
                        'pid': pid,
                        'company_id': company_id,
                    }
                    pid = int(pid) if pid else ''
                    customer_id = int(client_id)
                    if uid and pid != customer_id:  # 说明不是从后台预览的,是企业用户分享出去的,要绑定关系的。并且不是自己看了这种情况下
                        print('非静默--------- 企业雷达用户ID：%s 分享出去的,【新公众号ID: %s,customer_name: %s】客户要关联自己到文章 | json.dumps(data) ---------->' % (
                            uid, client_id, customer_name), '|', json.dumps(data))
                        tasks.binding_article_customer_relate.delay(data)

                else:
                    errcode = ret_json.get('errcode')
                    errmsg = ret_json.get('errmsg')
                    print('---------【公众号】拉取用户信息 报错：errcode | errmsg----------->>', errcode, "|", errmsg)

            print('-----------  微信-本次回调给我code后, 让其跳转的 redirect_url是： -------->>', redirect_url)

            if openid:
                _data = {
                    'openid': openid,
                    'authorizer_appid': appid,
                    'headimgurl': headimgurl,
                    'user_id' : uid,
                    'company_id': company_id,
                    'client_id' : client_id
                }
                # 获取 公众号的用户信息
                tasks.get_customer_gongzhonghao_userinfo.delay(_data)
            else:
                print('没有获取到 openid------->>')

            return redirect(redirect_url)


    else:
        response.code = 402
        response.msg = "请求方式异常"

    return JsonResponse(response.__dict__)


# 用于后台生成预览授权的二维码。
def create_gongzhonghao_yulan_auth_url(data):
    response = Response.ResponseObj()
    pid = data.get('pid')
    level = data.get('level')
    company_id = data.get('company_id')
    article_id = data.get('article_id')
    # uid = data.get('uid')
    uid = ''  # 后台生成预览二维码时，此时用户UID 就是admin_userprofile 的用户ID不要分享出去。

    gongzhonghao_app_obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
    authorization_appid = gongzhonghao_app_obj.authorization_appid
    appid = authorization_appid


    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
    qywx_config_dict = ''
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        qywx_config_dict = three_service_obj.config
        if qywx_config_dict:
            qywx_config_dict = json.loads(qywx_config_dict)

    api_url = qywx_config_dict.get('api_url')

    component_appid = qywx_config_dict.get('app_id')
    app_secret = qywx_config_dict.get('app_secret')
    api_url = '123456789'
    redirect_uri = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth?relate=article_id_%s|pid_%s|level_%s|uid_%s|company_id_%s' % (
        api_url,article_id, pid, level, uid, company_id)


    print('-------- 静默方式下跳转的 需拼接的 redirect_uri ------->', redirect_uri)
    scope = 'snsapi_userinfo'  # snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
    state = 'snsapi_userinfo'
    # component_appid = 'wx6ba07e6ddcdc69b3' # 三方平台-AppID

    authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&response_type=code&scope=%s&state=%s&redirect_uri=%s#wechat_redirect' % (
    appid, scope, state, redirect_uri)
    print('------ 【默认】生成的静默方式登录的 snsapi_base URL：------>>', authorize_url)
    response.data = {'authorize_url': authorize_url}
    response.code = 200
    response.msg = "返回成功"

    return response


## 绑定公众号通知消息的人
def binding_gzh_user_notify(request):

    # <QueryDict: {'code': ['071uPB5w1EudCa0g6b5w1ZAt5w1uPB5U'], 'state': ['snsapi_base'], 'relate': ['article_id_2|pid_|level_1'], 'appid': ['wxa77213c591897a13']}>

    print('-------- 公众号-登录验证 request.GET 数据 -->', request.GET)

    js_code = request.GET.get('code')
    code_objs = models.save_code.objects.filter(code=js_code)
    if not code_objs:
        models.save_code.objects.create(
            code=js_code
        )
        state = request.GET.get('state')
        appid = request.GET.get('appid')
        relate = request.GET.get('relate')
        company_id = relate.split('|')[1].split('_')[2]

        three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
        qywx_config_dict = ''
        if three_service_objs:
            three_service_obj = three_service_objs[0]
            qywx_config_dict = three_service_obj.config
            if qywx_config_dict:
                qywx_config_dict = json.loads(qywx_config_dict)

        component_appid = qywx_config_dict.get('app_id')
        app_secret = qywx_config_dict.get('app_secret')

        # component_appid = 'wx6ba07e6ddcdc69b3'

        data_dict = {
            'app_id': component_appid,  # 查看诸葛雷达_公众号的 appid
            'app_secret': app_secret  # 查看诸葛雷达_公众号的AppSecret
        }

        component_access_token_ret = create_component_access_token(data_dict)
        component_access_token = component_access_token_ret.data.get('component_access_token')

        get_token_data = {
            'appid': appid,
            'code': js_code,
            'grant_type': 'authorization_code',
            'component_appid': component_appid,
            'component_access_token': component_access_token
        }

        ret_data = get_openid_info(get_token_data)
        openid = ret_data['openid']
        access_token = ret_data['access_token']
        redirect_url = ''

        # 静默方式
        three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
        qywx_config_dict = ''
        if three_service_objs:
            three_service_obj = three_service_objs[0]
            qywx_config_dict = three_service_obj.config
            if qywx_config_dict:
                qywx_config_dict = json.loads(qywx_config_dict)

        url = qywx_config_dict.get('authorization_url')

        if state == 'snsapi_base':

            customer_objs = models.zgld_customer.objects.filter(openid=openid)
            if customer_objs:
                customer_objs.update(
                    session_key='notifier'  # 通知者
                )
                client_id = customer_objs[0].id

            else:
                obj = models.zgld_customer.objects.create(
                    company_id=company_id,
                    openid=openid,
                    user_type=1,  # (1 代表'微信公众号'),  (2 代表'微信小程序')
                    session_key='notifier'  # 通知者
                )
                print('---------- 公众号-新用户创建成功 crete successful ---->')
                client_id = obj.id

            fanhui_url = url + '/#/gzh_success/index'
            gzh_objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=appid)
            qrcode_url = ''
            if gzh_objs:
                qrcode_url = gzh_objs[0].qrcode_url

            redirect_url = '{fanhui_url}?user_id={client_id}&qrcode_url={qrcode_url}&company_id={company_id}'.format(
                fanhui_url=fanhui_url,
                qrcode_url=qrcode_url,
                client_id=client_id,
                company_id=company_id,
            )

        print('-----------  微信-本次回调给我code后, 让其跳转的 redirect_url是： -------->>', redirect_url)


        return redirect_url


# 公众号文章生成分享的url
@csrf_exempt
@account.is_token(models.zgld_customer)
def user_gongzhonghao_auth_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":

        three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
        qywx_config_dict = ''
        if three_service_objs:
            three_service_obj = three_service_objs[0]
            qywx_config_dict = three_service_obj.config
            if qywx_config_dict:
                qywx_config_dict = json.loads(qywx_config_dict)

        url = qywx_config_dict.get('authorization_url')
        api_url = qywx_config_dict.get('api_url')

        if oper_type == 'create_gongzhonghao_share_auth_url':
            forms_obj = CreateShareUrl(request.GET)
            if forms_obj.is_valid():
                customer_id = request.GET.get('user_id')
                uid = forms_obj.cleaned_data.get('uid')  # 雷达用户ID。代表此企业用户从雷达里分享出去-这个文章。
                # pid = forms_obj.cleaned_data.get('pid')
                level = forms_obj.cleaned_data.get('level')
                article_id = forms_obj.cleaned_data.get('article_id')
                company_id = forms_obj.cleaned_data.get('company_id')

                gongzhonghao_app_obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
                authorization_appid = gongzhonghao_app_obj.authorization_appid

                level += 1
                pid = customer_id
                appid = authorization_appid
                redirect_uri = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth?relate=article_id_%s|pid_%s|level_%s|uid_%s|company_id_%s' % (
                    api_url,article_id, pid, level, uid, company_id)

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                component_appid = qywx_config_dict.get('app_id')
                # token = qywx_config_dict.get('token')
                # encodingAESKey = qywx_config_dict.get('encodingAESKey')

                print('--------  嵌入创建【分享链接】的 redirect_uri ------->', redirect_uri)
                scope = 'snsapi_userinfo'  # snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
                state = 'snsapi_base'
                # component_appid = 'wx6ba07e6ddcdc69b3' # 三方平台-AppID

                share_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s&component_appid=%s#wechat_redirect' % (
                appid, redirect_uri, scope, state, component_appid)

                bianma_share_url = quote(share_url, 'utf-8')

                share_url = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth/redirect_share_url?share_url=%s' % (api_url,bianma_share_url)
                print('------ 客户正在触发【创建分享链接】 静默方式的 snsapi_base URL：------>>', share_url)

                response.data = {'share_url': share_url}
                response.code = 200
                response.msg = "返回成功"

            else:
                print('---------- 生成 分享的公众号文章链接 未通过验证 --------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        ##生成公众号JS-SDK使用权限签名算法
        elif oper_type == 'gongzhonghao_share_sign':
            '''
            生成签名之前必须先了解一下jsapi_ticket，jsapi_ticket是H5应用调用企业微信JS接口的临时票据。
            正常情况下，jsapi_ticket的有效期为7200秒，通过 access_token 来获取
            '''

            company_id = request.GET.get('company_id')
            location_href = request.GET.get('location_href')

            if '#' in location_href:
                location_href = location_href.split('#')[0]
                print('--------- location_href --------->>', location_href)

            print('------- 公众号 签名算法 request.GET --------->', request.GET)
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            if objs:
                authorizer_refresh_token = objs[0].authorizer_refresh_token
                authorizer_appid = objs[0].authorization_appid
                authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)

                authorizer_access_token = rc.get(
                    authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

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
                    data = {
                        'key_name': authorizer_access_token_key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid,
                        'app_id': app_id,
                        'app_secret': app_secret
                    }

                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = authorizer_access_token_result.data

                key_name = "company_%s_gongzhonghao_jsapi_ticket" % (company_id)
                ticket_ret = rc.get(key_name)
                print('--- 从redis里取出 %s : ---->>' % (key_name), ticket_ret)
                jsapi_ticket = ticket_ret

                if not ticket_ret:
                    # get_jsapi_ticket_url = 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket'
                    get_jsapi_ticket_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'

                    get_ticket_data = {
                        'access_token': authorizer_access_token,
                        'type': 'jsapi'
                    }

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    jsapi_ticket_ret = s.get(get_jsapi_ticket_url, params=get_ticket_data)

                    # jsapi_ticket_ret = requests.get(get_jsapi_ticket_url, params=get_ticket_data)
                    print('=========== 权限签名 jsapi_ticket_ret 接口返回 ==========>', jsapi_ticket_ret.json())
                    jsapi_ticket_ret = jsapi_ticket_ret.json()
                    ticket = jsapi_ticket_ret.get('ticket')
                    errmsg = jsapi_ticket_ret.get('errmsg')
                    if errmsg != "ok":
                        response.code = 402
                        response.msg = "没有生成生成签名所需的jsapi_ticket"
                        print('-------- 生成签名所需的jsapi_ticket ----------->>')
                        return JsonResponse(response.__dict__)
                    else:
                        rc.set(key_name, ticket, 7000)
                        jsapi_ticket = ticket

                noncestr = ''.join(random.sample(string.ascii_letters + string.digits, 16))
                timestamp = int(time.time())
                # url = 'http://zhugeleida.zhugeyingxiao.com/'
                url = location_href
                sha_string = "jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s" % (
                jsapi_ticket, noncestr, timestamp, url)
                signature = str_sha_encrypt(sha_string.encode('utf-8'))

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'signature': signature,
                    'timestamp': timestamp,
                    'nonceStr': noncestr,
                    'appid': authorizer_appid
                }
                print('------- 公众号 签名算法 response.data--------->', response.data)

            else:
                response.code = 301
                response.msg = "没有请求数据"

        return JsonResponse(response.__dict__)


# 分享去的文章链接当点击后，出首先走到 api.zhugeleida.com 域名,程序帮他跳转到授权的URL上。
@csrf_exempt
def user_gongzhonghao_redirect_share_url(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        share_url = request.GET.get('share_url')

        redirect_url = unquote(share_url, 'utf-8')
        print('-----------  文章分享之后, 客户打开让其跳转的 share_url是： -------->>', redirect_url)
        return redirect(redirect_url)

    else:
        response.code = 401
        response.msg = "请求方式异常"

    return JsonResponse(response.__dict__)
