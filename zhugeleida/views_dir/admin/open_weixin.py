from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
import json
import redis

@csrf_exempt
def open_weixin(request,oper_type):

    if request.method == "POST":
        response = Response.ResponseObj()
        if oper_type == 'tongzhi':
            print('------授权第三方 request.POST------>>',request.POST)

            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            postdata = request.POST.get('postdata')

            print('----- 授权公众号授权 postdata---->>',postdata)

            token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
            encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'

            app_id = 'wx67e2fde0f694111c'
            app_secret = '4a9690b43178a1287b2ef845158555ed'
            decrypt_test = WXBizMsgCrypt(token, encodingAESKey, app_id)

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            rc.set('postdata', postdata, 1000)

            decryp_xml =  rc.get('decryp_xml')
            if not  decryp_xml:
                ret, decryp_xml = decrypt_test.DecryptMsg(postdata, msg_signature, timestamp, nonce)
                print('--------授权公众号消息解密 DecryptMsg--------->>',ret, decryp_xml)
                if ret == 0:

                    rc.set('decryp_xml', decryp_xml, 7000)

            print('--------授权公众号消息解密 DecryptMsg--------->>',decryp_xml)




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




            return HttpResponse("success")


        elif oper_type == "create_grant_url":

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
            # post_component_data['component_verify_ticket'] = component_verify_ticket

            token_ret = rc.get('component_access_token')

            print('--- Redis 里存储的 component_access_token---->>', token_ret)

            if not token_ret:
                post_component_url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
                component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))
                print('--------- 获取第三方平台 component_token_ret.json --------->>', component_token_ret.json())
                component_token_ret = component_token_ret.json()
                access_token = component_token_ret.get('component_access_token')
                if  access_token:
                    get_pre_auth_data['component_access_token'] = access_token
                    rc.set('component_access_token', access_token, 7000)
                else:
                    response.code = 400
                    response.msg = "-------- 获取第三方平台 component_token_ret 返回错误 ------->"
                    return JsonResponse(response.__dict__)
            else:
                get_pre_auth_data['component_access_token'] = token_ret

            post_pre_auth_data['component_appid'] = app_id

            pre_auth_code_url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'
            pre_auth_code_ret = requests.post(pre_auth_code_url, params=get_pre_auth_data, data=json.dumps(post_pre_auth_data))
            pre_auth_code_ret = pre_auth_code_ret.json()
            pre_auth_code = pre_auth_code_ret.get('pre_auth_code')
            print('------ 获取第三方平台 pre_auth_code 预授权码 ----->',pre_auth_code,"   |  ", pre_auth_code_ret,)
            if pre_auth_code:
               pass
            else:
                response.code = 400
                response.msg = "--------- 获取第三方平台 pre_auth_code预授权码 返回错误 ------->"
                return JsonResponse(response.__dict__)

            # get_auth_info_data['component_access_token'] = token_ret
            # post_auth_info_data['component_appid'] = app_id
            # post_auth_info_data['authorization_code'] = app_id
            #
            # authorizer_info_url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth?component_access_token=xxxx'
            # authorizer_info_ret = requests.post(authorizer_info_url, params=get_auth_info_data,
            #                                   data=json.dumps(post_auth_info_data))
            # authorizer_info_ret = authorizer_info_ret.json()

        return JsonResponse(response.__dict__)
