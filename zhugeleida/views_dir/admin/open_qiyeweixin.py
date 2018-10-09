from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_ import  WXBizMsgCrypt_qiyeweixin
import sys
from zhugeleida.public import common
import json
import redis
import xml.etree.cElementTree as ET
from django import forms

## 第三方平台接入
@csrf_exempt
def  open_qiyeweixin(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 企业微信服务器会定时（每十分钟）推送ticket。https://work.weixin.qq.com/api/doc#10982/推送suite_ticket
        if oper_type == 'get_ticket':
            print('------ 第三方 request.body 企业微信服务器 推送suite_ticket ------>>', request.body.decode(encoding='UTF-8'))

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')

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
            xml_tree = ET.fromstring(sMsg)

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

                rc.set(key_name, AuthCode, 3000)
                print('--------企业微信服务器 SuiteId | AuthCode--------->>', SuiteId, '|', AuthCode)

            return HttpResponse("success")




        elif oper_type == "create_grant_url":

            suite_id = 'wx5d26a7a856b22bec'
            create_pre_auth_code_ret =  common.create_pre_auth_code()
            pre_auth_code = create_pre_auth_code_ret.data.get('pre_auth_code')
            redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/admin/#/empower/empower_company'

            get_bind_auth_data = 'suite_id=%s&pre_auth_code=%s&redirect_uri=%s&state=STATE' % (suite_id,pre_auth_code,redirect_uri)

            pre_auth_code_url = 'https://open.work.weixin.qq.com/3rdapp/install?' + get_bind_auth_data

            response.code = 200
            response.msg = '生成【授权链接】成功'
            response.data = {
                'pre_auth_code_url' : pre_auth_code_url
            }
            # 授权成功，返回临时授权码;第三方服务商需尽快使用临时授权码换取永久授权码及授权信息




        # 设置授权配置 /zhugeleida/admin/open_qiyeweixin/set_session_info
        elif oper_type == 'set_session_info':
            suite_id = 'wx5d26a7a856b22bec'
            create_pre_auth_code_ret =  common.create_pre_auth_code()
            pre_auth_code = create_pre_auth_code_ret.data.get('pre_auth_code')
            suite_access_token = create_pre_auth_code_ret.data.get('suite_access_token')

            set_session_info_url =  'https://qyapi.weixin.qq.com/cgi-bin/service/set_session_info'

            post_set_session_info_data =  {
                "pre_auth_code": pre_auth_code,
                "session_info":
                    {
                        "appid": [],
                        "auth_type": 1 #授权类型：0 正式授权， 1 测试授权。 默认值为0。注意，请确保应用在正式发布后的授权类型为“正式授权”
                    }
            }
            get_set_session_info_data = {
                'suite_access_token': suite_access_token,
            }
            set_session_info = requests.post(set_session_info_url, params=get_set_session_info_data,data=json.dumps(post_set_session_info_data))

            set_session_info = set_session_info.json()
            print('---------- [企业微信] - 设置授权配置 返回------------>>', set_session_info)

            response.code = 200
            response.msg = '生成【设置授权配置】成功'
            response.data = set_session_info


    elif request.method == "GET":

        if oper_type == 'get_ticket':

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')

            sToken = "5lokfwWTqHXnb58VCV"
            sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"
            # sCorpID = "wx5d26a7a856b22bec"
            sCorpID = "wx81159f52aff62388"
            wxcpt = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)


            # ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
            ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if (ret != 0):
                print("---- 验证回调URL: VerifyURL ret: ----> " + str(ret))
                sys.exit(1)
            print('----- [get_ticket]解密echostr参数得到消息内容 -------->>',sEchoStr)

            # 验证URL成功，将sEchoStr返回给企业号
            return HttpResponse(sEchoStr)

        elif oper_type == 'callback_data':

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')

            sToken = "5lokfwWTqHXnb58VCV"
            sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"
            # sCorpID = "wx5d26a7a856b22bec"
            sCorpID = "wx81159f52aff62388"
            wxcpt = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)


            # ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
            ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if (ret != 0):
                print("---- 验证回调URL: VerifyURL ret: ----> " + str(ret))
                sys.exit(1)
            print('----- [callback_data]解密echostr参数得到消息内容 -------->>',sEchoStr)

            # 验证URL成功，将sEchoStr返回给企业号
            return HttpResponse(sEchoStr)


    return JsonResponse(response.__dict__)





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
