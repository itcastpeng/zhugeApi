from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response, account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.qiyeweixin_auth_verify import CreateShareUrl
from ..conf import *
from urllib.parse import quote
from  publicFunc.account import str_sha_encrypt
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import create_authorizer_access_token
from zhugeleida.public.common import jianrong_create_qiyeweixin_access_token

import string, random, time, redis, json, requests, datetime

# 雷达用户登录
@csrf_exempt
def work_weixin_auth(request, company_id):
    print('work_weixin_auth -->', work_weixin_auth)
    response = Response.ResponseObj()

    if request.method == "GET":
        code = request.GET.get('code')
        get_code_data = {}
        get_token_data = {}
        post_userlist_data = {}
        get_userlist_data = {}

        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
        key_name = "company_%s_leida_app_token" % company_id
        token_ret = rc.get(key_name)

        company_obj = models.zgld_company.objects.get(id=company_id)
        account_expired_time = company_obj.account_expired_time

        print('---------【企业微信】 从Redis 取出的 ------->>', key_name, "是:", token_ret)

        if not token_ret:
        # if True:
            corpid = company_obj.corp_id
            corpsecret = company_obj.zgld_app_set.get(company_id=company_id,app_type=1).app_secret

            get_token_data['corpid'] = corpid
            get_token_data['corpsecret'] = corpsecret

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            ret = s.get(Conf['token_url'], params=get_token_data)

            # ret = requests.get(Conf['token_url'], params=get_token_data)


            ret_json = ret.json()
            access_token = ret_json.get('access_token')
            print('===========【企业微信】access_token 请求接口返回 和 access_token ==========>', ret_json,'\n',access_token)

            key_name = "company_%s_leida_app_token" % (company_id)
            rc.set(key_name, access_token, 7000)

        else:
            access_token = token_ret

        get_code_data['code'] = code
        get_code_data['access_token'] = access_token
        code_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        code_ret = s.get(code_url, params=get_code_data)

        # code_ret = requests.get(code_url, params=get_code_data)

        code_ret_json = code_ret.json()
        print('===========【企业微信】 获取 user_ticket 返回:==========>', json.dumps(code_ret_json))

        user_ticket = code_ret_json.get('user_ticket')
        if not user_ticket:
            print('===========【企业微信】获取 user_ticket【失败】,消费 code | 使用access_token:==========>', code, "|", access_token)
            return HttpResponse('404')
        else:
            print('===========【企业微信】获取 user_ticket【成功】,消费 code | 使用access_token | user_ticket==========>', code, "|", access_token, "|", user_ticket)

        post_userlist_data['user_ticket'] = user_ticket
        get_userlist_data['access_token'] = access_token

        print("Conf['userlist_url'] -->", Conf['userlist_url'])

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        user_list_ret = s.post(Conf['userlist_url'], params=get_userlist_data,data=json.dumps(post_userlist_data))

        # user_list_ret = requests.post(Conf['userlist_url'], params=get_userlist_data,data=json.dumps(post_userlist_data))
        user_list_ret_json = user_list_ret.json()

        userid = user_list_ret_json['userid']
        name = user_list_ret_json['name']
        avatar = user_list_ret_json['avatar']    # 加上100 获取小图
        gender = user_list_ret_json['gender']
        # email = user_list_ret_json['email']

        print('----------【企业微信】获取 《用户基本信息》 返回 | userid---->', json.dumps(user_list_ret_json),"|",userid)

        user_profile_objs = models.zgld_userprofile.objects.select_related('company').filter(
            userid=userid,
            company_id=company_id
        )

        if datetime.datetime.now() > account_expired_time:
            company_name = company_obj.name
            response.code = 403
            response.msg = '账户过期'
            print('-------- 雷达后台账户过期: %s-%s | 过期时间:%s ------->>' % (company_id, company_name, account_expired_time))
            return redirect('http://zhugeleida.zhugeyingxiao.com/#/expire_page/index')

        # 如果用户存在
        if user_profile_objs:
            print("---------------- 用户存在")
            user_profile_obj = user_profile_objs[0]
            status = user_profile_obj.status
            boss_status = user_profile_obj.boss_status

            if status == 1: #

                user_profile_obj.gender = gender
                user_profile_obj.avatar = avatar
                last_login_date = user_profile_obj.last_login_date
                # is_show_technical_support = user_profile_obj.company.is_show_jszc

                redirect_url = ''
                if not last_login_date: # 为空说明第一次登陆
                    is_first_login = 'Yes'
                    user_profile_obj.last_login_date = datetime.datetime.now()
                else:
                    is_first_login = 'No'

                user_profile_obj.save()
                # url = ''
                # if status == 1:  #  (1, "AI雷达启用"),
                #     url  = 'http://zhugeleida.zhugeyingxiao.com'
                # elif status == 3: # (3, "Boss雷达启用"),
                #     url = 'http://zhugeleida.zhugeyingxiao.com/#/bossLeida'
                url = 'http://zhugeleida.zhugeyingxiao.com'
                redirect_url = url + '?token=' + user_profile_obj.token + '&id=' + str(
                    user_profile_obj.id) + '&avatar=' + avatar + '&is_first_login=' + is_first_login

                print('----------【雷达用户】存在且《登录成功》，user_id | userid | redirect_url ---->', user_profile_obj.id, "|", userid, "\n", redirect_url)
                print('redirect_url -->', redirect_url)
                return redirect(redirect_url)

            else:
                print('----------【雷达用户】未开通 ,未登录成功 userid | company_id ------>', userid, company_id)
                return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')

        else:
            print('----------【雷达用户】不存在 ,未登录成功 userid | company_id ------>',userid,company_id)
            print('redirect_url --> http://zhugeleida.zhugeyingxiao.com/err_page')
            return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')

    else:
        response.code = 402
        response.msg = "请求方式异常"
    return JsonResponse(response.__dict__)
    # 从微信小程序接口中获取openid等信息


# 雷达用户登录操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def work_weixin_auth_oper(request,oper_type):
    print('work_weixin_auth_oper -->', work_weixin_auth_oper)
    response = Response.ResponseObj()

    if request.method == "GET":

        # 创建公众号分享url
        if oper_type == 'create_gongzhonghao_share_auth_url':
            forms_obj = CreateShareUrl(request.GET)
            if forms_obj.is_valid():

                user_id = request.GET.get('user_id') #企业雷达用户ID
                article_id = forms_obj.cleaned_data.get('article_id')
                user_obj = models.zgld_userprofile.objects.get(id=user_id)
                company_id = user_obj.company_id

                gongzhonghao_app_obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
                authorization_appid = gongzhonghao_app_obj.authorization_appid
                level = 1
                uid = user_id  # 文章所属用户ID，在这里指的是雷达用户 转发的这个文章，他就是这个所属的用户。
                pid =  ''      # 文章所属父级ID。为空代表是雷达用户分享出去的。

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                api_url = qywx_config_dict.get('api_url')

                appid = authorization_appid
                redirect_uri = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth?relate=article_id_%s|pid_%s|level_%s|uid_%s|company_id_%s' % (api_url,article_id,pid,level,uid,company_id)

                print('--------  【雷达企业用户】嵌入创建【分享链接】的 redirect_uri ------->', redirect_uri)
                scope = 'snsapi_userinfo'   # snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
                state = 'snsapi_base'

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                component_appid = qywx_config_dict.get('app_id')

                # component_appid = 'wx6ba07e6ddcdc69b3' # 三方平台-AppID

                share_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s&component_appid=%s#wechat_redirect' % (appid,redirect_uri,scope,state,component_appid)

                bianma_share_url = quote(share_url, 'utf-8')

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                leida_http_url = qywx_config_dict.get('authorization_url')
                share_url = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth/redirect_share_url?share_url=%s' % (leida_http_url,bianma_share_url)

                print('------ 【雷达企业用户】正在触发【创建分享链接】 静默方式的 snsapi_base URL：------>>',share_url)

                response.data = {'share_url': share_url}
                response.code = 200
                response.msg = "返回成功"

            else:
                print('---------- 【雷达企业用户】生成 分享的公众号文章链接 未通过验证 --------->>',forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # #雷达里生成【公众号】JS-SDK使用权限签名算法
        elif  oper_type == 'gongzhonghao_share_sign':
            '''
            生成签名之前必须先了解一下jsapi_ticket，jsapi_ticket是H5应用调用企业微信JS接口的临时票据。
            正常情况下，jsapi_ticket的有效期为7200秒，通过 access_token 来获取
            '''

            # company_id = request.GET.get('company_id')

            user_id = request.GET.get('user_id')  # 企业雷达用户ID
            user_obj = models.zgld_userprofile.objects.get(id=user_id)
            company_id = user_obj.company_id

            print('------- 【企业微信】调用 公众号 签名算法 request.GET --------->',request.GET)
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

            if objs:
                authorizer_refresh_token = objs[0].authorizer_refresh_token
                authorizer_appid = objs[0].authorization_appid
                authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)

                authorizer_access_token = rc.get(authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。


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
                        'app_id': app_id,   #'wx6ba07e6ddcdc69b3',
                        'app_secret':  app_secret,#'0bbed534062ceca2ec25133abe1eecba'
                    }

                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = authorizer_access_token_result.data

                key_name = "company_%s_gongzhonghao_jsapi_ticket" % (company_id)
                ticket_ret = rc.get(key_name)
                print('--- 【企业微信】 从redis里取出 %s : ---->>' % (key_name), ticket_ret)
                jsapi_ticket = ticket_ret

                if not ticket_ret:
                    # get_jsapi_ticket_url = 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket'
                    get_jsapi_ticket_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'

                    get_ticket_data = {
                        'access_token': authorizer_access_token,
                        'type' : 'jsapi'
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

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                url = qywx_config_dict.get('authorization_url') + '/'


                # url = 'http://zhugeleida.zhugeyingxiao.com/'
                sha_string = "jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s" % (jsapi_ticket, noncestr, timestamp, url)
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
                response.msg = "没有公众号app"

        # 创建录播视频 转发链接
        elif oper_type == 'create_link_repost_video':
            user_id = request.GET.get('user_id')        # 用户ID
            video_id = request.GET.get('video_id')      # 视频ID
            user_obj = models.zgld_userprofile.objects.get(id=user_id)
            company_id = user_obj.company_id

            gongzhonghao_app_obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
            authorization_appid = gongzhonghao_app_obj.authorization_appid

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
            qywx_config_dict = ''
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                if three_service_obj.config:
                    qywx_config_dict = json.loads(three_service_obj.config)

            api_url = qywx_config_dict.get('api_url')
            component_appid = qywx_config_dict.get('app_id')
            leida_http_url = qywx_config_dict.get('authorization_url')

            scope = 'snsapi_userinfo'  # snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
            state = 'snsapi_base'
            redirect_uri = '{}/zhugeleida/gongzhonghao/forwarding_video_jump_address?relate={}'.format(
                api_url,
                str(company_id) + '_' + str(video_id)
            )

            share_url = """
                https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope={}&state={}&component_appid={}#wechat_redirect
                """.format(
                    authorization_appid,
                    redirect_uri,
                    scope,
                    state,
                    component_appid
                )

            bianma_share_url = quote(share_url, 'utf-8')
            share_url = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth/redirect_share_url?share_url=%s' % (
            leida_http_url, bianma_share_url)
            print('share_url--------share_url----------share_url-----------share_url---------share_url--------> ', share_url)
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'share_url': share_url
            }

        return JsonResponse(response.__dict__)


# 企业微信 生成JS-SDK使用权限签名算法。
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def enterprise_weixin_sign(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        '''
        生成签名之前必须先了解一下jsapi_ticket，jsapi_ticket是H5应用调用企业微信JS接口的临时票据。
        正常情况下，jsapi_ticket的有效期为7200秒，通过access_token来获取
        '''

        user_id = request.GET.get('user_id')

        user_obj = models.zgld_userprofile.objects.get(id=user_id)
        company_id = user_obj.company_id
        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
        key_name = "company_%s_leida_app_token" % (company_id)
        token_ret = rc.get(key_name)
        print('---token_ret---->>', token_ret)
        company_obj = models.zgld_company.objects.get(id=company_id)
        corpid = company_obj.corp_id

        token_ret = jianrong_create_qiyeweixin_access_token(company_id)

        key_name = "company_%s_jsapi_ticket" % (company_id)
        ticket_ret = rc.get(key_name)
        print('--- 从redis里取出 %s : ---->>' % (key_name), ticket_ret)
        jsapi_ticket = ticket_ret

        if not ticket_ret:
            get_jsapi_ticket_url =  'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket'
            get_ticket_data  = {
                'access_token' : token_ret
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

        three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
        qywx_config_dict = ''
        if three_service_objs:
            three_service_obj = three_service_objs[0]
            qywx_config_dict = three_service_obj.config
            if qywx_config_dict:
                qywx_config_dict = json.loads(qywx_config_dict)

        url = qywx_config_dict.get('authorization_url') + '/'
        # url = 'http://zhugeleida.zhugeyingxiao.com/'

        sha_string = "jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s" % (jsapi_ticket,noncestr,timestamp,url)
        signature = str_sha_encrypt(sha_string.encode('utf-8'))

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'signature': signature,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'appId': corpid
        }

    else:
        response.code = 402
        response.msg = "请求方式异常"

    return JsonResponse(response.__dict__)
