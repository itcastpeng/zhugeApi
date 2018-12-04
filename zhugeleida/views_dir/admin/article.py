from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.article_verify import ArticleAddForm, ArticleSelectForm, ArticleUpdateForm, MyarticleForm, \
    ThreadPictureForm, EffectRankingByLevelForm,QueryCustomerTransmitForm

from django.db.models import Max, Avg, F, Q, Min, Count, Sum
import datetime
import json, base64
from django.db.models import Q, Count
from zhugeleida.public.condition_com import conditionCom
from zhugeleida.public.common import create_qrcode
from zhugeleida.views_dir.gongzhonghao.user_gongzhonghao_auth import create_gongzhonghao_yulan_auth_url
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64


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
            return JsonResponse(response.__dict__)

    return JsonResponse(response.__dict__)


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


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加文章
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

                user_id = request.GET.get('user_id')
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id

                dict_data = {
                    'user_id': user_id,
                    'company_id': company_id,
                    'title': forms_obj.cleaned_data['title'],
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

                # url = 'http://zhugeleida.zhugeyingxiao.com/zhugeleida/gongzhonghao/myarticle/%s' % (obj[0].id)

                # token = obj.user.token
                # rand_str = account.str_encrypt(timestamp + token)

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
                article_objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '文章不存在'

        # 修改文章
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
                # token = obj.user.token
                # rand_str = account.str_encrypt(timestamp + token)

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

    else:

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

                objs = models.zgld_article.objects.select_related('user', 'company', 'plugin_report').filter(
                    id=article_id)
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
                        'insert_ads': insert_ads  # 插入的广告语

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

            customer_id = request.GET.get('customer_id')
            request_data_dict = {
                # 'article_id': o_id,
                'customer_id': customer_id,  # 文章所属用户的ID
                # 'company_id': company_id,  # 文章所属用户的ID
            }

            forms_obj = ThreadPictureForm(request_data_dict)
            if forms_obj.is_valid():
                q1 = Q()
                q1.connector = 'AND'
                q1.children.append(('customer_id', customer_id))
                # q1.children.append(('user_id', user_id))

                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user',
                                                                                       'customer').filter(q1)
                if objs:
                    _objs = objs.values('article_id', 'article__title').annotate(Sum('stay_time'), Sum('read_count'),
                                                                                 Sum('forward_count'))

                    article_num = _objs.count()

                    ret_data = []
                    for _obj in _objs:
                        article_id = _obj.get('article_id')
                        last_access_date = models.zgld_article_access_log.objects.filter(article_id=article_id,
                                                                                         customer_id=customer_id).order_by(
                            '-last_access_date')[0].last_access_date
                        level = list(objs.filter(article_id=article_id).values_list('level', flat=True).distinct())
                        print('--- last_access_date ---->>', last_access_date)
                        stay_time = _obj.get('stay_time__sum')
                        stay_time = conversion_seconds_hms(stay_time)
                        ret_data.append({
                            'article_num': article_num,
                            'article_id': article_id,
                            'article_title': _obj.get('article__title'),
                            'stay_time': stay_time,
                            'read_count': _obj.get('read_count__sum'),
                            'forward_count': _obj.get('forward_count__sum'),
                            'level': sorted(level),
                            'create_date': last_access_date.strftime('%Y-%m-%d %H:%M:%S'),
                        })

                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {
                        'ret_data': ret_data,
                        # 'article_num': _article_num,
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
                    if objs:
                        obj = objs[0]
                        customer_username = obj.customer.username
                        customer_username = base64.b64decode(customer_username)
                        customer_username = str(customer_username, 'utf-8')
                        headimgurl = obj.customer.headimgurl
                        sex = obj.customer.get_sex_display()

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

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)
