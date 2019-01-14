from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.article_verify import ArticleAddForm, ArticleSelectForm, ArticleUpdateForm, MyarticleForm, \
    ThreadPictureForm, EffectRankingByLevelForm, QueryCustomerTransmitForm, EffectRankingByTableForm,GzhArticleSelectForm,SyncMyarticleForm

from django.db.models import Max, Avg, F, Q, Min, Count, Sum
import datetime
import json, base64
from django.db.models import Q, Count
from zhugeleida.public.condition_com import conditionCom
from zhugeleida.public.common import create_qrcode
from zhugeleida.views_dir.gongzhonghao.user_gongzhonghao_auth import create_gongzhonghao_yulan_auth_url
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.public.common import action_record
from zhugeleida.public.common import  get_customer_gongzhonghao_userinfo

from bs4 import BeautifulSoup
import time
import requests
import re,os
import random


def init_data(article_id, user_id, pid=None, level=1):
    """
    获取权限数据
    :param pid:  权限父级id
    :return:
    """
    result_data = []
    objs = models.zgld_article_to_customer_belonger.objects.select_related('user').filter(
        article_id=article_id,
        customer_parent_id=pid,
        user_id=user_id,
        level=level
    )
    for obj in objs:
        print('pid------------> ', pid)
        print('customer_parent_id------------> ', obj.customer_parent_id, obj.customer_id)
        if obj.customer_parent_id == obj.customer_id:
            continue

        # decode_username = base64.b64decode(obj.customer.username)
        # customer_username = str(decode_username, 'utf-8')
        customer_id = obj.customer_id
        customer_username = obj.customer.username
        customer_username = conversion_base64_customer_username_base64(customer_username, customer_id)

        current_data = {
            'name': customer_username,
            'id': obj.id,
            # 'user_id': obj.customer_id
        }
        children_data = init_data(article_id, user_id, pid=obj.customer_id, level=level + 1)
        if children_data:
            current_data['children'] = children_data

        result_data.append(current_data)

    print('result_data -->', result_data)
    return result_data


# 脉络图查询 调用init_data
def mailuotu(article_id, q):
    # children_data = init_data(user_id)
    # print('children_data--------> ',children_data)
    # print('q------------------------------> ',q)

    _objs = models.zgld_article_to_customer_belonger.objects.select_related('user', 'article').filter(q)

    _objs_list = _objs.values_list('level').annotate(Count('level'))
    level_list = []
    for _obj in _objs_list:
        level_count = _obj[1]
        level_list.append(level_count)

    if len(level_list) != 0:
        max_person_num = max(level_list)
    else:
        max_person_num = 0

    # < QuerySet[{'level': 1, 'level__count': 81}, {'level': 2, 'level__count': 49}, {'level': 3, 'level__count': 10}, {
    #     'level': 4, 'level__count': 9}, {'level': 5, 'level__count': 8}]>

    count_objs = _objs.values('user_id', 'user__username', 'article__title').annotate(Count('user'))

    result_data = []
    for obj in count_objs:
        user_id = obj['user_id']
        username = obj['user__username']
        print('user_id -->', user_id)
        print('username -->', username)

        children_data = init_data(article_id, user_id)
        print('children_data------> ', children_data)
        tmp = {'name': username}
        if children_data:
            tmp['children'] = children_data
        result_data.append(tmp)

    print('result_data -->', result_data)

    article_title = count_objs[0]['article__title']
    return article_title, result_data, max_person_num




# 文章管理查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def article(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        # 获取参数 页数 默认1

        if oper_type == 'myarticle_list':

            forms_obj = ArticleSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                user_id = request.GET.get('user_id')
                _type = request.GET.get('type')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

                field_dict = {
                    'id': '',
                    'status': '',  # 按状态搜索, (1,'已发'),  (2,'未发'),
                    'title': '__contains',  # 按文章标题搜索
                }

                request_data = request.GET.copy()
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id

                q = conditionCom(request_data, field_dict)
                q.add(Q(**{'company_id': company_id}), Q.AND)
                q.add(Q(**{'status__in': [1,2]}), Q.AND)

                tag_list = json.loads(request.GET.get('tags_list')) if request.GET.get('tags_list') else []
                if tag_list:
                    q.add(Q(**{'tags__in': tag_list}), Q.AND)

                already_choice_article_list = []
                if _type == 'exclude_already_choice_article':
                    now_date_time = datetime.datetime.now()

                    q1 = Q()
                    q1.connector = 'and'
                    q1.children.append(('end_time__gte', now_date_time))
                    q1.children.append(('company_id', company_id))
                    q1.children.append(('status__in', [1, 2, 4]))

                    # 找出可以不能选择的.  未开始的,进行中的
                    already_choice_article_list = list(
                        models.zgld_article_activity.objects.filter(q1).filter(q1).values_list('article_id', flat=True))

                objs = models.zgld_article.objects.filter(q).order_by(order).exclude(id__in=already_choice_article_list)
                count = objs.count()

                if length != 0:
                    print('current_page -->', current_page)
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 获取所有数据
                ret_data = []
                # 获取第几页的数据
                for obj in objs:
                    tag_list = list(obj.tags.values('id', 'name'))

                    # print('-----obj.tags.values---->', obj.tags.values('id','name'))
                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,  # 文章标题
                        'status_code': obj.status,  # 状态
                        'status': obj.get_status_display(),  # 状态
                        'source_code': obj.source,  # 状态
                        'source': obj.get_source_display(),  # 状态
                        'author': obj.user.username,  # 如果为原创显示,文章作者
                        'avatar': obj.user.avatar,  # 用户的头像
                        'read_count': obj.read_count,  # 被阅读数量
                        'forward_count': obj.forward_count,  # 被转发个数
                        'create_date': obj.create_date,  # 文章创建时间
                        'cover_url': obj.cover_picture,  # 文章图片链接
                        'tag_list': tag_list,
                        # 'insert_ads' : json.loads(obj.insert_ads)  if obj.insert_ads else '' # 插入的广告语
                    })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        #获取公众号文章列表
        elif oper_type == 'climb_gzh_article_list':

            forms_obj = GzhArticleSelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data.get('current_page')
                length = forms_obj.cleaned_data.get('length')
                company_id = forms_obj.cleaned_data.get('company_id')

                objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)

                if objs:

                    authorization_appid = objs[0].authorization_appid
                    _data = {
                        'authorizer_appid': authorization_appid,
                        'company_id': company_id,
                        'count' : length,
                        'offset' : current_page - 1,
                    }

                    user_obj_cla = get_customer_gongzhonghao_userinfo(_data)
                    _response = user_obj_cla.batchget_article_material()

                    # ret_json = {
                    #     "total_count": 1,
                    #     "item_count": 1,
                    #     "item": [{
                    #         "update_time": 1545553692,
                    #         "media_id": "ivcZrCjmhDznUrwcjIReRKw072mb7eq1Kn9MNz7oAxA",
                    #         "content": {
                    #             "update_time": 1545553692,
                    #             "news_item": [{
                    #                 "content_source_url": "",
                    #                 "author": "",
                    #                 "digest": "没【留量】比没流量更可怕—合众康桥2018-12-10关注公众号并分享文章领现金红包合众康桥-专注医院品牌营",
                    #                 "title": "没【留量】比没流量更可怕—合众康桥",
                    #                 "only_fans_can_comment": 0,
                    #                 "content": "<p>没【留量】比没流量更可怕—合众康桥</p><p>2018-12-10</p><p>关注公众号并分享文章</p><p>领现金红包</p><p style=\"line-height: 26px;text-align: center;\">合众康桥-专注医院品牌营销，<br  /></p><p style=\"line-height: 26px;text-align: center;\">帮助医院提升50%转化率</p><p style=\"line-height: 26px;text-align: center;\">5年来坚守一个小承诺</p><p style=\"line-height: 26px;text-align: center;\">不达标，就退款</p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4981684981684982\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7j1eqrTNvHN8W26vsZVLuKomhVRZ50vFTAtO77lpwoxiaxElBibloYJoA/640?wx_fmt=png\" data-type=\"png\" data-w=\"546\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4375\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7V62unBfhw6tAHf7oVE3fIQA2YmHyGBWz15c8HU5SVBm3UpeBY6RIcA/640?wx_fmt=png\" data-type=\"png\" data-w=\"544\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4132841328413284\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7RiaE9NbicwFQlLfeRoM7btadv0nmvfiaM9DHiaFyOrq0ibp4o8a0FMt2IhQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"542\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.449355432780847\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7nY8IE1knoqwpUuzNT3pz5a0v9YeZJQY57Iz55hFjBVxohkwxs2icplQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"543\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.5347912524850895\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7HMibZvLpzEqb7RuhQD32xwkNY20I2AXyHdh0dKKbPiajLsqduOkeI3rA/640?wx_fmt=png\" data-type=\"png\" data-w=\"503\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4453441295546559\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7hUtohc0S8ia46uZGhJp0HgzRMndh2WKd7XzBG2x7pxpwwvNjBughwzw/640?wx_fmt=png\" data-type=\"png\" data-w=\"494\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4225865209471766\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7AqxPpkkcgXV8u6kDic2acct2wfbez4Zno2op2Ws14Guq5PvHC2VNuEQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"549\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.501930501930502\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7TIib08I3WdpejzDWTDu5drZfr8t6qMXh2n7Q4U8mRrW0iaBpcibqpysqA/640?wx_fmt=png\" data-type=\"png\" data-w=\"518\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"0.5485110470701249\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7zIe58HmQnxq7wc1GNOia4T2MFCUj3jBBWEe459bvsjhGO35WJUnkeiaA/640?wx_fmt=png\" data-type=\"png\" data-w=\"1041\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;\"><br  /></p><p><img class=\"\" data-ratio=\"1\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7jnibhbsZqXxCYWq8YEjJwpibqmDQ2Kfm7gsFFZgAerX4ZS9RdWPUmBSg/640?wx_fmt=png\" data-type=\"png\" data-w=\"474\" style=\"width: 46px;height: 46px;border-radius: 23px;\"></p><p>张炬</p><p>营销专员</p><p>13020006631</p><p><br  /></p>",
                    #                 "thumb_media_id": "ivcZrCjmhDznUrwcjIReRF5RhHkNuJqdzycndksV39s",
                    #                 "thumb_url": "http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg",
                    #                 "show_cover_pic": 0,
                    #                 "url": "http://mp.weixin.qq.com/s?__biz=Mzg4MzA1ODU0Mw==&mid=100000003&idx=1&sn=53707000490e5f038874127c557caf03&chksm=4f4c7303783bfa1568406085f6715521b9e672a3472205bce4e5e9828de52edc19995c9e308e#rd",
                    #                 "need_open_comment": 0
                    #             }],
                    #             "create_time": 1545553602
                    #         }
                    #     }]
                    # }

                    ret_data = []
                    if _response.code == 200:

                        media_id_list = models.zgld_article.objects.filter(company_id=company_id).values_list('media_id',flat=True).distinct()

                        item_list = _response.data.get('item')
                        total_count = _response.data.get('total_count')
                        print('---- 临时素材列表 media_id_list ---->>',media_id_list)
                        status_text = ''
                        status = ''
                        for item in item_list:
                            media_id = item.get('media_id')

                            if media_id in media_id_list:
                                status_text = '已同步'
                                status = 1
                            else:
                                status_text = '未同步'
                                status = 0

                            thumb_url = item.get('content').get('news_item')[0].get('thumb_url')
                            thumb_url = deal_gzh_picture_url(thumb_url)

                            update_time = item.get('update_time')
                            ltime =  time.localtime(update_time)
                            update_time = time.strftime('%Y-%m-%d %H:%M:%S',ltime)

                            data  = {
                                'media_id' : media_id,
                                'update_time' : update_time,
                                'title' :  item.get('content').get('news_item')[0].get('title'),
                                'thumb_url' : thumb_url,
                                'digest' :  item.get('content').get('news_item')[0].get('digest'),
                                'url' :  item.get('content').get('news_item')[0].get('url'),
                                'content' : item.get('content').get('news_item')[0].get('content'),
                                'status_text': status_text,
                                'status' : status
                            }

                            ret_data.append(data)

                        response.data = {
                            'ret_data' : ret_data,
                            'total_count' : total_count,
                        }
                        response.code = 200
                        response.msg = '获取成功'

                    else:
                        response = _response



                else:
                    response.code = 302
                    response.msg = '公众号不存在'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    elif request.method == "POST":

        # 同步公众号文章入库
        if oper_type == 'sync_gzh_article':

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            media_id_list = request.POST.get('media_id_list')
            _form_data = {
                'company_id' : company_id,
                'media_id_list' : media_id_list
            }

            forms_obj = SyncMyarticleForm(_form_data)

            if forms_obj.is_valid():
                media_id_list = json.loads(media_id_list)

                company_id = forms_obj.cleaned_data.get('company_id')

                objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                authorization_appid = objs[0].authorization_appid

                for media_id in media_id_list:
                    _data = {
                        'authorizer_appid': authorization_appid,
                        'company_id': company_id,
                        'media_id' : media_id
                    }

                    user_obj_cla = get_customer_gongzhonghao_userinfo(_data)
                    _response = user_obj_cla.get_material()

                    if _response.code == 200:
                        article_data_dict = _response.data
                        news_item_dict = article_data_dict.get('news_item')[0]

                        title =  news_item_dict.get('title')
                        summary =  news_item_dict.get('digest')  # 摘要
                        content = news_item_dict.get('content')  # 封面图
                        cover_picture =  news_item_dict.get('thumb_url') #  封面图
                        url =  news_item_dict.get('url') #  原文链接
                        if cover_picture:
                            cover_picture = deal_gzh_picUrl_to_local(cover_picture)


                        if url:
                            content = deal_gzh_picture_url(url)

                        dict_data = {
                            'user_id': user_id,
                            'company_id': company_id,
                            'title': title,
                            'summary': summary,
                            'content': content,
                            'cover_picture': cover_picture,
                            'media_id': media_id,
                            'url' : url
                        }
                        article_objs = models.zgld_article.objects.filter(media_id=media_id)

                        if article_objs:
                            article_objs.update(**dict_data)

                        else:
                            models.zgld_article.objects.create(**dict_data)

                        response.code = 200
                        response.msg = '同步成功'

                    else:
                        response = _response



            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加文章
        if oper_type == "add":

            status = request.POST.get('status')
            article_data = {
                'user_id': request.GET.get('user_id'),
                'title': request.POST.get('title'),
                'summary': request.POST.get('summary'),
                'content': request.POST.get('content'),
                'cover_picture': request.POST.get('cover_picture'),
                'status': status
            }

            forms_obj = ArticleAddForm(article_data)

            if forms_obj.is_valid():

                user_id = request.GET.get('user_id')
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
                title = forms_obj.cleaned_data['title']

                dict_data = {
                    'status' : status, #
                    'user_id': user_id,
                    'company_id': company_id,
                    'title': title,
                    'summary': forms_obj.cleaned_data['summary'],
                    'content': forms_obj.cleaned_data['content'],
                    'cover_picture': forms_obj.cleaned_data['cover_picture'].strip(),
                    'insert_ads': request.POST.get('insert_ads')
                }

                obj = models.zgld_article.objects.create(**dict_data)

                insert_ads = request.POST.get('insert_ads')

                if insert_ads:
                    insert_ads = json.loads(insert_ads)
                    title = insert_ads.get('title')
                    plugin_id = insert_ads.get('id')
                    if title and plugin_id:
                        obj.plugin_report_id = plugin_id
                        obj.save()

                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    obj.tags = tags_id_list


                status = int(status)

                # 消息提示给雷达用户
                if status == 1:
                    user_objs = models.zgld_userprofile.objects.filter(company_id=company_id,status=1)
                    data = {}
                    customer_objs = models.zgld_customer.objects.filter(user_type=3, company_id=company_id)
                    if customer_objs:
                        customer_id = customer_objs[0].id
                    else:
                        encodestr = base64.b64encode('雷达管家'.encode('utf-8'))
                        customer_name = str(encodestr, 'utf-8')
                        obj = models.zgld_customer.objects.create(user_type=3, username=customer_name,
                                                                  company_id=company_id,headimgurl='statics/imgs/leidaguanjia.jpg')
                        customer_id = obj.id

                    for _obj in user_objs:
                        _user_id  = _obj.id
                        article_id  = obj.id

                        remark = '【温馨提示】:管理员发布了文章《%s》,大家积极转发呦' % (forms_obj.cleaned_data['title'])
                        print('---- 关注公众号提示 [消息提醒]--->>', remark)
                        data['user_id'] = customer_id
                        data['uid'] = _user_id
                        data['action'] = 666
                        data['article_id'] = article_id
                        action_record(data, remark)  # 此步骤封装到 异步中。



                data = {
                    'company_id': company_id,
                    'article_id': obj.id,
                    'uid': '',
                    'pid': '',
                    'level': 1,

                }

                auth_url_ret = create_gongzhonghao_yulan_auth_url(data)
                authorize_url = auth_url_ret.data.get('authorize_url')

                qrcode_data = {
                    'url': authorize_url,
                    'article_id': obj.id,
                }
                response_ret = create_qrcode(qrcode_data)
                pre_qrcode_url = response_ret.data.get('pre_qrcode_url')
                if pre_qrcode_url:
                    response.data = {'pre_qrcode_url': pre_qrcode_url, 'article_id': obj.id, }
                    response.code = 200
                    response.msg = "添加成功"

                else:
                    response.code = 303
                    response.msg = '生成文章体验二维码失败'

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除文章
        elif oper_type == "delete":
            print('------delete o_id --------->>', o_id)
            user_id = request.GET.get('user_id')
            article_objs = models.zgld_article.objects.filter(id=o_id)

            if article_objs:
                # article_objs.delete()
                article_objs.update(
                    status=3
                )
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '文章不存在'

        # 修改文章
        elif oper_type == "update":
            status = request.POST.get('status')

            article_data = {
                'status' : status,
                'article_id': o_id,
                'user_id': request.GET.get('user_id'),
                'title': request.POST.get('title'),
                'summary': request.POST.get('summary'),
                'content': request.POST.get('content'),
                'cover_picture': request.POST.get('cover_picture'),

            }

            forms_obj = ArticleUpdateForm(article_data)
            if forms_obj.is_valid():
                title  = forms_obj.cleaned_data['title']
                dict_data = {
                    'status' : status,
                    'title': forms_obj.cleaned_data['title'],
                    'summary': forms_obj.cleaned_data['summary'],
                    'content': forms_obj.cleaned_data['content'],
                    'cover_picture': forms_obj.cleaned_data['cover_picture'],
                    'insert_ads': request.POST.get('insert_ads')
                }

                article_id = forms_obj.cleaned_data['article_id']
                objs = models.zgld_article.objects.select_related('company', 'plugin_report').filter(
                    id=article_id
                )
                objs.update(**dict_data)

                insert_ads = request.POST.get('insert_ads')
                if insert_ads:
                    obj = objs[0]
                    insert_ads = json.loads(insert_ads)
                    title = insert_ads.get('title')
                    plugin_id = insert_ads.get('id')
                    if title and plugin_id:
                        obj.plugin_report_id = plugin_id
                        obj.save()

                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    objs[0].tags = tags_id_list

                company_id = objs[0].company_id


                status = int(status)
                # 消息提示给雷达用户
                if status == 1:
                    user_objs = models.zgld_userprofile.objects.filter(company_id=company_id,status=1)
                    data = {}

                    customer_objs = models.zgld_customer.objects.filter(user_type=3, company_id=company_id)
                    if customer_objs:
                        customer_id = customer_objs[0].id
                    else:
                        encodestr = base64.b64encode('雷达管家'.encode('utf-8'))
                        customer_name = str(encodestr, 'utf-8')
                        obj = models.zgld_customer.objects.create(user_type=3, username=customer_name,
                                                                  company_id=company_id,headimgurl='statics/imgs/leidaguanjia.jpg')
                        customer_id = obj.id

                    for _obj in user_objs:
                        _user_id  = _obj.id

                        remark = '【温馨提示】:管理员发布了文章《%s》,大家积极转发呦' % (forms_obj.cleaned_data['title'])
                        print('---- 关注公众号提示 [消息提醒]--->>', remark)
                        data['user_id'] = customer_id
                        data['uid'] = _user_id
                        data['action'] = 666
                        data['article_id'] = article_id
                        action_record(data, remark)  # 此步骤封装到 异步中。

                data = {
                    'company_id': company_id,
                    'article_id': objs[0].id,
                    'uid': '',
                    'pid': '',
                    'level': 1,
                }

                auth_url_ret = create_gongzhonghao_yulan_auth_url(data)
                authorize_url = auth_url_ret.data.get('authorize_url')

                qrcode_data = {
                    'url': authorize_url,
                    'article_id': objs[0].id,
                }
                response_ret = create_qrcode(qrcode_data)
                pre_qrcode_url = response_ret.data.get('pre_qrcode_url')

                if pre_qrcode_url:
                    response = response_ret

                else:
                    response.code = 303
                    response.msg = '生成文章体验二维码失败'


            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    elif request.method == 'GET':

        # 获取文章详情
        if oper_type == 'myarticle':
            user_id = request.GET.get('user_id')
            request_data_dict = {
                'article_id': o_id,
                # 'uid': user_id,  # 文章所属用户的ID
            }

            forms_obj = MyarticleForm(request_data_dict)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                article_id = forms_obj.cleaned_data.get('article_id')

                objs = models.zgld_article.objects.select_related('user', 'company', 'plugin_report').filter(id=article_id)
                count = objs.count()

                # 获取所有数据
                ret_data = []
                # 获取第几页的数据
                for obj in objs:
                    tag_list = list(obj.tags.values('id', 'name'))

                    insert_ads = obj.insert_ads
                    if insert_ads:
                        insert_ads = json.loads(insert_ads)
                    else:
                        insert_ads = ''

                    #         insert_ads =   {
                    #             'id': obj.plugin_report.id,
                    #             'belong_user_id': obj.plugin_report.user_id,
                    #             'belong_user': obj.plugin_report.user.username,
                    #             # 广告位
                    #             'ad_slogan': obj.plugin_report.ad_slogan,  # 广告语
                    #             'sign_up_button': obj.plugin_report.sign_up_button,  # 报名按钮
                    #             # 报名页
                    #             'title': obj.plugin_report.title,  # 活动标题
                    #             # 'name_list' :name_list_data,
                    #             'leave_message': obj.plugin_report.leave_message,
                    #             'introduce': obj.plugin_report.introduce,  # 活动说明
                    #             'is_get_phone_code': obj.plugin_report.is_get_phone_code,  # 是否获取手机验证码
                    #             'skip_link': obj.plugin_report.skip_link,  # 跳转链接
                    #             'create_date': obj.plugin_report.create_date.strftime("%Y-%m-%d %H:%M")
                    #         }
                    # else:
                    #     insert_ads = ''

                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,  # 文章标题
                        'author': obj.user.username,  # 如果为原创显示,文章作者
                        'avatar': obj.user.avatar,  # 用户的头像
                        'company_id': obj.company_id,
                        'summary': obj.summary,  # 摘要
                        'create_date': obj.create_date,  # 文章创建时间
                        'cover_url': obj.cover_picture,  # 文章图片链接
                        'content': obj.content,  # 文章内容
                        'tag_list': tag_list,
                        'insert_ads': insert_ads,  # 插入的广告语

                    })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

            return JsonResponse(response.__dict__)


        ## 客户基本信息和所看到的所有文章数据展示
        elif oper_type == 'customer_read_info':  # 脉络图

            current_page = request.GET.get('current_page')
            length = request.GET.get('length')

            customer_id = request.GET.get('customer_id')
            request_data_dict = {
                'article_id': o_id,
                'customer_id': customer_id,  # 文章所属用户的ID
                'current_page': current_page,  # 文章所属用户的ID
                'length': length,  # 文章所属用户的ID
            }

            forms_obj = ThreadPictureForm(request_data_dict)
            if forms_obj.is_valid():
                q1 = Q()
                q1.connector = 'AND'
                q1.children.append(('customer_id', customer_id))

                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(q1)
                if objs:
                    _objs = objs.values('article_id', 'article__title').annotate(Sum('stay_time'), Sum('read_count'),
                                                                                 Sum('forward_count'))

                    article_num = _objs.count()

                    current_page = forms_obj.cleaned_data['current_page']
                    length = forms_obj.cleaned_data['length']

                    ret_data = []
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        _objs = _objs[start_line: stop_line]

                    for _obj in _objs:
                        article_id = _obj.get('article_id')
                        _access_log_objs = models.zgld_article_access_log.objects.filter(article_id=article_id,

                                                                                         customer_id=customer_id).order_by(
                            '-last_access_date')
                        last_access_date = ''
                        if _access_log_objs:
                            last_access_date = _access_log_objs[0].last_access_date.strftime('%Y-%m-%d %H:%M:%S')

                        level = list(objs.filter(article_id=article_id).values_list('level', flat=True).distinct())

                        stay_time = _obj.get('stay_time__sum')
                        stay_time = conversion_seconds_hms(stay_time)
                        ret_data.append({

                            'article_id': article_id,
                            'article_title': _obj.get('article__title'),
                            'stay_time': stay_time,
                            'read_count': _obj.get('read_count__sum'),
                            'forward_count': _obj.get('forward_count__sum'),
                            'level': sorted(level),
                            'create_date': last_access_date or '',
                        })

                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {
                        'ret_data': ret_data,
                        'article_num': article_num,

                    }

                else:
                    response.code = 302
                    response.msg = '返回为空'

            else:
                print('------- 未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        ## 客户展示分级影响力。按level 展示出相对数据
        elif oper_type == 'customer_effect_ranking_by_level':

            level = request.GET.get('level')
            user_id = request.GET.get('user_id')

            current_page = request.GET.get('current_page')
            length = request.GET.get('length')

            # uid = request.GET.get('uid')
            request_data_dict = {
                'article_id': o_id,
                # 'uid': uid,  # 文章所属用户的ID
                'level': level,  # 文章所属用户的ID
                'current_page': current_page,
                'length': length
            }

            forms_obj = EffectRankingByLevelForm(request_data_dict)
            if forms_obj.is_valid():

                article_id = forms_obj.cleaned_data.get('article_id')
                level = forms_obj.cleaned_data.get('level')
                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(
                    article_id=article_id,

                ).order_by('-level')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                ret_data = []
                if objs:
                    level_num = objs[0].level
                    title = objs[0].article.title

                    if int(level) >= 1:
                        objs = objs.filter(level=level).order_by('-stay_time')

                    count = objs.count()
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    for obj in objs:
                        stay_time = obj.stay_time
                        stay_time = conversion_seconds_hms(stay_time)

                        username = obj.customer.username
                        username = base64.b64decode(username)
                        username = str(username, 'utf-8')
                        area = obj.customer.province + obj.customer.city

                        data_dict = {
                            'id': obj.id,
                            'uid': obj.user_id,  # 所属雷达用户
                            'user_name': obj.user.username,
                            'customer_id': obj.customer_id,
                            'customer_name': username,
                            'customer_headimgurl': obj.customer.headimgurl,
                            'sex': obj.customer.get_sex_display() or '',
                            'area': area,
                            'read_count': obj.read_count,
                            'stay_time': stay_time,

                            'forward_friend_circle_count': obj.forward_friend_circle_count,
                            'forward_friend_count': obj.forward_friend_count,

                            'level': level  # 所在的层级
                        }

                        ret_data.append(data_dict)

                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {

                        'ret_data': ret_data,
                        'total_level_num': level_num,  # 总共的层级
                        'article_id': article_id,
                        'article_title': title,
                        'count': count,
                    }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        ## 查询客户最短的层级
        elif oper_type == 'query_customer_transmit_path':

            level = request.GET.get('level')

            uid = request.GET.get('uid')
            customer_id = request.GET.get('customer_id')
            request_data_dict = {
                'article_id': o_id,
                'customer_id': customer_id,  # 文章所属用户的ID
                'level': level,  # 文章所属用户的ID
            }

            forms_obj = QueryCustomerTransmitForm(request_data_dict)
            if forms_obj.is_valid():

                article_id = forms_obj.cleaned_data.get('article_id')
                level = forms_obj.cleaned_data.get('level')
                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(
                    article_id=article_id,
                    user_id=uid
                ).order_by('-level')

                ret_data = []
                if objs:
                    article_id = objs[0].article_id
                    user_id = objs[0].user_id
                    avatar = objs[0].user.avatar
                    user_name = objs[0].user.username

                    customer_parent_id = objs.filter(customer_id=customer_id, level=level)[0].customer_parent_id

                    for l in range(int(level) - 1, 0, -1):
                        _objs = objs.filter(level=l)
                        print('------ objs ------>>', _objs.values_list('customer_id', 'user_id', 'level'))

                        for obj in _objs:
                            customerId = obj.customer_id

                            if customerId == customer_parent_id:
                                # stay_time = obj.stay_time
                                # stay_time = conversion_seconds_hms(stay_time)
                                customer_username = obj.customer.username
                                customer_username = base64.b64decode(customer_username)
                                customer_username = str(customer_username, 'utf-8')
                                area = obj.customer.province + obj.customer.city
                                data_dict = {
                                    'uid': user_id,
                                    'user_name': user_name,
                                    'customer_id': customerId,
                                    'customer_name': customer_username,
                                    'customer_headimgurl': obj.customer.headimgurl,
                                    'create_date': obj.create_date,
                                    # 'sex': obj.customer.get_sex_display(),
                                    # 'area': area,
                                    # 'read_count': obj.read_count,
                                    # 'stay_time': stay_time,
                                    'level': l
                                }

                                ret_data.insert(0, data_dict)
                                customer_parent_id = obj.customer_parent_id
                                print('---- customer_parent_id --->>', customer_parent_id)
                                break

                    objs = models.zgld_article_to_customer_belonger.objects.select_related('customer', 'user').filter(
                        user_id=uid,
                        article_id=article_id,
                        customer_id=customer_id,
                        level=level)
                    customer_username = ''
                    headimgurl = ''
                    sex = ''
                    area = ''
                    if objs:
                        obj = objs[0]
                        customer_username = obj.customer.username
                        customer_username = base64.b64decode(customer_username)
                        customer_username = str(customer_username, 'utf-8')
                        headimgurl = obj.customer.headimgurl
                        sex = obj.customer.get_sex_display()
                        area = obj.customer.province + obj.customer.city

                        data_dict = {
                            'uid': uid,
                            'user_name': user_name,
                            'customer_id': customer_id,
                            'customer_name': customer_username,
                            'customer_headimgurl': headimgurl,
                            'create_date': obj.create_date,
                            'level': level
                        }
                        ret_data.append(data_dict)

                    data_dict = {
                        'uid': uid,
                        'user_name': user_name,
                        'user_avatar': avatar,
                        'level': 0,

                    }
                    ret_data.insert(0, data_dict)

                    print('------ ret_data ------->>', ret_data)

                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {

                        'ret_data': ret_data,
                        'article_id': article_id,
                        'customer_id': customer_id,
                        'customer_name': customer_username,  # 昵称
                        'sex': sex,  # 性别
                        'area': area,  # 性别
                        'level': level,  # 客户所在层级
                    }

            else:
                print('------- 未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        # 脉络图 统计文章 转载情况
        elif oper_type == 'contextDiagram':
            article_id = o_id  # 文章id
            uid = request.GET.get('uid')  # 文章所属用户ID
            q = Q()
            q.add(Q(article_id=article_id), Q.AND)
            if uid:
                q.add(Q(user_id=uid), Q.AND)

            objs = models.zgld_article_to_customer_belonger.objects.filter(article_id=article_id)
            if objs:

                article_title, result_data, max_person_num = mailuotu(article_id, q)
                print('--- dataList --->>', result_data)
                dataList = {  # 顶端 首级
                    'name': article_title,
                    'children': result_data
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'dataList': dataList,
                    'article_title': article_title,
                    'max_person_num': max_person_num
                }
            else:
                response.code = 301
                response.msg = '该文章无查看'
                response.data = {}


        ## 按表格层级查看用户
        elif oper_type == 'query_customer_table_by_level':

            level = request.GET.get('level')
            user_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            # current_page = request.GET.get('current_page')
            # length = request.GET.get('length')

            query_customer_id = request.GET.get('query_customer_id')
            request_data_dict = {
                'article_id': o_id,
                # 'uid': uid,  # 文章所属用户的ID
                'level': level,  # 文章所属用户的ID
                # 'current_page': current_page,
                # 'length': length
            }

            forms_obj = EffectRankingByTableForm(request_data_dict)
            if forms_obj.is_valid():

                article_id = forms_obj.cleaned_data.get('article_id')
                level = forms_obj.cleaned_data.get('level')

                q1 = Q()
                q1.connector = 'AND'
                q1.children.append(('article_id', article_id))
                if uid:
                    q1.children.append(('user_id', uid))

                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(q1)

                # current_page = forms_obj.cleaned_data['current_page']
                # length = forms_obj.cleaned_data['length']

                ret_data = []
                from zhugeleida.views_dir.qiyeweixin.article import jisuan_level_num

                if objs:
                    obj = objs[0]
                    level_num = objs.order_by('-level')[0].level
                    title = obj.article.title
                    total_count = objs.count()

                    # 初始化数据，只获取用户的下拉列表。
                    if level == 0 and not uid:

                        # _objs = objs.filter(level=1).values('user_id','user__username').annotate(Count('user'))
                        _objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                                'customer').filter(
                            article_id=article_id, level=1).values('user_id', 'user__username').annotate(Count('user'))

                        ret_user_data = []

                        for _obj in _objs:
                            user_id = _obj.get('user_id')
                            username = _obj.get('user__username')
                            user__count = _obj.get('user__count')

                            print('-------> user_id username -------->>', user__count, "|", user_id, username)

                            data_dict = {
                                'uid': user_id,  # 所属雷达用户
                                'user_name': username
                            }
                            ret_user_data.append(data_dict)

                        username = obj.user.username
                        gender = obj.user.gender
                        user_dict = objs.values('user_id').annotate(Sum('read_count'), Sum(
                            'forward_friend_circle_count'), Sum('forward_friend_count'))[0]
                        print('---- user_dict 数据 ---->>',user_dict)


                        read_count_sum = user_dict.get('read_count__sum')
                        forward_friend_sum = user_dict.get('forward_friend_count__sum')
                        forward_friend_circle_sum = user_dict.get('forward_friend_circle_count__sum')
                        print('-------> [ 只算一个人 ] user_id username -------->>', username, '|', uid)

                        # result_data, result_level = jisuan_level_num(article_id, uid)
                        #
                        # lower_people_count = len(result_level)
                        # if lower_people_count > 0:
                        #     # lower_level = max(result_level) - min(result_level) + 1
                        #     lower_level = len(list(set(result_level)))
                        # else:
                        #     lower_level = 0

                        data_dict = {
                            # 'id': obj.id,
                            'uid': uid,  # 所属雷达用户
                            'user_name': username,

                            # 'customer_id': customer_id,
                            # 'customer_name': username,
                            # 'customer_headimgurl': obj.customer.headimgurl,
                            'sex': gender,
                            # 'area': area,

                            'read_count': read_count_sum,
                            'forward_friend_circle_count':forward_friend_sum,
                            'forward_friend_count': forward_friend_circle_sum,

                            'lower_people_count': total_count,
                            'lower_level': level_num,

                            # 'is_have_child': obj.is_have_child,
                            'level': 0  # 所在的层级
                        }
                        ret_data.append(data_dict)

                        response.code = 200
                        response.msg = '返回成功'
                        response.data = {
                            'user_list': ret_user_data,
                            'ret_data': ret_data,
                            'article_id': article_id,
                            'article_title': title
                        }
                        return JsonResponse(response.__dict__)

                    elif level == 0 and uid:
                        # _objs = objs.filter(level=1).values('user_id','user__username').annotate(Count('user'))
                        # _objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                        #                                                                         'customer').filter(
                        #     article_id=article_id, level=1).values('user_id', 'user__username').annotate(
                        #     Count('user'))
                        #
                        # ret_user_data = []
                        # for _obj in _objs:
                        #     user_id = _obj.get('user_id')
                        #     username = _obj.get('user__username')
                        #     user__count = _obj.get('user__count')
                        #
                        #     print('-------> user_id username -------->>', user__count, "|", user_id, username)
                        #
                        #     data_dict = {
                        #         'uid': user_id,  # 所属雷达用户
                        #         'user_name': username
                        #     }
                        #     ret_user_data.append(data_dict)

                        username = obj.user.username
                        gender = obj.user.gender
                        user_dict = objs.values('user_id').annotate(Sum('read_count'), Sum(
                            'forward_friend_circle_count'), Sum('forward_friend_count'))[0]
                        print('---- user_dict 数据 ---->>', user_dict)

                        read_count_sum = user_dict.get('read_count__sum')
                        forward_friend_sum = user_dict.get('forward_friend_count__sum')
                        forward_friend_circle_sum = user_dict.get('forward_friend_circle_count__sum')
                        print('-------> [ 只算一个人 ] user_id username -------->>', username, '|', uid)

                        # result_data, result_level = jisuan_level_num(article_id, uid)
                        #
                        # lower_people_count = len(result_level)
                        # if lower_people_count > 0:
                        #     # lower_level = max(result_level) - min(result_level) + 1
                        #     lower_level = len(list(set(result_level)))
                        # else:
                        #     lower_level = 0

                        data_dict = {
                            # 'id': obj.id,
                            'uid': uid,  # 所属雷达用户
                            'user_name': username,

                            # 'customer_id': customer_id,
                            # 'customer_name': username,
                            # 'customer_headimgurl': obj.customer.headimgurl,
                            'sex': gender,
                            # 'area': area,

                            'read_count': read_count_sum,
                            'forward_friend_circle_count': forward_friend_sum,
                            'forward_friend_count': forward_friend_circle_sum,

                            'lower_people_count': total_count,
                            'lower_level': level_num,

                            # 'is_have_child': obj.is_have_child,
                            'level': 0  # 所在的层级
                        }
                        ret_data.append(data_dict)

                        response.code = 200
                        response.msg = '返回成功'
                        response.data = {
                            'ret_data': ret_data,
                            'article_id': article_id,
                            'article_title': title
                        }
                        return JsonResponse(response.__dict__)

                    # 查询第一层所有的用户的下级层人数和层级数
                    elif level == 1 and not query_customer_id:
                        level = level + 1
                        objs = objs.order_by('level').filter(level=1, user_id=uid)

                    elif level >= 1 and query_customer_id:

                        objs = objs.order_by('level').filter(level=level+1, customer_parent_id=query_customer_id)
                        level = level + 2

                    # count = objs.count()
                    for obj in objs:
                        customer_id = obj.customer_id
                        _level = obj.level


                        print('---- article_id, uid, customer_id, level ----->>', article_id, uid, customer_id,
                              level + 1)

                        result_data, result_level = jisuan_level_num(article_id, uid, customer_id, level )

                        lower_people_count = len(result_level)
                        if lower_people_count > 0:
                            # lower_level = max(result_level) - min(result_level) + 1
                            lower_level = len(list(set(result_level)))
                        else:
                            lower_level = 0
                        print('--- result_level -->>', result_level)
                        print('----- lower_people_count ------>>', lower_people_count)
                        stay_time = obj.stay_time
                        stay_time = conversion_seconds_hms(stay_time)

                        username = obj.customer.username
                        username = base64.b64decode(username)
                        username = str(username, 'utf-8')
                        area = obj.customer.province + obj.customer.city

                        data_dict = {
                            'id': obj.id,
                            'uid': obj.user_id,  # 所属雷达用户
                            'user_name': obj.user.username,

                            'customer_id': customer_id,
                            'customer_name': username,
                            'customer_headimgurl': obj.customer.headimgurl,
                            'sex': obj.customer.get_sex_display() or '',
                            'area': area,

                            'read_count': obj.read_count,
                            'stay_time': stay_time,

                            'forward_friend_circle_count': obj.forward_friend_circle_count,
                            'forward_friend_count': obj.forward_friend_count,

                            'lower_people_count': lower_people_count,
                            'lower_level': lower_level,

                            'is_have_child': obj.is_have_child,
                            'level': _level  # 所在的层级
                        }

                        ret_data.append(data_dict)


                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {
                        'ret_data': ret_data,
                        'total_level_num': level_num,  # 总共的层级
                        'article_id': article_id,
                        'article_title': title,
                        # 'count': count,
                    }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


def deal_gzh_picture_url(url):

    '''
    ata-src 替换为src，将微信尾部?wx_fmt=jpeg去除
    http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg

    '''
    # content = 'data-src="111?wx_fmt=png data-src="222?wx_fmt=jpg'
    # phone = "2004-959-559#这是一个电话号码"
    # # 删除注释
    # num = re.sub(r'#.*$', "", phone)
    # print("电话号码 : ", num)

    # 移除非数字的内容
    url = 'https://mp.weixin.qq.com/s?__biz=MzA5NzQxODgzNw==&mid=502884331&idx=1&sn=863da48ef5bd01f5ba8ac30d45fea912&chksm=08acecd13fdb65c72e407f973c4db69a988a93a169234d2c4a95c0ca6c97054adff54c48a24f#rd'

    ret = requests.get(url)

    ret.encoding = 'utf8'

    soup = BeautifulSoup(ret.text, 'lxml')

    style_tags = soup.find_all('style')
    # print('style_tags -->', style_tags)

    # style_html = " ".join(style_tags)

    style = ""
    for style_tag in style_tags:
        print('style_tag -->', style_tag)
        style += str(style_tag)

    print(style)

    body = soup.find('div', id="js_content")

    body.attrs['style'] = "padding: 20px 16px 12px;"

    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        data_src = img_tag.attrs.get('data-src')
        if data_src:

            #######
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            html = s.get(data_src)
            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = "/gzh_article_%s.jpg" % (now_time)
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article') + filename
            with open(file_dir, 'wb') as file:
                file.write(html.content)
            print('-----公众号 生成 本地文章URL file_dir ---->>', file_dir)
            #######

            img_tag.attrs['data-src'] = file_dir
            print('data_src ----->',data_src)

    with open('index_template.html', 'r', encoding='utf8') as f:
        html = f.read().format(
            style=style,
            body=body
        )
    print('最后的html---->>', html)

    # dict = {'data-src': 'src', '?wx_fmt=jpg': '', '?wx_fmt=png': '' ,'?wx_fmt=jpeg' : '' }
    # for key, value in dict.items():
    #     content = content.replace(key, value)
    #     # print(url)
    # print('----- 此图片来自微信公众平台 替换为 ----->',content)


    return  html

def deal_gzh_picUrl_to_local(url):

    print('-----【公众号】 发送的图片 PicUrl ---->>', url)
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    html = s.get(url)

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
    filename = "/article_%s.jpg" % (now_time)

    file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article')  + filename
    with open(file_dir, 'wb') as file:
        file.write(html.content)


    return  file_dir