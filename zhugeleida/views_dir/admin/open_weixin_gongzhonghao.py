from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
import xml.dom.minidom as xmldom
from zhugeapi_celery_project import tasks
import time

import json
import redis
import xml.etree.cElementTree as ET
from django import forms


## 第三方平台接入
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

                token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
                encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
                appid = 'wx6ba07e6ddcdc69b3'

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

                app_id = 'wx6ba07e6ddcdc69b3'
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

                access_token_ret = requests.post(access_token_url, params=get_access_token_data,
                                                 data=json.dumps(post_access_token_data))
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
                    authorizer_info_ret = requests.post(url, params=get_wx_info_data,
                                                        data=json.dumps(post_wx_info_data))

                    print('----------- 获取_公众号授权方的authorizer_info信息 返回 ------------->',
                          json.dumps(authorizer_info_ret.json()))
                    authorizer_info_ret = authorizer_info_ret.json()
                    original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                    verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info'][
                                                   'id'] == 0 else False
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
                        template_list_ret = requests.post(api_set_industry_url, params=get_industry_data,
                                                          data=json.dumps(post_industry_data))
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

                        industry_ret = requests.post(api_add_template_url, params=get_industry_data,
                                                     data=json.dumps(post_add_template_data))
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

        # 生成接入的二维码
        elif oper_type == "create_grant_url":
            user_id = request.GET.get('user_id')
            app_id = 'wx6ba07e6ddcdc69b3'  # 诸葛雷达_公众号 appid
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            data_dict = {
                'app_id': 'wx6ba07e6ddcdc69b3',  # 查看诸葛雷达_公众号的 appid
                'app_secret': '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
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

            if not exist_pre_auth_code:
                pre_auth_code_url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'
                pre_auth_code_ret = requests.post(pre_auth_code_url, params=get_pre_auth_data,
                                                  data=json.dumps(post_pre_auth_data))
                pre_auth_code_ret = pre_auth_code_ret.json()
                pre_auth_code = pre_auth_code_ret.get('pre_auth_code')
                print('------ 获取第三方平台 pre_auth_code 预授权码 ----->', pre_auth_code_ret)
                if pre_auth_code:
                    rc.set(pre_auth_code_key_name, pre_auth_code, 1600)
                else:
                    response.code = 400
                    response.msg = "--------- 获取第三方平台 pre_auth_code预授权码 返回错误 ------->"
                    return JsonResponse(response.__dict__)
            else:
                pre_auth_code = exist_pre_auth_code

            # 生成授权链接
            redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/admin/#/empower/empower_xcx/'
            # get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=2' % (app_id, pre_auth_code, redirect_uri) #授权注册页面扫码授权
            get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=3' % (
            app_id, pre_auth_code, redirect_uri)  # auth_type=3 表示公众号和小程序都展示
            pre_auth_code_url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?' + get_bind_auth_data
            response.code = 200
            response.msg = '生成【授权链接】成功'
            response.data = pre_auth_code_url

        return JsonResponse(response.__dict__)


## 第三方平台接入
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

                token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
                encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
                appid = 'wx6ba07e6ddcdc69b3'

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

                app_id = 'wx6ba07e6ddcdc69b3'
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

                access_token_ret = requests.post(access_token_url, params=get_access_token_data,
                                                 data=json.dumps(post_access_token_data))
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
                    authorizer_info_ret = requests.post(url, params=get_wx_info_data,
                                                        data=json.dumps(post_wx_info_data))

                    print('----------- 获取_公众号授权方的authorizer_info信息 返回 ------------->',
                          json.dumps(authorizer_info_ret.json()))
                    authorizer_info_ret = authorizer_info_ret.json()
                    original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                    verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info'][
                                                   'id'] == 0 else False
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
                        template_list_ret = requests.post(api_set_industry_url, params=get_industry_data,
                                                          data=json.dumps(post_industry_data))
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

                        industry_ret = requests.post(api_add_template_url, params=get_industry_data,
                                                     data=json.dumps(post_add_template_data))
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

            xml_tree = ET.fromstring(postdata)
            encrypt = xml_tree.find("Encrypt").text
            token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
            encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
            appid = 'wx6ba07e6ddcdc69b3'

            decrypt_obj = WXBizMsgCrypt(token, encodingAESKey, appid)

            ret, decryp_xml = decrypt_obj.DecryptMsg(encrypt, msg_signature, timestamp, nonce)

            DOMTree = xmldom.parseString(decryp_xml)
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

                    objs = models.zgld_customer.objects.filter(openid=openid, company_id=company_id, user_type=1)
                    if objs:
                        customer_id = objs[0].id

                        if Event == 'unsubscribe':  # 取消关注
                            print('----- 公众号【取消关注】,看看是谁: 客户：%s | 公众号: %s | 公司ID: %s---->>', objs[0].id, name,
                                  company_id)
                            objs.update(
                                is_subscribe=0  # 改为取消
                            )

                        elif Event == 'subscribe':  # 关注公众号

                            print('----- 公众号【点击关注】啦, 客户是: %s 【点击关注】公众号: %s | 公司ID: %s---->>', customer_id, name,
                                  company_id)
                            objs.update(
                                is_subscribe=1  # 改为关注状态
                            )

                            if is_focus_get_redpacket:  # 开启了
                                _data = {
                                    'company_id': company_id,
                                    'customer_id': customer_id,
                                }
                                tasks.user_focus_send_activity_redPacket.delay(_data)  # 异步判断是否下发红包。

                    else:

                        print('------ [公众号]客户不存在: openid: %s |公司ID: %s----->>', openid, company_id)

                else:

                    print('------ [公众号]不存在: authorization_appid: %s ----->>', app_id)

            elif MsgType == 'text':
                Content = collection.getElementsByTagName("Content")[0].childNodes[0].data
                MsgId = collection.getElementsByTagName("MsgId")[0].childNodes[0].data
                CreateTime = collection.getElementsByTagName("CreateTime")[0].childNodes[0].data
                print('--内容Content-->>', Content)

                gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(authorization_appid=app_id)
                if gongzhonghao_app_objs:
                    gongzhonghao_app_obj = gongzhonghao_app_objs[0]
                    company_id = gongzhonghao_app_obj.company_id
                    name = gongzhonghao_app_obj.name

                    objs = models.zgld_customer.objects.filter(openid=openid, company_id=company_id, user_type=1)
                    if objs:
                        obj = objs[0]
                        customer_id = obj.id

                        import time
                        createtime = int(time.time())
                        content = '嗨,您好~ \n 丫挺的,欢迎您参加活动,刚才那谁查看了您转发的文章,还有2个人查看的话，我就给你发个大红包了，骗你是个小狗。'

                        # res_msg = '<xml><ToUserName><![CDATA[{openid}]]></ToUserName><FromUserName><![CDATA[{original_id}]]></FromUserName><CreateTime>{createtime}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{content}]]></Content></xml>'.format(
                        #     openid=openid, original_id=original_id, createtime=createtime, content='YYYY')

                        res_msg = "<xml>" \
                                  "<ToUserName>< ![CDATA[{openid}]]></ToUserName>" \
                                  "<FromUserName>< ![CDATA[{original_id}]]></FromUserName>" \
                                  "<CreateTime>{createtime}</CreateTime>" \
                                  "<MsgType>< ![CDATA[text]]></MsgType>" \
                                  "<Content>< ![CDATA[{content}]]></Content>" \
                                  "</xml>"\
                            .format(
                                openid=openid,
                                original_id=original_id,
                                createtime=createtime,
                                content='YYYY'
                            )


                        # print('----- 【加密前】的 消息---->>', res_msg)
                        # ret, encrypt_xml = decrypt_obj.EncryptMsg(res_msg, nonce)
                        # print('-----ret, encrypt_xml----->>', ret, encrypt_xml)
                        # print('-------【加密后】的 消息---->>', encrypt_xml)

                        # return HttpResponse(encrypt_xml)
                        print('res_msg -->', res_msg)
                        return HttpResponse(res_msg)

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

        if oper_type == 'app_id':  # 修改更新 original_id

            forms_obj = UpdateIDForm(request.POST)
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

        elif oper_type == 'info':  # 更新授权修改的信息。

            forms_obj = UpdateInfoForm(request.POST)
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

    elif request.method == 'GET':

        ###获取公众号基本信息
        if oper_type == 'gzh_get_authorizer_info':
            user_id = request.GET.get('user_id')
            company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            app_obj = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            if app_obj:
                authorizer_appid = app_obj[0].authorization_appid
                get_wx_info_data = {}
                post_wx_info_data = {}
                app_id = 'wx6ba07e6ddcdc69b3'  # 查看诸葛雷达_公众号的 appid

                data_dict = {
                    'app_id': 'wx6ba07e6ddcdc69b3',  # 查看诸葛雷达_公众号的 appid
                    'app_secret': '0bbed534062ceca2ec25133abe1eecba'  # 查看诸葛雷达_公众号的AppSecret
                }

                component_access_token_ret = create_component_access_token(data_dict)
                component_access_token = component_access_token_ret.data.get('component_access_token')
                post_wx_info_data['component_appid'] = app_id
                post_wx_info_data['authorizer_appid'] = authorizer_appid
                get_wx_info_data['component_access_token'] = component_access_token

                url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
                authorizer_info_ret = requests.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
                authorizer_info_ret = authorizer_info_ret.json()
                print('---------- 公众号帐号基本信息authorizer_info 返回 ----------------->', json.dumps(authorizer_info_ret))
                original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info'][
                                               'id'] == 0 else False
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
        component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
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
    authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data,
                                        data=json.dumps(post_auth_token_data))
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


class UpdateIDForm(forms.Form):
    authorization_appid = forms.CharField(
        required=True,
        error_messages={
            'required': "authorization_appid 不能为空"
        }
    )


class UpdateInfoForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "公众号名称不能为空"
        }
    )

    head_img = forms.CharField(
        required=True,
        error_messages={
            'required': "公众号头像不能为空"
        }
    )
    introduce = forms.CharField(
        required=False,
        error_messages={
            'required': "公众号头像不能为空"
        }
    )

    service_category = forms.CharField(
        required=True,
        error_messages={
            'required': "服务类目不能为空"
        }
    )
