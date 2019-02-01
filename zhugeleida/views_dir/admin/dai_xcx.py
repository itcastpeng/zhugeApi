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
from zhugeleida.forms.admin.dai_xcx_verify import CommitCodeInfoForm,SubmitAuditForm,RelaseCodeInfoForm,AuditCodeInfoForm,GetAuditForm,RevertCodeReleaseForm

from zhugeleida.public.WorkWeixinOper import WorkWeixinOper


# 查询小程序审核状态 供dai_xcx_oper 调用
def relase_code(data):
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    response = Response.ResponseObj()
    app_id = data.get('app_id')
    audit_code_id = data.get('audit_code_id')
    auditid = data.get('auditid')
    key_name = data.get('key_name')
    xcx_app_obj = models.zgld_xiaochengxu_app.objects.get(id=app_id)

    # app_id = obj.app_id
    # audit_code_id = obj.id
    authorizer_access_token = data.get('authorizer_access_token')

    now_time = datetime.datetime.now()
    print('-------- 代码审核状态【成功】---- auditid | audit_code_id -------->>', auditid, '|', audit_code_id)
    # release_obj = models.zgld_xiapchengxu_release.objects.filter(audit_code_id=audit_code_id)

    release_url = 'https://api.weixin.qq.com/wxa/release'
    get_release_data = {
        'access_token': authorizer_access_token
    }
    post_release_data = {

    }

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    get_release_ret = s.post(release_url, params=get_release_data, data=json.dumps(post_release_data))

    # get_release_ret = requests.post(release_url, params=get_release_data, data=json.dumps(post_release_data))

    get_release_ret = get_release_ret.json()
    errcode = int(get_release_ret.get('errcode'))
    errmsg = get_release_ret.get('errmsg')
    status = get_release_ret.get('status')
    reason = get_release_ret.get('reason')
    print('-------- 获取发布的状态 接口返回：---------->>', get_release_ret)

    if errmsg == "ok":
        xcx_app_obj.code_release_status = 7
        xcx_app_obj.code_release_result = '成功'

        # 目前版本号
        upload_audit_obj =  models.zgld_xiapchengxu_upload_audit.objects.filter(auditid=auditid)

        if  upload_audit_obj:
            upload_audit_obj = upload_audit_obj[0]
            now_version_num = upload_audit_obj.version_num
            xcx_app_obj.version_num = now_version_num


        release_result = 1  # 上线成功
        reason = ''



        response.code = 200
        response.msg = '上线成功'

        print('--------发布已通过审核的小程序【成功】: auditid | audit_code_id -------->>', auditid, '|', audit_code_id)

    else:
        code_release_result = '上线报错: %s : %s' % (errmsg,reason)
        xcx_app_obj.code_release_status = 8
        xcx_app_obj.code_release_result =  code_release_result

        release_result = 2  # 上线失败
        if errcode == -1:
            reason = '系统繁忙'
        elif errcode == 85019:
            reason = '没有审核版本'
        elif errcode == 85020:
            reason = '审核状态未满足发布'

        rc.delete(key_name)
        rc.delete('component_access_token')
        if not reason:
            reason = errmsg

        response.code = 303
        response.msg = reason

        print('-------发布已通过审核的小程序【失败】auditid | audit_code_id -------->>', auditid, '|', audit_code_id)

    xcx_app_obj.save()
    models.zgld_xiapchengxu_release.objects.create(
        app_id=app_id,
        audit_code_id=audit_code_id,
        release_result=release_result,
        release_commit_date=now_time,
        reason=reason
    )
    # else:
    #     models.zgld_xiapchengxu_release.objects.update(
    #         app_id=app_id,
    #         release_commit_date=now_time,
    #         release_result=release_result,
    #         reason=reason
    #     )
    return  response

# 获取（刷新）授权小程序的接口调用凭据
def create_authorizer_access_token(data):
    response = Response.ResponseObj()
    authorizer_appid = data.get('authorizer_appid')
    authorizer_refresh_token = data.get('authorizer_refresh_token')
    key_name = data.get('key_name')
    # app_id = data.get('app_id')
    # app_secret = data.get('app_secret')

    company_id = data.get('company_id')
    app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)
    services_type = app_objs[0].three_services_type

    three_services_type = ''
    if services_type == 1:  # (1, '小程序(名片版)第三方平台'),
        three_services_type = 3
    elif services_type == 2:  # (2, '小程序(案例库)第三方平台')
        three_services_type = 4

    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=three_services_type) # 小程序
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        qywx_config_dict = three_service_obj.config
        if qywx_config_dict:
            qywx_config_dict = json.loads(qywx_config_dict)

        app_id =  qywx_config_dict.get('app_id')
        app_secret = qywx_config_dict.get('app_secret')


        # app_id = 'wx67e2fde0f694111c' # 小程序
        # app_secret = '4a9690b43178a1287b2ef845158555ed'
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

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            component_token_ret = s.post(post_component_url, data=json.dumps(post_component_data))

            # component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))

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
        print('---- 接口调用凭据 post_auth_token_data : --->',post_auth_token_data)
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        authorizer_info_ret = s.post(authorizer_token_url, params=get_auth_token_data,data=json.dumps(post_auth_token_data))

        # authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data,data=json.dumps(post_auth_token_data))

        authorizer_info_ret = authorizer_info_ret.json()

        print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)

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
            print('------ 获取令牌（authorizer_access_token）成功------>>',authorizer_access_token)

        else:
            print('------ 获取令牌（authorizer_access_token）为空------>>')
            response.code = 400
            response.msg = "获取令牌authorizer_access_token为空"
            return JsonResponse(response.__dict__)

        return  response

    else:
        response.code = 301
        response.msg = '公众号第三方-无配置信息'
        print('------ 【公众号第三方-无配置信息】 create_authorizer_access_token ------>>')

# 获取第三方平台 component_token_ret.json
def create_component_access_token(company_id):
    response = Response.ResponseObj()

    app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)
    services_type = app_objs[0].three_services_type
    three_services_type = ''
    if services_type == 1:  # (1, '小程序(名片版)第三方平台'),
        three_services_type = 3
    elif services_type == 2:  # (2, '小程序(案例库)第三方平台')
        three_services_type = 4


    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=three_services_type) # 小程序
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        qywx_config_dict = three_service_obj.config
        if qywx_config_dict:
            qywx_config_dict = json.loads(qywx_config_dict)

        app_id =  qywx_config_dict.get('app_id')
        app_secret = qywx_config_dict.get('app_secret')

        # app_id = 'wx67e2fde0f694111c'
        # app_secret = '4a9690b43178a1287b2ef845158555ed'
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

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            component_token_ret = s.post(post_component_url, data=json.dumps(post_component_data))

            # component_token_ret = requests.post(post_component_url, data=json.dumps(post_component_data))

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

        return    component_access_token

    else:
        response.code = 301
        response.msg = '公众号第三方-无配置信息'
        print('------ 【公众号第三方-无配置信息】create_component_access_token ------>>')

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def dai_xcx_oper(request, oper_type):
    response = Response.ResponseObj()
    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    if request.method == "POST":

        # 第三方代小程序上传
        if oper_type   == 'upload_code':

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
                user_id = request.GET.get('user_id')  # 账户
                app_ids_list = request.POST.get('app_ids_list')  # 账户
                user_version = forms_obj.cleaned_data.get('user_version') # 版本
                template_id = forms_obj.cleaned_data.get('template_id')   #模板ID
                user_desc = forms_obj.cleaned_data.get('user_desc')       #描述
                # ext_json = forms_obj.cleaned_data.get('ext_json')
                app_ids_list = json.loads(app_ids_list)

                objs = models.zgld_xiaochengxu_app.objects.filter(id__in=app_ids_list)
                if objs:
                    for obj in objs:
                        authorizer_refresh_token = obj.authorizer_refresh_token
                        authorizer_appid = obj.authorization_appid

                        ext_json = {
                            "extEnable": "true",
                            "directCommit": "false"
                        }

                        ext_json['extAppid'] = authorizer_appid
                        ext_json['ext'] = {
                            'company_id': obj.company_id,
                            'user_version': user_version
                        }

                        user_version = user_version
                        template_id = template_id

                        # ext_json = {
                        #     'extEnable': 'true',
                        #     'extAppid': authorizer_appid,
                        #     'directCommit': 'false',
                        # }
                        # app_id = 'wx67e2fde0f694111c'
                        # app_secret = '4a9690b43178a1287b2ef845158555ed'


                        key_name = '%s_authorizer_access_token' % (authorizer_appid)
                        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                        if not authorizer_access_token:
                            data = {
                                'key_name': key_name,
                                'authorizer_refresh_token' : authorizer_refresh_token,
                                'authorizer_appid' : authorizer_appid,
                                'company_id': obj.company_id
                            }
                            authorizer_access_token_result = create_authorizer_access_token(data)
                            if authorizer_access_token_result.code == 200:
                                authorizer_access_token = authorizer_access_token_result.data
                            else:
                                return JsonResponse(authorizer_access_token.__dict__)


                        print('------ 第三方自定义的配置 ext_json ------>',json.dumps(ext_json))
                        get_wxa_commit_data =  {
                            'access_token': authorizer_access_token
                        }

                        post_wxa_commit_data = {
                            'template_id': template_id,        # 代码库中的代码模版ID
                            'ext_json': json.dumps(ext_json),  # 第三方自定义的配置
                            'user_version': user_version,      # 代码版本号，开发者可自定义
                            'user_desc': user_desc  # 代码描述，开发者可自定义
                        }

                        commit_url = 'https://api.weixin.qq.com/wxa/commit'

                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        wxa_commit_info_ret = s.post(commit_url, params=get_wxa_commit_data, data=json.dumps(post_wxa_commit_data))

                        # wxa_commit_info_ret = requests.post(commit_url, params=get_wxa_commit_data, data=json.dumps(post_wxa_commit_data))

                        wxa_commit_info_ret = wxa_commit_info_ret.json()
                        print('--------为授权的小程序帐号上传小程序代码 接口返回---------->>',wxa_commit_info_ret)

                        errcode = wxa_commit_info_ret.get('errcode')
                        errmsg = wxa_commit_info_ret.get('errmsg')
                        if int(errcode) == 0:
                            errcode = 0
                            reason = ''
                            code_release_status = 1
                            code_release_result = '成功'
                        else:
                            code_release_status = 2
                            code_release_result = '上传小程序报错: %s' %  errmsg
                            errcode = 1
                            reason = code_release_result

                        datetime_now = datetime.datetime.now()
                        upload_code_obj = models.zgld_xiapchengxu_upload_audit.objects.create(
                            app_id=obj.id,
                            publisher_id=user_id,
                            desc=user_desc,
                            version_num=user_version,
                            template_id=template_id,
                            upload_code_date=datetime_now,
                            upload_result = errcode,
                            reason=reason,
                        )

                        obj.code_release_status=code_release_status
                        obj.code_release_result=code_release_result
                        obj.save()


                        if errcode == 0:

                            response.code = 200
                            response.msg = '小程序帐号上传小程序代码成功'
                            print('------ 代小程序上传代码成功 ------>>')
                        else:
                            response.code = errcode
                            response.msg = errmsg  # https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1489140610_Uavc4&token=&lang=zh_CN
                            return  JsonResponse(response.__dict__)


                        get_qrcode_url = 'https://api.weixin.qq.com/wxa/get_qrcode'
                        # app_id = forms_obj.cleaned_data.get('app_id')  # 账户
                        # upload_code_id = forms_obj.cleaned_data.get('upload_code_id')


                        key_name = '%s_authorizer_access_token' % (authorizer_appid)
                        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                        if not authorizer_access_token:
                            data = {
                                'key_name': key_name,
                                'authorizer_refresh_token': authorizer_refresh_token,
                                'authorizer_appid': authorizer_appid,
                                'company_id': obj.company_id
                            }
                            authorizer_access_token_result = create_authorizer_access_token(data)
                            if authorizer_access_token_result.code == 200:
                                authorizer_access_token = authorizer_access_token_result.data
                            else:
                                return JsonResponse(authorizer_access_token.__dict__)
                        path = 'pages/mingpian/index'
                        # path = 'pages/mingpian/index?uid=1&source=1'
                        get_qrcode_data = {
                            'access_token': authorizer_access_token,
                            'path': path,
                        }

                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        get_qrcode_ret = s.get(get_qrcode_url, params=get_qrcode_data)

                        # get_qrcode_ret = requests.get(get_qrcode_url, params=get_qrcode_data)

                        try:

                            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                            BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'admin', 'qr_code')

                            qr_code_name = '/%s_%s_QRCode.jpg' % (authorizer_appid, now_time)

                            path_qr_code_name = BASE_DIR + qr_code_name
                            qr_url = 'statics/zhugeleida/imgs/admin/qr_code%s' % (qr_code_name)

                            with open(path_qr_code_name, 'wb') as f:
                                f.write(get_qrcode_ret.content)

                            response.code = 200
                            response.msg = '生成并获取小程序体验码成功'
                            print('---------生成并获取小程序体验码成功--------->>',qr_url)


                            upload_code_obj.experience_qrcode=qr_url
                            upload_code_obj.save()



                        except Exception as e:
                            response.code = 301
                            response.msg = '小程序的体验二维码_接口返回-错误'
                            print('------- 获取体验小程序的体验二维码_接口返回-错误 ---->>', get_qrcode_ret.text, '|', e)
                            return JsonResponse(response.__dict__)




                else:
                    print("验证不通过")
                    response.code = 301
                    response.msg = json.loads(forms_obj.errors.as_json())

        # 代码包提交审核
        elif oper_type == 'submit_audit':


            forms_obj = AuditCodeInfoForm(request.POST)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')  # 账户
                app_ids_list = forms_obj.cleaned_data.get('app_ids_list')  # 账户

                app_ids_list = json.loads(app_ids_list)
                objs = models.zgld_xiaochengxu_app.objects.filter(id__in=app_ids_list)
                if objs:
                    for obj in objs:

                        upload_code_obj = models.zgld_xiapchengxu_upload_audit.objects.filter(app_id=obj.id).order_by('-upload_code_date')
                        if upload_code_obj:
                                upload_code_obj = upload_code_obj[0]
                                auditid = upload_code_obj.auditid
                                upload_result = upload_code_obj.upload_result
                                if auditid  or upload_result != 0:
                                    print('------------ 已有正在审核中的的代码 或者上传的代码失败 - auditid | id ------------------>>', auditid,'|',upload_code_obj.id)
                                    continue

                                authorizer_refresh_token = obj.authorizer_refresh_token
                                authorizer_appid = obj.authorization_appid

                                key_name = '%s_authorizer_access_token' % (authorizer_appid)
                                authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                                if not authorizer_access_token:
                                    data = {
                                        'key_name': key_name,
                                        'authorizer_refresh_token': authorizer_refresh_token,
                                        'authorizer_appid': authorizer_appid,
                                        'company_id': obj.company_id
                                    }
                                    authorizer_access_token_result = create_authorizer_access_token(data)
                                    if authorizer_access_token_result.code == 200:
                                        authorizer_access_token = authorizer_access_token_result.data
                                    else:
                                        return JsonResponse(authorizer_access_token.__dict__)

                                ## 获取小程序的第三方提交代码的页面配置
                                get_page_url = 'https://api.weixin.qq.com/wxa/get_page'
                                get_page_data = {
                                    'access_token': authorizer_access_token,
                                }

                                s = requests.session()
                                s.keep_alive = False  # 关闭多余连接
                                page_data_ret = s.get(get_page_url, params=get_page_data)

                                # page_data_ret = requests.get(get_page_url, params=get_page_data)
                                page_data_ret = page_data_ret.json()
                                errcode = page_data_ret.get('errcode')
                                errmsg = page_data_ret.get('errmsg')
                                page_list = page_data_ret.get('page_list')

                                print('-------- 第三方提交代码的页面配置 page_data_ret 返回------>>', page_data_ret)
                                if errcode == 0:

                                    print('-----page_list--->>', page_list)
                                    # -----page_list--->> ['pages/index/index', 'pages/logs/logs']


                                else:
                                    response.code = errcode
                                    response.msg = '获取第三方-页面配置报错: %s' % (errmsg)
                                    return JsonResponse(response.__dict__)

                                # 获取授权小程序帐号的可选类目
                                get_category_url = 'https://api.weixin.qq.com/wxa/get_category'
                                get_category_data = {
                                    'access_token': authorizer_access_token,
                                }

                                s = requests.session()
                                s.keep_alive = False  # 关闭多余连接
                                page_category_ret = s.get(get_category_url, params=get_category_data)

                                # page_category_ret = requests.get(get_category_url, params=get_category_data)
                                page_category_ret = page_category_ret.json()
                                errcode = page_category_ret.get('errcode')
                                errmsg = page_category_ret.get('errmsg')
                                category_list = page_category_ret.get('category_list')

                                print('-------- 获取授权小程序帐号的可选类目 page_category_ret 返回------>>', page_category_ret)
                                if errcode == 0:
                                    print('----- 可选类目 category_list--->>', category_list)
                                    # -----category_list--->> [{'first_class': 'IT科技', 'second_class': '硬件与设备', 'first_id': 210, 'second_id': 211}]
                                    response.code = 200
                                    response.msg = '提交审核代码成功'

                                else:
                                    response.code = errcode
                                    response.msg = '获取第三方-页面配置报错: %s' % (errmsg)
                                    return JsonResponse(response.__dict__)

                                submit_audit_url = 'https://api.weixin.qq.com/wxa/submit_audit'
                                item_list = []

                                # -----page_list--->> ['pages/index/index', 'pages/logs/logs']
                                item_dict = {
                                    'address': page_list[0],
                                    'first_class': category_list[0].get('first_class'),
                                    'second_class': category_list[0].get('second_class'),
                                    'first_id': category_list[0].get('first_id'),
                                    'second_id': category_list[0].get('second_id'),
                                    'tag': '名片',
                                    'title': '名片'
                                }

                                item_list.append(item_dict)

                                '''
                                {'errcode': 0, 'errmsg': 'ok', 'page_list': ['pages/index/index', 'pages/logs/logs'] }
                    
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
                                    'item_list': item_list
                                }
                                post_submit_audit_data = json.dumps(post_submit_audit_data, ensure_ascii=False)
                                print('---- json.dumps(post_submit_audit_data) --->>', post_submit_audit_data)

                                s = requests.session()
                                s.keep_alive = False  # 关闭多余连接
                                submit_audit_ret = s.post(submit_audit_url, params=get_submit_audit_data, data=post_submit_audit_data.encode('utf-8'))

                                # submit_audit_ret = requests.post(submit_audit_url, params=get_submit_audit_data, data=post_submit_audit_data.encode('utf-8'))

                                submit_audit_ret = submit_audit_ret.json()
                                auditid = submit_audit_ret.get('auditid')
                                errcode = submit_audit_ret.get('errcode')
                                errmsg = submit_audit_ret.get('errmsg')
                                now_time = datetime.datetime.now()
                                print('-------- 代码包-提交审核 返回 submit_audit_ret 返回------>>', submit_audit_ret)
                                if errmsg == 'ok':

                                    print('-----auditid--->>', auditid)
                                    audit_result = 2  # (2,'审核中')
                                    code_release_status = 4 # app 代码发布流程显示的状态。
                                    code_release_result = '成功'
                                    reason = ''
                                    response.code = 200
                                    response.msg = '提交审核代码成功'

                                else:

                                    audit_result = 3  # (3,'提交审核失败')
                                    code_release_status = 3  # app 代码发布流程显示的状态。
                                    response.code = errcode
                                    reason = '提交审核代码报错: %s : %s' % (errcode, errmsg)
                                    response.msg = reason
                                    code_release_result = reason

                                obj.code_release_status = code_release_status
                                obj.code_release_result = code_release_result
                                obj.save()

                                upload_code_obj.auditid = auditid
                                upload_code_obj.audit_commit_date = now_time
                                upload_code_obj.audit_result = audit_result  # (2,'审核中')
                                upload_code_obj.reason = reason  # (2,'审核中')
                                upload_code_obj.save()


                else:
                    response.code = 301
                    response.msg = '没有需要提交审核的小程序'

        # 发布代码
        elif oper_type == 'relase_code':

            forms_obj = RelaseCodeInfoForm(request.POST)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')  # 账户
                app_ids_list = request.POST.get('app_ids_list')  # 账户  # 账户
                app_ids_list = json.loads(app_ids_list)

                forms_obj = AuditCodeInfoForm(request.POST)
                if forms_obj.is_valid():
                    user_id = request.GET.get('user_id')  # 账户
                    objs = models.zgld_xiaochengxu_app.objects.filter(id__in=app_ids_list)
                    if objs:
                        for obj in objs:

                            upload_code_obj = models.zgld_xiapchengxu_upload_audit.objects.filter(app_id=obj.id,
                                                                                                  auditid__isnull=False).order_by(
                                '-audit_commit_date')[0]

                            authorizer_refresh_token = obj.authorizer_refresh_token
                            authorizer_appid = obj.authorization_appid

                            key_name = '%s_authorizer_access_token' % (authorizer_appid)
                            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                            if not authorizer_access_token:
                                data = {
                                    'key_name': key_name,
                                    'authorizer_refresh_token': authorizer_refresh_token,
                                    'authorizer_appid': authorizer_appid,
                                    'company_id': obj.company_id
                                }
                                authorizer_access_token_result = create_authorizer_access_token(data)
                                if authorizer_access_token_result.code == 200:
                                    authorizer_access_token = authorizer_access_token_result.data
                                else:
                                    return JsonResponse(authorizer_access_token.__dict__)

                            # for obj in objs: # 循环上线代码
                            # {'errcode': 0, 'errmsg': 'ok', 'auditid': 451831474, 'status': 1, 'reason': '1:
                            relase_data = {
                                'key_name': key_name,
                                'app_id': upload_code_obj.app_id,
                                'audit_code_id': upload_code_obj.id,
                                'auditid': upload_code_obj.auditid,
                                'authorizer_access_token': authorizer_access_token
                            }
                            print('-------POST --> relase_data----------->>',relase_data)
                            response = relase_code(relase_data)

                    response.code = 200
                    response.msg = '发布已经审核通过的代码-执行完成'

                else:
                    response.code = 301
                    response.msg = '没有正在审核中的代码'

        # 撤销审核
        elif oper_type == 'undocode_audit':
            forms_obj = AuditCodeInfoForm(request.POST)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')  # 账户
                app_ids_list = forms_obj.cleaned_data.get('app_ids_list')  # 账户

                app_ids_list = json.loads(app_ids_list)
                objs = models.zgld_xiaochengxu_app.objects.filter(id__in=app_ids_list)
                if objs:
                    for obj in objs:
                        authorizer_refresh_token = obj.authorizer_refresh_token
                        authorizer_appid = obj.authorization_appid
                        now_time = datetime.datetime.now()
                        upload_code_objs = models.zgld_xiapchengxu_upload_audit.objects.filter(app_id=obj.id,
                                                                                              audit_result=2,
                                                                                              auditid__isnull=False).order_by(
                            '-upload_code_date')
                        if upload_code_objs:
                            upload_code_obj = upload_code_objs[0]

                            undocode_audit_url = 'https://api.weixin.qq.com/wxa/undocodeaudit'
                            key_name = '%s_authorizer_access_token' % (authorizer_appid)
                            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                            if not authorizer_access_token:
                                data = {
                                    'key_name': key_name,
                                    'authorizer_refresh_token': authorizer_refresh_token,
                                    'authorizer_appid': authorizer_appid,
                                    'company_id': obj.company_id
                                }
                                print('--- 创建token 数据data-->>',data)
                                authorizer_access_token_result = create_authorizer_access_token(data)
                                if authorizer_access_token_result.code == 200:
                                    authorizer_access_token = authorizer_access_token_result.data
                                else:
                                    return JsonResponse(authorizer_access_token_result.__dict__)

                            print('---- 生成token authorizer_appid | authorizer_access_token -->',authorizer_appid,authorizer_access_token)


                            undocode_audit_data = {
                                'access_token': authorizer_access_token
                            }

                            s = requests.session()
                            s.keep_alive = False  # 关闭多余连接
                            undocode_audit_ret = s.get(undocode_audit_url, params=undocode_audit_data)

                            # undocode_audit_ret = requests.get(undocode_audit_url, params=undocode_audit_data)

                            undocode_audit_ret = undocode_audit_ret.json()
                            reason = ''
                            errmsg = undocode_audit_ret.get('errmsg')
                            errcode = undocode_audit_ret.get('errcode')

                            if errmsg == 'ok':
                                response.code = 200
                                response.msg = '小程序审核撤回成功'
                                audit_result = 4  # (4,'审核撤回成功'),
                                print('-------- 小程序审核撤回成功 --------->>',authorizer_appid)
                            else:
                                response.code = 304
                                response.msg = '小程序审核撤回失败'
                                audit_result = 5  # (5,'审核撤回失败'),
                                if int(errcode) == -1:
                                    reason = '系统错误'
                                elif int(errcode) == 87013:
                                    reason = '撤回次数达到上限（每天一次，每个月10次）'

                                reason = '审核撤回报错: %s:%s' % (errmsg, reason)
                                print('-------- 小程序审核撤回失败  errcode | errmsg   --------->>', errcode, errmsg)

                            upload_code_obj.reason = reason
                            upload_code_obj.audit_result = audit_result
                            upload_code_obj.audit_reply_date = now_time
                            upload_code_obj.save()

                        else:
                            response.code = 301
                            response.msg = '没有正在审核中的代码'
                            print('-------- 没有正在审核中的代码 xcx_app_id：---------->', obj.id)

            else:
                response.code = 402
                response.msg = "未验证通过"
                response.data = json.loads(forms_obj.errors.as_json())

        # 代码回滚
        elif oper_type == 'revert_code_release':
            forms_obj = RevertCodeReleaseForm(request.POST)

            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')  # 账户
                app_ids_list = forms_obj.cleaned_data.get('app_ids_list')  # 账户

                app_ids_list = json.loads(app_ids_list)
                objs = models.zgld_xiaochengxu_app.objects.filter(id__in=app_ids_list)
                if objs:
                    for obj in objs:
                        authorizer_refresh_token = obj.authorizer_refresh_token
                        authorizer_appid = obj.authorization_appid
                        now_time = datetime.datetime.now()
                        upload_code_obj = models.zgld_xiapchengxu_upload_audit.objects.filter(app_id=obj.id,
                                                                                              auditid__isnull=False).order_by(
                            '-audit_commit_date')
                        if upload_code_obj:
                            upload_code_obj = upload_code_obj[0]
                            key_name = '%s_authorizer_access_token' % (authorizer_appid)
                            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                            if not authorizer_access_token:
                                data = {
                                    'key_name': key_name,
                                    'authorizer_refresh_token': authorizer_refresh_token,
                                    'authorizer_appid': authorizer_appid,
                                    'company_id': obj.company_id
                                }
                                authorizer_access_token_result = create_authorizer_access_token(data)
                                if authorizer_access_token_result.code == 200:
                                    authorizer_access_token = authorizer_access_token_result.data
                                else:
                                    return JsonResponse(authorizer_access_token.__dict__)

                            get_wx_info_data = {
                                'access_token': authorizer_access_token
                            }

                            url = 'https://api.weixin.qq.com/wxa/revertcoderelease'

                            s = requests.session()
                            s.keep_alive = False  # 关闭多余连接
                            authorizer_info_ret = s.get(url, params=get_wx_info_data)

                            # authorizer_info_ret = requests.get(url, params=get_wx_info_data)
                            authorizer_info_ret = authorizer_info_ret.json()
                            print('----------- 版库中的所有小程序代码模版 返回 ------------->', json.dumps(authorizer_info_ret))
                            errmsg = authorizer_info_ret.get('errmsg')
                            errcode = authorizer_info_ret.get('errcode')

                            reason=''
                            if errmsg == 'ok':

                                release_result = 3  # (4,'审核撤回成功'),
                                response.code = 200
                                response.msg = '小程序版本回退成功'
                                print('-------- 小程序版本回退成功 --------->>')

                            else:
                                response.code = 304
                                response.msg = '小程序版本回退失败'
                                release_result = 4  # (5,'审核撤回失败'),
                                reason = '版本撤回失败:%s | %s' % (errcode,errmsg)
                                print('-------- 小程序版本撤回失败  errcode | errmsg   --------->>', errcode, errmsg)

                            models.zgld_xiapchengxu_release.objects.create(
                                app_id=authorizer_appid,
                                audit_code_id=upload_code_obj.id,
                                release_result=release_result,
                                release_commit_date=now_time,
                                reason=reason
                            )

                        else:
                            response.code = 302
                            response.msg = '没有符合的正在审核过得的代码'


    elif  request.method == "GET":

        # 获取模板列表
        if oper_type == "template_list":

            gettemplate_list_url = 'https://api.weixin.qq.com/wxa/gettemplatelist'
            user_id =request.GET.get('user_id')

            company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id

            response_ret = create_component_access_token(company_id)
            component_access_token = response_ret

            gettemplate_list_data = {
                'access_token': component_access_token
            }

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            gettemplate_list_ret = s.post(gettemplate_list_url, params=gettemplate_list_data)

            # gettemplate_list_ret = requests.post(gettemplate_list_url, params=gettemplate_list_data)
            gettemplate_list_ret = gettemplate_list_ret.json()
            errmsg = gettemplate_list_ret.get('errmsg')
            template_list = gettemplate_list_ret.get('template_list')

            print('----------- 版库中的所有小程序代码模版 返回 ------------->', json.dumps(gettemplate_list_ret))
            if errmsg == 'ok':
                response.data = {
                    'template_list': template_list,
                }
                response.code = 200
                response.msg = '获取成功'
            else:
                response.code = 301
                response.msg = '获取失败'

        # 获取查询最新一次提交的审核状态 并提交审核通过的代码上线
        elif oper_type == 'get_latest_audit_status':

            objs = models.zgld_xiapchengxu_upload_audit.objects.filter(audit_result=2, auditid__isnull=False)

            audit_status_data = {
                'upload_audit_objs': objs
            }
            audit_status_response = batch_get_latest_audit_status(audit_status_data)  # 只管查询最后一次上传的代码，

            response.code = 200
            response.msg = '查询最新一次提交的审核状态-执行完成'

            # 查询某个指定版本的审核状态

        # 查询最新一次提交的审核状态，并把审核通过的代码提交上线。
        elif oper_type == 'get_auditstatus':
            forms_obj = GetAuditForm(request.POST)

            if forms_obj.is_valid():

                get_auditstatus_url = 'https://api.weixin.qq.com/wxa/get_auditstatus'
                app_id = forms_obj.cleaned_data.get('app_id')  # 账户
                audit_code_id = forms_obj.cleaned_data.get('audit_code_id')

                obj = models.zgld_xiaochengxu_app.objects.get(id=app_id)
                authorizer_refresh_token = obj.authorizer_refresh_token
                authorizer_appid = obj.authorization_appid

                key_name = '%s_authorizer_access_token' % (authorizer_appid)
                authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

                if not authorizer_access_token:
                    data = {
                        'key_name': key_name,
                        'authorizer_refresh_token': authorizer_refresh_token,
                        'authorizer_appid': authorizer_appid,
                        'company_id': obj.company_id
                    }
                    authorizer_access_token_result = create_authorizer_access_token(data)
                    if authorizer_access_token_result.code == 200:
                        authorizer_access_token = authorizer_access_token_result.data
                    else:
                        return JsonResponse(authorizer_access_token.__dict__)

                obj = models.zgld_xiapchengxu_upload_audit.objects.get(id=audit_code_id)

                if obj:

                    auditid = obj.auditid
                    get_audit_data = {
                        'access_token': authorizer_access_token
                    }
                    post_audit_data = {
                        'auditid': auditid
                    }

                    s = requests.session()
                    s.keep_alive = False  # 关闭多余连接
                    get_audit_ret = s.post(get_auditstatus_url, params=get_audit_data, data=post_audit_data)

                    # get_audit_ret = requests.post(get_auditstatus_url, params=get_audit_data, data=post_audit_data)

                    get_audit_ret = get_audit_ret.json()
                    errcode = get_audit_ret.get('errcode')
                    reason = get_audit_ret.get('reason')
                    status = get_audit_ret.get('status')
                    if status == 0:

                        response.code = 200
                        response.msg = '审核状态成功'

                    elif status == 1:  # 0为审核成功
                        response.code = 200
                        response.msg = '审核状态失败'

                    elif status == 2:
                        response.code = 200
                        response.msg = '审核中'

                    obj.audit_result = status
                    obj.reason = reason
                    obj.save()

                else:
                    print("--验证不通过-->", forms_obj.errors.as_json())
                    response.code = 301
                    response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


# 定时刷新 小程序审核
def  batch_get_latest_audit_status(data):
    response = Response.ResponseObj()
    objs = data.get('upload_audit_objs')
    now_time = datetime.datetime.now()

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    if objs:                            # 如果在审核中，并有编号，说明提交了审核。定时器要不停的去轮训,一旦发现有通过审核的，就要触发上线操作,并记录下来。
        auditid = objs[0].auditid
        for obj in objs:

            get_latest_auditstatus_url = 'https://api.weixin.qq.com/wxa/get_latest_auditstatus'

            authorizer_refresh_token = obj.app.authorizer_refresh_token
            authorizer_appid = obj.app.authorization_appid
            xcx_app_id = obj.app.id

            key_name = '%s_authorizer_access_token' % (authorizer_appid)
            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

            if not authorizer_access_token:
                data = {
                    'key_name': key_name,
                    'authorizer_refresh_token': authorizer_refresh_token,
                    'authorizer_appid': authorizer_appid,
                    'company_id': obj.app.company_id
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

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            get_latest_audit_ret = s.get(get_latest_auditstatus_url, params=get_latest_audit_data)

            # get_latest_audit_ret = requests.get(get_latest_auditstatus_url, params=get_latest_audit_data)

            get_latest_audit_ret = get_latest_audit_ret.json()
            print('------获取查询审核中+最新一次提交的审核状态 接口返回----->>', get_latest_audit_ret)

            errcode = get_latest_audit_ret.get('errcode')
            errmsg = get_latest_audit_ret.get('errmsg')
            status = int(get_latest_audit_ret.get('status'))
            reason = get_latest_audit_ret.get('reason')
            xcx_app_obj = models.zgld_xiaochengxu_app.objects.get(id=xcx_app_id)

            if status == 0:
                obj.audit_reply_date = now_time
                response.code = 0
                response.msg = '审核成功'
                xcx_app_obj.code_release_status = 5
                xcx_app_obj.code_release_result = '成功'

                print('-------- 代码审核状态为【成功】---- auditid | audit_code_id -------->>', auditid, '|', obj.app_id)

                # ### 开始上线
                # relase_data = {
                #     'app_id' : obj.app_id,
                #     'audit_code_id' : obj.audit_code_id,
                #     'auditid' : auditid
                # }
                # obj.audit_reply_date = now_time
                # # {'errcode': 0, 'errmsg': 'ok', 'auditid': 451831474, 'status': 1, 'reason': '1:
                # relase_code(relase_data)


            elif status == 1:  #
                obj.audit_reply_date = now_time
                code_release_result = '代码审核状态报错: %s : %s' % (errmsg,reason)

                xcx_app_obj.code_release_status = 6
                xcx_app_obj.code_release_result = code_release_result
                response.code = 1
                response.msg = '审核状态失败'
                print('-------- 代码审核状态为【失败】---- auditid | audit_code_id -------->>', auditid, '|', obj.app_id)


            elif status == 2:
                xcx_app_obj.code_release_status = 4
                xcx_app_obj.code_release_result = '审核中'
                response.code = 2
                response.msg = '审核中'
                print('-------- 代码审核状态为【审核中】---- auditid | audit_code_id -------->>', auditid, '|', obj.app_id)

            # response.data = {
            #     'obj': obj.id,
            #     'auditid': auditid
            # }
            xcx_app_obj.save()
            obj.audit_result = status  # 修改数据库-审核代码-状态无论是否通过或者不通过。
            obj.reason = reason
            obj.save()

            if status in [0, 1]:
                # 发送企业微信消息通知
                corpid = 'wx81159f52aff62388'  # 企业ID
                corpsecret = 'dGWYuaTTLi6ojhPYG1_mqp9GCMTyLkl2uwmsNkjsSjw'  # 应用的凭证密钥
                redis_access_token_name = "access_token_send_msg"  # 存放在redis中的access_token对应key的名称
                _obj = WorkWeixinOper(corpid, corpsecret, redis_access_token_name)

                xcx_app_name = xcx_app_obj.name
                msg = """【小程序名称】：{xcx_app_name}\n【审核状态】：{status}\n【备注】：{remark}""".format(
                    xcx_app_name=xcx_app_name,
                    status="审核通过" if status == 0 else "审核失败",
                    remark="" if status == 0 else xcx_app_obj.code_release_result,
                )
                _obj.send_message(
                    agentid=1000005,
                    msg=msg,
                    # touser="zhangcong"
                    touser="zhangcong|1530778413048|1531464629357|1531476018476"
                )

    else:
        response.code = 302
        response.msg = '没有正在审核中的代码'
        print('>>-------- 没有状态正在【审核中】状态的代码 ------<<')

    return response



