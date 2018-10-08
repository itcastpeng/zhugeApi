from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_ import  WXBizMsgCrypt_qiyeweixin
import sys

import json
import redis
import xml.etree.cElementTree as ET
from django import forms

## 第三方平台接入
@csrf_exempt
def  open_qiyeweixin(request, oper_type):
    if request.method == "POST":
        response = Response.ResponseObj()

        # 企业微信服务器会定时（每十分钟）推送ticket。https://work.weixin.qq.com/api/doc#10982/推送suite_ticket
        if oper_type == 'get_ticket':
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
def create_suite_access_token():
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    response = Response.ResponseObj()

    suite_id = 'wx5d26a7a856b22bec'
    Secret = 'vHBmQNLTkm2FF61pj7gqoQVNFP5fr5J0avEzYRdzr2k'
    key_name = 'suite_access_token_%s' % (suite_id)

    suite_access_token = rc.get(key_name)

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
