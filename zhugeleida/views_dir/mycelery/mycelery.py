from django.http import HttpResponse
from zhugeleida import models
from zhugeleida.views_dir.conf import Conf
from django.views.decorators.csrf import csrf_exempt

import requests
import json
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
import os
import datetime
import redis
from collections import OrderedDict
from zhugeleida.views_dir.admin.dai_xcx  import create_authorizer_access_token

import logging.handlers

# 小程序访问动作日志的发送到企业微信
@csrf_exempt
def user_send_action_log(request):
    response = ResponseObj()
    data = json.loads(request.POST.get('data'))
    print('data ===>', data)

    customer_id = data.get('customer_id', '')
    user_id = data.get('uid')
    content = data.get('content')
    agentid = data.get('agentid')

    get_token_data = {}
    send_token_data = {}

    user_obj = models.zgld_userprofile.objects.filter(id=user_id)[0]
    print('------ 企业通讯录corp_id | 通讯录秘钥  ---->>>', user_obj.company.corp_id, user_obj.company.tongxunlu_secret)
    corp_id = user_obj.company.corp_id

    get_token_data['corpid'] = corp_id
    # app_secret = models.zgld_app.objects.get(company_id=user_obj.company_id, name='AI雷达').app_secret
    app_secret = models.zgld_app.objects.get(company_id=user_obj.company_id, app_type=1).app_secret



    get_token_data['corpsecret'] = app_secret
    print('-------- 企业ID | 应用的凭证密钥  get_token_data数据 ------->', get_token_data)


    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    key_name = "company_%s_leida_app_token" % (user_obj.company_id)
    token_ret = rc.get(key_name)

    print('-------  Redis缓存的 keyname |value -------->>',key_name,"|",token_ret)


    if not token_ret:
        ret = requests.get(Conf['token_url'], params=get_token_data)

        weixin_ret_data = ret.json()
        errcode = weixin_ret_data.get('errcode')
        errmsg = weixin_ret_data.get('errmsg')
        access_token = weixin_ret_data.get('access_token')
        print('--------- 从【企业微信】接口, 获取access_token 返回 -------->>', weixin_ret_data)


        if errcode == 0:
            rc.set(key_name, access_token, 7000)
            send_token_data['access_token'] = access_token

        else:
            response.code = errcode
            response.msg = "企业微信验证未能通过"
            print('----------- 获取 access_token 失败 : errcode | errmsg  -------->>',errcode,"|",errmsg)


            return JsonResponse(response.__dict__)

    else:
        send_token_data['access_token'] = token_ret

    userid = user_obj.userid
    post_send_data = {
        "touser": userid,
        # "toparty" : "PartyID1|PartyID2",
        # "totag" : "TagID1 | TagID2",
        "msgtype": "text",
        "agentid": int(agentid),
        "text": {
            "content": content,
        },
        "safe": 0
    }
    print('-------- 发送应用消息 POST json.dumps 格式数据:  ---------->>', json.dumps(post_send_data))


    inter_ret = requests.post(Conf['send_msg_url'], params=send_token_data, data=json.dumps(post_send_data))

    weixin_ret_data = inter_ret.json()
    errcode = weixin_ret_data.get('errcode')
    errmsg = weixin_ret_data.get('errmsg')

    print('---- 发送应用消息 【接口返回】 --->>', weixin_ret_data)


    if errmsg == "ok":
        response.code = 200
        response.msg = '发送成功'
        print('--------- 发送应用消息 【成功】----------->')

    else:
        response.code = errcode
        response.msg = "企业微信验证未能通过"
        print('---------- 发送应用消息 【失败】 : errcode | errmsg ----------->',errcode,'|',errmsg)

    return JsonResponse(response.__dict__)


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@csrf_exempt
def create_user_or_customer_qr_code(request):
    response = ResponseObj()
    print('---- celery request.GET | data 数据 -->', request.GET, '|', request.GET.get('data'))

    data = request.GET.get('data')
    if data:
         data = json.loads(request.GET.get('data'))
         user_id = data.get('user_id')
         customer_id = data.get('customer_id', '')

    else:
         # data = request.POST.get('user_id')
         print('---- celery request.POST | data 数据 -->',request.POST, '|')
         user_id = request.POST.get('user_id')
         customer_id = request.POST.get('customer_id', '')



    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    if not customer_id:
        path = '/pages/mingpian/index?uid=%s&source=1' % (user_id)
        user_qr_code = '/%s_%s_qrcode.jpg' % (user_id,now_time)

    else:
        path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
        user_qr_code = '/%s_%s_%s_qrcode.jpg' % (user_id ,customer_id,now_time)

    get_qr_data = {}
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
    company_id = userprofile_obj.company_id
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid


    component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
    key_name = '%s_authorizer_access_token' % (authorizer_appid)

    authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

    if not authorizer_access_token:
        data = {
            'key_name' : key_name,
            'authorizer_refresh_token': authorizer_refresh_token,
            'authorizer_appid': authorizer_appid,

        }
        authorizer_access_token_ret = create_authorizer_access_token(data)
        authorizer_access_token = authorizer_access_token_ret.data # 调用生成 authorizer_access_token 授权方接口调用凭据, 也简称为令牌。

    get_qr_data['access_token'] = authorizer_access_token

    post_qr_data = {'path': path, 'width': 430}
    qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

    if not qr_ret.content:
        rc.delete('xiaochengxu_token')
        response.msg = "生成小程序二维码未验证通过"

        return response

    # print('-------qr_ret---->', qr_ret.text)

    IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'qr_code') + user_qr_code
    with open('%s' % (IMG_PATH), 'wb') as f:
        f.write(qr_ret.content)


    if  customer_id:
        user_obj = models.zgld_user_customer_belonger.objects.get(user_id=user_id,customer_id=customer_id)
        user_qr_code_path = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
        user_obj.qr_code=user_qr_code_path
        user_obj.save()
        print('----celery生成用户-客户对应的小程序二维码成功-->>','statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

    else:
        user_obj = models.zgld_userprofile.objects.get(id=user_id)
        user_obj.qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
        user_obj.save()
        print('----celery生成企业用户对应的小程序二维码成功-->>','statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

    response.data = {'qr_code': user_obj.qr_code}
    response.code = 200
    response.msg = "生成小程序二维码成功"

    return JsonResponse(response.__dict__)



# 小程序生成token，并然后发送模板消息
@csrf_exempt
def user_send_template_msg(request):
    response = ResponseObj()

    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id')
    userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
    company_id = userprofile_obj.company_id
    print('company_id -->', company_id)
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id


    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    customer_obj = models.zgld_customer.objects.filter(id=customer_id)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
        customer_id=customer_id,
        user_id=user_id
    )
    exist_formid_json = json.loads(objs[0].customer.formid)
    user_name = objs[0].user.username
    flag = True
    while flag:

        post_template_data =  {}
        # get_token_data['appid'] = authorization_appid
        # get_token_data['secret'] = authorization_secret
        # get_token_data['grant_type'] = 'client_credential'

        component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
        key_name = '%s_authorizer_access_token' % (authorizer_appid)
        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            data = {
                'key_name' : key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,

            }
            authorizer_access_token = create_authorizer_access_token(data)

        get_template_data = {
            'access_token' : authorizer_access_token      #授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
        }
        # global openid,form_id
        if customer_obj and objs:
            openid = customer_obj[0].openid
            post_template_data['touser'] = openid

            # post_template_data['template_id'] = 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE'
            post_template_data['template_id'] = template_id
            # path = 'pages/mingpian/index?source=2&uid=%s&pid=' % (user_id)
            path = 'pages/mingpian/msg?source=template_msg&uid=%s&pid=' % (user_id)
            post_template_data['page'] = path

            if len(exist_formid_json) == 0:
                response.msg = "没有formID"
                response.code = 301
                print('------- 没有消费的formID -------->>')
                break

            print('---------formId 消费前数据----------->>',exist_formid_json)
            form_id = exist_formid_json.pop(-1)
            obj = models.zgld_customer.objects.filter(id=customer_id)

            obj.update(formid=json.dumps(exist_formid_json))
            print('---------formId 消费了哪个 ----------->>', form_id)
            post_template_data['form_id'] = form_id


            # 留言回复通知
            data = {
                'keyword1': {
                    'value': user_name  # 回复者
                },
                'keyword2': {
                    'value': now_time   # 回复时间
                },
                'keyword3': {
                    'value': '您有未读消息,点击小程序查看哦'  #回复内容
                }
            }
            post_template_data['data'] = data
            # post_template_data['emphasis_keyword'] = 'keyword1.DATA'
            print('===========post_template_data=======>>',post_template_data)

            # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考

            template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()

            print('--------企业用户 send to 小程序 Template 接口返回数据--------->',template_ret)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"
                flag = False

            elif template_ret.get('errcode') == 40001:
                rc.delete(key_name)

            else:
                print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"

        else:
            response.msg = "客户不存在"
            response.code = 301
            print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)



@csrf_exempt
def user_send_gongzhonghao_template_msg(request):
    response = ResponseObj()

    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id')

    userprofile_obj = models.zgld_userprofile.objects.select_related('company').get(id=user_id)
    company_id = userprofile_obj.company_id
    company_name = userprofile_obj.company.name

    obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id



    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    customer_obj = models.zgld_customer.objects.filter(id=customer_id)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
        customer_id=customer_id,
        user_id=user_id
    )

    user_name = objs[0].user.username
    position = objs[0].user.position
    flag = True
    while flag:

        post_template_data =  {}

        component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
        key_name = '%s_authorizer_access_token' % (authorizer_appid)
        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            # data = {
            #     'key_name' : key_name,
            #     'authorizer_refresh_token': authorizer_refresh_token,
            #     'authorizer_appid': authorizer_appid,
            #
            # }
            authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)

            authorizer_access_token = rc.get(authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

            if not authorizer_access_token:
                data = {
                    'key_name': authorizer_access_token_key_name,
                    'authorizer_refresh_token': authorizer_refresh_token,
                    'authorizer_appid': authorizer_appid,
                    'app_id': 'wx6ba07e6ddcdc69b3',
                    'app_secret': '0bbed534062ceca2ec25133abe1eecba'
                }
                authorizer_access_token_result = create_authorizer_access_token(data)
                if authorizer_access_token_result.code == 200:
                    authorizer_access_token = authorizer_access_token_result.data

        get_template_data = {
            'access_token' : authorizer_access_token      #授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
        }

        if customer_obj and objs:
            openid = customer_obj[0].openid
            post_template_data['touser'] = openid


            post_template_data['template_id'] = template_id

            path = 'pages/mingpian/msg?source=template_msg&uid=%s&pid=' % (user_id)
            post_template_data['page'] = path


            post_template_data['form_id'] = form_id


            # 留言回复通知
            '''
            您好，您咨询商家的问题已回复
            咨询名称：孕儿美摄影工作室张炬
            消息回复：您有未读消息哦
            点击进入咨询页面
            '''
            consult_info = ('%s-%s(%s)') %  (company_name,position,user_name)
            data = {
                'first': {
                    'value': '您好，有什么可以帮助到您的吗?'  # 回复者
                },
                'keyword1': {
                    'value': consult_info   # 回复者
                },
                'keyword2': {
                    'value': '您有未读消息哦'   # 回复时间
                },
                'remark': {
                    'value': '点击进入咨询页面'  #回复内容
                }
            }
            post_template_data['data'] = data
            # post_template_data['emphasis_keyword'] = 'keyword1.DATA'
            print('===========post_template_data=======>>',post_template_data)

            # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考

            template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()

            print('--------企业用户 send to 小程序 Template 接口返回数据--------->',template_ret)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"
                flag = False

            elif template_ret.get('errcode') == 40001:
                rc.delete(key_name)

            else:
                print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"

        else:
            response.msg = "客户不存在"
            response.code = 301
            print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)





#获取查询最新一次提交的审核状态 并提交审核通过的代码上线.
@csrf_exempt
def get_latest_audit_status_and_release_code(request):
    from zhugeleida.views_dir.admin.dai_xcx import  batch_get_latest_audit_status
    response = ResponseObj()

    if request.method == "GET":

        objs = models.zgld_xiapchengxu_upload_audit.objects.filter(audit_result=2, auditid__isnull=False).order_by('-audit_commit_date')

        audit_status_data = {
            'upload_audit_objs': objs
        }
        audit_status_response = batch_get_latest_audit_status(audit_status_data)  # 只管查询最后一次上传的代码，

        response.code = 200
        response.msg = '查询最新一次提交的审核状态-执行完成'

    return JsonResponse(response.__dict__)