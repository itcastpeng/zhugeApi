from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
import json
import redis
import xml.etree.cElementTree as ET


@csrf_exempt
def open_weixin(request, oper_type):
    if request.method == "POST":
        response = Response.ResponseObj()
        if oper_type == 'tongzhi':

            print('------ 第三方   request.body------>>', request.body.decode(encoding='UTF-8'))

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
                appid = 'wx67e2fde0f694111c'

                decrypt_obj = WXBizMsgCrypt(token, encodingAESKey, appid)
                ret, decryp_xml = decrypt_obj.DecryptMsg(encrypt, msg_signature, timestamp, nonce)

                decryp_xml_tree = ET.fromstring(decryp_xml)
                ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text

                print('----ret -->', ret)
                print('-----decryp_xml -->', decryp_xml)

                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                # rc.get('ComponentVerifyTicket')

                if ret == 0:
                    rc.set('ComponentVerifyTicket', ComponentVerifyTicket, 10000)
                    print('--------授权公众号消息解密 ComponentVerifyTicket--------->>', ComponentVerifyTicket)

                else:
                    response.code = ret
                    response.msg = "-------- 授权公众号消息解密  ------->"
                    return JsonResponse(response.__dict__)

            except AttributeError as e:
                auth_code = decryp_xml_tree.find('AuthorizationCode').text
                authorization_appid = decryp_xml_tree.find('AuthorizerAppid').text       # authorizer_appid 授权方 appid

                user_id = request.sesson.get('user_id')
                app_id = 'wx67e2fde0f694111c'
                print('------ 授权码（authorization_code）------>> userId',user_id, '|',request.GET.get('auth_code'))

                if auth_code:
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    # exist_auth_code = rc.get('auth_code')
                    rc.set('auth_code', auth_code, 3400)
                    print("---------- 成功获取授权码auth_code --------->>", auth_code)

                else:
                    print('------ 授权码（authorization_code）为空------>>')
                    response.code = 400
                    response.msg = "授权码authorization_code为空"
                    return JsonResponse(response.__dict__)

                get_access_token_data = {}
                post_access_token_data = {}
                component_access_token = rc.get('component_access_token')
                access_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
                get_access_token_data['component_access_token'] = component_access_token
                post_access_token_data['component_appid'] = app_id
                post_access_token_data['authorization_code'] = auth_code

                access_token_ret = requests.post(access_token_url, params=get_access_token_data,
                                                 data=json.dumps(post_access_token_data))
                access_token_ret = access_token_ret.json()
                print('--------- 获取令牌 authorizer_access_token authorizer_refresh_token 返回---------->>',access_token_ret)
                authorizer_access_token = access_token_ret.get('authorizer_access_token')
                authorizer_refresh_token = access_token_ret.get('authorizer_refresh_token')
                authorizer_appid = access_token_ret.get('authorizer_appid')

                if authorizer_access_token and authorizer_refresh_token:

                    rc.set('authorizer_access_token', authorizer_access_token, 7000)

                    user_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
                    company_id = user_obj.company_id
                    obj = models.zgld_xiaochengxu_app.objects.filter(user_id=user_id,company_id=company_id)
                    if obj:
                        obj.update(
                            authorization_appid=authorization_appid,
                            authorizer_refresh_token=authorizer_refresh_token
                        )

                    else:

                        models.zgld_xiaochengxu_app.objects.create(
                            user_id=user_id,
                            company_id=company_id,
                            authorization_appid = authorization_appid,
                            authorizer_refresh_token = authorizer_refresh_token
                        )


                    get_wx_info_data = {}
                    post_wx_info_data = {}
                    post_wx_info_data['component_appid'] = app_id
                    post_wx_info_data['authorizer_appid'] = authorizer_appid
                    get_wx_info_data['component_access_token'] = component_access_token
                    url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
                    authorizer_info_ret = requests.post(url, params=get_wx_info_data,
                                                        data=json.dumps(post_wx_info_data))

                    print('----------- 获取小程序授权方的authorizer_info信息 返回 ------------->', authorizer_info_ret.json())
                    response.code = 200
                    response.msg = "成功获取auth_code和authorizer_info信息"


                else:
                    print('------ 令牌（authorizer_access_token）为空------>>')
                    response.code = 400
                    response.msg = "令牌 authorizer_access_token 为空"
                    return JsonResponse(response.__dict__)


            return HttpResponse("success")


        elif oper_type == "create_grant_url":
            user_id = request.GET.get('user_id')
            request.session['user_id'] = user_id
            print('----request.session userId--->',request.session.get('user_id'))

            app_id = 'wx67e2fde0f694111c'
            app_secret = '4a9690b43178a1287b2ef845158555ed'

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            post_component_data = {}
            post_pre_auth_data = {}
            get_pre_auth_data = {}
            get_auth_info_data = {}
            post_auth_info_data = {}

            post_component_data['component_appid'] = app_id
            post_component_data['component_appsecret'] = app_secret

            component_verify_ticket = rc.get('ComponentVerifyTicket')

            post_component_data['component_verify_ticket'] = component_verify_ticket

            token_ret = rc.get('component_access_token')

            print('--- Redis 里存储的 component_access_token---->>', token_ret)

            if not token_ret:
                post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
                component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
                print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
                component_token_ret = component_token_ret.json()
                access_token = component_token_ret.get('component_access_token')
                if access_token:
                    get_pre_auth_data['component_access_token'] = access_token
                    rc.set('component_access_token', access_token, 7000)
                else:
                    response.code = 400
                    response.msg = "-------- 获取第三方平台 component_token_ret 返回错误 ------->"
                    return JsonResponse(response.__dict__)
            else:
                get_pre_auth_data['component_access_token'] = token_ret

            post_pre_auth_data['component_appid'] = app_id

            exist_pre_auth_code = rc.get('pre_auth_code')

            if not exist_pre_auth_code:
                pre_auth_code_url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'
                pre_auth_code_ret = requests.post(pre_auth_code_url, params=get_pre_auth_data,
                                                  data=json.dumps(post_pre_auth_data))
                pre_auth_code_ret = pre_auth_code_ret.json()
                pre_auth_code = pre_auth_code_ret.get('pre_auth_code')
                print('------ 获取第三方平台 pre_auth_code 预授权码 ----->', pre_auth_code_ret)
                if pre_auth_code:
                    rc.set('pre_auth_code', pre_auth_code, 1600)
                else:
                    response.code = 400
                    response.msg = "--------- 获取第三方平台 pre_auth_code预授权码 返回错误 ------->"
                    return JsonResponse(response.__dict__)
            else:
                pre_auth_code = exist_pre_auth_code

            # 生成授权链接

            redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/admin/#/empower/empower_xcx/'
            get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=2' % (
                                    app_id, pre_auth_code, redirect_uri,)
            pre_auth_code_url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?' + get_bind_auth_data
            response.code = 200
            response.msg = '生成【授权链接】成功'
            response.data = pre_auth_code_url

        return JsonResponse(response.__dict__)


    elif request.method == "GET":
        response = Response.ResponseObj()
        if oper_type == 'auth_code':
            '''
            1、授权后回调URI，得到授权码（authorization_code）和过期时间, 
            授权流程完成后，授权页会自动跳转进入回调URI，并在URL参数中返回授权码和过期时间(/zhugeleida/admin/open_weixin/auth_code/?auth_code=xxx&expires_in=3600);
            
            2、使用auth_code授权码换取授权公众号或小程序的授权信息，并换取authorizer_access_token和authorizer_refresh_token;

            '''
            pass


        elif oper_type == 'code_commit':
            user_id = request.GET.get('customer_id')
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
            component_access_token = rc.get('component_access_token')
            authorizer_access_token = rc.get('authorizer_access_token')
            app_id = 'wx67e2fde0f694111c'
            global authorizer_appid

            obj = models.zgld_admin_userprofile.objects.get(user_id=user_id)
            authorizer_refresh_token = obj.authorizer_refresh_token
            authorizer_appid = obj.authorizer_appid

            if not authorizer_access_token:

                if not component_access_token:

                    get_pre_auth_data = {}
                    post_component_data = {}
                    post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
                    component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
                    print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
                    component_token_ret = component_token_ret.json()
                    access_token = component_token_ret.get('component_access_token')
                    if access_token:
                        get_pre_auth_data['component_access_token'] = access_token
                        rc.set('component_access_token', access_token, 7000)
                        component_access_token = access_token
                    else:
                        response.code = 400
                        response.msg = "-------- 获取第三方平台 component_token_ret 返回错误 ------->"
                        return JsonResponse(response.__dict__)

                get_auth_token_data = {}
                post_auth_token_data = {}
                post_auth_token_data['component_appid'] = app_id
                post_auth_token_data['authorizer_appid'] = authorizer_appid
                post_auth_token_data['authorizer_refresh_token'] = authorizer_refresh_token

                get_auth_token_data['component_access_token'] = component_access_token
                authorizer_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
                authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data,
                                                    data=json.dumps(post_auth_token_data))
                authorizer_info_ret = authorizer_info_ret.json()

                print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>',authorizer_info_ret)


            get_wxa_commit_data = {}
            post_wxa_commit_data = {}
            get_wxa_commit_data['access_token'] = authorizer_access_token
            post_wxa_commit_data['template_id'] = 0
            commit_url = 'https://api.weixin.qq.com/wxa/commit'

            wxa_commit_info_ret = requests.post(commit_url, params=get_wxa_commit_data, data=json.dumps(post_wxa_commit_data))



        return JsonResponse(response.__dict__)