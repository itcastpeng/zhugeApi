from django.http import HttpResponse
from zhugeleida import models
from django.views.decorators.csrf import csrf_exempt
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import \
    create_authorizer_access_token as create_gongzhonghao_authorizer_access_token

from zhugeleida.public.common import get_customer_gongzhonghao_userinfo, create_qrcode
import json, datetime, redis, base64, requests, time
from zhugeleida.views_dir.admin.article import deal_gzh_picture_url,deal_gzh_picUrl_to_local
from django.utils.timezone import now, timedelta
from django.db.models import Q, Sum
from zhugeleida.forms.boosleida.boos_leida_verify import QueryHaveCustomerDetailForm, \
    QueryHudongHaveCustomerDetailPeopleForm, LineInfoForm

from zhugeleida.views_dir.qiyeweixin.boss_leida import deal_search_time, deal_line_info,deal_sale_ranking_data

## 发送公众号模板消息提示到用户
@csrf_exempt
def common_send_gzh_template_msg(request):
    response = ResponseObj()

    print('---发送公众号模板消息request.GET -->', request.GET)
    company_id = request.GET.get('company_id')
    customer_id = request.GET.get('customer_id')
    type = request.GET.get('type')
    title = request.GET.get('title')
    content = request.GET.get('content')
    remark = request.GET.get('remark')

    # company_id_list = json.loads(company_id)
    # for company_id in company_id_list:
    # # 创建二维码
    #
    #     objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
    #     authorization_appid =  objs[0].authorization_appid
    #
    #     redirect_uri = 'http://api.zhugeyingxiao.com/zhugeleida/gongzhonghao/work_gongzhonghao_auth?relate=type_BindingUserNotify|company_id_%s' % (company_id)
    #
    #     print('-------- 静默方式下跳转的 需拼接的 redirect_uri ------->', redirect_uri)
    #     scope = 'snsapi_base'  # snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
    #     state = 'snsapi_base'
    #     component_appid = 'wx6ba07e6ddcdc69b3' # 三方平台-AppID
    #
    #     authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s&component_appid=%s#wechat_redirect' % (
    #         authorization_appid, redirect_uri, scope, state, component_appid)
    #
    #     print('------ 【默认】生成的静默方式登录的 snsapi_base URL：------>>', authorize_url)
    #     qrcode_data = {
    #         'url': authorize_url,
    #         'type': 'binding_gzh_user_notify'
    #     }
    #
    #     response_ret = create_qrcode(qrcode_data)
    #     pre_qrcode_url = response_ret.get('pre_qrcode_url')
    #
    #     if pre_qrcode_url:
    #         print('绑定公众号和客户通知者的二维码 pre_qrcode_url---------->>', pre_qrcode_url)
    #         objs.update(
    #             gzh_notice_qrcode=pre_qrcode_url
    #         )
    #
    # return  JsonResponse(response.__dict__)

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
                'app_id': app_id,  # 'wx6ba07e6ddcdc69b3',
                'app_secret': app_secret,  # '0bbed534062ceca2ec25133abe1eecba'
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
        if type == 'gongzhonghao_template_tishi':  ### 言简意赅的模板消息提示消息

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

        elif errcode == 43004 or errcode == 40013:  # {'errcode': 40013, 'errmsg': 'invalid appid hint: [Vc1zrA00434123]'}

            # {'errcode': 43004, 'errmsg': 'require subscribe hint: [_z5Nwa00958672]'}
            # {'errcode': 40003, 'errmsg': 'invalid openid hint: [JUmuwa08163951]'}

            _msg = '此客户【未关注】公众号'
            if info_type == 6 and errcode == 40013:
                _msg = '此公众号未绑定小程序,请联系管理员'  # 【名片商城】未送达
            print('模板消息 错误提示 ------->>', _msg)


        else:
            print('-----企业用户 send to 公众号 Template 消息 Failed---->>', )
            response.code = 301
            response.msg = "企业用户发送模板消息失败"


    else:
        response.msg = "客户不存在"
        response.code = 301
        print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)


## 定时器获取微信公众号文章到文章模板库
@csrf_exempt
def crontab_batchget_article_material(request):

    if request.method == 'POST':
        company_ids_list = models.zgld_gongzhonghao_app.objects.all().values_list('company_id',flat=True)
        for company_id in company_ids_list:
            url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/batchget_article_material'  # 获取产品的列表
            get_data = {
                'company_id': company_id
            }
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            s.get(url,params=get_data)


## 定时器获取微信公众号文章到文章模板库
@csrf_exempt
def batchget_article_material(request):
    response = ResponseObj()
    if request.method == 'GET':


        company_id = request.GET.get('company_id')
        print('----- company_id: %s | 批量获取-文章素材 GET ---->' % (company_id), request.GET)

        objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

        if objs:

            length = 20
            authorization_appid = objs[0].authorization_appid
            _data = {
                'authorizer_appid': authorization_appid,
                'company_id': company_id,
            }

            user_obj_cla = get_customer_gongzhonghao_userinfo(_data)
            material_count_response = user_obj_cla.get_material_count()
            news_count = material_count_response.data.get('news_count')
            if news_count > 0:
                divmod_ret = divmod(news_count, length)
                shoudle_page_num = divmod_ret[0] + 1  # 总共的页数

                for current_page in range(shoudle_page_num):

                    _data = {
                        'authorizer_appid': authorization_appid,
                        'company_id': company_id,
                        'count': length,
                        'offset': current_page,
                    }

                    user_obj_cla = get_customer_gongzhonghao_userinfo(_data)

                    _response = user_obj_cla.batchget_article_material()
                    # total_count = _response.data.get('total_count')

                    # if news_count == len(media_id_list):
                    #     response.code = 301
                    #     response.msg = '微信文章数据源和本地数据一致'
                    #     print('公司ID: %s | 微信文章数据源和本地数据一致 ------------>>' % (company_id))
                    #
                    #     return JsonResponse(response.__dict__)
                    #
                    # else:
                    '''
                     ret_json = {
                        "total_count": 1,
                        "item_count": 1,
                        "item": [{
                            "update_time": 1545553692,
                            "media_id": "ivcZrCjmhDznUrwcjIReRKw072mb7eq1Kn9MNz7oAxA",
                            "content": {
                                "update_time": 1545553692,
                                "news_item": [{
                                    "content_source_url": "",
                                    "author": "",
                                    "digest": "没【留量】比没流量更可怕—合众康桥2018-12-10关注公众号并分享文章领现金红包合众康桥-专注医院品牌营",
                                    "title": "没【留量】比没流量更可怕—合众康桥",
                                    "only_fans_can_comment": 0,
                                    "content": "<p>没【留量】比没流量更可怕—合众康桥</p><p>2018-12-10</p><p>关注公众号并分享文章</p><p>领现金红包</p><p style=\"line-height: 26px;text-align: center;\">合众康桥-专注医院品牌营销，<br  /></p><p style=\"line-height: 26px;text-align: center;\">帮助医院提升50%转化率</p><p style=\"line-height: 26px;text-align: center;\">5年来坚守一个小承诺</p><p style=\"line-height: 26px;text-align: center;\">不达标，就退款</p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4981684981684982\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7j1eqrTNvHN8W26vsZVLuKomhVRZ50vFTAtO77lpwoxiaxElBibloYJoA/640?wx_fmt=png\" data-type=\"png\" data-w=\"546\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4375\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7V62unBfhw6tAHf7oVE3fIQA2YmHyGBWz15c8HU5SVBm3UpeBY6RIcA/640?wx_fmt=png\" data-type=\"png\" data-w=\"544\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4132841328413284\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7RiaE9NbicwFQlLfeRoM7btadv0nmvfiaM9DHiaFyOrq0ibp4o8a0FMt2IhQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"542\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.449355432780847\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7nY8IE1knoqwpUuzNT3pz5a0v9YeZJQY57Iz55hFjBVxohkwxs2icplQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"543\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.5347912524850895\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7HMibZvLpzEqb7RuhQD32xwkNY20I2AXyHdh0dKKbPiajLsqduOkeI3rA/640?wx_fmt=png\" data-type=\"png\" data-w=\"503\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4453441295546559\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7hUtohc0S8ia46uZGhJp0HgzRMndh2WKd7XzBG2x7pxpwwvNjBughwzw/640?wx_fmt=png\" data-type=\"png\" data-w=\"494\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4225865209471766\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7AqxPpkkcgXV8u6kDic2acct2wfbez4Zno2op2Ws14Guq5PvHC2VNuEQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"549\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.501930501930502\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7TIib08I3WdpejzDWTDu5drZfr8t6qMXh2n7Q4U8mRrW0iaBpcibqpysqA/640?wx_fmt=png\" data-type=\"png\" data-w=\"518\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"0.5485110470701249\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7zIe58HmQnxq7wc1GNOia4T2MFCUj3jBBWEe459bvsjhGO35WJUnkeiaA/640?wx_fmt=png\" data-type=\"png\" data-w=\"1041\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;\"><br  /></p><p><img class=\"\" data-ratio=\"1\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7jnibhbsZqXxCYWq8YEjJwpibqmDQ2Kfm7gsFFZgAerX4ZS9RdWPUmBSg/640?wx_fmt=png\" data-type=\"png\" data-w=\"474\" style=\"width: 46px;height: 46px;border-radius: 23px;\"></p><p>张炬</p><p>营销专员</p><p>13020006631</p><p><br  /></p>",
                                    "thumb_media_id": "ivcZrCjmhDznUrwcjIReRF5RhHkNuJqdzycndksV39s",
                                    "thumb_url": "http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg",
                                    "show_cover_pic": 0,
                                    "url": "http://mp.weixin.qq.com/s?__biz=Mzg4MzA1ODU0Mw==&mid=100000003&idx=1&sn=53707000490e5f038874127c557caf03&chksm=4f4c7303783bfa1568406085f6715521b9e672a3472205bce4e5e9828de52edc19995c9e308e#rd",
                                    "need_open_comment": 0
                                }],
                                "create_time": 1545553602
                            }
                        }]
                    }    
                    '''
                    if _response.code != 200:
                        response.code = _response.code
                        response.msg = _response.msg

                    else:
                        title_list = list(
                            models.zgld_template_article.objects.filter(company_id=company_id, source=1).values_list(
                                'title', flat=True).distinct())  # 已经入模板库的 文章列表
                        media_id_list = list(
                            models.zgld_template_article.objects.filter(company_id=company_id, source=1).values_list(
                                'media_id', flat=True).distinct())  # 已经入模板库的 文章列表

                        item_list = _response.data.get('item')  # 获取的素材文章列表
                        for item in item_list: # 大列表
                            media_id = item.get('media_id')
                            update_time = item.get('update_time')
                            content_list = item.get('content').get('news_item') # 嵌套的小列表
                            ltime = time.localtime(int(update_time))
                            update_time = time.strftime('%Y-%m-%d %H:%M:%S', ltime)
                            for content in content_list:
                                title = content.get('title')
                                thumb_url = content.get('thumb_url')
                                source_url = content.get('url')
                                summary = content.get('digest')
                                content = content.get('content')
                                if title not in title_list or media_id not in media_id_list: # 如果不存在创建

                                    data = {
                                        'company_id' : company_id,
                                        'media_id': media_id,
                                        'source_url': source_url,
                                        'title': title,
                                        'cover_picture': thumb_url,
                                        'summary': summary,  #图文消息的摘要
                                        'content': content,
                                        'update_time': update_time,
                                        'source': 1  # (1, '同步[公众号文章]到模板库')
                                    }
                                    template_article_objs = models.zgld_template_article.objects.filter(company_id=1,source=1,media_id=media_id)
                                    if template_article_objs:
                                        template_article_objs.update(**data)
                                    else:
                                        models.zgld_template_article.objects.create(**data)

                                    media_id_list.append(media_id)
                                    title_list.append(title)

                                else: # 已存在
                                    print('-=-!!!!!!!!!!!!!!!!!!continue')
                                    continue

            else:
                print('----------->>')
                response.code = 302
                response.msg = '一个素材都没有'
                print('公司ID: %s | 微信文章【数据源为空】 ------------>>' % (company_id))

    return JsonResponse(response.__dict__)



## 定时器 ~ 数据【总览】统计 和 数据【客户统计】数据
@csrf_exempt
def crontab_batchget_article_material(request):

    if request.method == 'POST':

        company_objs = models.zgld_company.objects.all()
        for obj in company_objs:
            company_id =  obj.id
            account_expired_time =  obj.account_expired_time
            if datetime.datetime.now() > account_expired_time:
               continue

            url_1 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/acount_data'  # 获取产品的列表
            get_data_1 = {
                'company_id': company_id
            }
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            s.get(url_1,params=get_data_1)

            userprofile_objs = models.zgld_userprofile.objects.filter(status=1,company_id=company_id)
            for user_obj in userprofile_objs:
                url_2 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/acount_data'  # 获取产品的列表
                get_data_2 = {
                    'company_id': company_id,
                    'user_id' : user_obj.id,
                    'type' : 'personal',
                }
                s.get(url_2,params=get_data_2)


            url_3 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/line_info'  # 获取产品的列表
            get_data_3 = {
                'company_id': company_id
            }
            s.get(url_3,params=get_data_3)

            for user_obj in userprofile_objs:
                url_4 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/line_info'  # 获取产品的列表
                get_data_4 = {
                    'company_id': company_id,
                    'user_id' : user_obj.id,
                    'type' : 'personal',
                }
                s.get(url_4,params=get_data_4)

            url_5 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/sales_ranking_customer_num'  #
            get_data_5 = {
                'company_id': company_id
            }
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            s.get(url_5,params=get_data_5)

            url_6 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/hudong_pinlv_customer_num'  #
            get_data_6 = {
                'company_id': company_id
            }
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            s.get(url_6,params=get_data_6)

            url_7 = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/expect_chengjiaolv_customer_num'  #
            get_data_7 = {
                'company_id': company_id
            }
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            s.get(url_7,params=get_data_7)





##  数据【总览】统计 和 数据【客户统计】数据
def bossLeida_acount_data_and_line_info(request,oper_type):

    response = ResponseObj()

    if request.method == 'GET':
        company_id = request.GET.get('company_id')
        user_id = request.GET.get('user_id')
        type = request.GET.get('type')

        ## 数据【总览】统计
        if oper_type == "acount_data":
            ret_data = {}
            data = request.GET.copy()
            # 汇总数据
            q1 = Q()
            data['start_time'] = ''
            data['stop_time'] = ''
            ret_data['count_data'] = deal_search_time(data, q1)

            # 昨天数据
            q2 = Q()
            now_time = datetime.datetime.now()
            start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            # q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            # q2.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            data['start_time'] = start_time
            data['stop_time'] = stop_time
            ret_data['yesterday_data'] = deal_search_time(data, q2)

            q3 = Q()
            start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            # q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            # q3.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            data['start_time'] = start_time
            data['stop_time'] = stop_time
            ret_data['nearly_seven_days'] = deal_search_time(data, q3)

            q4 = Q()
            start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
            stop_time = now_time.strftime("%Y-%m-%d")
            data['start_time'] = start_time
            data['stop_time'] = stop_time
            # q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
            # q4.add(Q(**{'create_date__lt': stop_time}), Q.AND)
            ret_data['nearly_thirty_days'] = deal_search_time(data, q4)


            company_objs = models.zgld_company.objects.filter(id=company_id)
            if company_objs and  type != 'personal':
                data_tongji_dict = json.loads(company_objs[0].bossleida_data_tongji)
                data_tongji_dict['acount_data'] = ret_data
                bossleida_data_tongji = json.dumps(data_tongji_dict)
                company_objs.update(
                    bossleida_data_tongji=bossleida_data_tongji
                )

            elif type == 'personal':
                userprofile_objs  = models.zgld_userprofile.objects.filter(id=user_id)
                data_tongji_dict = json.loads(userprofile_objs[0].bossleida_data_tongji)
                data_tongji_dict['acount_data'] = ret_data
                bossleida_data_tongji = json.dumps(data_tongji_dict)
                if userprofile_objs:
                    userprofile_objs.update(
                        bossleida_data_tongji=bossleida_data_tongji
                    )



            response.code = 200
            response.msg = '查询成功'


        ## 数据【客户统计】数据
        elif oper_type == "line_info":

            forms_obj = LineInfoForm(request.POST)

            if forms_obj.is_valid():


                data = request.POST.copy()

                q1 = Q()
                q2 = Q()
                if type == 'personal':  # 个人数据
                    q1.add(Q(**{'user_id': user_id}), Q.AND)  # 搜索个人数据
                    q2.add(Q(**{'id': user_id}), Q.AND)  # 搜索个人数据

                data['company_id'] = company_id
                data['user_id'] = user_id
                data['type'] = type

                ret_data = {}
                for index in ['index_type_1', 'index_type_2', 'index_type_3', 'index_type_4']:
                    ret_dict = {}
                    if index == 'index_type_1':
                        data['index_type'] = 1

                    elif index == 'index_type_2':
                        data['index_type'] = 2

                    elif index == 'index_type_3':
                        data['index_type'] = 3

                    elif index == 'index_type_4':
                        data['index_type'] = 4

                    for day in [7, 15, 30]:
                        ret_list = []
                        if index == 'index_type_4' and day != 15:
                            continue

                        for _day in range(int(day), 0, -1):
                            now_time = datetime.datetime.now()
                            start_time = (now_time - timedelta(days=_day)).strftime("%Y-%m-%d")
                            stop_time = (now_time - timedelta(days=_day - 1)).strftime("%Y-%m-%d")

                            data['start_time'] = start_time
                            data['stop_time'] = stop_time

                            ret_list.append({'statics_date': start_time, 'value': deal_line_info(data)})

                        # print('------- ret_list ------->>', ret_list)
                        if day == 7:
                            ret_dict['nearly_seven_days'] = ret_list
                        elif day == 15:
                            ret_dict['nearly_fifteen_days'] = ret_list
                        elif day == 30:
                            ret_dict['nearly_thirty_days'] = ret_list

                    ret_data[index] = ret_dict

                user_pop_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q2).values(
                    'company_id').annotate(praise_num=Sum('praise'))  # 被点赞总数
                praise_num = 0
                if len(list(user_pop_queryset)) != 0:
                    praise_num = user_pop_queryset[0].get('praise_num')

                saved_total_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=5).filter(
                    q1).count()  # 保存微信
                query_product_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=7).filter(
                    q1).count()  # 咨询产品
                user_forward_queryset = models.zgld_userprofile.objects.filter(company_id=company_id).filter(q2).values(
                    'company_id').annotate(forward_num=Sum('forward'))  # 转发名片

                forward_num = 0
                if len(list(user_forward_queryset)) != 0:
                    forward_num = user_forward_queryset[0].get('forward_num')

                call_phone_num = models.zgld_accesslog.objects.filter(user__company_id=company_id, action=10).filter(
                    q1).count()  # 拨打电话

                _ret_dict = {
                    'praise_num': praise_num,  # 被点赞总数
                    'query_product_num': query_product_num,  # 咨询产品
                    'forward_mingpian_num': forward_num,  # 转发名片
                    'call_phone_num': call_phone_num,  # 拨打电话
                    'saved_phone_num': saved_total_num,  # 保存微信
                }

                ret_data['index_type_5'] = _ret_dict

                view_mingpian = models.zgld_accesslog.objects.filter(user__company_id=company_id,
                                                                     action=1).filter(q1).count()  # 保存电话

                view_product_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,
                                                                        action=2).filter(q1).count()  # 咨询产品

                view_website_num = models.zgld_accesslog.objects.filter(user__company_id=company_id,  # 拨打电话
                                                                        action=4).filter(q1).count()

                view_mingpian = int(view_mingpian)
                view_product_num = int(view_product_num)
                view_website_num = int(view_website_num)
                total = sum([view_mingpian, view_product_num, view_website_num])

                # print('--- total ----->', total)
                _ret_dict = {
                    'view_mingpian': '{:.2f}'.format(view_mingpian / total * 100),
                    'view_product_num': '{:.2f}'.format(view_product_num / total * 100),
                    'view_website_num': '{:.2f}'.format(view_website_num / total * 100)
                }

                # ret_list.append(_ret_dict)
                ret_data['index_type_6'] = _ret_dict

                # 查询成功 返回200 状态码
                company_objs = models.zgld_company.objects.filter(id=company_id)
                if company_objs and type != 'personal':
                    data_tongji_dict = json.loads(company_objs[0].bossleida_data_tongji)

                    data_tongji_dict['line_info'] = ret_data
                    data_tongji_dict['date_time'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    bossleida_data_tongji = json.dumps(data_tongji_dict)

                    company_objs.update(
                        bossleida_data_tongji=bossleida_data_tongji
                    )

                elif type == 'personal':
                    userprofile_objs = models.zgld_userprofile.objects.filter(id=user_id)
                    data_tongji_dict = json.loads(userprofile_objs[0].bossleida_data_tongji)
                    data_tongji_dict['line_info'] = ret_data
                    data_tongji_dict['date_time'] = datetime.datetime.now().strftime('%Y-%m-%d')

                    bossleida_data_tongji = json.dumps(data_tongji_dict)
                    if userprofile_objs:
                        userprofile_objs.update(
                            bossleida_data_tongji=bossleida_data_tongji
                        )

                response.code = 200
                response.msg = '查询成功'


            else:
                response.code = 303
                response.msg = "未验证通过"
                response.data = json.loads(forms_obj.errors.as_json())


        ## 销售排行【按客户人数】
        elif oper_type == "sales_ranking_customer_num":
            forms_obj = LineInfoForm(request.POST)

            if forms_obj.is_valid():
                # user_id = request.GET.get('user_id')
                # user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
                # company_id = user_obj[0].company_id
                ret_data = {}
                # 汇总数据
                q1 = Q()
                data = {'type': 'customer_data'}

                q1.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等
                ret_data['total_num_have_customer'] = deal_sale_ranking_data(data, q1)

                # 昨天数据
                q2 = Q()
                now_time = datetime.datetime.now()
                start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q2.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q2.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['yesterday_new_customer'] = deal_sale_ranking_data(data, q2)

                q3 = Q()
                start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q3.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q3.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['nearly_seven_new_customer'] = deal_sale_ranking_data(data, q3)

                q4 = Q()
                start_time = (now_time - timedelta(days=15)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q4.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q4.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['nearly_fifteen_new_customer'] = deal_sale_ranking_data(data, q4)

                q5 = Q()
                start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q5.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                q5.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q5.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_data['nearly_thirty_new_customer'] = deal_sale_ranking_data(data, q5)

                company_objs = models.zgld_company.objects.filter(id=company_id)
                if company_objs:
                    data_tongji_dict = json.loads(company_objs[0].bossleida_data_tongji)
                    data_tongji_dict['sales_ranking_customer_num'] = ret_data
                    data_tongji_dict['date_time'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    bossleida_data_tongji = json.dumps(data_tongji_dict)
                    company_objs.update(
                        bossleida_data_tongji=bossleida_data_tongji
                    )

        ## 销售排行【按互动频率】
        elif oper_type == "hudong_pinlv_customer_num":

            ret_data = {}
            for type in ['follow_num', 'consult_num']:
                data = {'type': type, 'company_id': company_id}
                ret_dict = {}

                # # 汇总数据
                # q1 = Q()
                # q1.add(Q(**{'user__company_id': company_id}), Q.AND)  # 大于等于
                # ret_data['total_num_have_customer'] = deal_sale_ranking_data(data,q1)

                # 昨天数据
                q2 = Q()
                now_time = datetime.datetime.now()
                start_time = (now_time - timedelta(days=1)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q2.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q2.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['yesterday_data'] = deal_sale_ranking_data(data, q2)

                q3 = Q()
                start_time = (now_time - timedelta(days=7)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q3.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q3.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['nearly_seven_data'] = deal_sale_ranking_data(data, q3)

                q4 = Q()
                start_time = (now_time - timedelta(days=15)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q4.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q4.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['nearly_fifteen_data'] = deal_sale_ranking_data(data, q4)

                q5 = Q()
                start_time = (now_time - timedelta(days=30)).strftime("%Y-%m-%d")
                stop_time = now_time.strftime("%Y-%m-%d")
                q5.add(Q(**{'create_date__gte': start_time}), Q.AND)  # 大于等于
                q5.add(Q(**{'create_date__lte': stop_time}), Q.AND)
                ret_dict['nearly_thirty_data'] = deal_sale_ranking_data(data, q5)

                ret_data[type] = ret_dict

                company_objs = models.zgld_company.objects.filter(id=company_id)
                if company_objs:
                    data_tongji_dict = json.loads(company_objs[0].bossleida_data_tongji)
                    data_tongji_dict['hudong_pinlv_customer_num'] = ret_data
                    data_tongji_dict['date_time'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    bossleida_data_tongji = json.dumps(data_tongji_dict)
                    company_objs.update(
                        bossleida_data_tongji=bossleida_data_tongji
                    )

            # response.code = 200
            # response.msg = '查询成功'
            # response.data = {
            #     'ret_data': ret_data
            # }

        ## 销售排行【按预计成交率】
        elif oper_type == "expect_chengjiaolv_customer_num":
            # user_id = request.GET.get('user_id')
            # user_obj = models.zgld_userprofile.objects.select_related('company').filter(id=user_id)
            # company_id = user_obj[0].company_id

            # for  pr in  in ['1_50','51_80','81_99','100']:
            ret_dict = {}
            q2 = Q()
            data = {'type': 'expect_chengjiaolv',
                    'company_id': company_id
                    }

            q2.add(Q(**{'expedted_pr__gte': 1}), Q.AND)  # 大于等于
            q2.add(Q(**{'expedted_pr__lte': 50}), Q.AND)
            ret_dict['pr_1_50'] = deal_sale_ranking_data(data, q2)

            q3 = Q()
            q3.add(Q(**{'expedted_pr__gte': 51}), Q.AND)  # 大于等于
            q3.add(Q(**{'expedted_pr__lte': 80}), Q.AND)
            ret_dict['pr_51_80'] = deal_sale_ranking_data(data, q3)

            q4 = Q()
            q4.add(Q(**{'expedted_pr__gte': 81}), Q.AND)  # 大于等于
            q4.add(Q(**{'expedted_pr__lte': 99}), Q.AND)
            ret_dict['pr_81_99'] = deal_sale_ranking_data(data, q4)

            q5 = Q()
            q5.add(Q(**{'expedted_pr': 100}), Q.AND)  # 大于等于
            ret_dict['pr_100'] = deal_sale_ranking_data(data, q5)

            company_objs = models.zgld_company.objects.filter(id=company_id)
            if company_objs:
                data_tongji_dict = json.loads(company_objs[0].bossleida_data_tongji)
                data_tongji_dict['expect_chengjiaolv_customer_num'] = ret_dict
                data_tongji_dict['date_time'] = datetime.datetime.now().strftime('%Y-%m-%d')
                bossleida_data_tongji = json.dumps(data_tongji_dict)
                company_objs.update(
                    bossleida_data_tongji=bossleida_data_tongji
                )

            # response.code = 200
            # response.msg = '查询成功'
            # response.data = {
            #     'ret_data': ret_dict
            # }





    return JsonResponse(response.__dict__)