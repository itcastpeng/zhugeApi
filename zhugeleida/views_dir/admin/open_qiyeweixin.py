from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import requests
from zhugeleida.public.crypto_ import WXBizMsgCrypt_qiyeweixin
import sys
from zhugeleida.public import common
import json
import redis
import xml.etree.cElementTree as ET
from django import forms
from django.shortcuts import render, redirect
import datetime


## 第三方平台接入
@csrf_exempt
def open_qiyeweixin(request, oper_type):
    response = Response.ResponseObj()
    application_data = {
        'leida': {
            'sToken': '5lokfwWTqHXnb58VCV',
            'sEncodingAESKey': 'ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt',
            'sCorpID': 'wx5d26a7a856b22bec',
        },
        'boss': {
            'sToken': '22LlaSyBP',
            'sEncodingAESKey': 'NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be',
            'sCorpID': 'wx36c67dd53366b6f0',
        },
        'address_book': {
            'sToken': '8sCAJ3YuU6EfYWxI',
            'sEncodingAESKey': '3gSz92t8espUQgbXembgcDk3e6Hrs9SpJf34zQ8lqEj',
            'sCorpID': 'wx1cbe3089128fda03',
        },
    }

    if request.method == "POST":

        # 企业微信服务器会定时（每十分钟）推送ticket。https://work.weixin.qq.com/api/doc#10982/推送suite_ticket
        if oper_type == 'get_ticket':
            print('------ 第三方 request.body 企业微信服务器 推送suite_ticket ------>>', request.body.decode(encoding='UTF-8'))

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            ticket_type = request.GET.get('type')

            postdata = request.body.decode(encoding='UTF-8')

            sToken = application_data[ticket_type]['sToken']
            sEncodingAESKey = application_data[ticket_type]['sEncodingAESKey']
            sCorpID = application_data[ticket_type]['sCorpID']

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
            xml_tree = ET.fromstring(sMsg)

            # 解密成功，sMsg即为xml格式的明文

            SuiteTicket = xml_tree.find("SuiteTicket").text
            SuiteId = xml_tree.find("SuiteId").text

            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            key_name = 'SuiteTicket_%s' % (SuiteId)
            rc.set(key_name, SuiteTicket, 3000)
            print('--------企业微信服务器 SuiteId | suite_ticket--------->>', SuiteId, '|', SuiteTicket)

            return HttpResponse("success")

        elif oper_type == "create_grant_url":

            app_type = int(request.POST.get('app_type')) if request.POST.get('app_type') else ''

            suite_id = ''
            if app_type == 1:  # 雷达AI
                suite_id = 'wx5d26a7a856b22bec'
                app_type = 'leida'
            elif app_type == 2:  # 雷达Boss
                suite_id = 'wx36c67dd53366b6f0'
                app_type = 'boss'

            redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/open_qiyeweixin/get_auth_code'  # 安装完成回调域名

            _data = {
                'app_type': app_type,
                'SuiteId': suite_id
            }
            create_pre_auth_code_ret = common.create_pre_auth_code(_data)

            pre_auth_code = create_pre_auth_code_ret.data.get('pre_auth_code')

            get_bind_auth_data = 'suite_id=%s&pre_auth_code=%s&redirect_uri=%s&state=%s' % (
            suite_id, pre_auth_code, redirect_uri, suite_id)

            pre_auth_code_url = 'https://open.work.weixin.qq.com/3rdapp/install?' + get_bind_auth_data

            response.code = 200
            response.msg = '生成【授权链接】成功'
            response.data = {
                'pre_auth_code_url': pre_auth_code_url
            }
            # 授权成功，返回临时授权码;第三方服务商需尽快使用临时授权码换取永久授权码及授权信息

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

            xml_tree = ET.fromstring(postdata) # 安装到这个企业后的 agent_id

            SuiteId = xml_tree.find("AgentID").text
            print('-----post callback_data postdata 数据:------>',postdata)

            return HttpResponse('success')

    elif request.method == "GET":

        if oper_type == 'get_ticket':

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')
            ticket_type = request.GET.get('type')

            sToken = application_data[ticket_type]['sToken']
            sEncodingAESKey = application_data[ticket_type]['sEncodingAESKey']
            # sCorpID = application_data[ticket_type]['sCorpID']
            # sToken = ''
            # sEncodingAESKey = ''
            # if type == 'leida':
            #     sToken = "5lokfwWTqHXnb58VCV"  # 回调配置
            #     sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"  # 回调配置
            #
            # elif type == 'boss':
            #     sToken = "22LlaSyBP"  # 回调配置
            #     sEncodingAESKey = "NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be"  # 回调配置

            sCorpID = "wx81159f52aff62388"
            wxcpt = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

            # ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
            ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if (ret != 0):
                print("---- 验证回调URL: VerifyURL ret: ----> " + str(ret))
                sys.exit(1)
            print('----- [get_ticket]解密echostr参数得到消息内容 -------->>', sEchoStr)

            # 验证URL成功，将sEchoStr返回给企业号
            return HttpResponse(sEchoStr)

        elif oper_type == 'callback_data':

            msg_signature = request.GET.get('msg_signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')

            type = request.GET.get('type')

            sToken = ''
            sEncodingAESKey = ''
            if type == 'leida':
                sToken = "5lokfwWTqHXnb58VCV"  # 回调配置
                sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"  # 回调配置
            elif type == 'boss':
                sToken = "22LlaSyBP"  # 回调配置
                sEncodingAESKey = "NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be"  # 回调配置

            sCorpID = "wx81159f52aff62388"  # 通用开发参数 CorpID
            wxcpt = WXBizMsgCrypt_qiyeweixin.WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

            # ret, sMsg = decrypt_obj.DecryptMsg(postdata, msg_signature, timestamp, nonce)
            ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if (ret != 0):
                print("---- 验证回调URL: VerifyURL ret: ----> " + str(ret))
                sys.exit(1)
            print('----- [callback_data]解密echostr参数得到消息内容 -------->>', sEchoStr)

            # 验证URL成功，将sEchoStr返回给企业号
            return HttpResponse(sEchoStr)

        #  网页授权登录第三方-登陆
        elif oper_type == 'work_weixin_auth':
            code = request.GET.get('code')
            app_type = request.GET.get('state')

            SuiteId = ''
            url = ''
            if app_type == 'leida':
                SuiteId = 'wx5d26a7a856b22bec'
                url = 'http://zhugeleida.zhugeyingxiao.com'

            elif app_type == 'boss':
                SuiteId = 'wx36c67dd53366b6f0'
                url = 'http://zhugeleida.zhugeyingxiao.com/#/bossLeida'

            _data = {
                'SuiteId': SuiteId
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
            if not user_ticket:
                print('===========【企业微信】获取 user_ticket【失败】,消费 code | 使用 access_token:==========>', code, "|",
                      suite_access_token)
                return HttpResponse('404')

            else:
                print('===========【企业微信】获取 user_ticket【成功】,消费 code | 使用access_token | user_ticket==========>', code,
                      "|", suite_access_token, "|", user_ticket)

            post_userlist_data = {
                'user_ticket': user_ticket
            }
            get_userlist_data = {
                'access_token': suite_access_token
            }

            userlist_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/getuserdetail3rd'
            user_list_ret = requests.post(userlist_url, params=get_userlist_data, data=json.dumps(post_userlist_data))
            user_list_ret_json = user_list_ret.json()

            userid = user_list_ret_json.get('userid')
            corpid = user_list_ret_json.get('corpid')
            name = user_list_ret_json.get('name')
            avatar = user_list_ret_json.get('avatar')  # 加上100 获取小图
            gender = user_list_ret_json.get('gender')
            # email = user_list_ret_json['email']

            print('----------【企业微信】获取 《用户基本信息》 返回 | userid---->', json.dumps(user_list_ret_json), "|", userid)
            company_objs = models.zgld_company.objects.filter(corp_id=corpid)

            if company_objs:
                company_id = company_objs[0].id
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
                        return redirect('http://zhugeleida.zhugeyingxiao.com/#/expire_page/index')

                    redirect_url = ''
                    if status == 1 and  app_type == 'leida':  #
                        user_profile_obj.gender = gender
                        # user_profile_obj.email = email
                        user_profile_obj.avatar = avatar

                        last_login_date = user_profile_obj.last_login_date
                        if not last_login_date:  # 为空说明第一次登陆
                            is_first_login = 'Yes'
                            user_profile_obj.last_login_date = datetime.datetime.now()
                        else:
                            is_first_login = 'No'
                        user_profile_obj.save()

                        redirect_url = url + '?token=' + user_profile_obj.token + '&id=' + str(
                            user_profile_obj.id) + '&avatar=' + avatar + '&is_first_login=' + is_first_login

                        print('----------【雷达用户】存在且《登录成功》，user_id | userid | redirect_url ---->', user_profile_obj.id, "|",
                              userid, "\n", redirect_url)
                        return redirect(redirect_url)

                    if  boss_status == 1 and app_type == 'boss': #
                        user_profile_obj.gender = gender
                        # user_profile_obj.email = email
                        user_profile_obj.avatar = avatar
                        user_profile_obj.save()

                        redirect_url = url + '?token=' + user_profile_obj.token + '&id=' + str(
                            user_profile_obj.id) + '&avatar=' + avatar

                        print('----------【雷达用户】存在且《登录成功》，user_id | userid | redirect_url ---->', user_profile_obj.id, "|",
                              userid, "\n", redirect_url)
                        return redirect(redirect_url)

                    else:
                        print('----------【雷达权限】未开通 ,未登录成功 userid | corpid ------>', userid, corpid)
                        return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')

                else:
                    print('----------【雷达权限】不存在 ,未登录成功 userid | corpid ------>', userid,"|",corpid)
                    return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')
            else:
                print('----------【公司不存在】,未登录成功 userid | corpid ------>', userid,"|",corpid)
                return redirect('http://zhugeleida.zhugeyingxiao.com/err_page')

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

            get_permanent_code_url = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code'
            _app_type = ''
            name = ''
            if SuiteId == 'wx5d26a7a856b22bec':
                name = '雷达AI'
                _app_type = 1
            elif SuiteId == 'wx36c67dd53366b6f0':
                name = '雷达Boss'
                _app_type = 2

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
            print('-------[企业微信] 获取企业永久授权码 返回------->>', get_permanent_code_info)

            corpid = get_permanent_code_info['auth_corp_info'].get('corpid')  # 授权方企业微信id
            corp_name = get_permanent_code_info['auth_corp_info'].get('corp_name')  # 授权方企业微信名称
            agent_list = get_permanent_code_info['auth_info'].get('agent')  # 授权方企业微信名称
            agentid = ''
            for _agent_dict in agent_list:
                _name = _agent_dict.get('name')
                if _name == name:
                    agentid = _agent_dict.get('agentid')

            access_token = get_permanent_code_info.get('access_token')  # 授权方（企业）access_token
            permanent_code = get_permanent_code_info.get('permanent_code')  # 企业微信永久授权码 | 每个企业授权的每个应用的永久授权码、授权信息都是唯一的


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
                            permanent_code = permanent_code
                        )
                    return redirect('http://zhugeleida.zhugeyingxiao.com/admin/#/empower/empower_company')

                else:
                    print('-------[企业微信] 企业不存在：------->>', corpid)
            else:
                print('-------[企业微信] 获取企业永久授权码 报错：------->>')

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
