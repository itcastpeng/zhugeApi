from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.gongzhonghao.article_verify import ArticleAddForm, ArticleSelectForm, ArticleUpdateForm, \
    MyarticleForm, StayTime_ArticleForm, Forward_ArticleForm
from zhugeapi_celery_project import tasks
from zhugeleida.public.common import action_record

import json
from django.db.models import Q,F
from zhugeleida.public.condition_com import conditionCom
import datetime
from django.db.models import Count

import requests
from zhugeleida.views_dir.admin.open_weixin_gongzhonghao import create_authorizer_access_token


@csrf_exempt
# @account.is_token(models.zgld_admin_userprofile)
def article(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        # 获取参数 页数 默认1

        if oper_type == 'myarticle_list':

            forms_obj = ArticleSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count
                user_id = request.GET.get('user_id')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

                field_dict = {
                    'id': '',
                    # 'user_id' : '',
                    'status': '',  # 按状态搜索, (1,'已发'),  (2,'未发'),
                    # 【暂时不用】 按员工搜索文章、目前只显示出自己的文章
                    'title': '__contains',  # 按文章标题搜索
                }

                request_data = request.GET.copy()

                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                q = conditionCom(request_data, field_dict)
                q.add(Q(**{'company_id': company_id}), Q.AND)

                tag_list = json.loads(request.GET.get('tags_list')) if request.GET.get('tags_list') else []
                if tag_list:
                    q.add(Q(**{'tags__in': tag_list}), Q.AND)

                objs = models.zgld_article.objects.select_related('user', 'company').filter(q).order_by(order)
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
                    print('----- obj.tags.values---->', obj.tags.values('id', 'name'))
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
                        'tag_list': list(obj.tags.values('id', 'name')),
                        'insert_ads': json.loads(obj.insert_ads) if obj.insert_ads else ''  # 插入的广告语

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

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_customer)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    import json
    if request.method == "POST":
        if oper_type == "add":
            article_data = {
                'user_id': request.GET.get('user_id'),
                'title': request.POST.get('title'),
                'summary': request.POST.get('summary'),
                'content': request.POST.get('content'),
                'cover_picture': request.POST.get('cover_picture'),
            }

            forms_obj = ArticleAddForm(article_data)

            if forms_obj.is_valid():
                print('======forms_obj.cleaned_data====>>', forms_obj.cleaned_data)

                dict_data = {
                    'user_id': request.GET.get('user_id'),
                    'title': forms_obj.cleaned_data['title'],
                    'summary': forms_obj.cleaned_data['summary'],
                    'content': forms_obj.cleaned_data['content'],
                    'cover_picture': forms_obj.cleaned_data['cover_picture'].strip(),
                    'insert_ads': request.POST.get('insert_ads')
                }

                obj = models.zgld_article.objects.create(**dict_data)
                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    obj.tags = tags_id_list

                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('------delete o_id --------->>', o_id)
            user_id = request.GET.get('user_id')
            article_objs = models.zgld_article.objects.filter(id=o_id, user_id=user_id)

            if article_objs:
                article_objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '文章不存在'

        elif oper_type == "update":
            article_data = {
                'article_id': o_id,
                'user_id': request.GET.get('user_id'),
                'title': request.POST.get('title'),
                'summary': request.POST.get('summary'),
                'content': request.POST.get('content'),
                'cover_picture': request.POST.get('cover_picture'),

            }

            forms_obj = ArticleUpdateForm(article_data)
            if forms_obj.is_valid():
                dict_data = {
                    'title': forms_obj.cleaned_data['title'],
                    'summary': forms_obj.cleaned_data['summary'],
                    'content': forms_obj.cleaned_data['content'],
                    'cover_picture': forms_obj.cleaned_data['cover_picture'],
                    'insert_ads': request.POST.get('insert_ads')
                }
                user_id = request.GET.get('user_id')
                article_id = forms_obj.cleaned_data['article_id']
                obj = models.zgld_article.objects.filter(
                    id=article_id, user_id=user_id
                )
                obj.update(**dict_data)

                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    obj[0].tags = tags_id_list

                response.code = 200
                response.msg = "修改成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        if oper_type == 'myarticle':

            print('----- 公众号查看文章 request.GET myarticle----->>', request.GET)
            customer_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            parent_id = request.GET.get('pid')
            company_id = request.GET.get('company_id')
            activity_id = request.GET.get('activity_id')

            request_data_dict = {
                'article_id': o_id,
                'uid': uid,  # 文章所属用户的ID
                'parent_id': parent_id
            }

            forms_obj = MyarticleForm(request_data_dict)
            if forms_obj.is_valid():
                # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                article_id = forms_obj.cleaned_data.get('article_id')
                zgld_article_objs = models.zgld_article.objects.filter(id=article_id)

                obj = zgld_article_objs[0]
                insert_ads = json.loads(obj.insert_ads) if obj.insert_ads else ''  # 插入的广告语
                if insert_ads and insert_ads.get('mingpian'):
                    zgld_userprofile_obj = models.zgld_userprofile.objects.get(id=uid)  # 获取企业微信中雷达AI分享出来文章对应用户的信息
                    insert_ads['username'] = zgld_userprofile_obj.username
                    insert_ads['avatar'] = zgld_userprofile_obj.avatar
                    insert_ads['phone'] = zgld_userprofile_obj.mingpian_phone
                    insert_ads['position'] = zgld_userprofile_obj.position
                    insert_ads['webchat_code'] = zgld_userprofile_obj.qr_code  # 展示企业微信二维码

                # 获取所有数据
                ret_data = []
                # 获取第几页的数据

                tag_list = list(obj.tags.values('id', 'name'))
                # print('-----obj.tags.values---->', tag_list)
                title =  obj.title
                ret_data.append({
                    'id': obj.id,
                    'title': title,  # 文章标题
                    'author': obj.user.username,  # 如果为原创显示,文章作者
                    'avatar': obj.user.avatar,  # 用户的头像
                    'summary': obj.summary,  # 摘要
                    'create_date': obj.create_date,  # 文章创建时间
                    'cover_url': obj.cover_picture,  # 文章图片链接
                    'content': obj.content,  # 文章内容
                    'tag_list': tag_list,
                    'insert_ads': insert_ads
                })

                article_access_log_id = ''
                if customer_id and uid:  ## 说明是客户查看了这个雷达用户分享出来的，uid为空说明是后台预览分享的，不要做消息提示了

                    q = Q()
                    q.add(Q(**{'article_id': article_id}), Q.AND)
                    q.add(Q(**{'customer_id': customer_id}), Q.AND)
                    q.add(Q(**{'user_id': uid}), Q.AND)

                    activity_objs = models.zgld_article_activity.objects.filter(article_id=article_id, status=2)
                    if activity_objs:
                        activity_id = activity_objs[0].id
                        is_have_activity = 1  # 活动已经开启

                    else:
                        is_have_activity = 0  # 没有搞活动

                    if parent_id:
                        q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)

                        ## 判断转发后阅读的人数 +转发后阅读时间 此处要 封装到异步中。
                        if activity_objs:  # 说明有参与活动，活动在进行中
                            _data = {
                                'parent_id': parent_id,
                                'article_id': article_id,
                                'activity_id': activity_id,
                                'company_id': company_id,
                            }
                            tasks.user_forward_send_activity_redPacket.delay(_data)





                    else:
                        q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

                    customer_objs = models.zgld_customer.objects.filter(id=customer_id, user_type=1)
                    zgld_article_objs.update(status=1)  # 改为已发状态
                    zgld_article_objs.update(read_count=F('read_count') + 1)  # 文章阅读数量+1，针对所有的雷达用户来说

                    models.zgld_article_to_customer_belonger.objects.filter(q).update(read_count=F('read_count') + 1)
                    customer_obj = ''
                    if customer_objs:  # 说明客户访问时候经过认证的
                        customer_obj = customer_objs[0]
                        username = customer_obj.username
                        user_type = customer_obj.user_type
                        if username:
                            remark = '%s》,看来对您的文章感兴趣' % (('正在查看文章《' + title))
                            print('---- 公众号查看文章[消息提醒]--->>', remark)
                            data = request.GET.copy()
                            data['action'] = 14
                            action_record(data, remark)  # 此步骤封装到 异步中。

                        if parent_id and uid : # 说明被人转发后有人查看后,发送公众号模板消息给他的父亲级，提示他有人查看了他的文章

                            data_ = {
                                'customer_id': parent_id,
                                'user_id' :  uid,
                                'type' : 'forward_look_article_tishi'
                            }
                            print('--- 【公众号发送模板消息】 user_send_gongzhonghao_template_msg --->', data_)

                            tasks.user_send_gongzhonghao_template_msg.delay(data_)  # 发送【公众号发送模板消息】



                    ## 先记录一个用户查看文章的日志
                    now_date_time = datetime.datetime.now()

                    article_access_log_obj = models.zgld_article_access_log.objects.create(
                        article_id=article_id,
                        customer_id=customer_id,
                        user_id=uid,
                        customer_parent_id=parent_id,
                        last_access_date=now_date_time
                    )
                    article_access_log_id = article_access_log_obj.id
                    is_subscribe = customer_obj.is_subscribe
                    is_subscribe_text = customer_obj.get_is_subscribe_display()

                    gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                    qrcode_url = ''
                    if gongzhonghao_app_objs:
                        qrcode_url = gongzhonghao_app_objs[0].qrcode_url

                    response.code = 200
                    response.data = {
                        'ret_data': ret_data,
                        'article_access_log_id': article_access_log_id,
                        'is_subscribe': is_subscribe,  # 是否关注了公众号。0 为没有关注 1为关注了。
                        'is_subscribe_text': is_subscribe_text,
                        'is_have_activity': is_have_activity,  # 是否搞活动。0 是没有活动，1 是活动已经开启。
                        'qrcode_url': qrcode_url
                    }

                else:
                    response.code = 403
                    response.msg = '没有uid或者customer_id'
                    response.data = {
                        'ret_data': ret_data,
                        'article_access_log_id': article_access_log_id,
                    }


            else:
                print('------- 公众号查看我的文章未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

            return JsonResponse(response.__dict__)

        elif oper_type == 'forward_article':

            uid = request.GET.get('uid')
            customer_id = request.GET.get('user_id')
            parent_id = request.GET.get('pid')
            forward_type = request.GET.get('forward_type')

            request_data_dict = {
                'article_id': o_id,
                'uid': uid,  # 文章所属用户的ID
                'customer_id': customer_id,  # 文章所属用户的ID
                'forward_type': forward_type,  # 文章所属用户的ID

            }

            forms_obj = Forward_ArticleForm(request_data_dict)
            if forms_obj.is_valid():
                article_id = o_id
                forward_type = forms_obj.cleaned_data.get('forward_type')

                objs = models.zgld_article.objects.filter(id=article_id)
                objs.update(forward_count=F('forward_count') + 1)  #

                if uid:
                    q = Q()
                    q.add(Q(**{'article_id': article_id}), Q.AND)
                    q.add(Q(**{'customer_id': customer_id}), Q.AND)
                    q.add(Q(**{'user_id': uid}), Q.AND)

                    if parent_id:
                        q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
                    else:
                        q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

                    models.zgld_article_to_customer_belonger.objects.filter(q).update(
                        forward_count=F('forward_count') + 1)

                    action = ''
                    place = ''
                    if int(forward_type) == 1:  # 1 转发朋友
                        action = 15
                        place = '分享给【朋友】'
                        models.zgld_article_to_customer_belonger.objects.filter(q).update(
                            forward_friend_count=F('forward_friend_count') + 1)

                    elif int(forward_type) == 2:  # 3转发朋友圈
                        action = 16
                        place = '分享到【朋友圈】'
                        models.zgld_article_to_customer_belonger.objects.filter(q).update(
                            forward_friend_circle_count=F('forward_friend_circle_count') + 1)

                    remark = '转发了您的文章《%s》%s,帮您进一步扩大了传播效果' % (objs[0].title, place)
                    data = request.GET.copy()
                    data['action'] = action
                    response = action_record(data, remark)
                    response.code = 200
                    response.msg = "记录转发文章成功"
            else:

                print('------- 公众号-转发文章未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'staytime':
            uid = request.GET.get('uid')
            customer_id = request.GET.get('user_id')
            parent_id = request.GET.get('pid')
            article_access_log_id = request.GET.get('article_access_log_id')

            request_data_dict = {
                'article_id': o_id,
                'uid': uid,  # 文章所属用户的ID
                'customer_id': customer_id,  # 文章所属用户的ID
                'parent_id': parent_id,  # 文章所属用户的ID
                'article_access_log_id': article_access_log_id,  # 文章日志ID
            }

            forms_obj = StayTime_ArticleForm(request_data_dict)
            if forms_obj.is_valid():
                article_id = o_id
                if uid:  # 说明是雷达客户分享出去的文章
                    q = Q()
                    q.add(Q(**{'article_id': article_id}), Q.AND)
                    q.add(Q(**{'customer_id': customer_id}), Q.AND)
                    q.add(Q(**{'user_id': uid}), Q.AND)

                    if parent_id:
                        q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
                    else:
                        q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

                    objs = models.zgld_article_to_customer_belonger.objects.filter(q)
                    if objs:
                        objs.update(stay_time=F('stay_time') + 5)  #
                    # else:
                    #     models.zgld_article_to_customer_belonger.objects.create(
                    #         article_id=article_id,
                    #         customer_id=customer_id,
                    #         user_id=uid,
                    #         customer_parent_id=parent_id
                    #         # stay_time=0
                    #     )

                    article_access_log_obj = models.zgld_article_access_log.objects.filter(
                        id=article_access_log_id,
                    )
                    now_date_time = datetime.datetime.now()
                    if article_access_log_obj:
                        article_access_log_obj.update(
                            stay_time=F('stay_time') + 5,
                            last_access_date=now_date_time
                        )  #

                    response.code = 200
                    response.msg = "记录客户查看文章时间成功"

            else:
                # print('------- 公众号-记录查看文章时间未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'test_send_redPacket':

            # _data = {
            #
            #     'parent_id': 9,
            #     'article_id': 23,
            #     'activity_id': 1,
            #     'company_id': 1,
            # }
            #
            # tasks.user_forward_send_activity_redPacket.delay(_data)

            _data = {
                'authorizer_appid': 'wxa77213c591897a13',
                'authorizer_refresh_token': 'refreshtoken@@@RAVUheyR510HyjAYrDxgSrX8MHDkbbb5ysHgGRWHeUc',
                'key_name': 'authorizer_access_token_wxa77213c591897a13',
                'app_id': 'wx6ba07e6ddcdc69b3',                     # 查看诸葛雷达_公众号的 appid
                'app_secret': '0bbed534062ceca2ec25133abe1eecba'    # 查看诸葛雷达_公众号的AppSecret
            }

            authorizer_access_token_ret = create_authorizer_access_token(_data)
            authorizer_access_token = authorizer_access_token_ret.data

            # access_token = "14_8p_bIh8kVgaZpnn_8IQ3y77mhJcSLoLuxnqtrE-mKYuOfXFPnNYhZAOWk8AZ-NeK6-AthHxolrSOJr1HvlV-gSlspaO0YFYbkPrsjJzKxalWQtlBxX4n-v11mqJElbT0gn3WVo9UO5zQpQMmTDGjAEDZJM"
            openid = 'ob5mL1Q4faFlL2Hv2S43XYKbNO-k'

            # get_user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
            get_user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'
            get_user_info_data = {
                'access_token': authorizer_access_token,
                'openid': openid,
                'lang': 'zh_CN',
            }

            ret = requests.get(get_user_info_url, params=get_user_info_data)
            ret.encoding = 'utf-8'
            ret_json = ret.json()

            print('----------- 【公众号】拉取用户信息 接口返回 ---------->>', json.dumps(ret_json))

    return JsonResponse(response.__dict__)
