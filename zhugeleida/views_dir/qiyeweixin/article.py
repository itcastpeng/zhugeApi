from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.article_verify import ArticleAddForm, ArticleSelectForm, \
    ArticleUpdateForm, MyarticleForm, ThreadPictureForm, EffectRankingByLevelForm, QueryCustomerTransmitForm, \
    HideCustomerDataForm, ArticleAccessLogForm, ArticleForwardInfoForm,EffectRankingByTableForm, VideoForm
from zhugeleida.public.common import action_record
from django.db.models import Max, Avg, F, Q, Min, Count, Sum
from zhugeleida.views_dir.admin.article import mailuotu
from zhugeleida.public.pub import get_min_s
from django.db.models import Q
from zhugeleida.public.condition_com import conditionCom
from zhugeleida.public.common import conversion_seconds_hms
import json, datetime, time, base64


# 企业微信端文章查询
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def article(request, oper_type):
    response = Response.ResponseObj()
    # oper_type=myarticle_list
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        # 雷达AI 查询我的文章  (我--我的文章)
        if oper_type == 'myarticle_list':
            forms_obj = ArticleSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                user_id = request.GET.get('user_id')
                status = request.GET.get('status')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

                field_dict = {
                    'id': '',
                    'status': '',  # 按状态搜索, (1,'已发'),  (2,'未发')
                    'title': '__contains',  # 按文章标题搜索
                    'tags': '',     # 按标签查询
                }

                request_data = request.GET.copy()

                user_obj = models.zgld_userprofile.objects.get(id=user_id)
                company_id = user_obj.company_id
                article_admin_status = user_obj.article_admin_status
                article_admin_status_text = user_obj.get_article_admin_status_display()

                _status = 1
                if status:
                    _status = status

                q = conditionCom(request_data, field_dict)
                q.add(Q(**{'company_id': company_id}), Q.AND)
                q.add(Q(**{'status': _status }), Q.AND)

                objs = models.zgld_article.objects.select_related('company', 'user').filter(q).order_by(order)
                count = objs.count()
                if length != 0:
                    print('current_page -->', current_page)
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    article_to_customer_belonger_objs = models.zgld_article_to_customer_belonger.objects.select_related(
                        'article', 'user',
                        'customer').filter(
                        article_id=obj.id, user_id=user_id).order_by('-stay_time')

                    total_forward_num_dict = article_to_customer_belonger_objs.aggregate(forward_num=Sum('forward_count'))
                    forward_count = total_forward_num_dict.get('forward_num')
                    if not forward_count:
                        forward_count = 0

                    total_read_num_dict = article_to_customer_belonger_objs.aggregate(read_num=Sum('read_count'))
                    read_count = total_read_num_dict.get('read_num')
                    if not read_count:
                        read_count = 0

                    article_id = obj.id
                    activity_objs = models.zgld_article_activity.objects.filter(article_id=article_id).exclude(
                        status=3).order_by('-create_date')
                    now_date_time = datetime.datetime.now()
                    is_have_activity = 2  #
                    if activity_objs:
                        activity_obj = activity_objs[0]
                        start_time = activity_obj.start_time
                        end_time = activity_obj.end_time
                        if now_date_time >= start_time and now_date_time <= end_time:  # 活动开启并活动在进行中
                            is_have_activity = 1  # 活动已经开启

                    ret_data.append({
                        'id': article_id,
                        'title': obj.title,  # 文章标题
                        'status_code': obj.status,  # 状态
                        'status': obj.get_status_display(),  # 状态
                        'source_code': obj.source,  # 状态
                        'source': obj.get_source_display(),  # 状态
                        'author': obj.user.username,  # 如果为原创显示,文章作者
                        'avatar': obj.user.avatar,  # 用户的头像
                        'read_count': read_count,  # 被阅读数量
                        'forward_count': forward_count,  # 被转发个数
                        'create_date': obj.create_date,  # 文章创建时间
                        'cover_url': obj.cover_picture,  # 文章图片链接
                        'tag_list': list(obj.tags.values('id', 'name')),
                        'insert_ads': json.loads(obj.insert_ads) if obj.insert_ads else '',  # 插入的广告语
                        'is_have_activity': is_have_activity,



                    })


                response.code = 200
                response.data = {
                    'article_admin_status' : article_admin_status,
                    'article_admin_status_text' : article_admin_status_text,
                    'ret_data': ret_data,
                    'data_count': count,
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        elif oper_type == 'get_article_tags':
            company_id = models.zgld_userprofile.objects.get(id=user_id).company_id

            tag_list = models.zgld_article_tag.objects.filter(user__company_id=company_id).values('id', 'name')
            tag_data = list(tag_list)

            response.code = 200
            response.data = {
                'ret_data': tag_data,
                'data_count': tag_list.count(),
            }

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 企业微信端文章操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":

        # 添加企业微信端文章
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

        # 删除企业微信端文章
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

        # 修改企业微信端文章
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


        # 修改用户启用状态
        elif oper_type == "update_article_status":
            article_id = o_id
            status = request.POST.get('status')    #(1, "启用"),  (2, "未启用")
            company_id = request.GET.get('company_id')

            objs = models.zgld_article.objects.filter(id=o_id,company_id=company_id)

            if objs:
                if status:
                    objs.update(status=status)
                    response.code = 200
                    response.msg = "发布成功"

                    if status == 1:
                        user_objs = models.zgld_userprofile.objects.filter(company_id=company_id, status=1)
                        data = {}

                        customer_objs = models.zgld_customer.objects.filter(user_type=3, company_id=company_id)
                        if customer_objs:
                            customer_id = customer_objs[0].id
                        else:
                            encodestr = base64.b64encode('雷达管家'.encode('utf-8'))
                            customer_name = str(encodestr, 'utf-8')
                            obj = models.zgld_customer.objects.create(user_type=3, username=customer_name,
                                                                      company_id=company_id,
                                                                      headimgurl='statics/imgs/leidaguanjia.jpg')
                            customer_id = obj.id

                        for _obj in user_objs:
                            _user_id = _obj.id

                            remark = '【温馨提示】:管理员发布了文章《%s》,大家积极转发呦' % (objs[0].title)
                            print('---- 关注公众号提示 [消息提醒]--->>', remark)
                            data['user_id'] = customer_id
                            data['uid'] = _user_id
                            data['action'] = 666
                            data['article_id'] = article_id
                            action_record(data, remark)  # 此步骤封装到 异步中。

            else:
                response.code = 302
                response.msg = "文章不存在"



    elif request.method == "GET":
        # 查询自己的文章
        if oper_type == 'myarticle':
            request_data_dict = {
                'article_id': o_id,
            }
            user_id = request.GET.get('user_id')
            forms_obj = MyarticleForm(request_data_dict)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                article_id = forms_obj.cleaned_data.get('article_id')

                objs = models.zgld_article.objects.select_related('user', 'company').filter(id=article_id)
                count = objs.count()

                obj = objs[0]
                # 获取所有数据
                insert_ads = json.loads(obj.insert_ads) if obj.insert_ads else ''  # 插入的广告语
                if insert_ads and insert_ads.get('mingpian'):
                    zgld_userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)  # 获取企业微信中雷达AI分享出来文章对应用户的信息
                    insert_ads['username'] = zgld_userprofile_obj.username
                    insert_ads['avatar'] = zgld_userprofile_obj.avatar
                    insert_ads['phone'] = zgld_userprofile_obj.mingpian_phone
                    insert_ads['position'] = zgld_userprofile_obj.position
                    insert_ads['webchat_code'] = zgld_userprofile_obj.qr_code  # 企业用户个人二维码[小程序]

                ret_data = []
                tag_list = list(obj.tags.values('id', 'name'))

                ret_data.append({
                    'id': obj.id,
                    'title': obj.title,  # 文章标题
                    'author': obj.user.username,  # 如果为原创显示,文章作者
                    'company_id': obj.company_id,  # 公司ID
                    'avatar': obj.user.avatar,  # 用户的头像
                    'summary': obj.summary,  # 摘要
                    'create_date': obj.create_date,  # 文章创建时间
                    'cover_url': obj.cover_picture,  # 文章图片链接
                    'content': obj.content,  # 文章内容
                    'tag_list': tag_list,
                    'insert_ads': insert_ads  # 插入的广告语
                })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,

                }


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

            return JsonResponse(response.__dict__)


        ## 客户基本信息和所看到的所有文章数据展示
        elif oper_type == 'customer_read_info':  # 脉络图
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')
            log_type = request.GET.get('log_type')   # log_type 为1 为文章 2为录播视频


            current_page = request.GET.get('current_page')
            length = request.GET.get('length')
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
                q1.children.append(('user_id', user_id))

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                code = 302
                msg = '返回为空'
                data = {}

                # 录播视频
                if log_type in [2, '2']:
                    q1.add(Q(customer_id=customer_id) & Q(parent_customer__isnull=True) | Q(
                        parent_customer_id=customer_id), Q.AND)
                    objs = models.zgld_video_to_customer_belonger.objects.select_related(
                        'video',
                        'user',
                        'customer'
                    ).filter(q1)

                    article_num = objs.count()
                    ret_data = []
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    for obj in objs:
                        belonger_objs_one = models.zgld_video_to_customer_belonger.objects.filter(
                            user_id=user_id,
                            customer_id=obj.customer_id,
                            video_id=obj.video_id,
                            parent_customer__isnull=True
                        ).count()
                        belonger_objs_two = models.zgld_video_to_customer_belonger.objects.filter(
                            user_id=user_id,
                            parent_customer_id=obj.parent_customer_id,
                            video_id=obj.video_id,
                            parent_customer__isnull=False
                        ).count()
                        belonger_data = belonger_objs_one + belonger_objs_two
                        stay_time = get_min_s(int(obj.video_duration_stay))
                        ret_data.append({
                            'article_id': obj.video_id,
                            'article_title': obj.video.title,
                            'stay_time': stay_time,
                            'read_count': belonger_data,
                            'forward_count': belonger_data,
                            'level': 0,
                            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                        })
                    code = 200
                    msg = '查询成功'
                    data = {
                        'article_num': article_num,
                        'ret_data': ret_data
                    }

                else:
                    objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                        'customer').filter(q1)
                    if objs:
                        _objs = objs.values('article_id', 'article__title').annotate(Sum('stay_time'),
                            Sum('read_count'),
                            Sum('forward_count'))
                        article_num = _objs.count()

                        ret_data = []
                        if length != 0:
                            start_line = (current_page - 1) * length
                            stop_line = start_line + length
                            _objs = _objs[start_line: stop_line]

                        for _obj in _objs:
                            article_id = _obj.get('article_id')
                            last_access_objs = models.zgld_article_access_log.objects.filter(article_id=article_id,
                                customer_id=customer_id).order_by('-last_access_date')
                            print('v-last_access_objs--------------------> ', last_access_objs)
                            if last_access_objs:
                                last_access_date = last_access_objs[0].last_access_date.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                last_access_date = '00:00:00 00:00:00'

                            level = list(objs.filter(article_id=article_id).values_list('level', flat=True).distinct())
                            print('--- last_access_date ---->>', last_access_date)
                            stay_time = _obj.get('stay_time__sum')
                            stay_time = conversion_seconds_hms(stay_time)
                            ret_data.append({

                                'article_id': article_id,
                                'article_title': _obj.get('article__title'),
                                'stay_time': stay_time,
                                'read_count': _obj.get('read_count__sum'),
                                'forward_count': _obj.get('forward_count__sum'),
                                'level': sorted(level),
                                'create_date': last_access_date,
                            })

                        code = 200
                        msg = '返回成功'
                        data = {
                            'ret_data': ret_data,
                            'article_num': article_num,
                        }

                response.code = code
                response.msg = msg
                response.data = data


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
                    user_id=user_id
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
            user_id = request.GET.get('user_id')
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
                    user_id=user_id
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
                        user_id=user_id,
                        article_id=article_id,
                        customer_id=customer_id,
                        level=level)
                    customer_username = ''

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
                            'uid': user_id,
                            'user_name': user_name,
                            'customer_id': customer_id,
                            'customer_name': customer_username,
                            'customer_headimgurl': headimgurl,
                            'create_date': obj.create_date,
                            'level': level
                        }
                        ret_data.append(data_dict)


                    data_dict = {
                        'uid': user_id,
                        'user_name': user_name,
                        'user_avatar': avatar,
                        'level': 0
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


        # 每个文章的潜在客户的访问数据和访问日志
        elif oper_type == 'hide_customer_data':
            # level = request.GET.get('level')
            user_id = request.GET.get('user_id')
            current_page = request.GET.get('current_page')
            length = request.GET.get('length')
            order = request.GET.get('order','-last_access_date')   # 排序 -stay_time停留时长  -read_count 被阅读数量

            # uid = request.GET.get('uid')
            request_data_dict = {
                'article_id': o_id,
                'current_page': current_page,
                'length': length,
                # 'uid': user_id,  # 文章所属用户的ID
                # 'level': level,  # 文章所属用户的ID
            }

            forms_obj = HideCustomerDataForm(request_data_dict)
            if forms_obj.is_valid():

                article_id = forms_obj.cleaned_data.get('article_id')
                # level = forms_obj.cleaned_data.get('level')
                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(
                    article_id=article_id, user_id=user_id).order_by(order)

                # total_customer_num = objs.values_list('customer_id').distinct().count()
                # total_read_num = objs.aggregate(total_read_num=Sum('read_count'))
                # total_read_num = total_read_num.get('total_read_num')
                # if not  total_read_num:
                #     total_read_num = 0

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                ret_data = []
                if objs:
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
                        # print('------- jie -------->>', str(username, 'utf-8'))
                        username = str(username, 'utf-8')
                        area = obj.customer.province + obj.customer.city
                        last_access_date = obj.last_access_date.strftime('%Y-%m-%d %H:%M:%S') if obj.last_access_date  else ''

                        data_dict = {
                            'article_id': obj.article_id,
                            'uid': obj.user_id,
                            'user_name': obj.user.username,  # 雷达用户姓名
                            'customer_id': obj.customer_id,  # 客户ID
                            'customer_name': username,  # 客户姓名
                            'customer_headimgurl': obj.customer.headimgurl,  # 客户头像
                            'sex_text': obj.customer.get_sex_display(),  # 性别
                            'sex': obj.customer.sex,  # 性别
                            'area': area,  # 地区
                            'read_count': obj.read_count,  # 阅读次数
                            'forward_count': obj.forward_count,  # 转发次数
                            'stay_time': stay_time,  # 停留时间
                            'level': obj.level,  # 所在层级
                            'pid': obj.customer_parent_id,
                            'last_access_date': last_access_date
                        }

                        # level_ret_data.append(data_dict)
                        # print('----- level_ret_data --------->?',level_ret_data)

                        ret_data.append(data_dict)

                    print('------ ret_data ------->>', ret_data)
                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {
                        # 'level_num': level_num,
                        'ret_data': ret_data,
                        'article_id': article_id,
                        # 'total_customer_num': total_customer_num,  # 浏览人数
                        # 'total_read_num': total_read_num,          # 浏览总数
                        'count': count,  # 数据总条数
                    }



            else:
                print('------- 未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 获取文章访问日志
        elif oper_type == 'get_article_access_log':
            log_type = request.GET.get('log_type')  # log_type 为1 为文章 2为录播视频
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')
            parent_id = request.GET.get('pid')
            current_page = request.GET.get('current_page')
            length = request.GET.get('length')
            type =  request.GET.get('type')

            if log_type in [2, '2']:
                form_objs = VideoForm(request.GET)
                if form_objs.is_valid():
                    q_video = Q()
                    q_video.add(Q(customer_id=customer_id) & Q(parent_customer__isnull=True) | Q(parent_customer_id=customer_id), Q.AND)
                    objs = models.zgld_video_to_customer_belonger.objects.filter(
                        q_video,
                        user_id=user_id,
                    )
                    count = objs.count()
                    if objs:
                        obj = objs[0]

                        result_data = []
                        q_video_1 = Q()
                        q_video_1.add(Q(customer_id=customer_id) | Q(parent_customer_id=customer_id), Q.AND)
                        belonger_objs = models.zgld_video_to_customer_belonger.objects.filter(q_video_1, user_id=user_id).order_by('-create_date')
                        for belonger_obj in belonger_objs:
                            result_data.append({
                                'article_access_log_id': belonger_obj.id,
                                'last_read_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                'stay_time': get_min_s(int(obj.video_duration_stay)),  # 停留时间
                            })

                        area = obj.customer.province + obj.customer.city
                        username = ''
                        response.code = 200
                        response.msg = '查询成功'
                        response.data = {
                            'customer_id': obj.customer_id,  # 客户ID
                            'customer_name': username,  # 客户姓名
                            'customer_headimgurl': obj.customer.headimgurl,  # 客户头像
                            'sex_text': obj.customer.get_sex_display(),  # 性别
                            'sex': obj.customer.sex,  # 性别
                            'pid': obj.parent_customer_id,  # 父级Id
                            'area': area,  # 地区

                            'ret_data': result_data,
                            'data_count': count,
                        }

                else:
                    response.code = 301
                    response.msg = json.loads(form_objs.errors.as_json())

            else:
                request_data_dict = {
                    'article_id': o_id,
                    'customer_id': customer_id,
                    'user_id': user_id,  # 文章所属用户的ID
                    'current_page': current_page,
                    'length': length,
                }

                forms_obj = ArticleAccessLogForm(request_data_dict)
                if forms_obj.is_valid():
                    article_id = o_id

                    q = Q()
                    q.add(Q(**{'article_id': article_id}), Q.AND)
                    q.add(Q(**{'customer_id': customer_id}), Q.AND)
                    q.add(Q(**{'user_id': user_id}), Q.AND)

                    if not type:
                        if parent_id:
                            q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
                        else:
                            q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

                    print('---- 获取文章访问日志 q------>>',q)

                    objs = models.zgld_article_access_log.objects.filter(q).order_by('-last_access_date')
                    count = objs.count()
                    if objs:
                        current_page = forms_obj.cleaned_data['current_page']
                        length = forms_obj.cleaned_data['length']

                        ret_data = []
                        if objs:

                            if length != 0:
                                start_line = (current_page - 1) * length
                                stop_line = start_line + length
                                objs = objs[start_line: stop_line]

                            for obj in objs:
                                stay_time = obj.stay_time
                                stay_time = conversion_seconds_hms(stay_time)

                                last_access_date = obj.last_access_date.strftime('%Y-%m-%d %H:%M:%S')
                                data_dict = {
                                    'article_access_log_id': obj.id,
                                    'last_read_time': last_access_date,
                                    'stay_time': stay_time,  # 停留时间
                                }

                                # level_ret_data.append(data_dict)
                                # print('----- level_ret_data --------->?',level_ret_data)

                                ret_data.append(data_dict)

                            area = objs[0].customer.province + objs[0].customer.city
                            username = objs[0].customer.username
                            username = base64.b64decode(username)
                            # print('------- jie -------->>', str(username, 'utf-8'))
                            username = str(username, 'utf-8')

                            response.code = 200
                            response.data = {
                                'customer_id': objs[0].customer_id,  # 客户ID
                                'customer_name': username,  # 客户姓名
                                'customer_headimgurl': objs[0].customer.headimgurl,  # 客户头像
                                'sex_text': objs[0].customer.get_sex_display(),  # 性别
                                'sex': objs[0].customer.sex,  # 性别
                                'pid': objs[0].customer_parent_id,  # 父级Id
                                'area': area,  # 地区

                                'ret_data': ret_data,
                                'data_count': count,
                            }

                            print('------ ret_data ------->>', ret_data)

                else:
                    # print("验证不通过")
                    print(forms_obj.errors)
                    response.code = 301
                    response.msg = json.loads(forms_obj.errors.as_json())

        #
        elif oper_type == 'get_article_forward_info':
            print('----- request.GET ------->>', request.GET)
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')
            parent_id = request.GET.get('pid')
            current_page = request.GET.get('current_page')
            length = request.GET.get('length')

            request_data_dict = {
                'article_id': o_id,
                'customer_id': customer_id,
                'user_id': user_id,  # 文章所属用户的ID
                'current_page': current_page,
                'length': length,

            }

            forms_obj = ArticleForwardInfoForm(request_data_dict)
            if forms_obj.is_valid():
                article_id = o_id

                q = Q()
                q.add(Q(**{'article_id': article_id}), Q.AND)
                q.add(Q(**{'customer_id': customer_id}), Q.AND)
                q.add(Q(**{'user_id': user_id}), Q.AND)

                if parent_id:
                    q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
                else:
                    q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

                objs = models.zgld_article_to_customer_belonger.objects.filter(q)
                count = objs.count()
                print('------- objs ---->>', objs)
                if objs:
                    current_page = forms_obj.cleaned_data['current_page']
                    length = forms_obj.cleaned_data['length']

                    ret_data = []
                    if objs:

                        if length != 0:
                            start_line = (current_page - 1) * length
                            stop_line = start_line + length
                            objs = objs[start_line: stop_line]

                        for obj in objs:

                            username = obj.customer.username
                            username = base64.b64decode(username)
                            username = str(username, 'utf-8')
                            area = obj.customer.province + obj.customer.city
                            forward_customer_objs = models.zgld_article_to_customer_belonger.objects.filter(
                                article_id=article_id,
                                user_id=user_id,
                                customer_parent_id=obj.customer_id
                            )
                            forward_customer_read_people = forward_customer_objs.count()
                            forward_customer_read_num = forward_customer_objs.aggregate(
                                forward_customer_read_num=Sum('read_count'))
                            print('------ forward_customer_read_num ------>', forward_customer_read_num)

                            forward_customer_read_num = forward_customer_read_num.get('forward_customer_read_num')
                            if not forward_customer_read_num:
                                forward_customer_read_num = 0

                            data_dict = {
                                'article_id': obj.article_id,
                                'customer_id': obj.customer_id,  # 客户ID
                                'customer_name': username,  # 客户姓名
                                'customer_headimgurl': obj.customer.headimgurl,  # 客户头像
                                'area': area,  # 地区
                                'sex_text': obj.customer.get_sex_display(),  # 性别
                                'sex': obj.customer.sex,  # 性别
                                'forward_customer_read_people': forward_customer_read_people,
                                'forward_customer_read_num': forward_customer_read_num,
                                'level': obj.level,
                                'forward_friend_count': obj.forward_friend_count,  # 转发给朋友的个数 分享方式(朋友圈/朋友)
                                'forward_friend_circle_count': obj.forward_friend_circle_count,  # 转发给朋友圈的个数
                                'pid': obj.customer_parent_id,
                            }
                            ret_data.append(data_dict)

                        response.code = 200
                        response.data = {
                            'ret_data': ret_data,
                            'data_count': count,
                        }

                else:
                    response.code = 302
                    response.msg = '没有数据'

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = forms_obj.errors.as_json()

        # 脉络图 统计文章 转载情况
        elif oper_type == 'contextDiagram':
            article_id = o_id  # 文章id
            user_id = request.GET.get('user_id')
            objs = models.zgld_article_to_customer_belonger.objects.filter(article_id=article_id)
            if objs:
                q = Q()
                q.add(Q(article_id=article_id), Q.AND)
                if user_id:
                    q.add(Q(user_id=user_id), Q.AND)

                article_title, result_data,max_person_num = mailuotu(article_id,q)

                dataList = {  # 顶端 首级
                    'name': article_title,
                    'children': result_data
                }

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'dataList': dataList,
                    'article_title': article_title,
                    'max_person_num' : max_person_num
                }
            else:
                response.code = 301
                response.msg = '该文章无数据'
                response.data = {}


        elif oper_type == 'test_update_customer_child_status':
            article_id = request.GET.get('article_id')

            for article_id in  list(models.zgld_article_to_customer_belonger.objects.all().values_list('article_id', flat=True).distinct()):

                objs = models.zgld_article_to_customer_belonger.objects.filter(article_id=article_id).order_by('level')
                if objs:
                    i = 0
                    for obj in objs:
                        id = obj.id
                        level = obj.level
                        customer_id = obj.customer_id
                        _article_id = obj.article_id
                        user_id = obj.user_id


                        q1 = Q()
                        q1.add(Q(**{'article_id': _article_id}), Q.AND)
                        if level:
                            level = int(level) + 1

                        q1.add(Q(**{'user_id': user_id}), Q.AND)
                        q1.add(Q(**{'level': level}), Q.AND)
                        q1.add(Q(**{'customer_parent_id': customer_id}), Q.AND)

                        _objs = models.zgld_article_to_customer_belonger.objects.filter(q1)
                        if _objs:
                            print('-----  打标签【成功】  q1:----->>', id,'|',q1)
                            obj.is_have_child = True
                            obj.save()

                        else:
                            print('-----  打有标签【失败】 |  搜索条件 q1:----->>',id,q1)

                        # i = i +1
                        # if i > 10:



        elif oper_type == 'query_customer_table_by_level':

            level = request.GET.get('level')
            # user_id = request.GET.get('user_id')
            user_id = 17

            query_customer_id = request.GET.get('query_customer_id')
            request_data_dict = {
                'article_id': o_id,
                'level': level,  # 文章所属用户的ID

            }

            forms_obj = EffectRankingByTableForm(request_data_dict)
            if forms_obj.is_valid():

                article_id = forms_obj.cleaned_data.get('article_id')
                level = forms_obj.cleaned_data.get('level')

                q1 = Q()
                q1.connector = 'AND'
                q1.children.append(('article_id', article_id))
                q1.children.append(('user_id', user_id))

                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(q1)

                ret_data = []
                if objs:
                    obj = objs[0]
                    level_num = objs.order_by('-level')[0].level
                    title = obj.article.title
                    total_count = objs.count()

                    # 初始化数据，只获取用户的下拉列表。

                    if level == 0 and user_id:

                        username = obj.user.username
                        gender = obj.user.gender
                        user_dict = objs.values('user_id').annotate(Sum('read_count'), Sum(
                            'forward_friend_circle_count'), Sum('forward_friend_count'))[0]
                        print('---- user_dict 数据 ---->>', user_dict)

                        read_count_sum = user_dict.get('read_count__sum')
                        forward_friend_sum = user_dict.get('forward_friend_count__sum')
                        forward_friend_circle_sum = user_dict.get('forward_friend_circle_count__sum')
                        print('-------> [ 只算一个人 ] user_id username -------->>', username, '|', user_id)

                        data_dict = {
                            'uid': user_id,  # 所属雷达用户
                            'user_name': username,
                            'sex': gender,
                            'read_count': read_count_sum,
                            'forward_friend_circle_count': forward_friend_sum,
                            'forward_friend_count': forward_friend_circle_sum,

                            'lower_people_count': total_count,
                            'lower_level': level_num,

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
                        objs = objs.order_by('level').filter(level=1, user_id=user_id)

                    elif level >= 1 and query_customer_id:

                        objs = objs.order_by('level').filter(level=level+1, customer_parent_id=query_customer_id)
                        level = level + 2

                    # count = objs.count()
                    for obj in objs:
                        customer_id = obj.customer_id
                        _level = obj.level

                        print('---- article_id, uid, customer_id, level ----->>', article_id, user_id, customer_id,level)

                        result_data, result_level = jisuan_level_num(article_id, user_id, customer_id, level )

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

            # article_id = request.GET.get('article_id')
            # user_id = request.GET.get('uid')
            # pid = request.GET.get('pid') or None
            # level = request.GET.get('level')
            # if level:
            #     level = int(level) + 1
            #
            # jisuan_level_num(article_id,user_id,pid,level)










    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


def jisuan_level_num(article_id, user_id, pid=None, level=1):
    """
    获取权限数据
    :param pid:  权限父级id
    :return:
    """

    result_level = []
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

        decode_username = base64.b64decode(obj.customer.username)
        customer_username = str(decode_username, 'utf-8')
        # customer_id = obj.customer_id
        # customer_username = obj.customer.username

        current_data = {
            'name': customer_username,
            'id': obj.id,
            # 'user_id': obj.customer_id
        }
        children_data,result_level_ret = jisuan_level_num(article_id, user_id, pid=obj.customer_id, level=level + 1)
        if children_data:
            current_data['children'] = children_data

            result_level.extend(result_level_ret[:])


        result_level.append(level)

        result_data.append(current_data)

    # print('level -->', result_level)
    # print('len*(level) -->', len(result_level))
    #
    # print('data -->', json.dumps(result_data))

    return result_data,result_level
