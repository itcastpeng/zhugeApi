from zhugeleida import models
from publicFunc import Response
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.public.crypto_ import WXBizMsgCrypt_qiyeweixin
from zhugeleida.public import common
from django.shortcuts import render, redirect
from zhugeapi_celery_project import tasks
import xml.dom.minidom as xmldom, datetime, xml.etree.cElementTree as ET
import json, redis, sys, requests
from zhugeleida.public.common import create_qrcode


def get_provider_token():
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    get_token_data = {  # 通用开发参数
        "corpid": "wx81159f52aff62388",  # 服务商的corpid
        "provider_secret": "HwX3RsMfMx9O4KBTqzwk9UMJ9pjNGbjE7PTyPaK7Gyxu4Z_G0ypv9iXT97A3EFDt"  # 服务商的secret
    }

    key_name = "%s_provider_token" % get_token_data['corpid']

    provider_access_token = rc.get(key_name)
    print('----- 从 Redis 获取 %s: ------>>' % (key_name), provider_access_token)

    if not provider_access_token:
        appurl = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_provider_token'
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        ret = s.post(appurl, data=json.dumps(get_token_data))

        ret_json = ret.json()
        print('------ 第三方平台 【服务商的token】 接口返回 ----->>', ret_json)

        provider_access_token = ret_json.get('provider_access_token')  # 用户唯一标识

        print('-----第三方平台 生成 provider_access_token------->>', provider_access_token)
        rc.set(key_name, provider_access_token, 7000)

    return provider_access_token


## 第三方平台接入
@csrf_exempt
def open_qiyeweixin(request, oper_type):
    response = Response.ResponseObj()
    # application_data = {
    #     'leida': {
    #         'sToken': '5lokfwWTqHXnb58VCV',
    #         'sEncodingAESKey': 'ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt',
    #         'sCorpID': 'wx5d26a7a856b22bec',
    #     },
    #     'boss': {
    #         'sToken': '22LlaSyBP',
    #         'sEncodingAESKey': 'NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be',
    #         'sCorpID': 'wx36c67dd53366b6f0',
    #     },
    #     'address_book': {
    #         'sToken': '8sCAJ3YuU6EfYWxI',
    #         'sEncodingAESKey': '3gSz92t8espUQgbXembgcDk3e6Hrs9SpJf34zQ8lqEj',
    #         'sCorpID': 'wx1cbe3089128fda03',
    #     }
    # }
    if request.method == "POST":

        # 企业微信服务器会定时（每十分钟）推送ticket。https://work.weixin.qq.com/api/doc#10982/推送suite_ticket
        if oper_type == 'get_ticket':
            print('------ 第三方 request.body 企业微信服务器 推送suite_ticket ------>>', request.body.decode(encoding='UTF-8'))

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            ticket_type = request.GET.get('type')

            postdata = request.body.decode(encoding='UTF-8')

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)

            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                sToken = qywx_config_dict[ticket_type]['sToken']
                sEncodingAESKey = qywx_config_dict[ticket_type]['sEncodingAESKey']
                sCorpID = qywx_config_dict[ticket_type]['sCorpID']

                print('sToken -->', sToken)
                print('sEncodingAESKey -->', sEncodingAESKey)
                print('sCorpID -->', sCorpID)
                decrypt_obj = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

                # xml_tree = ET.fromstring(postdata)
                # msg_signature = "2b29a5534ed8b50981ae0069c1f4c48127789cec"
                # timestamp = "1538228121"
                # nonce = "1537294388"
                # sReqData = '<xml><ToUserName><![CDATA[wx5d26a7a856b22bec]]></ToUserName><Encrypt><![CDATA[uh2c6Yqs5f8nPcXQmTtxifpYEIX0Y5FV/nrsbAo4FGKdCPCLVA1p7XSDnC6XN5/1YiFE4ywFs2CvT0n1xHbJ4vSksICKqkPr0z9PtxhJDcbuhz7wgsUSLmEMeXWR1f6YVaOGkFKqa6YJ0lalvpGcS03RRwTuqb49VccfuV5KO4y3eabi6qQRh5QG6SHYKGPZmTfD32Q5GGgGhm4QH3ne/hUTLtMdk3CONblGcodRs5/iAArxfGCFxYADT9d/9Q6ZoNoLruYD66RPrX8AghjKE6KoCqNomsgLHbINJEBxkyEaTBd9qqJe+zoXJMXhyFJ6CsmfKRITwC/Lz32wZF0bF44fzhybguIyMOohxZEhyl1pJpwpgX5DjpjKs47jKf76]]></Encrypt><AgentID><![CDATA[]]></AgentID></xml>'

                ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
                print(ret, sMsg)
                if (ret != 0):
                    print("--- 企业微信解密 ERR: DecryptMsg ret --->: " + str(ret))
                    sys.exit(1)

                DOMTree = xmldom.parseString(sMsg)
                collection = DOMTree.documentElement
                ChangeType = collection.getElementsByTagName("ChangeType")  # update_user

                if ChangeType:  # 通讯录的触发事件，增删改查用户 和关注微工作台的事件提示。
                    InfoType = collection.getElementsByTagName("InfoType")[0].childNodes[
                        0].data  # <InfoType><![CDATA[change_contact]]></InfoType>
                    ChangeType = collection.getElementsByTagName("ChangeType")[0].childNodes[
                        0].data  # <ChangeType><![CDATA[update_user]]></ChangeType>
                    UserID = collection.getElementsByTagName("UserID")[0].childNodes[0].data
                    AuthCorpId = collection.getElementsByTagName("AuthCorpId")[0].childNodes[0].data

                    company_objs = models.zgld_company.objects.filter(corp_id=AuthCorpId)
                    company_id = ''
                    if company_objs:
                        company_obj = company_objs[0]
                        company_id = company_obj.id

                    _Status = collection.getElementsByTagName(
                        "Status")  # <Status>1</Status></xml> #激活状态: 1=已激活，2=已禁用，4=未激活。
                    if _Status:  # 代表既未激活企业微信又未关注微工作台（原企业号）。
                        Status = collection.getElementsByTagName("Status")[0].childNodes[0].data
                        if int(Status) == 1:  # 1=已激活
                            _data = {
                                'company_id': company_id,
                                'userid': UserID,
                            }
                            tasks.qiyeweixin_user_get_userinfo.delay(_data)  # 异步获取用户的头像
                        return HttpResponse("success")

                    elif not _Status:  # 没有status ，说明 是用户的增删改查。

                        return HttpResponse("success")
                xml_tree = ET.fromstring(sMsg)
                xml_tree.find("SuiteTicket")

                # 解密成功，sMsg即为xml格式的明文
                try:
                    SuiteTicket = xml_tree.find("SuiteTicket").text
                    SuiteId = xml_tree.find("SuiteId").text

                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

                    key_name = 'SuiteTicket_%s' % (SuiteId)
                    rc.set(key_name, SuiteTicket, 3000)
                    print('--------企业微信服务器 SuiteId | suite_ticket--------->>', SuiteId, '|', SuiteTicket)

                except  Exception as e:

                    SuiteId = xml_tree.find("SuiteId").text
                    AuthCode = xml_tree.find("AuthCode").text

                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    key_name = 'AuthCode_%s' % (SuiteId)

                    rc.set(key_name, AuthCode, 1000)  # 授权的auth_code。用于获取企业的永久授权码。5分钟内有效
                    print('--------【通讯录】企业微信服务器 SuiteId | AuthCode--------->>', SuiteId, '|', AuthCode)

                    get_permanent_code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code'

                    _app_type = ''
                    name = '通讯录应用'
                    if SuiteId == qywx_config_dict['address_book']['sCorpID']:
                        name = '通讯录'
                        _app_type = 3

                    _data = {
                        'SuiteId': SuiteId
                    }
                    create_pre_auth_code_ret = common.create_pre_auth_code(_data)
                    suite_access_token = create_pre_auth_code_ret.data.get('suite_access_token')

                    get_permanent_code_url_data = {
                        'suite_access_token': suite_access_token
                    }
                    post_permanent_code_url_data = {
                        'auth_code': AuthCode
                    }

                    get_permanent_code_info_ret = requests.post(get_permanent_code_url,
                                                                params=get_permanent_code_url_data,
                                                                data=json.dumps(post_permanent_code_url_data))

                    get_permanent_code_info = get_permanent_code_info_ret.json()
                    print('-------[企业微信-通讯录] 获取企业永久授权码 返回------->>', get_permanent_code_info)

                    corpid = get_permanent_code_info['auth_corp_info'].get('corpid')  # 授权方企业微信id
                    corp_name = get_permanent_code_info['auth_corp_info'].get('corp_name')  # 授权方企业微信名称
                    # agent_list = get_permanent_code_info['auth_info'].get('agent')  # 授权方企业微信名称

                    access_token = get_permanent_code_info.get('access_token')  # 授权方（企业）access_token
                    permanent_code = get_permanent_code_info.get(
                        'permanent_code')  # 企业微信永久授权码 | 每个企业授权的每个应用的永久授权码、授权信息都是唯一的

                    if permanent_code:
                        key_name = 'access_token_qiyeweixin_%s_%s' % (corpid, SuiteId)
                        rc.set(key_name, access_token, 7000)
                        objs = models.zgld_company.objects.filter(corp_id=corpid)
                        if objs:
                            company_id = objs[0].id
                            app_objs = models.zgld_app.objects.filter(app_type=_app_type, company_id=company_id)
                            if app_objs:
                                print('----- [企业微信-通讯录] 授权方-企业微信【修改了】数据库 corpid: --->', corpid, '|', permanent_code,
                                      corp_name)

                                app_objs.update(
                                    name=name,
                                    app_type=_app_type,
                                    is_validate=True,
                                    # agent_id=agentid,
                                    permanent_code=permanent_code
                                )

                            else:
                                print('----- [企业微信-通讯录] 授权方-企业微信【创建了】数据库 corpid: --->', corpid, '|', permanent_code,
                                      corp_name)
                                models.zgld_app.objects.create(
                                    is_validate=True,
                                    name=name,
                                    app_type=_app_type,
                                    # agent_id=agentid,
                                    company_id=company_id,
                                    permanent_code=permanent_code
                                )
                    else:
                        print('-------[企业微信] 获取企业永久授权码 报错：------->>')


            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 get_ticket ------>>')

            return HttpResponse("success")

        # 生成微信授权的页面
        elif oper_type == "create_grant_url":

            app_type = int(request.POST.get('app_type')) if request.POST.get('app_type') else ''
            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)

            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                suite_id = ''
                if app_type == 1:  # 雷达AI
                    # suite_id = 'wx5d26a7a856b22bec'
                    app_type = 'leida'
                    suite_id = qywx_config_dict['leida']['sCorpID']

                elif app_type == 2:  # 雷达Boss
                    # suite_id = 'wx36c67dd53366b6f0'
                    suite_id = qywx_config_dict['boss']['sCorpID']
                    app_type = 'boss'

                elif app_type == 3:  # 通讯录
                    # suite_id = 'wx1cbe3089128fda03'
                    suite_id = qywx_config_dict['address_book']['sCorpID']
                    app_type = 'address_book'


                leida_http_url = qywx_config_dict.get('domain_urls').get('leida_http_url')
                redirect_uri = '%s/open_qiyeweixin/get_auth_code' % (leida_http_url)  # 安装完成回调域名

                _data = {
                    'SuiteId': suite_id
                }
                create_pre_auth_code_ret = common.create_pre_auth_code(_data)

                pre_auth_code = create_pre_auth_code_ret.data.get('pre_auth_code')

                get_bind_auth_data = 'suite_id={}&pre_auth_code={}&redirect_uri={}&state={}'.format(suite_id,
                                                                                                    pre_auth_code,
                                                                                                    redirect_uri,
                                                                                                    suite_id)

                pre_auth_code_url = 'https://open.work.weixin.qq.com/3rdapp/install?' + get_bind_auth_data

                response.code = 200
                response.msg = '生成【授权链接】成功'
                response.data = {
                    'pre_auth_code_url': pre_auth_code_url
                }
                # 授权成功，返回临时授权码;第三方服务商需尽快使用临时授权码换取永久授权码及授权信息

            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 create_grant_url ------>>')


        # 设置授权配置 /zhugeleida/admin/open_qiyeweixin/set_session_info
        elif oper_type == 'set_session_info':

            suite_id = request.GET.get('suite_id')

            _data = {
                'SuiteId': suite_id
            }
            create_pre_auth_code_ret = common.create_pre_auth_code(_data)

            pre_auth_code = create_pre_auth_code_ret.data.get('pre_auth_code')
            suite_access_token = create_pre_auth_code_ret.data.get('suite_access_token')

            set_session_info_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/set_session_info'

            post_set_session_info_data = {
                "pre_auth_code": pre_auth_code,
                "session_info":
                    {
                        "appid": [],
                        "auth_type": 1  # 授权类型：0 正式授权， 1 测试授权。 默认值为0。注意，请确保应用在正式发布后的授权类型为“正式授权”
                    }
            }
            get_set_session_info_data = {
                'suite_access_token': suite_access_token,
            }
            set_session_info = requests.post(set_session_info_url, params=get_set_session_info_data,
                                             data=json.dumps(post_set_session_info_data))

            set_session_info = set_session_info.json()
            print('---------- [企业微信] - 设置授权配置 返回------------>>', set_session_info)

            response.code = 200
            response.msg = '生成【设置授权配置】成功'
            response.data = set_session_info

        # 授权之后的回调
        elif oper_type == 'callback_data':

            '''
             授权之后有两个回调,一个是  POST /zhugeleida/admin/open_qiyeweixin/callback_data?type=boss&msg_signature=ed2912f1df90240f8ec02085769db7837b8548b6&timestamp=1539251675&nonce=1539178361
             解密得到： ww24123520340ba230 是每个企业的ID | 1000007 agent_id
             <xml><ToUserName><![CDATA[ww24123520340ba230]]></ToUserName>
                <FromUserName><![CDATA[GuoKeDian]]></FromUserName>
                <CreateTime>1539253005</CreateTime>
                <MsgType><![CDATA[event]]></MsgType>
             <AgentID>1000007</AgentID><Event><![CDATA[subscribe]]></Event></xml>
             
             另一个是授权回调域名
             redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/open_qiyeweixin/get_auth_codeauth_code=AtLOpL38bexv_im5HOekFAlwjk4bITVn9cpYxY0VCB06peY12fNGPzypAOmvsUU1rMmd47mPVxGWElBahIpGSRFWnG2c3EgW5KQozilnB98&state=wx5d26a7a856b22bec&expires_in=1200'   #三方应用安装完成回调域名
                            
                    
            '''
            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            postdata = request.body.decode(encoding='UTF-8')
            type = request.GET.get('state')

            xml_tree = ET.fromstring(postdata)  # 安装到这个企业后的 agent_id

            SuiteId = xml_tree.find("AgentID").text
            print('-----post callback_data postdata 数据:------>', postdata)

            return HttpResponse('success')

    elif request.method == "GET":

        # 微信发送要解密的ticket 获取票据
        if oper_type == 'get_ticket':
            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')
            ticket_type = request.GET.get('type')

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                sToken = qywx_config_dict[ticket_type]['sToken']
                sEncodingAESKey = qywx_config_dict[ticket_type]['sEncodingAESKey']

                # sCorpID = "wx81159f52aff62388"
                sCorpID = qywx_config_dict['general_parm'].get('sCorpID')  # 三方通用参数
                wxcpt = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

                # ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
                ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
                if (ret != 0):
                    print("---- 验证回调URL: VerifyURL ret: ----> " + str(ret))
                    sys.exit(1)
                print('----- [get_ticket]解密echostr参数得到消息内容 -------->>', sEchoStr)

                # 验证URL成功，将sEchoStr返回给企业号
                return HttpResponse(sEchoStr)

            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 get_ticket ------>>')



        # 获取微信回调数据
        elif oper_type == 'callback_data':
            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')

            type = request.GET.get('type')

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                sToken = ''
                sEncodingAESKey = ''
                if type == 'leida':
                    # sToken = "5lokfwWTqHXnb58VCV"  # 回调配置
                    # sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"  # 回调配置
                    sToken = qywx_config_dict['leida']['sToken']
                    sEncodingAESKey = qywx_config_dict['leida']['sEncodingAESKey']


                elif type == 'boss':
                    # sToken = "22LlaSyBP"  # 回调配置
                    # sEncodingAESKey = "NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be"  # 回调配置
                    sToken = qywx_config_dict['boss']['sToken']
                    sEncodingAESKey = qywx_config_dict['boss']['sEncodingAESKey']

                # sCorpID = "wx81159f52aff62388"  # 通用开发参数 CorpID
                sCorpID = qywx_config_dict['general_parm']['sCorpID']  # 通用开发参数 CorpID
                wxcpt = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

                # ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
                ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
                if (ret != 0):
                    print("---- 验证回调URL: VerifyURL ret: ----> " + str(ret))
                    sys.exit(1)
                print('----- [callback_data]解密echostr参数得到消息内容 -------->>', sEchoStr)

                # 验证URL成功，将sEchoStr返回给企业号
                return HttpResponse(sEchoStr)


            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 callback_data ------>>')

        #  网页授权登录第三方-登陆
        elif oper_type == 'work_weixin_auth':
            code = request.GET.get('code')
            app_type = request.GET.get('state')

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                # SuiteId = 'wx1cbe3089128fda03'  # 通讯录三方应用
                # SuiteId = qywx_config_dict['address_book'].get('sCorpID') # 通讯录三方应用
                SuiteId = ''
                auth_code = ''
                _app_type = ''
                url = ''
                domain = qywx_config_dict['domain_urls'].get('leida_http_url')
                if app_type == 'leida':
                    # SuiteId = 'wx5d26a7a856b22bec'
                    SuiteId = qywx_config_dict['leida'].get('sCorpID')
                    url = domain
                elif app_type == 'boss':
                    # SuiteId = 'wx36c67dd53366b6f0'
                    # url = 'http://zhugeleida.zhugeyingxiao.com/#/bossLeida'
                    SuiteId = qywx_config_dict['boss'].get('sCorpID')
                    url = domain + '/#/bossLeida'

                elif 'scan_code_web_login' in app_type:
                    _app_type = app_type.split('|')[0]
                    auth_code = app_type.split('|')[1]
                    url = domain

                    # SuiteId = 'wx5d26a7a856b22bec'
                    # url = 'http://zhugeleida.zhugeyingxiao.com/'
                    SuiteId = qywx_config_dict['leida'].get('sCorpID')

                _data = {
                    'SuiteId': SuiteId,  # 通讯录三方应用
                }

                suite_access_token_ret = common.create_suite_access_token(_data)
                suite_access_token = suite_access_token_ret.data.get('suite_access_token')

                get_code_data = {
                    'code': code,
                    'access_token': suite_access_token
                }
                code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/getuserinfo3rd'
                code_ret = requests.get(code_url, params=get_code_data)

                code_ret_json = code_ret.json()
                print('===========【企业微信】 获取 user_ticket 返回:==========>', json.dumps(code_ret_json))

                user_ticket = code_ret_json.get('user_ticket')
                errcode = code_ret_json.get('errcode')
                userid = code_ret_json.get('UserId')
                corpid = code_ret_json.get('CorpId')

                # print('----------【企业微信】获取 《用户基本信息》 返回 | userid---->', json.dumps(code_ret_json), "|", userid)
                company_objs = models.zgld_company.objects.filter(corp_id=corpid)

                if company_objs:
                    company_id = company_objs[0].id
                    product_function_type = company_objs[0].product_function_type  #  (1, '小程序版|公众号版'),   (2, '小程序版'),   (3, '公众号版'),

                    # is_show_technical_support = company_objs[0].is_show_jszc

                    _data = {
                        'company_id': company_id,
                        'userid': userid,
                    }
                    tasks.qiyeweixin_user_get_userinfo.delay(_data)

                    user_profile_objs = models.zgld_userprofile.objects.select_related('company').filter(
                        userid=userid,
                        company_id=company_id
                    )

                    # 如果用户存在
                    if user_profile_objs:
                        user_profile_obj = user_profile_objs[0]
                        status = user_profile_obj.status
                        boss_status = user_profile_obj.boss_status

                        account_expired_time = company_objs[0].account_expired_time
                        if datetime.datetime.now() > account_expired_time:
                            response.code = 403
                            response.msg = '账户过期'
                            print('-------- 雷达后台账户过期 - corpid: %s | 过期时间:%s ------->>' % (corpid, account_expired_time))
                            return redirect('%s/#/expire_page/index' % (domain) )

                        avatar = user_profile_obj.avatar
                        user_id = user_profile_obj.id
                        token = user_profile_obj.token
                        if status == 1 and app_type == 'leida':  #

                            last_login_date = user_profile_obj.last_login_date
                            if not last_login_date:  # 为空说明第一次登陆
                                is_first_login = 'Yes'
                                user_profile_obj.last_login_date = datetime.datetime.now()
                            else:
                                is_first_login = 'No'
                            user_profile_obj.save()

                            redirect_url = url + '?token=' + token + '&id=' + str(
                                user_id) + '&avatar=' + avatar + '&is_first_login=' + is_first_login + '&company_id=' + str(company_id) + '&product_function_type=' + str(product_function_type)

                            print('----------【雷达用户】存在且《登录成功》，user_id | userid | redirect_url ---->', user_id, "|",
                                  userid,
                                  "\n", redirect_url)

                            return redirect(redirect_url)

                        elif boss_status == 1 and app_type == 'boss':  #
                            redirect_url = url + '?token=' + token + '&id=' + str(user_id) + '&avatar=' + avatar + '&company_id=' + str(company_id) +  '&product_function_type=' + str(product_function_type)

                            print('----------【雷达用户】存在且《登录成功》，user_id | userid | redirect_url ---->', userid, "|",
                                  userid, "\n", redirect_url)

                            return redirect(redirect_url)

                        elif status == 1 and _app_type == 'scan_code_web_login':
                            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                            rc.set(auth_code, True, 120)
                            user_profile_obj.password = auth_code
                            user_profile_obj.save()

                            print('----------【雷达用户】《扫码登录成功》，user_id | userid  ---->', user_id, "|", userid)
                            return redirect('%s/#/login_success/index?code=200' % (domain))

                        elif status != 1 and _app_type == 'scan_code_web_login':
                            print('----------【雷达用户】《扫码登录失败》没权限，user_id | userid  ---->', user_id, "|", userid)
                            return redirect('%s/#/login_success/index?code=403' % (domain))

                        else:
                            print('----------【雷达权限】未开通 ,未登录成功 user_id | corpid ------>', user_id, corpid)
                            return redirect('%s/err_page' % (domain))

                    else:
                        print('----------【雷达用户】不存在 ,未登录成功 userid | corpid ------>', userid, "|", corpid)
                        return redirect('%s/err_page' % (domain))
                else:
                    print('----------【公司不存在】,未登录成功 userid | corpid ------>', userid, "|", corpid)
                    return redirect('%s/err_page' % (domain))

            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 work_weixin_auth ------>>')



        #  用户确认授权后，会进入回调URI(即redirect_uri)，并在URI参数中带上临时授权码
        elif oper_type == 'get_auth_code':
            # SuiteId = xml_tree.find("SuiteId").text
            # AuthCode = xml_tree.find("AuthCode").text

            SuiteId = request.GET.get('state')
            AuthCode = request.GET.get('auth_code')

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            key_name = 'AuthCode_%s' % (SuiteId)

            rc.set(key_name, AuthCode, 1000)  # 授权的auth_code。用于获取企业的永久授权码。5分钟内有效
            print('--------企业微信服务器 SuiteId | AuthCode--------->>', SuiteId, '|', AuthCode)

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                url = qywx_config_dict['domain_urls'].get('leida_http_url')
                get_permanent_code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code'
                _app_type = ''
                name = ''
                if SuiteId == qywx_config_dict['leida'].get('sCorpID'):  # 'wx5d26a7a856b22bec'
                    name = '雷达AI'
                    _app_type = 1

                elif SuiteId == qywx_config_dict['boss'].get('sCorpID'):  # 'wx36c67dd53366b6f0':
                    name = '雷达Boss'
                    _app_type = 2

                elif SuiteId == qywx_config_dict['address_book'].get('sCorpID'):  # 'wx1cbe3089128fda03':
                    name = '诸葛通讯录'
                    _app_type = 3

                _data = {
                    'SuiteId': SuiteId
                }
                create_pre_auth_code_ret = common.create_pre_auth_code(_data)

                suite_access_token = create_pre_auth_code_ret.data.get('suite_access_token')

                get_permanent_code_url_data = {
                    'suite_access_token': suite_access_token
                }
                post_permanent_code_url_data = {
                    'auth_code': AuthCode
                }

                get_permanent_code_info_ret = requests.post(get_permanent_code_url, params=get_permanent_code_url_data,
                                                            data=json.dumps(post_permanent_code_url_data))

                get_permanent_code_info = get_permanent_code_info_ret.json()
                print('-------[企业微信] 获取企业永久授权码 返回------->>', json.dumps(get_permanent_code_info))

                corpid = get_permanent_code_info['auth_corp_info'].get('corpid')  # 授权方企业微信id
                corp_name = get_permanent_code_info['auth_corp_info'].get('corp_name')  # 授权方企业微信名称
                agent_list = get_permanent_code_info['auth_info'].get('agent')  # 授权方企业微信名称
                agentid = ''
                for _agent_dict in agent_list:
                    _name = _agent_dict.get('name')
                    if _name == name:
                        agentid = _agent_dict.get('agentid')

                access_token = get_permanent_code_info.get('access_token')  # 授权方（企业）access_token
                permanent_code = get_permanent_code_info.get(
                    'permanent_code')  # 企业微信永久授权码 | 每个企业授权的每个应用的永久授权码、授权信息都是唯一的

                if permanent_code:
                    key_name = 'access_token_qiyeweixin_%s_%s' % (corpid, SuiteId)
                    rc.set(key_name, access_token, 7000)
                    objs = models.zgld_company.objects.filter(corp_id=corpid)
                    if objs:
                        company_id = objs[0].id
                        app_objs = models.zgld_app.objects.filter(app_type=_app_type, company_id=company_id)
                        if app_objs:
                            print('----- [企业微信] 授权方-企业微信【修改了】数据库 corpid: --->', corpid, '|', permanent_code, corp_name)

                            app_objs.update(
                                name=name,
                                app_type=_app_type,
                                is_validate=True,
                                agent_id=agentid,
                                permanent_code=permanent_code

                            )

                        else:
                            print('----- [企业微信] 授权方-企业微信【创建了】数据库 corpid: --->', corpid, '|', permanent_code, corp_name)
                            models.zgld_app.objects.create(
                                is_validate=True,
                                name=name,
                                app_type=_app_type,
                                agent_id=agentid,
                                company_id=company_id,
                                permanent_code=permanent_code
                            )

                    else:
                        print('-------[企业微信] 企业不存在：------->>', corpid)

                    return redirect('%s/admin/#/empower/empower_company' % (url))

                else:
                    print('-------[企业微信] 获取企业永久授权码 报错：------->>')


            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 work_weixin_auth ------>>')


        # 用户使用企业微信管理员或成员帐号登录第三方网站，该登录授权基于OAuth2.0协议标准构建。
        elif oper_type == 'third_fang_single_login':

            auth_code = request.GET.get('auth_code')
            provider_access_token = get_provider_token()

            if provider_access_token:

                get_login_info_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_login_info'
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                get_login_info_data = {
                    "access_token": provider_access_token
                }
                post_login_info_data = {
                    "auth_code": auth_code
                }
                ret = s.post(get_login_info_url, params=get_login_info_data, data=json.dumps(post_login_info_data))

                ret_json = ret.json()
                print('------ 第三方平台 【服务商获取-登录用户信息】 接口返回 ----->>', json.dumps(ret_json))
                # ret_json = {'usertype': 1,
                #             'user_info':
                #                 {'userid': 'ZhangJu',
                #                  'name': '张炬1',
                #                  'avatar': 'https://p.qlogo.cn/bizmail/Tj5TZc6xibicYIiaQm9mghQl5oE5712iaVIBYicEAM0C20zpn8FBZUnXKmQ/0'
                #                  },
                #             'corp_info':
                #                 {'corpid': 'wwf358ba1c3f3560c5'},
                #             'agent':
                #                 [{'agentid': 1000007, 'auth_type': 1}, {'agentid': 1000009, 'auth_type': 1}],
                #             'auth_info': {'department': [{'id': 1, 'writable': True}]}}

                userid = ret_json.get('user_info')['userid']  # 用户唯一标识
                name = ret_json.get('user_info')['name']  # 用户名字
                avatar = ret_json.get('user_info')['avatar']  # 头像
                corpid = ret_json.get('corp_info')['corpid']  #

                if userid:
                    print('-----第三方平台 【服务商获取-用户信息】UserId: %s | corpid : %s  ------->>' % (userid, corpid))
                    company_objs = models.zgld_company.objects.filter(corp_id=corpid)
                    if company_objs:
                        obj = company_objs[0]
                        company_id = obj.id
                        user_profile_objs = models.zgld_userprofile.objects.select_related('company').filter(
                            userid=userid,
                            company_id=company_id
                        )

                        # 如果用户存在
                        if user_profile_objs:

                            userprofile_obj = user_profile_objs[0]
                            status = userprofile_obj.status

                            account_expired_time = company_objs[0].account_expired_time
                            if datetime.datetime.now() < account_expired_time:

                                if status == 1:  # (1, "AI雷达启用"),

                                    last_login_date_obj = userprofile_obj.last_login_date
                                    last_login_date = last_login_date_obj.strftime(
                                        '%Y-%m-%d %H:%M:%S') if last_login_date_obj else ''

                                    response.data = {
                                        'user_id': userprofile_obj.id,
                                        'token': userprofile_obj.token,
                                        'role_id': 1,
                                        'username': name,
                                        'avatar': avatar,

                                        'company_name': userprofile_obj.company.name,
                                        'company_id': userprofile_obj.company_id,

                                        'weChatQrCode': userprofile_obj.company.weChatQrCode,
                                        'state': 'scan_code_web_login',
                                        'last_login_date': last_login_date,

                                    }

                                    userprofile_obj.last_login_date = datetime.datetime.now()
                                    userprofile_obj.avatar = avatar
                                    userprofile_obj.save()
                                    response.code = 200
                                    response.msg = '登录成功'
                                    print('----------【后台雷达用户】登录成功 userid: %s | corpid: %s ----<<' % (userid, corpid))

                                else:
                                    response.code = 405
                                    response.msg = "账户未启用"
                                    print('----------【雷达权限】未开通 ,未登录成功 userid | corpid ------>>', userid, corpid)

                            else:
                                company_name = userprofile_obj.company.name
                                response.code = 403
                                response.msg = '账户过期'
                                print('-------- 雷达后台账户过期: %s-%s | 过期时间:%s ------->>' % (
                                    company_id, company_name, account_expired_time))

                        else:
                            response.code = 402
                            response.msg = "用户不存在 userid: %s" % (userid)
                            print('----公司不存在 UserId: %s  | corpid : %s ----->>' % (userid, corpid))

                    else:
                        response.code = 401
                        response.msg = "公司不存在 corpid: %s " % (corpid)
                        print('----公司不存在 UserId: %s  | corpid : %s ----->>' % (userid, corpid))

                else:
                    response.code = 401
                    response.msg = '服务商获取-用户信息报错'
                    print('------第三方平台 【服务商获取-用户信息】报错 ----->')

        # 雷达后台扫码登录
        elif oper_type == 'web_scan_authorize_qrcode':
            import uuid
            uuid = str(uuid.uuid1())
            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

                url = qywx_config_dict['domain_urls'].get('leida_http_url') #http://zhugeleida.zhugeyingxiao.com
                sCorpID =  qywx_config_dict['leida'].get('sCorpID')
                authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s/open_qiyeweixin/work_weixin_auth&response_type=code&scope=snsapi_userinfo&state=scan_code_web_login|%s#wechat_redirect' % (
                    sCorpID,url,uuid)

                qrcode_data = {
                    'url': authorize_url,
                    'type': 'web_scan_authorize_qrcode'
                }
                response_ret = create_qrcode(qrcode_data)
                pre_qrcode_url = response_ret.get('pre_qrcode_url')

                if pre_qrcode_url:
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    response.data = {
                        'auth_qrcode_url': pre_qrcode_url,
                        'auth_code': uuid
                    }
                    rc.set(uuid, False, 120)

                    response.code = 200
                    response.msg = '生成二维码成功'

                else:
                    response.code = 401
                    response.msg = '生成二维码失败'

            else:
                response.code = 301
                response.msg = '企业微信第三方-无配置信息'
                print('------ 【企业微信第三方-无配置信息】 web_scan_authorize_qrcode ------>>')


    else:

        response.code = 400
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)
