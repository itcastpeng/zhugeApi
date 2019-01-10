from django.http import HttpResponse
from zhugeleida import models
from django.views.decorators.csrf import csrf_exempt
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import \
    create_authorizer_access_token as create_gongzhonghao_authorizer_access_token

from zhugeapi_celery_project import tasks
from zhugeleida.public import common
import json,datetime,redis,base64,requests


## 发送公众号模板消息提示到用户
@csrf_exempt
def monitor_send_gzh_template_msg(request):
    response = ResponseObj()

    print('---发送公众号模板消息request.GET -->', request.GET)
    company_id = request.GET.get('company_id')
    customer_id = request.GET.get('customer_id')
    title = request.GET.get('title')
    content = request.GET.get('content')
    remark = request.GET.get('remark')


    obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id

    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

    key_name = 'authorizer_access_token_%s' % (authorizer_appid)
    authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
    qywx_config_dict = ''
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        qywx_config_dict = three_service_obj.config
        if qywx_config_dict:
            qywx_config_dict = json.loads(qywx_config_dict)

    app_id = qywx_config_dict.get('app_id')
    app_secret = qywx_config_dict.get('app_secret')



    if not authorizer_access_token:
        authorizer_access_token_key_name = 'authorizer_access_token_%s' % (authorizer_appid)
        authorizer_access_token = rc.get(
            authorizer_access_token_key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            data = {
                'key_name': authorizer_access_token_key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,
                'app_id': app_id ,  #'wx6ba07e6ddcdc69b3',
                'app_secret': app_secret  ,# '0bbed534062ceca2ec25133abe1eecba'
            }

            authorizer_access_token_result = create_gongzhonghao_authorizer_access_token(data)
            if authorizer_access_token_result.code == 200:
                authorizer_access_token = authorizer_access_token_result.data

    get_template_data = {
        'access_token': authorizer_access_token  # 授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
    }
    customer_objs = models.zgld_customer.objects.filter(id=customer_id)

    if customer_objs:
        openid = customer_objs[0].openid

        # 留言回复通知
        '''
        您好，您咨询商家的问题已回复
        咨询名称：孕儿美摄影工作室-张炬
        消息回复：您有未读消息哦
        点击进入咨询页面
        '''
        info_type = ''
        post_template_data = {}
        if type == 'gongzhonghao_template_tishi': ### 言简意赅的模板消息提示消息

            data = {
                'first': {
                    'value': ''  # 回复者
                },
                'keyword1': {
                    'value': title + '\n',
                    "color": "#0000EE"
                },
                'keyword2': {
                    'value': content + '\n',
                    "color": "#FF0000"
                },
                'remark': {
                    'value': remark  # 回复内容
                }
            }

            post_template_data = {
                'touser': openid,
                'template_id': template_id,
                # "miniprogram": {
                #     "appid": appid,
                #     "pagepath": path,
                # },
                'data': data
            }


        print('发送出去的【模板消息】请求数据 ----------->>', json.dumps(post_template_data))

        # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考
        template_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'

        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        template_ret = s.post(template_msg_url, params=get_template_data, data=json.dumps(post_template_data))
        template_ret = template_ret.json()
        errcode = template_ret.get('errcode')

        print('--------企业用户 send to 公众号 Template 接口返回数据--------->', template_ret)


        if errcode == 40001:
            rc.delete(key_name)

        if template_ret.get('errmsg') == "ok":
            print('-----企业用户 send to 公众号 Template 消息 Successful---->>', )
            response.code = 200
            response.msg = "企业用户发送模板消息成功"

        elif errcode == 43004 or errcode == 40013: #{'errcode': 40013, 'errmsg': 'invalid appid hint: [Vc1zrA00434123]'}

            # {'errcode': 43004, 'errmsg': 'require subscribe hint: [_z5Nwa00958672]'}
            # {'errcode': 40003, 'errmsg': 'invalid openid hint: [JUmuwa08163951]'}

            _msg = '此客户【未关注】公众号'
            if info_type == 6 and errcode == 40013:
                _msg = '此公众号未绑定小程序,请联系管理员' # 【名片商城】未送达
            print('模板消息 错误提示 ------->>',_msg)


        else:
            print('-----企业用户 send to 公众号 Template 消息 Failed---->>', )
            response.code = 301
            response.msg = "企业用户发送模板消息失败"


    else:
        response.msg = "客户不存在"
        response.code = 301
        print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)

