
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.article_verify import ArticleAddForm,ArticleSelectForm, \
    ArticleUpdateForm,MyarticleForm,ThreadPictureForm,EffectRankingByLevelForm,QueryCustomerTransmitForm,HideCustomerDataForm,ArticleAccessLogForm


from django.db.models import Max, Avg, F, Q, Min, Count,Sum

import time
import datetime
import json
from django.db.models import Q
from zhugeleida.public.condition_com import conditionCom
from zhugeleida.public.common import  conversion_seconds_hms
import base64

@csrf_exempt
@account.is_token(models.zgld_userprofile)
def article(request,oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
            # 获取参数 页数 默认1

       if oper_type == 'myarticle_list':

            forms_obj = ArticleSelectForm(request.GET)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count

                field_dict = {
                    'id': '',
                    # 'user_id' : '',
                    'status': '',           # 按状态搜索, (1,'已发'),  (2,'未发'),
                                            # 【暂时不用】 按员工搜索文章、目前只显示出自己的文章
                    'title': '__contains',  # 按文章标题搜索
                }

                request_data = request.GET.copy()

                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id

                q = conditionCom(request_data, field_dict)
                q.add(Q(**{'company_id': company_id }), Q.AND)

                tag_list = json.loads(request.GET.get('tags_list')) if request.GET.get('tags_list') else []
                if tag_list:
                    q.add(Q(**{'tags__in': tag_list}), Q.AND)

                objs = models.zgld_article.objects.select_related('company','user').filter(q).order_by(order)


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
                    print('-----obj.tags.values---->', obj.tags.values('id','name'))
                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,       # 文章标题
                        'status_code': obj.status,   # 状态
                        'status': obj.get_status_display(),   # 状态
                        'source_code': obj.source,   # 状态
                        'source': obj.get_source_display(),   # 状态
                        'author': obj.user.username,   # 如果为原创显示,文章作者
                        'avatar': obj.user.avatar,  # 用户的头像
                        'read_count': obj.read_count,        #被阅读数量
                        'forward_count': obj.forward_count,  #被转发个数
                        'create_date': obj.create_date,      #文章创建时间
                        'cover_url' : obj.cover_picture,     #文章图片链接
                        'tag_list' :  list(obj.tags.values('id','name')),
                        'insert_ads' : json.loads(obj.insert_ads)  if obj.insert_ads else '' # 插入的广告语


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
@account.is_token(models.zgld_userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

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
                    'title' :forms_obj.cleaned_data['title'],
                    'summary' :forms_obj.cleaned_data['summary'],
                    'content' :forms_obj.cleaned_data['content'],
                    'cover_picture' :forms_obj.cleaned_data['cover_picture'].strip(),
                    'insert_ads': request.POST.get('insert_ads')
                }

                obj = models.zgld_article.objects.create(**dict_data)
                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if  tags_id_list:
                    obj.tags = tags_id_list

                response.code = 200
                response.msg = "添加成功"
            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('------delete o_id --------->>',o_id)
            user_id = request.GET.get('user_id')
            article_objs = models.zgld_article.objects.filter(id=o_id,user_id=user_id)

            if article_objs:
               article_objs.delete()
               response.code = 200
               response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '文章不存在'

        elif oper_type == "update":
            article_data = {
                'article_id' : o_id,
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
            request_data_dict = {
                'article_id' : o_id,

            }

            forms_obj = MyarticleForm(request_data_dict)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                article_id = forms_obj.cleaned_data.get('article_id')

                # order = request.GET.get('order', '-create_date')  # 默认是最新内容展示 ，阅读次数展示read_count， 被转发次数forward_count
                # field_dict = {
                #     'id': '',
                #     'user_id': '',
                #     'status': '',  # 按状态搜索, (1,'已发'),  (2,'未发'),
                #     # 【暂时不用】 按员工搜索文章、目前只显示出自己的文章
                #     'title': '__contains',  # 按文章标题搜索
                # }
                # request_data = request.GET.copy()
                # q = conditionCom(request_data, field_dict)


                objs = models.zgld_article.objects.select_related('user','company').filter(id=article_id)
                count = objs.count()

                # 获取所有数据
                ret_data = []
                # 获取第几页的数据
                for obj in objs:
                    print('-----obj.tags.values---->', obj.tags.values('id', 'name'))
                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,  # 文章标题
                        'author': obj.user.username,  # 如果为原创显示,文章作者
                        'company_id': obj.company_id, # 公司ID
                        'avatar': obj.user.avatar,  # 用户的头像
                        'summary': obj.summary,     # 摘要
                        'create_date': obj.create_date,  # 文章创建时间
                        'cover_url': obj.cover_picture,  # 文章图片链接
                        'content': obj.content,  # 文章内容
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

        ## 客户基本信息和所看到的所有文章数据展示
        elif oper_type == 'customer_base_info':  # 脉络图
            user_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            request_data_dict = {
                'article_id': o_id,
                'uid': uid,  # 文章所属用户的ID
            }

            forms_obj = ThreadPictureForm(request_data_dict)
            if forms_obj.is_valid():
                article_id = forms_obj.cleaned_data.get('article_id')
                objs = models.zgld_article_to_customer_belonger.objects.select_related('article').filter(article_id=article_id,
                                                                        user_id=user_id
                                                                        ).order_by('-level')
                if objs:
                    level_num = objs[0].level
                    title  =  objs[0].article.title
                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {
                        'level_num': level_num,
                        'article_id': article_id,
                        'title': title
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
            # uid = request.GET.get('uid')
            request_data_dict = {
                'article_id': o_id,
                # 'uid': uid,  # 文章所属用户的ID
                'level': level,  # 文章所属用户的ID
            }



            forms_obj = EffectRankingByLevelForm(request_data_dict)
            if forms_obj.is_valid():
                # objs = models.zgld_article_to_customer_belonger.objects.filter(article_id=2, user_id=1).values_list(
                #                                                                                                'customer_id',
                #                                                                                                'customer__username',
                #                                                                                                'customer_parent_id',
                #                                                                                                'level'
                #
                #                                                                                                )
                # print('---- 字典 ------->\n',list(objs))



                article_id = forms_obj.cleaned_data.get('article_id')
                level = forms_obj.cleaned_data.get('level')
                objs = models.zgld_article_to_customer_belonger.objects.select_related('article','user','customer').filter(
                                                                        article_id=article_id,
                                                                        user_id=user_id
                                                                        ).order_by('-level')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']


                ret_data = []
                if objs:
                        level_num = objs[0].level

                        if int(level) != 0:
                            objs = objs.filter(level=level).order_by('-stay_time')

                        if int(level) == 0 and level_num:
                            objs = objs.filter(level=1).order_by('-stay_time')
                            level = int(level) + 1

                        if length != 0:
                            start_line = (current_page - 1) * length
                            stop_line = start_line + length
                            objs = objs[start_line: stop_line]

                        count = objs.count()

                        for obj in objs:

                            stay_time = obj.stay_time
                            stay_time = conversion_seconds_hms(stay_time)

                            username =  obj.customer.username
                            username = base64.b64decode(username)
                            # print('------- jie -------->>', str(username, 'utf-8'))
                            username = str(username, 'utf-8')
                            area = obj.customer.province + obj.customer.city
                            data_dict = {
                             'article_id' : obj.article_id,
                             'uid' : obj.user_id,
                             'user_name' : obj.user.username,
                             'customer_id' : obj.customer_id,
                             'customer_name' : username,
                             'customer_headimgurl' : obj.customer.headimgurl,
                             'sex' : obj.customer.get_sex_display(),
                             'area' : area,
                             'read_count' : obj.read_count,
                             'stay_time': stay_time,
                             'level' : level
                            }

                            # level_ret_data.append(data_dict)
                            # print('----- level_ret_data --------->?',level_ret_data)

                            ret_data.append(data_dict)

                        print('------ ret_data ------->>',ret_data)
                        response.code = 200
                        response.msg = '返回成功'
                        response.data = {
                            'level_num' : level_num,
                            'ret_data': ret_data,
                            'article_id': article_id,
                            'count' : count,
                        }

            else:
                print('------- 未能通过------->>', forms_obj.errors)
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
                    level_num = objs[0].level
                    customer_parent_id = objs.filter(customer_id=customer_id,level=level)[0].customer_parent_id

                    for l in range(int(level)-1,0,-1):
                        _objs = objs.filter(level=l)
                        print('------ objs ------>>',_objs.values_list('customer_id','user_id','level'))

                        for obj in _objs:
                                customerId = obj.customer_id

                                if customerId == customer_parent_id:

                                    stay_time = obj.stay_time
                                    stay_time = conversion_seconds_hms(stay_time)
                                    username = obj.customer.username
                                    username = base64.b64decode(username)
                                    username = str(username, 'utf-8')
                                    area = obj.customer.province + obj.customer.city
                                    data_dict = {
                                        'article_id': obj.article_id,
                                        'uid': obj.user_id,
                                        'user_name': obj.user.username,
                                        'customer_id': obj.customer_id,
                                        'customer_name': username,
                                        'customer_headimgurl': obj.customer.headimgurl,
                                        'sex': obj.customer.get_sex_display(),
                                        'area': area,
                                        'read_count': obj.read_count,
                                        'stay_time': stay_time,
                                        'level': level
                                    }

                                    ret_data.append(data_dict)
                                    customer_parent_id = obj.customer_parent_id
                                    print('---- customer_parent_id --->>',customer_parent_id)
                                    break

                        print('------ ret_data ------->>', ret_data)

                    response.code = 200
                    response.msg = '返回成功'
                    response.data = {
                        'level': level,
                        'ret_data': ret_data,
                        'article_id': article_id
                    }

            else:
                print('------- 未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 每个文章的潜在客户的访问数据和访问日志
        elif oper_type == 'hide_customer_data':
            # level = request.GET.get('level')
            user_id = request.GET.get('user_id')
            # uid = request.GET.get('uid')
            request_data_dict = {
                'article_id': o_id,
                # 'uid': user_id,  # 文章所属用户的ID
                # 'level': level,  # 文章所属用户的ID
            }

            forms_obj = HideCustomerDataForm(request_data_dict)
            if forms_obj.is_valid():

                article_id = forms_obj.cleaned_data.get('article_id')
                # level = forms_obj.cleaned_data.get('level')
                objs = models.zgld_article_to_customer_belonger.objects.select_related('article', 'user','customer').filter(article_id=article_id,user_id=user_id).order_by('-stay_time')


                total_customer_num = objs.values_list('customer_id').distinct().count()
                total_read_num = objs.aggregate(total_read_num=Sum('read_count'))
                total_read_num = total_read_num.get('total_read_num')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                ret_data = []
                if objs:
                    count = objs.count()
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    # print('---- count --->', objs.all())
                    #


                    for obj in objs:
                        stay_time = obj.stay_time
                        stay_time = conversion_seconds_hms(stay_time)

                        username = obj.customer.username
                        username = base64.b64decode(username)
                        # print('------- jie -------->>', str(username, 'utf-8'))
                        username = str(username, 'utf-8')
                        area = obj.customer.province + obj.customer.city
                        data_dict = {
                            'article_id': obj.article_id,
                            'uid': obj.user_id,
                            'user_name': obj.user.username,     #雷达用户姓名
                            'customer_id': obj.customer_id,     #客户ID
                            'customer_name': username,          # 客户姓名
                            'customer_headimgurl': obj.customer.headimgurl, # 客户头像
                            'sex_text': obj.customer.get_sex_display(),   # 性别
                            'sex': obj.customer.sex,   # 性别
                            'area': area,   # 地区
                            'read_count': obj.read_count,       # 阅读次数
                            'forward_count': obj.forward_count, # 转发次数
                            'stay_time': stay_time,       # 停留时间
                            'level': obj.level            # 所在层级
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
                        'total_customer_num': total_customer_num,    # 浏览人数
                        'total_read_num': total_read_num,            # 浏览总数
                        'count': count,                              # 数据总条数
                    }

            else:
                print('------- 未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'get_article_access_log':

            parent_id = request.GET.get('pid')
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')

            request_data_dict = {
                'article_id': o_id,
                'customer_id': customer_id,
                'user_id': user_id,  # 文章所属用户的ID

            }

            forms_obj = ArticleAccessLogForm(request_data_dict)
            if forms_obj.is_valid():
                article_id = o_id

                q = Q()
                q.add(Q(**{'article_id': article_id}), Q.AND)
                q.add(Q(**{'customer_id': customer_id}), Q.AND)
                q.add(Q(**{'user_id': user_id}), Q.AND)

                # if parent_id:
                #     q.add(Q(**{'customer_parent_id': parent_id}), Q.AND)
                # else:
                #     q.add(Q(**{'customer_parent_id__isnull': True}), Q.AND)

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

                            username = obj.customer.username
                            username = base64.b64decode(username)
                            # print('------- jie -------->>', str(username, 'utf-8'))
                            username = str(username, 'utf-8')
                            area = obj.customer.province + obj.customer.city
                            last_access_date = obj.last_access_date.strftime('%Y-%m-%d %H:%M')
                            data_dict = {
                                'article_id': obj.article_id,
                                'customer_id': obj.customer_id,  # 客户ID
                                'customer_name': username,  # 客户姓名
                                'customer_headimgurl': obj.customer.headimgurl,  # 客户头像
                                'last_read_time': last_access_date ,
                                'sex_text': obj.customer.get_sex_display(),  # 性别
                                'sex': obj.customer.sex,  # 性别
                                'area': area,  # 地区
                                'stay_time': stay_time,  # 停留时间

                            }

                            # level_ret_data.append(data_dict)
                            # print('----- level_ret_data --------->?',level_ret_data)

                            ret_data.append(data_dict)
                        response.code = 200
                        response.data = {
                            'ret_data': ret_data,
                            'data_count': count,
                        }

                        print('------ ret_data ------->>', ret_data)

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)
