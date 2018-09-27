
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.article_verify import ArticleAddForm,ArticleSelectForm, ArticleUpdateForm,MyarticleForm
import time
import datetime
import json, base64
from django.db.models import Q, Count
from zhugeleida.public.condition_com import conditionCom
from zhugeleida.public.common import create_qrcode
from zhugeleida.views_dir.gongzhonghao.user_gongzhonghao_auth import create_gongzhonghao_yulan_auth_url

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
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
                    'status': '',           # 按状态搜索, (1,'已发'),  (2,'未发'),
                                            # 【暂时不用】 按员工搜索文章、目前只显示出自己的文章
                    'title': '__contains',  # 按文章标题搜索
                }

                request_data = request.GET.copy()
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id

                q = conditionCom(request_data, field_dict)
                q.add(Q(**{'company_id': company_id}), Q.AND)

                tag_list = json.loads(request.GET.get('tags_list')) if request.GET.get('tags_list') else []
                if tag_list:
                    q.add(Q(**{'tags__in': tag_list}), Q.AND)

                objs = models.zgld_article.objects.filter(q).order_by(order)


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
            return JsonResponse(response.__dict__)


    return JsonResponse(response.__dict__)

# # 递归 脉络图
# def init_data(user_id, article_id, o_id=None):
#     datadict = []
#     if o_id:
#         objs = models.zgld_article_to_customer_belonger.objects.filter(customer_parent_id=o_id).filter(
#             article_id=article_id).filter(user_id=user_id)
#         for obj in objs:
#             if obj.customer_parent.id == obj.customer.id:
#                 continue
#             decode_username = base64.b64decode(obj.customer_parent.username)
#             username = str(decode_username, 'utf-8')
#             parentId = obj.customer.id
#             result = init_data(user_id, article_id, parentId)
#             flag = True
#             # print('result=====> ',result)
#             for other in datadict:
#                 if username in other.get('name'):
#                     flag = False
#                     if result:
#                         print(result)
#                         other.get('children').append(result[0])
#             if flag:
#                 if result:
#                     datadict.append({
#                         'name':username,
#                         'children': result
#                     })
#                 else:
#                     datadict.append({
#                         'name': username,
#                     })
#
#     return datadict


def init_data(user_id, pid=None, level=1):
    """
    获取权限数据
    :param pid:  权限父级id
    :return:
    """
    result_data = []
    objs = models.zgld_article_to_customer_belonger.objects.select_related('user').filter(
        customer_parent_id=pid,
        user_id=user_id,
        level=level
    )
    for obj in objs:
        print('pid------------> ',pid)
        print('customer_parent_id------------> ',obj.customer_parent_id, obj.customer_id)
        if obj.customer_parent_id == obj.customer_id:
            continue

        decode_username = base64.b64decode(obj.customer.username)
        customer_username = str(decode_username, 'utf-8')
        current_data = {
            'name': customer_username,
            'id':obj.id,
            # 'user_id': obj.customer_id
        }
        children_data = init_data(user_id, pid=obj.customer_id, level=level+1)
        if children_data:
            current_data['children'] = children_data
        result_data.append(current_data)

    print('result_data -->', result_data)
    return result_data

def mailuotu(q):
    # children_data = init_data(user_id)
    # print('children_data--------> ',children_data)
    # print('q------------------------------> ',q)
    count_objs = models.zgld_article_to_customer_belonger.objects.select_related(
        'user',
        'article'
    ).filter(q).values('user_id', 'user__username', 'article__title').annotate(Count('user'))
    result_data = []
    for obj in count_objs:
        user_id = obj['user_id']
        username = obj['user__username']
        print('user_id -->', user_id)
        print('username -->', username)

        children_data = init_data(user_id)
        print('children_data------> ',children_data)
        tmp = {'name': username}
        if children_data:
            tmp['children'] = children_data
        result_data.append(tmp)

    print('result_data -->', result_data)

    article_title = count_objs[0]['article__title']
    return article_title, result_data

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    timestamp = str(int(time.time() * 1000))

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

                user_id = request.GET.get('user_id')
                company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id

                dict_data = {
                    'user_id': user_id,
                    'company_id': company_id,
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

                # url = 'http://zhugeleida.zhugeyingxiao.com/zhugeleida/gongzhonghao/myarticle/%s' % (obj[0].id)

                # token = obj.user.token
                # rand_str = account.str_encrypt(timestamp + token)

                data = {
                    'company_id' : company_id,
                    'article_id': obj.id,
                    'uid': '',
                    'pid':  '',
                    'level':  1,

                }

                auth_url_ret =  create_gongzhonghao_yulan_auth_url(data)
                authorize_url = auth_url_ret.data.get('authorize_url')

                qrcode_data = {
                    'url': authorize_url,
                    'article_id' : obj.id,
                }
                response_ret = create_qrcode(qrcode_data)
                pre_qrcode_url = response_ret.data.get('pre_qrcode_url')
                if pre_qrcode_url:
                    response = response_ret
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
                    id=article_id
                )
                obj.update(**dict_data)

                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    obj[0].tags = tags_id_list

                # url = 'http://zhugeleida.zhugeyingxiao.com/zhugeleida/gongzhonghao/myarticle/%s' % (obj[0].id)
                # data = {
                #     'url': url,
                #     'article_id' : obj[0].id,
                # }
                # response_ret = create_qrcode(data)
                # pre_qrcode_url = response_ret.data.get('pre_qrcode_url')
                company_id = obj[0].company_id
                # token = obj.user.token
                # rand_str = account.str_encrypt(timestamp + token)

                data = {
                    'company_id': company_id,
                    'article_id': obj[0].id,
                    'uid': '',
                    'pid': '',
                    'level': 1,
                }

                auth_url_ret = create_gongzhonghao_yulan_auth_url(data)
                authorize_url = auth_url_ret.data.get('authorize_url')

                qrcode_data = {
                    'url': authorize_url,
                    'article_id': obj[0].id,
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
        if oper_type == 'myarticle':
            user_id = request.GET.get('user_id')
            request_data_dict = {
                'article_id' : o_id,
                # 'uid': user_id,  # 文章所属用户的ID
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
                        'avatar': obj.user.avatar,  # 用户的头像
                        'company_id': obj.company_id,
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

        elif oper_type == 'thread_base_info': # 脉络图
            user_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            request_data_dict = {
                'article_id': o_id,
                # 'uid': user_id,  # 文章所属用户的ID
            }

            forms_obj = MyarticleForm(request_data_dict)
            if forms_obj.is_valid():
                article_id = forms_obj.cleaned_data.get('article_id')
                models.zgld_article_to_customer_belonger.objects.filter(article_id=article_id,user_id=uid).order_by('-level').values('id','level')

            else:
                print('------- 未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 脉络图 统计文章 转载情况
        elif oper_type == 'contextDiagram':
            article_id = o_id   # 文章id
            uid = request.GET.get('uid')
            q = Q()
            q.add(Q(article_id=article_id), Q.AND)
            if uid:
                q.add(Q(user_id=uid), Q.AND)
            objs = models.zgld_article_to_customer_belonger.objects.filter(article_id=article_id)
            if objs:

                article_title, result_data = mailuotu(q)

                dataList = {                    # 顶端 首级
                    'name': article_title,
                    'children': result_data
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'dataList': dataList,
                    'article_title': article_title
                }
            else:
                response.code = 301
                response.msg = '该文章无查看'
                response.data = {}
        else:
            response.code = 402
            response.msg = '请求异常'
    return JsonResponse(response.__dict__)




