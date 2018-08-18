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
    print('---------->>>', user_obj.company.corp_id, user_obj.company.tongxunlu_secret)
    corp_id = user_obj.company.corp_id

    get_token_data['corpid'] = corp_id
    # app_secret = models.zgld_app.objects.get(company_id=user_obj.company_id, name='AI雷达').app_secret
    app_secret = models.zgld_app.objects.get(company_id=user_obj.company_id, app_type=1).app_secret
    # if not app_secret:
    #     response.code = 404
    #     response.msg = "数据库不存在corpsecret"
    #     return response

    get_token_data['corpsecret'] = app_secret
    print('get_token_data -->', get_token_data)

    import redis
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    key_name = "company_%s_leida_app_token" % (user_obj.company_id)
    token_ret = rc.get(key_name)

    print('---token_ret---->>', token_ret)

    if not token_ret:
        ret = requests.get(Conf['token_url'], params=get_token_data)

        weixin_ret_data = ret.json()
        print('----weixin_ret_data--->', weixin_ret_data)

        if weixin_ret_data['errcode'] == 0:
            access_token = weixin_ret_data['access_token']
            send_token_data['access_token'] = access_token

            rc.set(key_name, access_token, 7000)

        else:
            print('企业微信验证未能通过')
            response.code = weixin_ret_data['errcode']
            response.msg = "企业微信验证未能通过"
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
    print('post_send_data ==>', post_send_data)

    inter_ret = requests.post(Conf['send_msg_url'], params=send_token_data, data=json.dumps(post_send_data))

    weixin_ret_data = json.loads(inter_ret.text)
    print('---- access_token --->>', weixin_ret_data)

    if weixin_ret_data['errcode'] == 0:
        response.code = 200
        response.msg = '发送成功'

    else:
        response.code = weixin_ret_data['errcode']
        response.msg = "企业微信验证未能通过"

    return JsonResponse(response.__dict__)


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@csrf_exempt
def create_user_or_customer_qr_code(request):
    response = ResponseObj()
    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id','')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    get_token_data = {}

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    if not customer_id:
        path = '/pages/mingpian/index?uid=%s&source=1' % (user_id)
        user_qr_code = '/%s_%s_qrcode.jpg' % (user_id,now_time)

    else:
        path = '/pages/mingpian/index?uid=%s&source=1&pid=%s' % (user_id, customer_id)  # 来源 1代表扫码 2 代表转发
        user_qr_code = '/%s_%s_%s_qrcode.jpg' % (user_id ,customer_id,now_time)

    get_qr_data = {}
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    # get_token_data['appid'] = Conf['appid']
    # get_token_data['secret'] = Conf['appsecret']
    # get_token_data['grant_type'] = 'client_credential'
    # company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
    # import redis

    # key_name = "company_%s_xiaochengxu_token" % (company_id)
    # token_ret = rc.get(key_name)
    # print('---token_ret---->>', token_ret)
    #
    # if not token_ret:
    #     # {"errcode": 0, "errmsg": "created"}
    #     token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
    #     token_ret_json = token_ret.json()
    #     print('-----token_ret_json------>', token_ret_json)
    #     if not token_ret_json.get('access_token'):
    #         response.code = token_ret_json['errcode']
    #         response.msg = "生成小程序二维码未验证通过"
    #         return response
    #
    #     access_token = token_ret_json['access_token']
    #     print('---- access_token --->>', token_ret_json)
    #     get_qr_data['access_token'] = access_token
    #
    #     rc.set(key_name, access_token, 7000)
    #
    # else:
    #     get_qr_data['access_token'] = token_ret
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
        authorizer_access_token = create_authorizer_access_token(data) # 调用生成 authorizer_access_token 授权方接口调用凭据, 也简称为令牌。

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
        obj = models.zgld_user_customer_belonger.objects.get(user_id=user_id,customer_id=customer_id)
        user_qr_code_path = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
        obj.qr_code=user_qr_code_path
        obj.save()
        print('----celery生成用户-客户对应的小程序二维码成功-->>','statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

    else:
        user_obj = models.zgld_userprofile.objects.get(id=user_id)
        user_obj.qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code
        user_obj.save()
        print('----celery生成企业用户对应的小程序二维码成功-->>','statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)


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
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id


    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    customer_obj = models.zgld_customer.objects.filter(id=customer_id)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    objs = models.zgld_user_customer_belonger.objects.filter(
        customer_id=customer_id, user_id=user_id
    )

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



        # key_name = "company_%s_xiaochengxu_token" % (company_id)
        # token_ret = rc.get(key_name)
        # print('---token_ret---->>', token_ret)
        #
        # if not token_ret:
        #     # {"errcode": 0, "errmsg": "created"}
        #     token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
        #     token_ret_json = token_ret.json()
        #     print('------- 生成小程序模板信息用的token： 接口返回数据------>', token_ret_json)
        #     if not token_ret_json.get('access_token'):
        #         response.code = token_ret_json['errcode']
        #         response.msg = "生成模板信息用的token未通过"
        #         return response
        #
        #     access_token = token_ret_json['access_token']
        #     print('---- access_token --->>', token_ret_json)
        #     get_template_data['access_token'] = access_token
        #     rc.set(key_name, access_token, 7000)
        #
        # else:
        #     get_template_data['access_token'] = token_ret
        get_template_data = {
            'access_token' : authorizer_access_token      #授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
        }
        global openid,form_id
        if customer_obj:
            form_id =  customer_obj[0].formid
            openid =  customer_obj[0].openid
            post_template_data['touser'] = openid

            # post_template_data['template_id'] = 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE'
            post_template_data['template_id'] = template_id
            path = 'pages/mingpian/index?source=2&uid=%s&pid=' % (user_id)
            post_template_data['page'] = path

            user_name = ''
            if objs:
                exist_formid_json = json.loads(objs[0].customer.formid )
                user_name = objs[0].user.username
                if len(exist_formid_json) == 0:
                    response.msg = "没有formID"
                    response.code = 301
                    print('------- 没有消费的formID -------->>')
                    return JsonResponse(response.__dict__)

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

            if  template_ret.get('errmsg') == "ok":
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


# 获取查询最新一次提交的审核状态 并提交审核通过的代码上线
@csrf_exempt
def get_latest_audit_status_and_release_code(data):
    response = Response.ResponseObj()
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    # forms_obj = GetLatestAuditForm(request.POST)
    # if forms_obj.is_valid():

    objs = models.zgld_xiapchengxu_upload_audit.objects.filter(audit_result=2, auditid__isnull=False)

    if objs:  # 如果在审核中，并有编号，说明提交了审核。定时器要不停的去轮训,一旦发现有通过审核的，就要触发上线操作,并记录下来。
        auditid = objs[0].auditid
        for obj in objs:

            app_id = obj.app_id
            get_latest_auditstatus_url = 'https://api.weixin.qq.com/wxa/get_latest_auditstatus'
            # app_id = forms_obj.cleaned_data.get('app_id')  # 账户
            # audit_code_id= forms_obj.cleaned_data.get('audit_code_id')

            # app_obj = models.zgld_xiaochengxu_app.objects.get(id=app_id)
            authorizer_refresh_token = obj.app.authorizer_refresh_token
            authorizer_appid = obj.app.authorization_appid

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
                    authorizer_access_token = authorizer_access_token_result.data
                else:
                    return JsonResponse(authorizer_access_token.__dict__)

            get_latest_audit_data = {
                'access_token': authorizer_access_token
            }
            print('------get_latest_audit_data--------<<', get_latest_audit_data)

            get_latest_audit_ret = requests.get(get_latest_auditstatus_url, params=get_latest_audit_data)
            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            get_latest_audit_ret = get_latest_audit_ret.json()
            print('------获取查询审核中+最新一次提交的审核状态 接口返回----->>', get_latest_audit_ret)

            errcode = get_latest_audit_ret.get('errcode')
            errmsg = get_latest_audit_ret.get('errmsg')
            status = int(get_latest_audit_ret.get('status'))
            reason = get_latest_audit_ret.get('reason')

            if status == 0:

                print('-------- 代码审核状态【成功】---- auditid | audit_code_id -------->>', auditid, '|', obj.app_id)
                release_obj = models.zgld_xiapchengxu_release.objects.filter(audit_code_id=obj.app_id)
                obj.audit_reply_date = now_time

                if not release_obj:  # 没有发布相关的代码记录,说明没有上过线呢。
                    release_url = 'https://api.weixin.qq.com/wxa/release'
                    get_release_data = {
                        'access_token': authorizer_access_token
                    }

                    get_release_ret = requests.post(release_url, params=get_release_data)
                    get_release_ret = get_release_ret.json()
                    errcode = int(get_release_ret.get('errcode'))
                    errmsg = get_release_ret.get('errmsg')
                    status = get_release_ret.get('status')
                    reason = get_release_ret.get('reason')
                    print('-------- 获取发布的状态 接口返回：---------->>', get_release_ret)

                    if errmsg == "ok":
                        release_result = 1  # 上线成功
                        reason = ''
                        print('--------发布已通过审核的小程序【成功】: auditid | audit_code_id -------->>', auditid, '|', obj.app_id)

                    else:
                        release_result = 2  # 上线失败
                        if errcode == -1:
                            reason = '系统繁忙'
                        elif errcode == 85019:
                            reason = '没有审核版本'
                        elif errcode == 85020:
                            reason = '审核状态未满足发布'
                        print('-------发布已通过审核的小程序【失败】auditid | audit_code_id -------->>', auditid, '|', obj.app_id)

                    models.zgld_xiapchengxu_release.objects.create(
                        app=app_id,
                        audit_code_id=obj.app_id,
                        release_result=release_result,
                        release_commit_date=now_time,
                        reason=reason
                    )
                    response.code = 200
                    response.msg = '审核成功ID'


            elif status == 1:  # 0为审核成功
                response.code = 200
                response.msg = '审核状态失败'
                print('-------- 代码审核状态【失败】---- auditid | audit_code_id -------->>', auditid, '|', obj.app_id)


            elif status == 2:
                response.code = 200
                response.msg = '审核中'
                print('-------- 代码审核状态【审核中】---- auditid | audit_code_id -------->>', auditid, '|', obj.app_id)

            obj.audit_result = status
            obj.reason = reason
            obj.save()

        # else:
        #     print("--验证不通过-->",forms_obj.errors.as_json())
        #     response.code = 301
        #     response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 302
        response.msg = '没有正在审核中的代码'
        print('-------- 没有正在【审核中】状态的代码 ------>>')

    return response