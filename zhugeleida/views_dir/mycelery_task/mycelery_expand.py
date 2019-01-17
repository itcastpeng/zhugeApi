from django.http import HttpResponse
from zhugeleida import models
from django.views.decorators.csrf import csrf_exempt
from publicFunc.Response import ResponseObj
from django.http import JsonResponse
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import \
    create_authorizer_access_token as create_gongzhonghao_authorizer_access_token

from zhugeleida.public.common import get_customer_gongzhonghao_userinfo, create_qrcode
import json, datetime, redis, base64, requests, time
from zhugeleida.views_dir.admin.article import deal_gzh_picture_url


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
def batchget_article_material(request):
    response = ResponseObj()
    print('---批量获取-文章素材 request.GET -->', request.GET)
    company_id = request.GET.get('company_id')

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
            media_id_list = models.zgld_template_article.objects.filter(company_id=company_id, source=1).values_list(
                'media_id', flat=True).distinct()  # 已经入模板库的 文章列表

            if news_count == len(media_id_list):
                response.code = 301
                response.msg = '微信文章数据源和本地数据一致'
                print('公司ID: %s | 微信文章数据源和本地数据一致 news_count:%s ------------>>' % (company_id,news_count))
                return JsonResponse(response.__dict__)

            divmod_ret = divmod(news_count, length)
            shoudle_page_num = divmod_ret[0] + 1  # 总共的页数
            yushu = divmod_ret[1]

            print('数值 shoudle_page_num ------>>',shoudle_page_num)
            for current_page in range(shoudle_page_num):

                _data = {
                    'authorizer_appid': authorization_appid,
                    'company_id': company_id,
                    'count': length,
                    'offset': current_page,
                }

                user_obj_cla = get_customer_gongzhonghao_userinfo(_data)

                _response = user_obj_cla.batchget_article_material()
                total_count = _response.data.get('total_count')

                if news_count == len(media_id_list):
                    response.code = 301
                    response.msg = '微信文章数据源和本地数据一致'
                    print('公司ID: %s | 微信文章数据源和本地数据一致 ------------>>' % (company_id))

                    return JsonResponse(response.__dict__)

                else:
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

                    if _response.code == 200:
                        item_list = _response.data.get('item')  # 获取的素材文章列表
                        print('---- 接口返回-获取素材列表 item_list ------->>', item_list)

                        for item in item_list:
                            media_id = item.get('media_id')
                            update_time = item.get('update_time')

                            if media_id in media_id_list:
                                #status_text = '已同步'
                                #status = 1
                                print('media_id: %s 已同步至模板库,直接pass -------->>' % media_id)
                                continue

                            else:
                                #status_text = '未同步'
                                #status = 0

                                thumb_url = item.get('content').get('news_item')[0].get('thumb_url')
                                thumb_url = deal_gzh_picture_url(thumb_url)

                                ltime = time.localtime(update_time)
                                update_time = time.strftime('%Y-%m-%d %H:%M:%S', ltime)

                                data = {
                                    'company_id' : company_id,
                                    'media_id': media_id,
                                    'source_url': item.get('content').get('news_item')[0].get('url'),

                                    'title': item.get('content').get('news_item')[0].get('title'),
                                    'cover_picture': thumb_url,
                                    'summary': item.get('content').get('news_item')[0].get('digest'),  #图文消息的摘要
                                    'content': item.get('content').get('news_item')[0].get('content'),
                                    'update_time': update_time,

                                    'source': 1  # (1, '同步[公众号文章]到模板库')
                                }
                                template_article_objs = models.zgld_template_article.objects.filter(company_id=1,source=1,media_id=media_id)
                                if template_article_objs:
                                    template_article_objs.update(**data)
                                else:
                                    models.zgld_template_article.objects.create(**data)
                                media_id_list.append(media_id)
                                print('media_id: %s 新增同步至模板库,创建成功 -------->>' % media_id)

                    else:
                        response.code = _response.code
                        response.msg =  _response.msg
                        print('获取素材报错: %s | %s  ------------>>' % (_response.code,_response.msg))

        else:
            print('----------->>')
            response.code = 302
            response.msg = '一个素材都没有'
            print('公司ID: %s | 微信文章【数据源为空】 ------------>>' % (company_id))

        return JsonResponse(response.__dict__)