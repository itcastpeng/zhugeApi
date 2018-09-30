from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
from zhugeleida.public.crypto_ import  WXBizMsgCrypt_qiyeweixin
import json
import redis
import xml.etree.cElementTree as ET
from django import forms
import sys

## 第三方平台接入
@csrf_exempt
def open_weixin(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "POST":

        if oper_type == 'tongzhi':

            print('------ 第三方 request.body tongzhi 通知内容 ------>>', request.body.decode(encoding='UTF-8'))

            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            user_id = request.GET.get('user_id')

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

                token = '5lokfwWTqHXnb58VCV'
                encodingAESKey = 'HwX3RsMfMx9O4KBTqzwk9UMJ9pjNGbjE7PTyPaK7Gyxu4Z_G0ypv9iXT97A3EFDt'
                appid = 'wx81159f52aff62388'

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

            except Exception as e:
                auth_code = decryp_xml_tree.find('AuthorizationCode').text
                authorization_appid = decryp_xml_tree.find('AuthorizerAppid').text  # authorizer_appid 授权方de  appid

                userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
                company_id   =  userprofile_obj.company_id

                app_id = 'wx67e2fde0f694111c'
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

                access_token_ret = requests.post(access_token_url, params=get_access_token_data,data=json.dumps(post_access_token_data))
                access_token_ret = access_token_ret.json()
                print('--------- 获取令牌 authorizer_access_token authorizer_refresh_token 返回---------->>', access_token_ret)
                authorizer_access_token = access_token_ret['authorization_info'].get('authorizer_access_token')
                authorizer_refresh_token = access_token_ret['authorization_info'].get('authorizer_refresh_token')
                authorizer_appid = access_token_ret['authorization_info'].get('authorizer_appid')

                key_name = '%s_authorizer_access_token' % (authorization_appid)
                if authorizer_access_token and authorizer_refresh_token:

                    rc.set(key_name, authorizer_access_token, 7000)

                    ##################### 获取小程序授权方的authorizer_info信息 ##################
                    get_wx_info_data = {}
                    post_wx_info_data = {}
                    post_wx_info_data['component_appid'] = app_id
                    post_wx_info_data['authorizer_appid'] = authorizer_appid
                    get_wx_info_data['component_access_token'] = component_access_token
                    url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
                    authorizer_info_ret = requests.post(url, params=get_wx_info_data,data=json.dumps(post_wx_info_data))

                    print('----------- 获取小程序授权方的authorizer_info信息 返回 ------------->',json.dumps(authorizer_info_ret.json()))
                    authorizer_info_ret = authorizer_info_ret.json()
                    original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                    verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info']['id'] == 0 else False
                    #
                    principal_name = authorizer_info_ret['authorizer_info'].get('principal_name')  # 主体名称
                    qrcode_url = authorizer_info_ret['authorizer_info'].get('qrcode_url')   # 二维码
                    head_img = authorizer_info_ret['authorizer_info'].get('head_img')       # 头像
                    nick_name = authorizer_info_ret['authorizer_info'].get('nick_name')     # 头像

                    miniprograminfo = authorizer_info_ret['authorizer_info'].get('MiniProgramInfo')
                    categories = ''
                    if miniprograminfo:
                        categories = authorizer_info_ret['authorizer_info']['MiniProgramInfo'].get('categories')  # 类目

                        if len(categories) != 0:
                            categories = json.dumps(categories)
                        else:
                            categories = ''

                    if original_id:
                        obj = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)

                        if obj:
                            obj.update(
                                authorization_appid=authorization_appid,  # 授权方appid
                                authorizer_refresh_token=authorizer_refresh_token,  # 刷新的 令牌
                                original_id=original_id,  # 小程序的原始ID
                                verify_type_info=verify_type_info,  # 是否 微信认证

                                principal_name=principal_name,  # 主体名称
                                qrcode_url=qrcode_url,   # 二维码
                                head_img=head_img,       # 头像
                                name=nick_name,          # 昵称
                                service_category=categories,  # 服务类目
                            )

                        print('----------成功获取auth_code和帐号基本信息authorizer_info成功---------->>')
                        response.code = 200
                        response.msg = "成功获取auth_code和帐号基本信息authorizer_info成功"

                        ########################### 修改小程序服务器域名 ######################################
                        get_domin_data = {
                            'access_token': authorizer_access_token
                        }
                        post_domain_data = {
                            'action': 'add',
                            'requestdomain': ['https://api.zhugeyingxiao.com'],
                            'wsrequestdomain': ['wss://api.zhugeyingxiao.com'],
                            'uploaddomain': ['https://api.zhugeyingxiao.com'],
                            'downloaddomain': ['https://api.zhugeyingxiao.com']
                        }
                        post_domain_url = 'https://api.weixin.qq.com/wxa/modify_domain'
                        domain_data_ret = requests.post(post_domain_url, params=get_domin_data,
                                                        data=json.dumps(post_domain_data))
                        domain_data_ret = domain_data_ret.json()
                        print('--------- 修改小程序服务器 接口返回---------->>',domain_data_ret)

                        errcode = domain_data_ret.get('errcode')
                        errmsg = domain_data_ret.get('errmsg')

                        if errcode == 0:
                            response.code = 200
                            response.msg = "修改小程序服务器域名成功"
                            print('---------授权appid: %s , 修改小程序服务器域名 【成功】------------>>' % (authorization_appid))
                        else:
                            response.code = errcode
                            response.msg = errmsg
                            print ('---------授权appid: %s, 修改小程序服务器域名 【失败】------------>>' % (authorization_appid),errmsg,'|',errcode)


                        ########################## 组合模板并添加至帐号下的个人模板库 ###############################
                        get_template_add_data = {'access_token': authorizer_access_token}

                        template_add_url = 'https://api.weixin.qq.com/cgi-bin/wxopen/template/add'
                        '''
                            keyword_id_list : [25, 22, 11]
                            {
                                "keyword_id": 25,
                                "name": "回复者",
                                "example": "徐志娟"
                            }
                            {
                                "keyword_id": 22,
                                "name": "回复时间",
                                "example": "2018-6-22 10:48:37"
                            }
                            {
                                "keyword_id": 11,
                                "name": "回复内容",
                                "example": "您直接提交相关信息即可"
                            }                            
                        
                        '''
                        post_template_add_data = {
                            'id': 'AT0782',
                            "keyword_id_list": [25, 22, 11]
                        }
                        add_ret = requests.post(template_add_url, params=get_template_add_data,data=json.dumps(post_template_add_data))
                        add_ret = add_ret.json()

                        errcode = add_ret.get('errcode')
                        errmsg = add_ret.get('errmsg')
                        list = add_ret.get('list')

                        print('------- 组合模板并添加至帐号下的个人模板库[接口返回] ---->', json.dumps(add_ret))

                        if errcode == 0:
                            response.code = 200
                            response.msg = "组合模板添加成功"
                            if list:
                                list_ret = list[0]
                                template_id = list_ret.get('template_id')
                                obj.update(
                                    template_id=template_id
                                )

                            print('---------授权appid: %s , 组合模板并添加 【成功】------------>>' % (authorization_appid))
                        else:
                            response.code = errcode
                            response.msg = errmsg
                            print('---------授权appid: %s , 组合模板并添加 【失败】------------>>' % (authorization_appid),errmsg, '|', errcode)



                        ########################## 绑定微信用户为小程序体验者 ###############################
                        bind_tester_url = 'https://api.weixin.qq.com/wxa/bind_tester'
                        get_bind_tester_data = {
                            'access_token' : authorizer_access_token
                        }
                        for wechatid in ['Ju_do_it','ai6026325','crazy_acong','lihanjie5201314','wxid_6bom1qvrrjhv22']:
                            post_bind_tester_data = {
                                    "wechatid": wechatid
                            }
                            domain_data_ret = requests.post(bind_tester_url, params=get_bind_tester_data,data=json.dumps(post_bind_tester_data))
                            domain_data_ret = domain_data_ret.json()
                            print('---------- 第三方平台 - 绑定微信用户为小程序体验者 返回------------>>',domain_data_ret)


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
            request.session['user_id'] = user_id
            print('----request.session userId--->', request.session.get('user_id'))

            app_id = 'wx67e2fde0f694111c'
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            response_ret =  create_component_access_token()
            component_access_token = response_ret.data.get('component_access_token')

            get_pre_auth_data = {
                'component_access_token' : component_access_token
            }
            post_pre_auth_data = {
                'component_appid' :  app_id
            }
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
            # get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=2' % (app_id, pre_auth_code, redirect_uri) #授权注册页面扫码授权
            get_bind_auth_data = '&component_appid=%s&pre_auth_code=%s&redirect_uri=%s&auth_type=3' % (app_id, pre_auth_code, redirect_uri)   #auth_type=3 表示公众号和小程序都展示
            pre_auth_code_url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?' + get_bind_auth_data
            response.code = 200
            response.msg = '生成【授权链接】成功'
            response.data = pre_auth_code_url

        # 企业微信服务器会定时（每十分钟）推送ticket。https://work.weixin.qq.com/api/doc#10982/推送suite_ticket
        elif oper_type == 'get_ticket':
            print('------ 第三方 request.body 企业微信服务器 推送suite_ticket ------>>', request.body.decode(encoding='UTF-8'))

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')


            postdata = request.body.decode(encoding='UTF-8')

            sToken = "5lokfwWTqHXnb58VCV"
            sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"
            sCorpID = "wx5d26a7a856b22bec"
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

            # 解密成功，sMsg即为xml格式的明文
            xml_tree = ET.fromstring(sMsg)
            SuiteTicket = xml_tree.find("SuiteTicket").text
            SuiteId = xml_tree.find("SuiteId").text

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            key_name = 'SuiteTicket_%s' % (SuiteId)
            rc.set(key_name, SuiteTicket, 3000)
            print('--------企业微信服务器 SuiteId | suite_ticket--------->>', SuiteId, '|', SuiteTicket)



            return HttpResponse("success")

    return JsonResponse(response.__dict__)


## 生成接入流程控制页面
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def xcx_auth_process(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        user_id = request.GET.get('user_id')

        userprofile_obj =  models.zgld_admin_userprofile.objects.get(id=user_id)
        obj = models.zgld_xiaochengxu_app.objects.filter(company_id=userprofile_obj.company_id)

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

                release_obj = models.zgld_xiapchengxu_release.objects.filter(app_id=obj[0].id).order_by('-release_commit_date')


                version_num = ''
                release_time = ''
                if release_obj:
                    release_result = release_obj[0].release_result

                    if release_result == 1:  # 上线成功
                        audit_code_id = release_obj[0].audit_code_id
                        upload_audit_obj = models.zgld_xiapchengxu_upload_audit.objects.filter(id=audit_code_id)
                        if upload_audit_obj:
                            version_num = upload_audit_obj[0].version_num

                        version_num =  version_num
                        release_time = release_obj[0].release_commit_date.strftime('%Y-%m-%d %H:%M')

                upload_audit_obj = models.zgld_xiapchengxu_upload_audit.objects.filter(app_id=obj[0].id, audit_result=2,auditid__isnull=False).order_by(
                    '-audit_commit_date')  #在审核中并且auditid 不能为空。
                stay_version_num = ''
                stay_audit_time = ''

                if upload_audit_obj:
                    stay_version_num = upload_audit_obj[0].version_num ,
                    stay_audit_time = upload_audit_obj[0].audit_commit_date.strftime('%Y-%m-%d %H:%M')

                response.data = {
                    'step': '',
                    'ret_data': {
                        'authorization_appid': authorization_appid,  # 授权方appid
                        'name': name,  # 小程序名称
                        'principal_name': principal_name,  # 小程序主体名称
                        'head_img': head_img,  # 授权方头像
                        'verify_type_info': verify_type_info,  # 微信认证是否通过. True 为认证通过，Falsew为认证通过
                        'service_category': service_category,  #服务类目
                        'version_num': version_num,  #上线版本号
                        'release_time': release_time,   # 上线时间
                        'stay_version_num': stay_version_num,  #代上线-版本号
                        'stay_audit_time': stay_audit_time,    #代上线-审核时间

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
def xcx_auth_process_oper(request, oper_type):
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
                objs = models.zgld_xiaochengxu_app.objects.filter(user_id=user_id)
                if objs:
                    objs.update(
                        authorization_appid=authorization_appid,
                        company_id=company_id
                    )
                else:
                    models.zgld_xiaochengxu_app.objects.create(
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
                name = forms_obj.cleaned_data.get('name')  # 小程序名称
                head_img = forms_obj.cleaned_data.get('head_img')  # 头像
                introduce = forms_obj.cleaned_data.get('introduce')  # 介绍
                service_category = forms_obj.cleaned_data.get('service_category')  # 服务类目

                objs = models.zgld_xiaochengxu_app.objects.filter(user_id=user_id)
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

        ###获取小程序基本信息
        if oper_type == 'xcx_get_authorizer_info':
            user_id = request.GET.get('user_id')
            company_id =  models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            app_obj =   models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)
            if app_obj:
                authorizer_appid = app_obj[0].authorization_appid
                get_wx_info_data = {}
                post_wx_info_data = {}
                app_id = 'wx67e2fde0f694111c' # 三方平台的appid

                component_access_token_ret = create_component_access_token()
                component_access_token = component_access_token_ret.data.get('component_access_token')
                post_wx_info_data['component_appid'] = app_id
                post_wx_info_data['authorizer_appid'] = authorizer_appid
                get_wx_info_data['component_access_token'] = component_access_token

                url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'

                authorizer_info_ret = requests.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
                authorizer_info_ret = authorizer_info_ret.json()

                print('---------- 小程序帐号基本信息authorizer_info 返回 ----------------->',json.dumps(authorizer_info_ret))
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
                            original_id=original_id,  # 小程序的原始ID
                            verify_type_info=verify_type_info,  # 是否 微信认证

                            principal_name=principal_name,  # 主体名称
                            qrcode_url=qrcode_url,  # 二维码
                            head_img=head_img,  # 头像
                            name=nick_name,  # 昵称
                            service_category=categories,  # 服务类目
                        )
                    print('----------成功获取小程序帐号基本信息authorizer_info---------->>')
                    response.code = 200
                    response.msg = "成功获取小程序帐号基本信息authorizer_info"


            else:
                response.msg = '小程序不存在'
                response.code = 302


    return JsonResponse(response.__dict__)




## 生成请 第三方平台 自己 的component_access_token
def create_component_access_token():
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    response = Response.ResponseObj()

    component_verify_ticket = rc.get('ComponentVerifyTicket')
    app_id = 'wx67e2fde0f694111c'
    app_secret = '4a9690b43178a1287b2ef845158555ed'
    post_component_data = {
        'component_appid': app_id,
        'component_appsecret' : app_secret,
        'component_verify_ticket' : component_verify_ticket
    }


    token_ret = rc.get('component_access_token')
    print('--- Redis 里存储的 component_access_token---->>', token_ret)

    if not token_ret:
        post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
        component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
        print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
        component_token_ret = component_token_ret.json()
        access_token = component_token_ret.get('component_access_token')

        if access_token:
            token_ret = access_token
            rc.set('component_access_token', access_token, 7000)
        else:
            response.code = 400
            response.msg = "-------- 获取第三方平台 component_token_ret 返回错误 ------->"
            return JsonResponse(response.__dict__)

    response.data = {
        'component_access_token'  : token_ret
    }
    response.code = 200

    return response



# 添加企业的产品
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
            'required': "小程序名称不能为空"
        }
    )

    head_img = forms.CharField(
        required=True,
        error_messages={
            'required': "小程序头像不能为空"
        }
    )
    introduce = forms.CharField(
        required=False,
        error_messages={
            'required': "小程序头像不能为空"
        }
    )

    service_category = forms.CharField(
        required=True,
        error_messages={
            'required': "服务类目不能为空"
        }
    )
