
from django.shortcuts import render, redirect
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.smallprogram_verify import SmallProgramAddForm,LoginBindingForm

import time
import datetime
import json
import requests
from publicFunc.condition_com import conditionCom
from ..conf import *
import base64


# 从微信小程序接口中获取openid等信息
def get_openid_info(get_token_data):
    ret = requests.get(Conf['appurl'], params=get_token_data)
    ret_json = ret.json()
    print('--- 获取openid等信息 ret_json-->>', ret_json)
    openid = ret_json['openid']  # 用户唯一标识
    session_key = ret_json['session_key']  # 会话密钥

    unionid = ''
    if 'unionid' in ret_json:
        unionid = ret_json['unionid']  # 用户在开放平台的唯一标识符

    ret_data = {
        'openid': openid,
        'session_key': session_key,
        'unionid': unionid
    }

    return ret_data


@csrf_exempt
def login(request):
    response = Response.ResponseObj()

    if request.method == "GET":
        print('------login(request) request.GET -->', request.GET)
        # forms_obj = SmallProgramAddForm(request.GET)
        #
        # if forms_obj.is_valid():

        js_code = request.GET.get('code')

        get_token_data = {
            'appid': 'wx13dd9e1b8940d0a1',
            'secret': '522daa0c0e27d27f226feb078500b979',
            'js_code': js_code,
            'grant_type': 'authorization_code',
        }

        ret_data = get_openid_info(get_token_data)
        openid = ret_data['openid']
        # session_key = ret_data['session_key']
        # unionid = ret_data['unionid']

        customer_objs = models.zgld_customer.objects.filter(
            openid=openid,
            user_type=2,
        )
        # 如果openid存在一条数据
        if customer_objs:
            token = customer_objs[0].token
            client_id = customer_objs[0].id

        else:
            token = account.get_token(account.str_encrypt(openid))
            obj = models.zgld_customer.objects.create(
                token=token,
                openid=openid,

                user_type=2,   #  (1 代表'微信公众号'),  (2 代表'微信小程序'),
                # superior=customer_id,  #上级人。
            )

            #models.zgld_information.objects.filter(customer_id=obj.id,source=source)
            # models.zgld_user_customer_belonger.objects.create(customer_id=obj.id,user_id=user_id,source=source)
            client_id = obj.id
            print('---------- [创建用户成功] openid | client_id ---->',openid,"|",client_id)

        ret_data = {
            'cid': client_id,
            'token': token
        }
        response.code = 200
        response.msg = "返回成功"
        response.data = ret_data


    else:
        response.code = 402
        response.msg = "请求方式异常"

    return  JsonResponse(response.__dict__)


def crate_token_func():
    import redis

    get_token_data = {
        'appid': 'wx13dd9e1b8940d0a1',
        'secret': '522daa0c0e27d27f226feb078500b979',
        'grant_type': 'client_credential'
    }

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    access_token = rc.get('Test_xiaochengxu_token')
    print('--- rc.get token 数据: ---->>', access_token)

    if not access_token:
        # {"errcode": 0, "errmsg": "created"}
        token_ret = requests.get(Conf['qr_token_url'], params=get_token_data)
        token_ret_json = token_ret.json()
        print('-----生成小程序模板信息用的token：微信接口返回数据------>', token_ret_json)


        access_token = token_ret_json['access_token']
        print('---- access_token --->>', token_ret_json)

        rc.set('Test_xiaochengxu_token', access_token, 7000)

    return  access_token



@csrf_exempt
# @account.is_token(models.zgld_customer)
def login_oper(request,oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        if oper_type == 'binding':
            print('request.GET -->', request.GET)

            forms_obj = LoginBindingForm(request.GET)
            if forms_obj.is_valid():

                # user_type = forms_obj.cleaned_data.get('user_type')
                source = forms_obj.cleaned_data.get('source')
                user_id = forms_obj.cleaned_data.get('uid')
                customer_id = forms_obj.cleaned_data.get('user_id')
                parent_id = forms_obj.cleaned_data.get('pid')

                # get_token_data = {
                #     'appid': Conf['appid'],
                #     'secret': Conf['appsecret'],
                #     'grant_type': 'authorization_code',
                # }
                #
                # ret_data = get_openid_info(get_token_data)
                # openid = ret_data['openid']
                # session_key = ret_data['session_key']
                # unionid = ret_data['unionid']

                # customer_objs = models.zgld_customer.objects.filter(
                #     openid=openid,
                #     user_type=user_type,
                # )
                # 如果openid存在一条数据

                user_customer_belonger_obj = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,user_id=user_id)

                if user_customer_belonger_obj:
                    response.code = 302
                    response.msg = "关系存在"

                else:

                    # obj = models.zgld_customer.objects.create(
                    #     customer_id=customer_id
                    #     # user_type=user_type,  #  (1 代表'微信公众号'),  (2 代表'微信小程序'),
                    #     # superior=customer_id,  #上级人。
                    # )
                    # user_customer_belonger_obj.user_type = user_type     #  (1 代表'微信公众号'),  (2 代表'微信小程序'),
                    user_customer_belonger_obj.superior = parent_id      #上级人。

                    #models.zgld_information.objects.filter(customer_id=obj.id,source=source)
                    models.zgld_user_customer_belonger.objects.create(customer_id=customer_id,user_id=user_id,source=source)

                    print('---------- crete successful ---->')

                # ret_data = {
                #     'cid': client_id,
                #     'token': token
                # }
                    response.code = 200
                    response.msg = "绑定关系成功"
                # response.data = ret_data

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



    else:

        #小程序发送 用户信息
        if oper_type == 'send_user_info':
            customer_id = request.GET.get('user_id')
            headimgurl = request.POST.get('avatarUrl')
            city = request.POST.get('city')
            country = request.POST.get('country')
            province = request.POST.get('province')

            gender = request.POST.get('gender')  #1代表男
            language = request.POST.get('language')
            username =  request.POST.get('nickName')

            objs = models.zgld_customer.objects.filter(
                id = customer_id,
            )


            encodestr = base64.b64encode(username.encode('utf-8'))
            customer_name = str(encodestr, 'utf-8')

            if objs:
                objs.update( username = customer_name,
                             headimgurl=headimgurl,
                             city =city,
                             country=country,
                             province = province,
                             language = language,
                )
                response.code = 200
                response.msg = "保存成功"
            else:
                response.code = 301
                response.msg = "用户不存在"


            # else:
            #     response.code = 301
            #     response.msg = json.loads(forms_obj.errors.as_json())

        # 发送FormID
        elif oper_type == 'send_form_id':

            formid = request.POST.get('formId')
            customer_id = request.GET.get('user_id')
            print(' ------ send_form_id request.POST -------->', request.POST)
            objs = models.zgld_customer.objects.filter(id=customer_id)

            global list
            if objs and formid and 'formId' not in formid:
                print('------- 发送过来的 formid ------>', formid)

                exist_formid = objs[0].formid
                if not exist_formid:
                    exist_formid = "[]"

                exist_formid_json = json.loads(exist_formid)
                exist_formid_json.append(formid)
                now_form_id_json = list(set(exist_formid_json))

                print('============ Exist_formid_json =====>>', exist_formid_json)
                print('============ now_form_id_list =====>>', now_form_id_json)
                objs.update(formid=json.dumps(now_form_id_json))

                response.code = 200
                response.msg = "保存成功"
            else:
                response.code = 301
                response.msg = "formID 不规矩"

        # 小程序发送模板消息
        elif oper_type == 'user_send_template_msg':

            response = Response.ResponseObj()

            print('---- request -->', request.GET)

            # user_id = request.GET.get('user_id')
            customer_id = request.GET.get('user_id')

            get_template_data = {}
            post_template_data = {}

            token_ret = crate_token_func()

            get_template_data['access_token'] = token_ret

            customer_objs = models.zgld_customer.objects.filter(id=customer_id)
            if customer_objs:
                customer_obj = customer_objs[0]
                openid = customer_obj.openid
                exist_formid_json = json.loads(customer_obj.formid)
                # post_template_data['touser'] = openid
                now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # post_template_data['template_id'] = ''

                path = 'pages/test/test'

                # post_template_data['page'] = path

                if len(exist_formid_json) == 0:
                    response.msg = "没有formID"
                    response.code = 301
                    print('------- 没有消费的formID customer_id: -------->>',customer_id)
                    return JsonResponse(response.__dict__)

                print('---------formId 消费前数据----------->>', exist_formid_json)
                form_id = exist_formid_json.pop(-1)
                obj = models.zgld_customer.objects.filter(id=customer_id)

                obj.update(formid=json.dumps(exist_formid_json))
                print('---------formId 消费了哪个 ----------->>', form_id)
                # post_template_data['form_id'] = form_id
                # 留言回复通知
                data = {
                    'keyword1': {
                        'value': '客户ID:%s | 消费FormID: %s' % (customer_id,form_id)  # 回复者
                    },
                    'keyword2': {
                        'value': now_time  # 回复时间
                    },
                    'keyword3': {
                        'value': '您有未读消息哦'  # 回复内容
                    }
                }
                # post_template_data['data'] = data

                post_template_data = {
                    'touser' : openid,
                    'template_id' : 'sg_YWTXaiV1-ZN8AHbv51tIqdANesDmaxqXYla9E904',
                    'page'  : path,
                    'form_id': form_id,
                    'data': data
                }

                print('===========post_template_data=======>>', post_template_data)

                # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html#发送模板消息
                # return  HttpResponse(post_template_data)

                template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
                template_ret = template_ret.json()
                print('--------企业用户 send to 小程序 Template 接口返回数据--------->', template_ret)

                if template_ret.get('errmsg') == "ok":
                    print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                    response.code = 200
                    response.msg = "企业用户发送模板消息成功"

                else:
                    print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                    response.code = 200
                    response.msg = "企业用户发送模板消息成功"

            else:
                response.msg = "客户不存在"
                response.code = 301
                print('---- Template Msg 客户不存在---->>')


        ## 为新小程序绑定 模板ID
        elif oper_type == 'binding_templateid':

            # authorizer_access_token = crate_token_func()
            authorizer_access_token = '15_TOfK_2ewwuw8vDMQkWKK4gxxYxaxWJOdp7z6GQZLBSKwDcq38AHe7stlgONtX97f43a9mTwk9tnHf5Sk7oe0aS3nBFllfFYOjLa7sAd16m2x8YuyI3G7Oq-z-g9MlseyHFEa7PQ4DRiIFefvVLHfALDCSO'

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
            add_ret = requests.post(template_add_url, params=get_template_add_data,
                                    data=json.dumps(post_template_add_data))
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


                print('---------授权appid: %s , 组合模板并添加 【成功】------------>>' )
                # {"errcode": 0, "errmsg": "ok", "template_id": "sg_YWTXaiV1-ZN8AHbv51tIqdANesDmaxqXYla9E904"}
            else:
                response.code = errcode
                response.msg = errmsg
                print('---------授权appid: %s , 组合模板并添加 【失败】------------>>', errmsg, '|', errcode)

        ## 为小程序绑定体验者
        elif oper_type == 'binding_tiyanzhe':

            authorizer_access_token = crate_token_func()

            bind_tester_url = 'https://api.weixin.qq.com/wxa/bind_tester'
            get_bind_tester_data = {
                'access_token': authorizer_access_token
            }
            for wechatid in ['Ju_do_it', 'ai6026325', 'crazy_acong', 'lihanjie5201314', 'wxid_6bom1qvrrjhv22']:
                post_bind_tester_data = {
                    "wechatid": wechatid
                }
                domain_data_ret = requests.post(bind_tester_url, params=get_bind_tester_data,
                                                data=json.dumps(post_bind_tester_data))
                domain_data_ret = domain_data_ret.json()
                print('---------- 第三方平台 - 绑定微信用户为小程序体验者 返回------------>>', domain_data_ret)

        # 为小程序绑定域名
        elif oper_type == 'binding_domain':

            authorizer_access_token = crate_token_func()

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
            domain_data_ret = requests.post(post_domain_url, params=get_domin_data, data=json.dumps(post_domain_data))
            domain_data_ret = domain_data_ret.json()
            print('--------- 修改小程序服务器 接口返回---------->>', domain_data_ret)

            errcode = domain_data_ret.get('errcode')
            errmsg = domain_data_ret.get('errmsg')

            if errcode == 0:
                response.code = 200
                response.msg = "修改小程序服务器域名成功"
                print('---------授权appid: %s , 修改小程序服务器域名 【成功】------------>>')
            else:
                response.code = errcode
                response.msg = errmsg
                print('---------授权appid: %s, 修改小程序服务器域名 【失败】------------>>' , errmsg, '|',errcode)



    return JsonResponse(response.__dict__)