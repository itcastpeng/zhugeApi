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
from django import forms
import datetime
from django.conf import settings
import os
from zhugeleida.forms.admin.dai_xcx_verify import CommitCodeInfoForm,SubmitAuditForm,GetqrCodeForm

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

            except Exception as e:
                auth_code = decryp_xml_tree.find('AuthorizationCode').text
                authorization_appid = decryp_xml_tree.find('AuthorizerAppid').text  # authorizer_appid 授权方 appid

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

                access_token_ret = requests.post(access_token_url, params=get_access_token_data,
                                                 data=json.dumps(post_access_token_data))
                access_token_ret = access_token_ret.json()
                print('--------- 获取令牌 authorizer_access_token authorizer_refresh_token 返回---------->>',
                      access_token_ret)
                authorizer_access_token = access_token_ret['authorization_info'].get('authorizer_access_token')
                authorizer_refresh_token = access_token_ret['authorization_info'].get('authorizer_refresh_token')
                authorizer_appid = access_token_ret['authorization_info'].get('authorizer_appid')

                if authorizer_access_token and authorizer_refresh_token:

                    rc.set('authorizer_access_token', authorizer_access_token, 7000)

                    ##################### 获取小程序授权方的authorizer_info信息 ##################
                    get_wx_info_data = {}
                    post_wx_info_data = {}
                    post_wx_info_data['component_appid'] = app_id
                    post_wx_info_data['authorizer_appid'] = authorizer_appid
                    get_wx_info_data['component_access_token'] = component_access_token
                    url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
                    authorizer_info_ret = requests.post(url, params=get_wx_info_data,
                                                        data=json.dumps(post_wx_info_data))

                    print('----------- 获取小程序授权方的authorizer_info信息 返回 ------------->',
                          json.dumps(authorizer_info_ret.json()))
                    authorizer_info_ret = authorizer_info_ret.json()
                    original_id = authorizer_info_ret['authorizer_info'].get('user_name')

                    verify_type_info = True if authorizer_info_ret['authorizer_info']['verify_type_info'][
                                                   'id'] == 0 else False
                    # ---->预留代码
                    principal_name = authorizer_info_ret['authorizer_info'].get('principal_name')  # 主体名称
                    qrcode_url = authorizer_info_ret['authorizer_info'].get('qrcode_url')  # 二维码
                    head_img = authorizer_info_ret['authorizer_info'].get('head_img')  # 头像
                    nick_name = authorizer_info_ret['authorizer_info'].get('nick_name')  # 头像
                    categories = authorizer_info_ret['authorizer_info']['MiniProgramInfo'].get('categories')  # 头像
                    if len(categories) != 0:
                        categories = json.dumps(categories)

                    if original_id:
                        obj = models.zgld_xiaochengxu_app.objects.filter(authorization_appid=authorization_appid)
                        if obj:
                            obj.update(
                                authorization_appid=authorization_appid,  # 授权方appid
                                authorizer_refresh_token=authorizer_refresh_token,  # 刷新的 令牌
                                original_id=original_id,  # 小程序的原始ID
                                verify_type_info=verify_type_info,  # 是否 微信认证

                                principal_name=principal_name,  # 主体名称
                                qrcode_url=qrcode_url,  # 二维码
                                head_img=head_img,  # 头像
                                name=nick_name,  # 昵称
                                service_category=categories,  # 服务类目
                            )

                        response.code = 200
                        response.msg = "成功获取auth_code和帐号基本信息authorizer_info成功"
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


        elif oper_type == "create_grant_url":
            user_id = request.GET.get('user_id')
            request.session['user_id'] = user_id
            print('----request.session userId--->', request.session.get('user_id'))

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


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def dai_xcx_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

        # 第三方代小程序发布
        if oper_type == 'code_commit':

            # user_id = request.GET.get('user_id')
            '''
            ext.json  指导文件 https://developers.weixin.qq.com/miniprogram/dev/devtools/ext.html
                      extEnable	Boolean	 是	配置ext.json 是否生效
                      extAppid	String	 是	配置 授权方Appid
                      directCommit	Boolean	否	是否直接提交到待审核列表
                      {
                          "extEnable": true,
                          "extAppid": "wxf9c4501a76931b33",
                          "directCommit": false,
                      }
                      
            app.json  全局配置文件  https://developers.weixin.qq.com/miniprogram/dev/framework/config.html
            
            '''

            forms_obj = CommitCodeInfoForm(request.POST)
            if forms_obj.is_valid():
                customer_id = request.POST.get('customer_id')  # 账户
                user_version = forms_obj.cleaned_data.get('user_version')
                template_id = forms_obj.cleaned_data.get('template_id')
                user_desc = forms_obj.cleaned_data.get('user_desc')
                ext_json = forms_obj.cleaned_data.get('ext_json')



                # app_id = 'wx67e2fde0f694111c'
                # app_secret = '4a9690b43178a1287b2ef845158555ed'

                obj = models.zgld_xiaochengxu_app.objects.get(user_id=customer_id)
                authorizer_refresh_token = obj.authorizer_refresh_token
                authorizer_appid = obj.authorization_appid

                key_name = '%s_authorizer_access_token' % (authorizer_appid)
                authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                if not authorizer_access_token:
                    data = {
                        'key_name': key_name,
                        'authorizer_refresh_token' : authorizer_refresh_token,
                        'authorizer_appid' : authorizer_appid
                    }
                    authorizer_access_token = create_authorizer_access_token(data)
                    # component_access_token = rc.get('component_access_token')
                    # if not component_access_token:
                    #
                    #     get_pre_auth_data = {}
                    #     post_component_data = {}
                    #     post_component_data['component_appid'] = app_id
                    #     post_component_data['component_appsecret'] = app_secret
                    #     component_verify_ticket = rc.get('ComponentVerifyTicket')
                    #     post_component_data['component_verify_ticket'] = component_verify_ticket
                    #
                    #     post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
                    #     component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
                    #     print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
                    #     component_token_ret = component_token_ret.json()
                    #     access_token = component_token_ret.get('component_access_token')
                    #     if access_token:
                    #         get_pre_auth_data['component_access_token'] = access_token
                    #         rc.set('component_access_token', access_token, 7000)
                    #         component_access_token = access_token
                    #     else:
                    #         response.code = 400
                    #         response.msg = "-------- 获取第三方平台 component_token_ret 返回错误 ------->"
                    #         return JsonResponse(response.__dict__)
                    #
                    # get_auth_token_data = {}
                    # post_auth_token_data = {}
                    # post_auth_token_data['component_appid'] = app_id
                    # post_auth_token_data['authorizer_appid'] = authorizer_appid
                    # post_auth_token_data['authorizer_refresh_token'] = authorizer_refresh_token
                    #
                    # get_auth_token_data['component_access_token'] = component_access_token
                    # authorizer_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
                    # authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data,
                    #                                     data=json.dumps(post_auth_token_data))
                    # authorizer_info_ret = authorizer_info_ret.json()
                    #
                    # print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)
                    #
                    # authorizer_access_token = authorizer_info_ret.get('authorizer_access_token')
                    # authorizer_refresh_token = authorizer_info_ret.get('authorizer_refresh_token')
                    #
                    # if authorizer_access_token and authorizer_refresh_token:
                    #     rc.set(key_name, authorizer_access_token, 7000)
                    #
                    # else:
                    #     print('------ 获取令牌（authorizer_access_token）为空------>>')
                    #     response.code = 400
                    #     response.msg = "获取令牌authorizer_access_token为空"
                    #     return JsonResponse(response.__dict__)

                get_wxa_commit_data = {}
                post_wxa_commit_data = {}

                print('------ 第三方自定义的配置 ext_json ------>',ext_json)
                get_wxa_commit_data['access_token'] = authorizer_access_token
                post_wxa_commit_data['template_id'] = template_id  # 代码库中的代码模版ID
                post_wxa_commit_data['ext_json'] = ext_json  # 第三方自定义的配置
                post_wxa_commit_data['user_version'] = user_version  # 代码版本号，开发者可自定义
                post_wxa_commit_data['user_desc'] = user_desc  # 代码描述，开发者可自定义
                commit_url = 'https://api.weixin.qq.com/wxa/commit'

                wxa_commit_info_ret = requests.post(commit_url, params=get_wxa_commit_data,
                                                    data=json.dumps(post_wxa_commit_data))

                wxa_commit_info_ret = wxa_commit_info_ret.json()
                print('--------为授权的小程序帐号上传小程序代码 接口返回---------->>',wxa_commit_info_ret)

                errcode = wxa_commit_info_ret.get('errcode')
                errmsg = wxa_commit_info_ret.get('errmsg')
                if errcode == 0:
                    response.code = 200
                    response.msg = '小程序帐号上传小程序代码成功'
                else:
                    response.code = errcode
                    response.msg = errmsg  # https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1489140610_Uavc4&token=&lang=zh_CN


            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 获取体验小程序的体验二维码
        elif oper_type == 'get_qrcode':
            forms_obj = GetqrCodeForm(request.POST)

            if forms_obj.is_valid():

                get_qrcode_url = 'https://api.weixin.qq.com/wxa/get_qrcode'
                customer_id = request.POST.get('customer_id') # 用户的ID。
                path = forms_obj.cleaned_data.get('path')

                obj = models.zgld_xiaochengxu_app.objects.get(user_id=customer_id)
                authorizer_refresh_token = obj.authorizer_refresh_token
                authorizer_appid = obj.authorization_appid

                key_name = '%s_authorizer_access_token' % (authorizer_appid)
                authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                if not authorizer_access_token:
                    data = {
                        'key_name': key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid
                    }
                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = response.data
                    else:
                        return JsonResponse(authorizer_access_token.__dict__)

                get_qrcode_data = {
                    'access_token': authorizer_access_token
                }
                if path:
                    get_qrcode_data['path'] = path

                get_qrcode_ret = requests.get(get_qrcode_url, params=get_qrcode_data)

                try:

                    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida' , 'imgs', 'admin','qr_code')

                    qr_code_name = '/%s_%s_QRCode.jpg' % (authorizer_appid, now_time)

                    path_qr_code_name = BASE_DIR + qr_code_name
                    qr_url = 'statics/zhugeleida/imgs/admin/qr_code%s' % (qr_code_name)

                    with open(path_qr_code_name, 'wb') as f:
                        f.write(get_qrcode_ret.content)

                    response.code = 200
                    response.data = {
                        'qrcode_url' : qr_url

                    }
                    response.msg = '生成小程序体验码成功'

                except Exception as e:
                    response.code = 301
                    response.msg = '小程序的体验二维码_接口返回-错误'

                    print('------- 获取体验小程序的体验二维码_接口返回-错误 ---->>', get_qrcode_ret.text,'|',e)

            else:
                print("--验证不通过-->",forms_obj.errors.as_json())
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 将第三方提交的代码包提交审核
        elif oper_type == 'submit_audit':
            forms_obj = SubmitAuditForm(request.POST)
            if forms_obj.is_valid():
                customer_id = request.POST.get('customer_id')  # 用户的ID。
                obj = models.zgld_xiaochengxu_app.objects.get(user_id=customer_id)
                authorizer_refresh_token = obj.authorizer_refresh_token
                authorizer_appid = obj.authorization_appid

                key_name = '%s_authorizer_access_token' % (authorizer_appid)
                authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                if not authorizer_access_token:
                    data = {
                        'key_name': key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid
                    }
                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = response.data
                    else:
                        return JsonResponse(authorizer_access_token.__dict__)

                # 获取小程序的第三方提交代码的页面配置
                get_page_url = 'https://api.weixin.qq.com/wxa/get_page'
                get_page_data = {
                    'access_token' : authorizer_access_token,
                }
                page_data_ret = requests.get(get_page_url, params=get_page_data)
                page_data_ret = page_data_ret.json()
                errcode = page_data_ret.get('errcode')
                errmsg = page_data_ret.get('errmsg')
                page_list = page_data_ret.get('page_list')

                print('-------- 第三方提交代码的页面配置 page_data_ret 返回------>>',page_data_ret)
                if errcode == 0:
                    first_page = page_list[0]
                    print('-----page_list--->>',page_list)

                else:
                    response.code = errcode
                    response.msg = '获取第三方-页面配置报错: %s' % (errmsg)
                    return JsonResponse(response.__dict__)


                # 获取授权小程序帐号的可选类目
                get_category_url = 'https://api.weixin.qq.com/wxa/get_category'
                get_category_data = {
                    'access_token': authorizer_access_token,
                }
                page_category_ret = requests.get(get_category_url, params=get_category_data)
                page_category_ret = page_category_ret.json()
                errcode = page_category_ret.get('errcode')
                errmsg = page_category_ret.get('errmsg')
                category_list = page_category_ret.get('category_list')

                print('-------- 获取授权小程序帐号的可选类目 page_category_ret 返回------>>', page_category_ret)
                if errcode == 0:
                    print('-----category_list--->>', category_list)

                else:
                    response.code = errcode
                    response.msg = '获取第三方-页面配置报错: %s' % (errmsg)
                    return JsonResponse(response.__dict__)


                submit_audit_url = 'https://api.weixin.qq.com/wxa/submit_audit'
                item_list = []
                item_dict = {}
                item_list.append(item_dict)
                '''
                {'errcode': 0, 'errmsg': 'ok', 'page_list': ['pages/index/index', 'pages/logs/logs']}
                
                {'errcode': 0, 'errmsg': 'ok', 
                     'category_list': [{
                            "first_class":"教育",
                            "second_class":"学历教育",
                            "third_class":"高等",
                            "first_id":3,
                            "second_id":4,
                            "third_id":5
                        }]
                     }

                '''

                get_submit_audit_data = {
                    'access_token': authorizer_access_token,
                }
                post_submit_audit_data = {
                    'item_list' : item_list
                }
                submit_audit_ret = requests.get(submit_audit_url, params=get_submit_audit_data,data=post_submit_audit_data)
                submit_audit_ret = submit_audit_ret.json()
                auditid = submit_audit_ret.get('auditid')
                errcode = submit_audit_ret.get('errcode')
                errmsg = submit_audit_ret.get('errmsg')

                print('-------- 代码包-提交审核 返回 submit_audit_ret 返回------>>', submit_audit_ret)
                if errcode == 0:
                    print('-----auditid--->>', auditid)
                    response.code = 200
                    response.msg = '提交审核代码成功'

                else:
                    response.code = errcode
                    response.msg = '提交审核代码报错: %s' % (errmsg)
                    return JsonResponse(response.__dict__)



    elif request.method == "GET":
        pass

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def dai_xcx_oper_(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":

        if oper_type == "update":

            if int(o_id) == 1:  # 修改更新 original_id
                print('---xcx_auth_process --->', request.POST)
                forms_obj = CommitCodeInfoForm(request.POST)
                if forms_obj.is_valid():
                    authorization_appid = request.POST.get('authorization_appid')
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

            elif int(o_id) == 3:  # 更新授权修改的信息。

                forms_obj = CommitCodeInfoForm(request.POST)
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

    return JsonResponse(response.__dict__)


def create_authorizer_access_token(data):
    response = Response.ResponseObj()
    authorizer_appid = data.get('authorizer_appid')
    authorizer_refresh_token = data.get('authorizer_refresh_token')
    key_name = data.get('key_name')

    app_id = 'wx67e2fde0f694111c'
    app_secret = '4a9690b43178a1287b2ef845158555ed'
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    component_access_token = rc.get('component_access_token')
    if not component_access_token:

        get_pre_auth_data = {}
        post_component_data = {}
        post_component_data['component_appid'] = app_id
        post_component_data['component_appsecret'] = app_secret
        component_verify_ticket = rc.get('ComponentVerifyTicket')
        post_component_data['component_verify_ticket'] = component_verify_ticket

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

    print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)

    authorizer_access_token = authorizer_info_ret.get('authorizer_access_token')
    authorizer_refresh_token = authorizer_info_ret.get('authorizer_refresh_token')

    if authorizer_access_token and authorizer_refresh_token:
        rc.set(key_name, authorizer_access_token, 7000)
        response.code = 200
        response.msg = "获取令牌成功"
        response.data = authorizer_access_token
        print('------ 获取令牌（authorizer_access_token）成功------>>',authorizer_access_token)

    else:
        print('------ 获取令牌（authorizer_access_token）为空------>>')
        response.code = 400
        response.msg = "获取令牌authorizer_access_token为空"
        return JsonResponse(response.__dict__)

    return  response