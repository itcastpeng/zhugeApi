from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
from zhugeapi_celery_project import tasks
from wechatpy.replies import TextReply,ImageReply
from wechatpy.crypto import WeChatCrypto
from zhugeleida.public.common import action_record
from zhugeleida.forms.admin import open_weixin_gongzhonghao_verify
import json, redis, base64, os, datetime, time, xml.etree.cElementTree as ET
import xml.dom.minidom as xmldom, requests
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
import subprocess,os,time,threading
from zhugeleida.public.common import  get_customer_gongzhonghao_userinfo
from zhugeleida.public.common import create_qrcode

## 线程非阻塞执行
def thread_func_grant_callback(objs,qrcode_url,authorizer_appid,component_appid,api_url):

    ## 下载URL参数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    html = s.get(qrcode_url)
    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "/%s_%s.jpg" % (authorizer_appid, now_time)
    file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'qr_code') + filename
    with open(file_dir, 'wb') as file:
        file.write(html.content)
    print('----- 生成 本地二维码 file_dir ---->>', file_dir)
    objs.update(qrcode_url=file_dir)  # 二维码

    company_id = objs[0].company_id
    # 创建二维码

    redirect_uri = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth?relate=type_BindingUserNotify|company_id_%s' % (api_url,company_id)

    print('-------- 静默方式下跳转的 需拼接的 redirect_uri ------->', redirect_uri)
    scope = 'snsapi_base'  # snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
    state = 'snsapi_base'
    # component_appid = 'wx6ba07e6ddcdc69b3' # 三方平台-AppID

    authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s&component_appid=%s#wechat_redirect' % (
        authorizer_appid, redirect_uri, scope, state, component_appid)

    print('------ 【默认】生成的静默方式登录的 snsapi_base URL：------>>', authorize_url)
    qrcode_data = {
        'url': authorize_url,
        'type': 'binding_gzh_user_notify'
    }

    response_ret = create_qrcode(qrcode_data)
    pre_qrcode_url = response_ret.get('pre_qrcode_url')

    if pre_qrcode_url:
        print('绑定公众号和客户通知者的二维码 pre_qrcode_url---------->>', pre_qrcode_url)
        objs.update(
            gzh_notice_qrcode=pre_qrcode_url
        )




# 第三方平台接入
@csrf_exempt
def open_weixin_gongzhonghao(request, oper_type):
    if request.method == "POST":
        response = Response.ResponseObj()
        if oper_type == 'tongzhi':

            print('------ 第三方 request.body tongzhi 通知内容 ------>>', request.body.decode(encoding='UTF-8'))

            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            # postdata =  request.POST.get('postdata')

            postdata = request.body.decode(encoding='UTF-8')

            global decryp_xml_tree
            xml_tree = ET.fromstring(postdata)
            try:

                '''
                调用示例代码中的DecryptMsg函数（需传入msg_signature、timetamp、nonce和postdata，前3个参数可从接收已授权公众号消息和事件的URL中获得，
                postdata即为POST过来的数据包内容），若调用成功，sMsg则为输出结果，其内容为如下的明文的xml消息体:
                <xml>
                    <ToUserName></ToUserName>
                    <FromUserName></FromUserName>
                    <CreateTime>1411035097</CreateTime>
                    <MsgType></MsgType>
                    <Content></Content>
                    <MsgId>6060349595123187712</MsgId>
                </xml>


                #测试加密接口
                encryp_test = WXBizMsgCrypt(token, encodingAESKey, app_id)
                ret, encrypt_xml = encryp_test.EncryptMsg(to_xml, nonce)
                print(ret, encrypt_xml)

                '''
                encrypt = xml_tree.find("Encrypt").text
                app_id = xml_tree.find("AppId").text

                # print('----- 授权公众号授权 postdata---->>',postdata)

                print('appid -->', app_id)
                print('encrypt -->', encrypt)

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                appid = qywx_config_dict.get('app_id')
                token = qywx_config_dict.get('token')
                encodingAESKey = qywx_config_dict.get('encodingAESKey')

                # token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
                # encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
                # appid = 'wx6ba07e6ddcdc69b3'

                decrypt_obj = WXBizMsgCrypt(token, encodingAESKey, appid)
                ret, decryp_xml = decrypt_obj.DecryptMsg(encrypt, msg_signature, timestamp, nonce)

                decryp_xml_tree = ET.fromstring(decryp_xml)
                ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text

                print('----ret -->', ret)
                print('-----decryp_xml -->', decryp_xml)

                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

                ComponentVerifyTicket_key_name = 'ComponentVerifyTicket_%s' % (appid)
                if ret == 0:
                    rc.set(ComponentVerifyTicket_key_name, ComponentVerifyTicket, 10000)
                    print('--------授权-诸葛雷达_公众号消息解密 ComponentVerifyTicket--------->>', ComponentVerifyTicket)

                else:
                    response.code = ret
                    response.msg = "-------- 授权-诸葛雷达_公众号消息解密  ------->"
                    return JsonResponse(response.__dict__)

            except Exception as e:
                auth_code = decryp_xml_tree.find('AuthorizationCode').text
                authorization_appid = decryp_xml_tree.find('AuthorizerAppid').text  # authorizer_appid 授权方de  appid

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                app_id = qywx_config_dict.get('app_id')
                api_url = qywx_config_dict.get('api_url')

                # app_id = 'wx6ba07e6ddcdc69b3'
                if auth_code:
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    # exist_auth_code = rc.get('auth_code')
                    auth_code_key_name = 'auth_code_%s' % (app_id)
                    rc.set(auth_code_key_name, auth_code, 3400)

                    print("---------- 成功获取授权码auth_code --------->>", auth_code)

                else:
                    print('------ 授权码（authorization_code）为空------>>')
                    response.code = 400
                    response.msg = "授权码authorization_code为空"
                    return JsonResponse(response.__dict__)

                component_access_token_key_name = 'component_access_token_%s' % (app_id)
                get_access_token_data = {}
                post_access_token_data = {}
                component_access_token = rc.get(component_access_token_key_name)

                access_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
                get_access_token_data['component_access_token'] = component_access_token
                post_access_token_data['component_appid'] = app_id
                post_access_token_data['authorization_code'] = auth_code

                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                access_token_ret = s.post(access_token_url, params=get_access_token_data, data=json.dumps(post_access_token_data))

                # access_token_ret = requests.post(access_token_url, params=get_access_token_data, data=json.dumps(post_access_token_data))

                access_token_ret = access_token_ret.json()
                print('--------- 获取令牌 authorizer_access_token authorizer_refresh_token 返回---------->>',
                      access_token_ret)
                authorizer_access_token = access_token_ret['authorization_info'].get('authorizer_access_token')
                authorizer_refresh_token = access_token_ret['authorization_info'].get('authorizer_refresh_token')
                authorizer_appid = access_token_ret['authorization_info'].get('authorizer_appid')

                authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)
                if authorizer_access_token and authorizer_refresh_token:

                    rc.set(authorizer_access_token_key_name, authorizer_access_token, 7000)

                    ##################### 获取公众号授权方的authorizer_info信息 ##################
                    get_wx_info_data = {}
                    post_wx_info_data = {}
                    post_wx_info_data['component_appid'] = app_id
                    post_wx_info_data['authorizer_appid'] = authorizer_appid
                    get_wx_info_data['component_access_token'] = component_access_token
                    url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    authorizer_info_ret = s.post(url, params=get_wx_info_data,data=json.dumps(post_wx_info_data))

                    # authorizer_info_ret = requests.post(url, params=get_wx_info_data,data=json.dumps(post_wx_info_data))

                    print('----------- 获取_公众号授权方的authorizer_info信息 返回 ------------->',json.dumps(authorizer_info_ret.json()))
                    authorizer_info_ret = authorizer_info_ret.json()
                    original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                    verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info'][
                                                   'id'] == 0 else False

                    principal_name = authorizer_info_ret['authorizer_info'].get('principal_name')  # 主体名称
                    qrcode_url = authorizer_info_ret['authorizer_info'].get('qrcode_url')  # 二维码
                    head_img = authorizer_info_ret['authorizer_info'].get('head_img')  # 头像
                    nick_name = authorizer_info_ret['authorizer_info'].get('nick_name')  # 头像

                    miniprograminfo = authorizer_info_ret['authorizer_info'].get('MiniProgramInfo')
                    categories = ''
                    if miniprograminfo:
                        categories = authorizer_info_ret['authorizer_info']['MiniProgramInfo'].get('categories')  # 类目

                        if len(categories) != 0:
                            categories = json.dumps(categories)
                        else:
                            categories = ''

                    if original_id:
                        objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=authorization_appid)
                        if objs:

                            t1 = threading.Thread(target=thread_func_grant_callback,args=(objs,qrcode_url,authorization_appid,app_id,api_url))  # 创建一个线程对象t1 子线程
                            t1.start()

                            objs.update(
                                authorization_appid=authorization_appid,  # 授权方appid
                                authorizer_refresh_token=authorizer_refresh_token,  # 刷新的 令牌
                                original_id=original_id,  # 公众号的原始ID
                                verify_type_info=verify_type_info,  # 是否 微信认证

                                principal_name=principal_name,  # 主体名称
                                qrcode_url=qrcode_url,  # 二维码
                                head_img=head_img,  # 头像
                                name=nick_name,  # 昵称
                                service_category=categories,  # 服务类目
                            )

                            # html = s.get(qrcode_url)
                            # now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                            # filename = "/%s_%s.jpg" % (authorizer_appid, now_time)
                            # file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'qr_code') + filename
                            # with open(file_dir, 'wb') as file:
                            #     file.write(html.content)
                            # print('----- 生成 本地二维码 file_dir ---->>',file_dir)
                            # objs.update(qrcode_url=file_dir)  # 二维码


                        print('----------成功获取auth_code和帐号基本信息authorizer_info成功---------->>')
                        response.code = 200
                        response.msg = "成功获取auth_code和帐号基本信息authorizer_info成功"

                        ########################### 公众号设置所属行业 ######################################
                        get_industry_data = {'access_token': authorizer_access_token}

                        api_set_industry_url = 'https://api.weixin.qq.com/cgi-bin/template/api_set_industry'
                        post_industry_data = {
                            "industry_id1": "1",  # IT科技 互联网|电子商务，
                            "industry_id2": "2"
                        }

                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        template_list_ret = s.post(api_set_industry_url, params=get_industry_data, data=json.dumps(post_industry_data))

                        # template_list_ret = requests.post(api_set_industry_url, params=get_industry_data, data=json.dumps(post_industry_data))
                        template_list_ret = template_list_ret.json()
                        errcode = template_list_ret.get('errcode')
                        errmsg = template_list_ret.get('errmsg')

                        print('---- 公众号设置所属行业【返回】 ---->', json.dumps(template_list_ret))

                        # {"errcode": 0, "errmsg": "ok"}

                        if errmsg == "ok":
                            response.code = 200
                            response.msg = "公众号设置所属行业成功"

                            print('---------  授权appid: %s  公众号设置所属行业【成功】 ------------>>' % (authorization_appid))
                        else:
                            response.code = errcode
                            response.msg = errmsg
                            print('---------  授权appid: %s  公众号设置所属行业【失败】------------>>' % (authorization_appid), errmsg,
                                  '|', errcode)

                        ########### 添加模板ID到该公众号下 ##################
                        # doc https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1433751277
                        # OPENTM202109783	咨询回复消息提醒	IT科技	互联网|电子商务
                        api_add_template_url = 'https://api.weixin.qq.com/cgi-bin/template/api_add_template'

                        post_add_template_data = {
                            "template_id_short": "OPENTM202109783"
                        }

                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        industry_ret = s.post(api_add_template_url, params=get_industry_data, data=json.dumps(post_add_template_data))

                        # industry_ret = requests.post(api_add_template_url, params=get_industry_data, data=json.dumps(post_add_template_data))
                        industry_ret = industry_ret.json()
                        template_id = industry_ret.get('template_id')
                        errmsg = industry_ret.get('errmsg')
                        errcode = industry_ret.get('errcode')

                        print('-------- 【公众号】添加模板ID到该账户下 返回 ---->', json.dumps(industry_ret))

                        if errmsg == "ok":
                            response.code = 200
                            response.msg = "公众号添加模板ID成功"
                            objs.update(template_id=template_id)
                            # {"errcode": 0, "errmsg": "ok", "template_id": "yIqr5W_MVshHlyjZIvEd8Lg0KI-nyrOlsTIWMyX_NME"}
                            print('--------- 公众号添加模板ID【成功】  appid: %s ------------>>' % (authorization_appid))

                        else:
                            response.code = errcode
                            response.msg = errmsg
                            print('--------- 公众号添加模板ID 【失败】 appid: %s ------------>>' % (authorization_appid), errmsg,
                                  '|', errcode)




                    else:
                        response.code = 400
                        response.msg = "获取帐号基本信息 authorizer_info信息为空"
                        return JsonResponse(response.__dict__)

                        ######################### end ############################################

                else:
                    print('------ 令牌（authorizer_access_token）为空------>>')
                    response.code = 400
                    response.msg = "令牌 authorizer_access_token 为空"
                    return JsonResponse(response.__dict__)

            return HttpResponse("success")

        # 生成接入的二维码
        elif oper_type == "create_grant_url":
            user_id = request.GET.get('user_id')

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
            qywx_config_dict = ''
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

            app_id = qywx_config_dict.get('app_id')
            app_secret = qywx_config_dict.get('app_secret')

            # app_id = 'wx6ba07e6ddcdc69b3'  # 诸葛雷达_公众号 appid
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            data_dict = {
                'app_id': app_id,  # 查看诸葛雷达_公众号的 appid
                'app_secret': app_secret # 查看诸葛雷达_公众号的AppSecret
            }

            response_ret = create_component_access_token(data_dict)
            component_access_token = response_ret.data.get('component_access_token')

            get_pre_auth_data = {
                'component_access_token': component_access_token
            }
            post_pre_auth_data = {
                'component_appid': app_id
            }
            pre_auth_code_key_name = 'pre_auth_code_%s' % (app_id)
            exist_pre_auth_code = rc.get(pre_auth_code_key_name)
            # if not exist_pre_auth_code:

            pre_auth_code_url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            pre_auth_code_ret = s.post(pre_auth_code_url, params=get_pre_auth_data, data=json.dumps(post_pre_auth_data))

            # pre_auth_code_ret = requests.post(pre_auth_code_url, params=get_pre_auth_data, data=json.dumps(post_pre_auth_data))
            pre_auth_code_ret = pre_auth_code_ret.json()
            pre_auth_code = pre_auth_code_ret.get('pre_auth_code')

            print('------ 获取第三方平台 pre_auth_code 预授权码 ----->', pre_auth_code_ret)

            if pre_auth_code:
                rc.set(pre_auth_code_key_name, pre_auth_code, 1600)

            else:
                response.code = 400
                response.msg = "获取第三方平台预授权码返回错误"
                print("--------- 获取第三方平台 pre_auth_code预授权码 返回错误 ------->")
                return JsonResponse(response.__dict__)

            # else:
            #     pre_auth_code = exist_pre_auth_code

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=1)  # 公众号
            qywx_config_dict = ''
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

            leida_http_url = qywx_config_dict.get('domain_urls').get('leida_http_url')

            # 生成授权链接
            redirect_uri = '%s/admin/#/empower/empower_xcx/' % (leida_http_url)
            # get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=2' % (app_id, pre_auth_code, redirect_uri) #授权注册页面扫码授权
            get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=1' % (app_id, pre_auth_code, redirect_uri)  # auth_type=1  1则商户扫码后，手机端仅展示公众号

            pre_auth_code_url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?' + get_bind_auth_data

            print('------- [生成授权链接-公众号] pre_auth_code_url ---------->>', pre_auth_code_url)

            response.code = 200
            response.msg = '生成【授权链接】成功'
            response.data = pre_auth_code_url

        return JsonResponse(response.__dict__)


# 第三方平台接入
@csrf_exempt
def open_weixin_gongzhonghao_oper(request, oper_type, app_id):
    if request.method == "POST":
        response = Response.ResponseObj()
        if oper_type == 'tongzhi':

            print('------ 第三方 request.body tongzhi 通知内容 ------>>', request.body.decode(encoding='UTF-8'))

            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            # postdata =  request.POST.get('postdata')

            postdata = request.body.decode(encoding='UTF-8')

            global decryp_xml_tree
            xml_tree = ET.fromstring(postdata)
            try:

                '''
                调用示例代码中的DecryptMsg函数（需传入msg_signature、timetamp、nonce和postdata，前3个参数可从接收已授权公众号消息和事件的URL中获得，
                postdata即为POST过来的数据包内容），若调用成功，sMsg则为输出结果，其内容为如下的明文的xml消息体:
                <xml>
                    <ToUserName></ToUserName>
                    <FromUserName></FromUserName>
                    <CreateTime>1411035097</CreateTime>
                    <MsgType></MsgType>
                    <Content></Content>
                    <MsgId>6060349595123187712</MsgId>
                </xml>


                #测试加密接口
                encryp_test = WXBizMsgCrypt(token, encodingAESKey, app_id)
                ret, encrypt_xml = encryp_test.EncryptMsg(to_xml, nonce)
                print(ret, encrypt_xml)

                '''
                encrypt = xml_tree.find("Encrypt").text
                app_id = xml_tree.find("AppId").text

                # print('----- 授权公众号授权 postdata---->>',postdata)

                print('appid -->', app_id)
                print('encrypt -->', encrypt)


                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                appid = qywx_config_dict.get('app_id')
                token = qywx_config_dict.get('token')
                encodingAESKey = qywx_config_dict.get('encodingAESKey')

                # token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
                # encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
                # appid = 'wx6ba07e6ddcdc69b3'

                decrypt_obj = WXBizMsgCrypt(token, encodingAESKey, appid)
                ret, decryp_xml = decrypt_obj.DecryptMsg(encrypt, msg_signature, timestamp, nonce)

                decryp_xml_tree = ET.fromstring(decryp_xml)
                ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text

                print('----ret -->', ret)
                print('-----decryp_xml -->', decryp_xml)

                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

                ComponentVerifyTicket_key_name = 'ComponentVerifyTicket_%s' % (appid)
                if ret == 0:
                    rc.set(ComponentVerifyTicket_key_name, ComponentVerifyTicket, 10000)
                    print('--------授权-诸葛雷达_公众号消息解密 ComponentVerifyTicket--------->>', ComponentVerifyTicket)

                else:
                    response.code = ret
                    response.msg = "-------- 授权-诸葛雷达_公众号消息解密  ------->"
                    return JsonResponse(response.__dict__)

            except Exception as e:
                auth_code = decryp_xml_tree.find('AuthorizationCode').text
                authorization_appid = decryp_xml_tree.find('AuthorizerAppid').text  # authorizer_appid 授权方de  appid

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                app_id = qywx_config_dict.get('app_id')

                # app_id = 'wx6ba07e6ddcdc69b3'
                if auth_code:
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    # exist_auth_code = rc.get('auth_code')
                    auth_code_key_name = 'auth_code_%s' % (app_id)
                    rc.set(auth_code_key_name, auth_code, 3400)

                    print("---------- 成功获取授权码auth_code --------->>", auth_code)

                else:
                    print('------ 授权码（authorization_code）为空------>>')
                    response.code = 400
                    response.msg = "授权码authorization_code为空"
                    return JsonResponse(response.__dict__)

                component_access_token_key_name = 'component_access_token_%s' % (app_id)
                get_access_token_data = {}
                post_access_token_data = {}
                component_access_token = rc.get(component_access_token_key_name)

                access_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
                get_access_token_data['component_access_token'] = component_access_token
                post_access_token_data['component_appid'] = app_id
                post_access_token_data['authorization_code'] = auth_code

                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                access_token_ret = s.post(access_token_url, params=get_access_token_data, data=json.dumps(post_access_token_data))

                # access_token_ret = requests.post(access_token_url, params=get_access_token_data, data=json.dumps(post_access_token_data))
                access_token_ret = access_token_ret.json()
                print('--------- 获取令牌 authorizer_access_token authorizer_refresh_token 返回---------->>',
                      access_token_ret)
                authorizer_access_token = access_token_ret['authorization_info'].get('authorizer_access_token')
                authorizer_refresh_token = access_token_ret['authorization_info'].get('authorizer_refresh_token')
                authorizer_appid = access_token_ret['authorization_info'].get('authorizer_appid')

                authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)
                if authorizer_access_token and authorizer_refresh_token:

                    rc.set(authorizer_access_token_key_name, authorizer_access_token, 7000)

                    ##################### 获取公众号授权方的authorizer_info信息 ##################
                    get_wx_info_data = {}
                    post_wx_info_data = {}
                    post_wx_info_data['component_appid'] = app_id
                    post_wx_info_data['authorizer_appid'] = authorizer_appid
                    get_wx_info_data['component_access_token'] = component_access_token

                    url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    authorizer_info_ret = s.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))

                    # authorizer_info_ret = requests.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))

                    print('----------- 获取_公众号授权方的authorizer_info信息 返回 ------------->', json.dumps(authorizer_info_ret.json()))
                    authorizer_info_ret = authorizer_info_ret.json()
                    original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                    verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info']['id'] == 0 else False
                    #
                    principal_name = authorizer_info_ret['authorizer_info'].get('principal_name')  # 主体名称
                    qrcode_url = authorizer_info_ret['authorizer_info'].get('qrcode_url')  # 二维码
                    head_img = authorizer_info_ret['authorizer_info'].get('head_img')  # 头像
                    nick_name = authorizer_info_ret['authorizer_info'].get('nick_name')  # 头像

                    miniprograminfo = authorizer_info_ret['authorizer_info'].get('MiniProgramInfo')
                    categories = ''
                    if miniprograminfo:
                        categories = authorizer_info_ret['authorizer_info']['MiniProgramInfo'].get('categories')  # 类目

                        if len(categories) != 0:
                            categories = json.dumps(categories)
                        else:
                            categories = ''

                    if original_id:
                        obj = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=authorization_appid)
                        if obj:
                            obj.update(
                                authorization_appid=authorization_appid,  # 授权方appid
                                authorizer_refresh_token=authorizer_refresh_token,  # 刷新的 令牌
                                original_id=original_id,  # 公众号的原始ID
                                verify_type_info=verify_type_info,  # 是否 微信认证

                                principal_name=principal_name,  # 主体名称
                                qrcode_url=qrcode_url,  # 二维码
                                head_img=head_img,  # 头像
                                name=nick_name,  # 昵称
                                service_category=categories,  # 服务类目
                            )
                        print('----------成功获取auth_code和帐号基本信息authorizer_info成功---------->>')
                        response.code = 200
                        response.msg = "成功获取auth_code和帐号基本信息authorizer_info成功"

                        ########################### 公众号设置所属行业 ######################################
                        get_industry_data = {'access_token': authorizer_access_token}

                        api_set_industry_url = 'https://api.weixin.qq.com/cgi-bin/template/api_set_industry'
                        post_industry_data = {
                            "industry_id1": "1",  # IT科技 互联网|电子商务，
                            "industry_id2": "2"
                        }

                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        template_list_ret = s.post(api_set_industry_url, params=get_industry_data, data=json.dumps(post_industry_data))

                        # template_list_ret = requests.post(api_set_industry_url, params=get_industry_data, data=json.dumps(post_industry_data))
                        template_list_ret = template_list_ret.json()
                        errcode = template_list_ret.get('errcode')
                        errmsg = template_list_ret.get('errmsg')

                        print('---- 公众号设置所属行业【返回】 ---->', json.dumps(template_list_ret))

                        # {"errcode": 0, "errmsg": "ok"}

                        if errcode == 0:
                            response.code = 200
                            response.msg = "公众号设置所属行业成功"

                            print('---------授权appid: %s , 公众号设置所属行业 【成功】------------>>' % (authorization_appid))
                        else:
                            response.code = errcode
                            response.msg = errmsg
                            print('---------授权appid: %s , 公众号设置所属行业 【失败】------------>>' % (authorization_appid), errmsg,
                                  '|', errcode)

                        ########### 添加模板ID到该公众号下 ##################
                        # doc https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1433751277
                        # OPENTM202109783	咨询回复消息提醒	IT科技	互联网|电子商务
                        api_add_template_url = 'https://api.weixin.qq.com/cgi-bin/template/api_add_template'

                        post_add_template_data = {
                            "template_id_short": "OPENTM202109783"
                        }

                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        industry_ret = s.post(api_add_template_url, params=get_industry_data,data=json.dumps(post_add_template_data))

                        # industry_ret = requests.post(api_add_template_url, params=get_industry_data,data=json.dumps(post_add_template_data))
                        industry_ret = industry_ret.json()
                        template_id = industry_ret.get('template_id')

                        print('-------- 【公众号】添加模板ID到该账户下 返回 ---->', json.dumps(industry_ret))

                        if errcode == 0:
                            response.code = 200
                            response.msg = "公众号添加模板ID成功"
                            obj.update(template_id=template_id)
                            # {"errcode": 0, "errmsg": "ok", "template_id": "yIqr5W_MVshHlyjZIvEd8Lg0KI-nyrOlsTIWMyX_NME"}
                            print('---------授权appid: %s , 公众号添加模板ID 【成功】------------>>' % (authorization_appid), )

                        else:
                            response.code = errcode
                            response.msg = errmsg
                            print('---------授权appid: %s , 公众号添加模板ID 【失败】------------>>' % (authorization_appid), errmsg,
                                  '|', errcode)




                    else:
                        response.code = 400
                        response.msg = "获取帐号基本信息 authorizer_info信息为空"
                        return JsonResponse(response.__dict__)

                        ######################### end ############################################

                else:
                    print('------ 令牌（authorizer_access_token）为空------>>')
                    response.code = 400
                    response.msg = "令牌 authorizer_access_token 为空"
                    return JsonResponse(response.__dict__)

            return HttpResponse("success")

        # 消息与事件接收URL [授权后实现业务]
        elif oper_type == 'callback':

            print('------- 【消息与事件接收URL】------->>', request.body, "|", app_id)

            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            postdata = request.body.decode(encoding='UTF-8')
            # postdata = request.POST.get('xml')

            xml_tree = ET.fromstring(postdata)
            encrypt = xml_tree.find("Encrypt").text

            three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
            qywx_config_dict = ''
            if three_service_objs:
                three_service_obj = three_service_objs[0]
                qywx_config_dict = three_service_obj.config
                if qywx_config_dict:
                    qywx_config_dict = json.loads(qywx_config_dict)

            appid = qywx_config_dict.get('app_id')
            token = qywx_config_dict.get('token')
            encodingAESKey = qywx_config_dict.get('encodingAESKey')

            # token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
            # encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
            # appid = 'wx6ba07e6ddcdc69b3'

            crypto = WeChatCrypto(token, encodingAESKey, appid)
            decrypted_xml = crypto.decrypt_message(
                postdata,
                msg_signature,
                timestamp,
                nonce
            )

            # decrypt_obj = WXBizMsgCrypt(token, encodingAESKey, appid)
            # ret, decryp_xml = decrypt_obj.DecryptMsg(encrypt, msg_signature, timestamp, nonce)
            print('----- 【公众号】客户发过来的消息 【解密后】xml ---->', decrypted_xml)

            DOMTree = xmldom.parseString(decrypted_xml)
            collection = DOMTree.documentElement
            original_id = collection.getElementsByTagName("ToUserName")[0].childNodes[0].data
            openid = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data
            MsgType = collection.getElementsByTagName("MsgType")[0].childNodes[0].data
            '''
            <xml>
            <ToUserName><![CDATA[gh_21c48bcaa193]]></ToUserName>
            <FromUserName><![CDATA[ob5mL1Q4faFlL2Hv2S43XYKbNO-k]]></FromUserName>
            <CreateTime>1539841157</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[您好！！]]></Content>
            <MsgId>6613567410772340882</MsgId>
            </xml> 
            
            
            <xml><ToUserName><![CDATA[gh_21c48bcaa193]]></ToUserName>
            <FromUserName><![CDATA[ob5mL1Q4faFlL2Hv2S43XYKbNO-k]]></FromUserName>
            <CreateTime>1539827462</CreateTime>
            <MsgType><![CDATA[event]]></MsgType>
            <Event><![CDATA[unsubscribe]]></Event>
            <EventKey><![CDATA[]]></EventKey>
            </xml>
            
            '''

            print('--original_id-->>', original_id)
            print('--MsgType-->>', MsgType)
            print('--openid-->>', openid)

            if MsgType == 'event':  # 事件处理
                Event = collection.getElementsByTagName("Event")[0].childNodes[0].data
                print('--事件Event-->>', Event)
                gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=app_id)
                if gongzhonghao_app_objs:
                    gongzhonghao_app_obj = gongzhonghao_app_objs[0]
                    company_id = gongzhonghao_app_obj.company_id
                    name = gongzhonghao_app_obj.name
                    is_focus_get_redpacket = gongzhonghao_app_obj.is_focus_get_redpacket  # 是否开启了 关注领红包的活动


                    if Event == 'unsubscribe':  # 取消关注
                        objs = models.zgld_customer.objects.filter(openid=openid, user_type=1)

                        print('----- 公众号【取消关注】,看看是谁: 客户：%s | 公众号: %s | 公司ID: %s---->>', name, company_id)
                        objs.update(
                            is_subscribe=0  # 改为取消

                        )

                    elif Event == 'subscribe':  # 关注公众号

                        customer_objs = models.zgld_customer.objects.filter(openid=openid)
                        if customer_objs:
                            customer_id = customer_objs[0].id
                            is_subscribe = customer_objs[0].is_subscribe  #用户是否订阅该公众号
                            is_receive_redPacket = customer_objs[0].is_receive_redPacket  #用户是否订阅该公众号

                        else:
                            obj = models.zgld_customer.objects.create(
                                company_id=company_id,
                                user_type=1,
                                openid=openid
                            )
                            customer_id = obj.id
                            is_subscribe = obj.is_subscribe  # 用户是否订阅该公众号
                            is_receive_redPacket = obj.is_receive_redPacket  # 是否发送过关注红包


                        objs = models.zgld_customer.objects.filter(openid=openid, id=customer_id, user_type=1)

                        user_objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
                            customer_id=customer_id, user__company_id=company_id).order_by('-last_follow_time')


                        if user_objs:
                            user_id = user_objs[0].user_id
                            # customer_username = user_objs[0].customer.username
                            # customer_username = conversion_base64_customer_username_base64(customer_username,customer_id)

                        else:
                            userprofile_objs = models.zgld_userprofile.objects.filter(company_id=company_id,status=1).order_by('?')
                            user_id =   userprofile_objs[0].id
                            # obj_ = models.zgld_user_customer_belonger.objects.create(customer_id=customer_id, user_id=user_id,source=4)
                            # customer_username = obj_.customer.username
                            # customer_username = conversion_base64_customer_username_base64(customer_username, customer_id)

                        ## 发提示给雷达用户
                        if user_id and  is_subscribe == 0: ##没有订阅该公众号
                            gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

                            gongzhonghao_name = ''
                            if gongzhonghao_app_objs:
                                gongzhonghao_name = gongzhonghao_app_objs[0].name

                            data = {}
                            remark = ' 关注了您的公众号【%s】,赶快在通讯录里和Ta沟通吧' % (gongzhonghao_name)

                            print('---- 关注公众号提示 [消息提醒]--->>', remark)
                            data['user_id'] = customer_id
                            data['uid'] = user_id
                            data['action'] = 14
                            action_record(data, remark)  # 此步骤封装到 异步中。

                        if user_id and  is_subscribe == 0: #没有订阅该公众号
                            a_data = {}
                            a_data['customer_id'] = customer_id
                            a_data['user_id'] = user_id
                            a_data['type'] = 'gongzhonghao_template_tishi'  # 简单的公众号模板消息提示。
                            a_data['content'] = json.dumps(
                                {'msg': '终于等到你🌹，感谢您的关注，我是您的专属咨询代表,您现在可以直接给我发消息哦，期待您的回复~' ,'info_type': 1})

                            print('-----企业用户 公众号_模板消息 订阅公众号 json.dumps(a_data)---->>', json.dumps(a_data))
                            tasks.user_send_gongzhonghao_template_msg.delay(a_data)  # 发送【公众号发送模板消息】

                        objs.update(
                            is_subscribe=1,  # 改为关注状态
                            subscribe_time=datetime.datetime.now()
                        )
                        __data = {
                            'openid': openid,
                            'authorizer_appid': app_id,
                            'company_id': company_id,
                            'type': 'get_gzh_user_whole_info',

                        }
                        tasks.get_customer_gongzhonghao_userinfo.delay(__data)

                        if is_focus_get_redpacket and is_receive_redPacket == 0:  # 开启了发红包的活动并且没有得到红包
                            _data = {
                                'user_id': user_id,
                                'company_id': company_id,
                                'customer_id': customer_id,
                            }
                            tasks.user_focus_send_activity_redPacket.delay(_data)  # 异步判断是否下发红包。
                        print('----- 公众号【点击关注】啦, 客户是: %s 【点击关注】公众号: %s | 公司ID: %s---->>', customer_id, name,company_id)


                else:

                    print('------ [公众号]不存在: authorization_appid: %s ----->>', app_id)


            else:
                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

                gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=app_id)
                if gongzhonghao_app_objs:

                    gongzhonghao_app_obj = gongzhonghao_app_objs[0]
                    company_id = gongzhonghao_app_obj.company_id

                    objs = models.zgld_customer.objects.filter(openid=openid, company_id=company_id, user_type=1)
                    if objs:
                        obj = objs[0]
                        customer_id = obj.id

                        Content = ''
                        _content = ''
                        if MsgType == 'text':

                            Content = collection.getElementsByTagName("Content")[0].childNodes[0].data
                            # CreateTime = collection.getElementsByTagName("CreateTime")[0].childNodes[0].data
                            print('-----【公众号】客户发送的内容 Content ---->>', Content)

                            if Content.startswith('T') or Content.startswith('t'):

                                    activity_id = ''
                                    if Content.startswith('t'):
                                        activity_id = int(Content.split('t')[1])
                                    elif Content.startswith('T'):
                                        activity_id = int(Content.split('T')[1])

                                    print('值 activity_id--->',activity_id)
                                    print('值 customer_id--->',customer_id)
                                    print('值 openid--->',openid)

                                    redPacket_objs = models.zgld_activity_redPacket.objects.select_related('article','activity').filter(customer_id=customer_id,activity_id=activity_id)

                                    if redPacket_objs:
                                        redPacket_obj = redPacket_objs[0]
                                        forward_read_count = redPacket_obj.forward_read_count
                                        already_send_redPacket_num = redPacket_obj.already_send_redPacket_num
                                        start_time = redPacket_obj.activity.start_time
                                        end_time = redPacket_obj.activity.end_time
                                        status = redPacket_obj.activity.status

                                        activity_obj = models.zgld_article_activity.objects.get(id=activity_id)
                                        reach_forward_num = activity_obj.reach_forward_num
                                        divmod_ret = divmod(forward_read_count, reach_forward_num)

                                        shoudle_send_num = divmod_ret[0]
                                        yushu = divmod_ret[1]
                                        short_num = reach_forward_num - yushu
                                        now_date_time = datetime.datetime.now()

                                        if status != 3 and  now_date_time >= start_time and now_date_time <= end_time:  # 活动开启并活动在进行中

                                            if forward_read_count >= reach_forward_num:

                                                _content = '转发后阅读人数:【%s】人\n已发红包:【%s】个\n还差【%s】人又能再拿现金红包 \n    转发多多,红包多多🤞🏻,上不封顶,邀请朋友继续助力呦!🤗 ' % (
                                                    forward_read_count, already_send_redPacket_num, short_num)

                                            else:
                                                _content = '转发后阅读人数:【%s】人\n还差【%s】人可立获现金红包,\n    转发多多,红包多多🤞🏻,上不封顶,邀请朋友继续助力呦! 🤗 ' % (
                                                    forward_read_count, short_num)


                                        else:
                                            _content = '此活动已经结束,转发后阅读人数【%s】人,已发红包【%s】个, 请继续关注下次活动哦' % (forward_read_count, already_send_redPacket_num)


                                    else:
                                        _content = '输入查询ID可能有误, 客服已通知技术小哥👨🏻‍💻, 快马加鞭🕙为您解决问题,\n 请您及时关注消息提醒🔔!'

                                    reply = TextReply(content=_content)
                                    reply._data['ToUserName'] = openid
                                    reply._data['FromUserName'] = original_id
                                    xml = reply.render()

                                    print('------ 被动回复消息【加密前】xml -->', xml)

                                    timestamp = str(int(time.time()))
                                    crypto = WeChatCrypto(token, encodingAESKey, appid)
                                    encrypted_xml = crypto.encrypt_message(xml, nonce, timestamp)
                                    print('------ 被动回复消息【加密后】xml------>', encrypted_xml)  ## 加密后的xml 数据

                                    return HttpResponse(encrypted_xml, content_type="application/xml")

                            elif Content.startswith('A') or Content.startswith('a'):

                                objs =  models.zgld_chatinfo.objects.filter(customer_id=customer_id,send_type=4).order_by('-create_date')
                                media_id = ''
                                if objs:
                                    obj = objs[0]
                                    msg_dict = obj.msg
                                    print('--- 1 msg_dict ----->', msg_dict)
                                    # msg_dict = '{"msgtype": "image", "image": {"media_id": "qTvPOX-uZE4xw3RCCC9SsDs3w10jirOb60aSTeX8kfmy2FfM-jKg5INF7bznrdor"}}'

                                    msg_dict =  json.loads(str(msg_dict))

                                    '''
                                        {
                                           "msgtype": "image",
                                            "image":
                                                {
                                                    "media_id": media_id
                                                }
                                        }
                                    '''
                                    print('--- 2  msg_dict ----->',msg_dict)
                                    msgtype = msg_dict.get('msgtype')
                                    if msgtype == 'image':
                                        media_id = msg_dict.get('image').get('media_id')


                                reply = ImageReply(media_id=media_id)
                                reply._data['ToUserName'] = openid
                                reply._data['FromUserName'] = original_id
                                xml = reply.render()

                                print('------ 被动回复消息【加密前】xml -->', xml)

                                timestamp = str(int(time.time()))
                                crypto = WeChatCrypto(token, encodingAESKey, appid)
                                encrypted_xml = crypto.encrypt_message(xml, nonce, timestamp)
                                print('------ 被动回复消息【加密后】xml------>', encrypted_xml)  ## 加密后的xml 数据

                                return HttpResponse(encrypted_xml, content_type="application/xml")



                        if MsgType == 'text' or MsgType == 'voice' or  MsgType == 'image':
                            MediaId = collection.getElementsByTagName("MsgId")[0].childNodes[0].data

                            flow_up_objs = models.zgld_user_customer_belonger.objects.filter(
                                customer_id=customer_id).order_by('-last_follow_time')
                            if flow_up_objs:
                                user_id = flow_up_objs[0].user_id

                                models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                                    userprofile_id=user_id,
                                    customer_id=customer_id,
                                ).update(
                                    is_customer_new_msg=False
                                ) # 把客户标记为自己已经读取了。

                                models.zgld_chatinfo.objects.filter(userprofile_id=user_id, customer_id=customer_id,
                                                                    is_last_msg=True).update(is_last_msg=False)  # 把所有的重置为不是最后一条

                                if  MsgType == 'text':
                                    encodestr = base64.b64encode(Content.encode('utf-8'))
                                    msg = str(encodestr, 'utf-8')
                                    _content = {
                                        'msg': msg,
                                        'info_type': 1
                                    }

                                elif MsgType ==  'image':
                                    PicUrl = collection.getElementsByTagName("PicUrl")[0].childNodes[0].data

                                    print('-----【公众号】客户发送的图片 PicUrl ---->>', PicUrl)
                                    s = requests.session()
                                    s.keep_alive = False  # 关闭多余连接
                                    html = s.get(PicUrl)

                                    # html = requests.get(qrcode_url)

                                    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
                                    filename = "/customer_%s_user_%s_%s.jpg" % (customer_id,user_id, now_time)
                                    file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin','chat') + filename
                                    with open(file_dir, 'wb') as file:
                                        file.write(html.content)

                                    _content = {
                                        'url': file_dir,
                                        'info_type': 4 # 图片
                                    }


                                elif MsgType == 'voice':
                                    # MediaId = collection.getElementsByTagName("MediaId")[0].childNodes[0].data
                                    # Content = '【收到不支持的消息类型，暂无法显示】'
                                    objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                                    if objs:
                                        authorizer_refresh_token = objs[0].authorizer_refresh_token
                                        authorizer_appid = objs[0].authorization_appid
                                        authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)

                                        authorizer_access_token = rc.get(authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                                        three_service_objs = models.zgld_three_service_setting.objects.filter(
                                            three_services_type=2)  # 公众号
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

                                        s = requests.session()
                                        s.keep_alive = False  # 关闭多余连接
                                        url = 'https://api.weixin.qq.com/cgi-bin/media/get'
                                        get_data = {
                                              'access_token' : authorizer_access_token,
                                              'media_id' : MediaId
                                        }
                                        res = s.get(url,params=get_data,stream=True)

                                        now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
                                        filename = "/customer_%s_user_%s_%s.amr" % (customer_id, user_id, now_time) #amr
                                        file_dir = os.path.join('statics', 'zhugeleida', 'voice','gongzhonghao') + filename

                                        # 写入收到的视频数据
                                        with open(file_dir, 'ab') as file:
                                            file.write(res.content)
                                            file.flush()

                                        ###amr2转mp3
                                        print('----- 语音amr 地址 --->>',file_dir)
                                        mp3_file_dir = amr2mp3(file_dir)
                                        if mp3_file_dir == 1:
                                            Content = '【收到不支持的消息类型，暂无法显示】'
                                            encodestr = base64.b64encode(Content.encode('utf-8'))
                                            msg = str(encodestr, 'utf-8')
                                            _content = {
                                                'msg': msg,
                                                'info_type': 1
                                            }
                                        else:
                                            _content = {
                                                'url': mp3_file_dir,
                                                'info_type': 5  #
                                            }


                                content = json.dumps(_content)

                                if MediaId:
                                    chatinfo_objs = models.zgld_chatinfo.objects.filter(msg=MediaId)

                                    if not chatinfo_objs:
                                        obj = models.zgld_chatinfo.objects.create(
                                            content=content,
                                            userprofile_id=user_id,
                                            customer_id=customer_id,
                                            send_type=2
                                        )
                                        obj.msg = MediaId
                                        obj.save()


                                else:

                                    obj = models.zgld_chatinfo.objects.create(
                                        content=content,
                                        userprofile_id=user_id,
                                        customer_id=customer_id,
                                        send_type=2
                                    )


                                if user_id and customer_id:  # 发送的文字消息
                                    remark = ': %s' % (Content)

                                    data = {
                                        'action': 0,  # 代表发送客户聊天信息
                                        'uid': user_id,
                                        'user_id': customer_id
                                    }
                                    action_record(data, remark)

                                redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                                redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)
                                redis_user_query_info_key = 'message_user_id_{uid}_info_num'.format(
                                    uid=user_id)  # 小程序发过去消息,雷达用户的key 消息数量发生变化
                                redis_user_query_contact_key = 'message_user_id_{uid}_contact_list'.format(
                                    uid=user_id)  # 小程序发过去消息,雷达用户的key 消息列表发生变化

                                ##
                                rc.set(redis_customer_id_key, False)     # 说明 公众号已经获取过用户发送给他的消息。标记为已读。
                                rc.set(redis_user_id_key, True)          # 触发雷达的循环，让其获取公众号发出去的消息
                                rc.set(redis_user_query_info_key, True)  # 代表 雷达用户 消息数量发生了变化
                                rc.set(redis_user_query_contact_key, True)  # 代表 雷达用户 消息列表的数量发生了变化


                            response.code = 200
                            response.msg = 'send msg successful'



                    else:
                        print('------ [公众号]客户不存在: openid: %s |公司ID: %s----->>', openid, company_id)


                else:
                    print('------ [公众号]不存在: authorization_appid: %s ----->>', app_id)


        return HttpResponse("success")


## 生成接入流程控制页面
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def gzh_auth_process(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        user_id = request.GET.get('user_id')

        userprofile_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
        obj = models.zgld_gongzhonghao_app.objects.filter(company_id=userprofile_obj.company_id)

        if not obj:
            response.code = 200
            response.msg = "请求成功。请先填写步骤1 app_id信息"
            response.data = {
                'step': 1
            }

        else:
            authorization_appid = obj[0].authorization_appid  # 授权方appid
            verify_type_info = obj[0].verify_type_info
            authorizer_refresh_token = obj[0].authorizer_refresh_token
            name = obj[0].name
            principal_name = obj[0].principal_name
            head_img = obj[0].head_img
            service_category = obj[0].service_category
            is_open_comment = obj[0].is_open_comment
            is_open_comment_text = obj[0].get_is_open_comment_display()

            if not authorization_appid:  # 没有App ID，首先填写
                response.code = 200
                response.msg = "请求成功。请先进行步骤1"
                response.data = {
                    'step': 1
                }


            elif not authorizer_refresh_token:  # 没有通过授权

                response.code = 200
                response.msg = "请求成功.请先进行步骤2"
                response.data = {
                    'step': 2,
                    'ret_data': {
                        'authorization_appid': authorization_appid,

                    }
                }

            elif authorizer_refresh_token and not name:
                response.code = 200
                response.msg = "请求成功.请先进行步骤3"
                response.data = {
                    'step': 3,
                    'ret_data': {
                        'authorization_appid': authorization_appid
                    }
                }
            elif authorizer_refresh_token and name:  # 授权通过以及填写信息完毕展示授权完整信息。

                response.data = {
                    'step': '',
                    'ret_data': {
                        'authorization_appid': authorization_appid,  # 授权方appid
                        'name': name,  # 公众号名称
                        'principal_name': principal_name,  # 公众号主体名称
                        'head_img': head_img,  # 授权方头像
                        'verify_type_info': verify_type_info,  # 微信认证是否通过. True 为认证通过，Falsew为认证通过
                        'service_category': service_category,  # 服务类目
                        'is_open_comment' : is_open_comment,
                        'is_open_comment_text' : is_open_comment_text
                    }
                }
                response.code = 200
                response.msg = "请求成功"

        return JsonResponse(response.__dict__)


    elif request.method == "POST":
        pass

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def gzh_auth_process_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 修改更新 original_id
        if oper_type == 'app_id':

            forms_obj = open_weixin_gongzhonghao_verify.UpdateIDForm(request.POST)
            if forms_obj.is_valid():
                authorization_appid = request.POST.get('authorization_appid').strip()

                print("验证通过")
                user_id = request.GET.get('user_id')
                user_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
                company_id = user_obj.company_id
                objs = models.zgld_gongzhonghao_app.objects.filter(user_id=user_id)
                if objs:
                    objs.update(
                        authorization_appid=authorization_appid,
                        company_id=company_id
                    )
                else:
                    models.zgld_gongzhonghao_app.objects.create(
                        user_id=user_id,
                        company_id=company_id,
                        authorization_appid=authorization_appid,

                    )
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 更新授权修改的信息
        elif oper_type == 'info':

            forms_obj = open_weixin_gongzhonghao_verify.UpdateInfoForm(request.POST)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                name = forms_obj.cleaned_data.get('name')  # 公众号名称
                head_img = forms_obj.cleaned_data.get('head_img')  # 头像
                introduce = forms_obj.cleaned_data.get('introduce')  # 介绍
                service_category = forms_obj.cleaned_data.get('service_category')  # 服务类目

                objs = models.zgld_gongzhonghao_app.objects.filter(user_id=user_id)
                if objs:
                    objs.update(
                        name=name,
                        head_img=head_img,
                        introduce=introduce,
                        service_category=service_category
                    )

                response.code = 200
                response.msg = "修改成功"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        ## 公众号绑定微信
        elif oper_type == 'gzh_authorization_binding_xcx':
            user_id = request.GET.get('user_id')

            company_id = request.POST.get('company_id')
            appid = request.POST.get('appid')             #小程序appid

            gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(authorization_appid=appid)
            print('------ POST ---->>',request.POST)

            if gongzhonghao_app_objs:

                if xiaochengxu_app_objs:
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    gongzhonghao_app_obj = gongzhonghao_app_objs[0]

                    authorizer_appid = gongzhonghao_app_obj.authorization_appid
                    authorizer_refresh_token = gongzhonghao_app_obj.authorizer_refresh_token

                    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                    qywx_config_dict = ''
                    if three_service_objs:
                        three_service_obj = three_service_objs[0]
                        qywx_config_dict = three_service_obj.config
                        if qywx_config_dict:
                            qywx_config_dict = json.loads(qywx_config_dict)


                    app_id = qywx_config_dict.get('app_id')
                    app_secret = qywx_config_dict.get('app_secret')

                    authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)

                    authorizer_access_token = rc.get(authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                    data = {
                        'key_name': authorizer_access_token_key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid,
                        'app_id': app_id,          # 查看诸葛雷达_公众号的 appid
                        'app_secret': app_secret   # 查看诸葛雷达_公众号的AppSecret
                    }

                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = authorizer_access_token_result.data


                    url = 'https://api.weixin.qq.com/cgi-bin/wxopen/wxamplink'
                    get_wx_info_data = {
                        'access_token' : authorizer_access_token
                    }
                    post_wx_info_data = {
                        "appid": appid, # 小程序appID
                        "notify_users": 1,
                        "show_profile": 1,
                    }

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    authorizer_info_ret = s.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))

                    authorizer_info_ret = authorizer_info_ret.json()
                    print('---------- 公众号 关联小程序 接口返回 ----------------->', json.dumps(authorizer_info_ret))
                    # {"errcode": 89015, "errmsg": "has linked wxa hint: [Bhrtpa00391975]"}

                    errmsg = authorizer_info_ret.get('errmsg')
                    errcode = authorizer_info_ret.get('errcode')

                    if errmsg == 'ok' or errcode == 89015:
                        introduce_list = gongzhonghao_app_obj.introduce
                        introduce_list =  json.loads(introduce_list)
                        introduce_list.append(appid)

                        gongzhonghao_app_objs.update(
                            introduce=json.dumps(introduce_list),  # 服务类目
                        )
                        print('--------- 公众号 【成功】关联小程序---------->>')

                        msg = "成功关联"
                        if errcode == 89015:
                            msg = '公众号已经绑定过小程序'

                        response.code = 200
                        response.msg = msg

                    else:

                        print('--------- 公众号 【失败】关联小程序---------->>',company_id,"|",errmsg)
                        response.code = errcode
                        response.msg = errmsg


                else:
                    response.msg = '小程序不存在'
                    response.code = 302
            else:
                response.msg = '公众号不存在'
                response.code = 302


        ## 解除已关联的小程序
        elif oper_type == 'gzh_authorization_unlock_xcx':
            user_id = request.GET.get('user_id')
            company_id = request.POST.get('company_id')
            appid = request.POST.get('appid')  # 小程序appid

            gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(authorization_appid=appid)

            if gongzhonghao_app_objs:

                if  xiaochengxu_app_objs:

                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    gongzhonghao_app_obj = gongzhonghao_app_objs[0]
                    xiaochengxu_app_obj = xiaochengxu_app_objs[0]
                    authorizer_appid = gongzhonghao_app_obj.authorization_appid
                    authorizer_refresh_token = gongzhonghao_app_obj.authorizer_refresh_token

                    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                    qywx_config_dict = ''
                    if three_service_objs:
                        three_service_obj = three_service_objs[0]
                        qywx_config_dict = three_service_obj.config
                        if qywx_config_dict:
                            qywx_config_dict = json.loads(qywx_config_dict)

                    app_id = qywx_config_dict.get('app_id')
                    app_secret = qywx_config_dict.get('app_secret')

                    authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)

                    authorizer_access_token = rc.get(
                        authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                    data = {
                        'key_name': authorizer_access_token_key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid,
                        'app_id': app_id,  # 查看诸葛雷达_公众号的 appid
                        'app_secret': app_secret  # 查看诸葛雷达_公众号的AppSecret
                    }

                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = authorizer_access_token_result.data

                    url = 'https://api.weixin.qq.com/cgi-bin/wxopen/wxampunlink'
                    get_wx_info_data = {
                        'access_token': authorizer_access_token
                    }
                    post_wx_info_data = {
                        "appid": appid,  # 小程序appID

                    }

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    authorizer_info_ret = s.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))

                    authorizer_info_ret = authorizer_info_ret.json()
                    print('---------- 公众号 关联小程序 接口返回 ----------------->', json.dumps(authorizer_info_ret))

                    errmsg = authorizer_info_ret.get('errmsg')
                    errcode = authorizer_info_ret.get('errcode')

                    if errmsg == 'ok':
                        introduce_list = gongzhonghao_app_obj.introduce
                        introduce_list = json.loads(introduce_list)
                        introduce_list.remove(appid)

                        gongzhonghao_app_objs.update(
                            introduce=json.dumps(introduce_list),  # 服务类目
                        )
                        print('--------- 公众号 【解绑】关联小程序---------->>')
                        response.code = 200
                        response.msg = "成功解绑关联小程序"

                    else:
                        response.code = errcode
                        response.msg = '解绑失败'
                        print('--------- 公众号 【失败】解绑小程序---------->>',company_id,errcode)

                else:
                    response.msg = '小程序不存在'
                    response.code = 302

            else:
                response.msg = '公众号不存在'
                response.code = 302


    elif request.method == "GET":

        #获取公众号基本信息
        if oper_type == 'gzh_get_authorizer_info':
            user_id = request.GET.get('user_id')
            company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            app_obj = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            if app_obj:
                authorizer_appid = app_obj[0].authorization_appid
                get_wx_info_data = {}
                post_wx_info_data = {}

                three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
                qywx_config_dict = ''
                if three_service_objs:
                    three_service_obj = three_service_objs[0]
                    qywx_config_dict = three_service_obj.config
                    if qywx_config_dict:
                        qywx_config_dict = json.loads(qywx_config_dict)

                app_id = qywx_config_dict.get('app_id')
                app_secret = qywx_config_dict.get('app_secret')


                # app_id = 'wx6ba07e6ddcdc69b3'  # 查看诸葛雷达_公众号的 appid

                data_dict = {
                    'app_id': app_id,                     # 查看诸葛雷达_公众号的 appid
                    'app_secret':app_secret  # 查看诸葛雷达_公众号的AppSecret
                }

                component_access_token_ret = create_component_access_token(data_dict)
                component_access_token = component_access_token_ret.data.get('component_access_token')
                post_wx_info_data['component_appid'] = app_id
                post_wx_info_data['authorizer_appid'] = authorizer_appid
                get_wx_info_data['component_access_token'] = component_access_token

                url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'

                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                authorizer_info_ret = s.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))

                # authorizer_info_ret = requests.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
                authorizer_info_ret = authorizer_info_ret.json()
                print('---------- 公众号帐号基本信息authorizer_info 返回 ----------------->', json.dumps(authorizer_info_ret))
                original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info']['id'] == 0 else False
                # ---->预留代码
                principal_name = authorizer_info_ret['authorizer_info'].get('principal_name')  # 主体名称
                qrcode_url = authorizer_info_ret['authorizer_info'].get('qrcode_url')  # 二维码
                head_img = authorizer_info_ret['authorizer_info'].get('head_img')  # 头像
                nick_name = authorizer_info_ret['authorizer_info'].get('nick_name')  # 头像

                miniprograminfo = authorizer_info_ret['authorizer_info'].get('MiniProgramInfo')
                categories = ''
                if miniprograminfo:
                    categories = authorizer_info_ret['authorizer_info']['MiniProgramInfo'].get('categories')  # 类目

                    if len(categories) != 0:
                        categories = json.dumps(categories)
                    else:
                        categories = ''
                _qrcode_url = app_obj[0].qrcode_url

                if  _qrcode_url: ## 有二维码
                    qrcode_url = _qrcode_url


                if original_id:
                    app_obj.update(
                        # authorization_appid=authorization_appid,  # 授权方appid
                        # authorizer_refresh_token=authorizer_refresh_token,  # 刷新的 令牌
                        original_id=original_id,  # 公众号的原始ID
                        verify_type_info=verify_type_info,  # 是否 微信认证

                        principal_name=principal_name,  # 主体名称
                        qrcode_url=qrcode_url,  # 二维码
                        head_img=head_img,  # 头像
                        name=nick_name,  # 昵称
                        service_category=categories,  # 服务类目
                    )
                    print('----------成功获取公众号帐号基本信息authorizer_info---------->>')
                    response.code = 200
                    response.msg = "成功获取公众号帐号基本信息authorizer_info"


            else:
                response.msg = '公众号不存在'
                response.code = 302

        # 查询已经绑定的小程序
        elif oper_type == 'query_already_bind_xcx':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)


            if gongzhonghao_app_objs:

                gongzhonghao_app_obj =gongzhonghao_app_objs[0]
                introduce_list = gongzhonghao_app_obj.introduce
                introduce_list =  json.loads(introduce_list)

                objs =   models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)

                ret_data = []
                status = '未授权'
                for obj in objs:
                    authorization_appid = obj.authorization_appid
                    print('--- authorization_appid ---->>',authorization_appid,introduce_list)
                    if authorization_appid in introduce_list:
                        status =  '已授权'

                    dict = {
                        'id' : obj.id,
                        'name' : obj.name,
                        'appid' : obj.authorization_appid,
                        'principal_name' : obj.principal_name,
                        'status' : status
                    }
                    ret_data.append(dict)

                response.data = {
                    'ret_data' : ret_data
                }
                response.code = 200
                response.msg = "获取成功"



            else:
                response.msg = '公众号不存在'
                response.code = 302

    else:

        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


## 生成请 第三方平台 自己 的component_access_token
def create_component_access_token(data):
    response = Response.ResponseObj()
    app_id = data.get('app_id')
    app_secret = data.get('app_secret')
    # app_id = 'wx6ba07e6ddcdc69b3'                    # 查看诸葛雷达_公众号的 appid
    # app_secret = '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    ComponentVerifyTicket_key_name = 'ComponentVerifyTicket_%s' % (app_id)

    component_verify_ticket = rc.get(ComponentVerifyTicket_key_name)

    post_component_data = {
        'component_appid': app_id,
        'component_appsecret': app_secret,
        'component_verify_ticket': component_verify_ticket
    }

    component_access_token_key_name = 'component_access_token_%s' % (app_id)
    token_ret = rc.get(component_access_token_key_name)
    print('----- Redis 里存储的 component_access_token ---->>', token_ret)
    print('---- post_component_data ---->>', json.dumps(post_component_data))
    if not token_ret:

        post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        component_token_ret = s.post(post_component_url, data=json.dumps(post_component_data))

        # component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
        print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
        component_token_ret = component_token_ret.json()
        access_token = component_token_ret.get('component_access_token')

        if access_token:
            token_ret = access_token
            rc.set(component_access_token_key_name, access_token, 7000)
        else:
            response.code = 400
            response.msg = "-------- 获取第三方平台 component_token_ret 返回错误 ------->"
            return JsonResponse(response.__dict__)

    response.data = {
        'component_access_token': token_ret,

    }
    response.code = 200

    return response


## 生成 公众号-authorizer_access_token
def create_authorizer_access_token(data):
    response = Response.ResponseObj()

    authorizer_appid = data.get('authorizer_appid')  # 授权方appid
    authorizer_refresh_token = data.get('authorizer_refresh_token')
    key_name = data.get('key_name')
    app_id = data.get('app_id')  # 三方平台的appid
    app_secret = data.get('app_secret')

    # app_id = 'wx67e2fde0f694111c'
    # app_secret = '4a9690b43178a1287b2ef845158555ed'
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    data_dict = {
        'app_id': app_id,  # 查看诸葛雷达_公众号的 appid
        'app_secret': app_secret,  # 查看诸葛雷达_公众号的AppSecret
    }

    response_ret = create_component_access_token(data_dict)
    component_access_token = response_ret.data.get('component_access_token')

    get_auth_token_data = {
        'component_access_token': component_access_token
    }

    post_auth_token_data = {
        'component_appid': app_id,
        'authorizer_appid': authorizer_appid,
        'authorizer_refresh_token': authorizer_refresh_token
    }

    authorizer_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    authorizer_info_ret = s.post(authorizer_token_url, params=get_auth_token_data, data=json.dumps(post_auth_token_data))


    # authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data, data=json.dumps(post_auth_token_data))
    authorizer_info_ret = authorizer_info_ret.json()

    print('-------获取（刷新）授权【公众号】的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)

    authorizer_access_token = authorizer_info_ret.get('authorizer_access_token')
    authorizer_refresh_token = authorizer_info_ret.get('authorizer_refresh_token')

    if authorizer_access_token and authorizer_refresh_token:
        rc.set(key_name, authorizer_access_token, 7000)
        response.code = 200
        response.msg = "获取令牌成功"
        response.data = authorizer_access_token

        # response.data = {
        #     'authorizer_access_token' : authorizer_access_token
        # }
        print('------ 获取【公众号】令牌（authorizer_access_token）成功------>>', authorizer_access_token)

    else:
        print('------ 获取【公众号】令牌（authorizer_access_token）为空------>>')
        response.code = 400
        response.msg = "获取【公众号】令牌 authorizer_access_token为空"
        return JsonResponse(response.__dict__)

    return response


## 把amr2转成mp3
def amr2mp3(amr_path, mp3_path=None):
    path, name = os.path.split(amr_path)
    if name.split('.')[-1] != 'amr':
        print(' ----- amr file ----->')
        return 1
    if mp3_path is None or mp3_path.split('.')[-1] != 'mp3':
        mp3_path = os.path.join(path, name.split('.')[0] + '.mp3')

    error = subprocess.call(['/usr/bin/ffmpeg', '-i', amr_path, mp3_path])
    print('------ subprocess 返回码 -------->>', error)
    if error:
        return 1

    print(' ---- 转码成功 mp3地址 success ----->>',mp3_path)

    return mp3_path