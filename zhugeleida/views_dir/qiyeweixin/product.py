from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.qiyeweixin.product_verify import ProductAddForm, ProductUpdateForm, ProductSelectForm
import json
import os
import base64
from django import forms

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from django.db.models import Q



@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        if oper_type == 'product_single':

            user_id = request.GET.get('user_id')
            product_id = request.GET.get('product_id')
            field_dict = {
                'id': '',

            }
            q = conditionCom(request, field_dict)
            q.add(Q(**{'id': product_id}), Q.AND)

            objs = models.zgld_product.objects.select_related('user', 'company').filter(q)
            count = objs.count()

            if objs:
                ret_data = []
                for obj in objs:
                    if obj.user_id:
                        if int(obj.user_id) == int(user_id):
                            publisher = '我添加的'
                        else:
                            publisher = obj.user.username + '添加的'
                    else:
                        publisher = '企业发布'

                    cover_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                    picture_type=1).order_by(
                        'create_date').values('id', 'picture_url')

                    product_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id,
                                                                                      picture_type=2).values('id',
                                                                                                             'order',
                                                                                                             'picture_url')

                    article_data = models.zgld_product_article.objects.filter(product_id=obj.id).values('id', 'order',
                                                                                                        'content',
                                                                                                        'title')

                    article_picture_list = []
                    article_picture_list.extend(product_picture_data)
                    article_picture_list.extend(article_data)

                    print('---article_picture_list-->>', article_picture_list)

                    # article_content_data = models.zgld_product_article.objects.filter(type=2).values_list('id','order','content')
                    ret_data_list = sort_article_data(list(article_picture_list))
                    user_avatar = models.zgld_userprofile.objects.get(id=user_id).avatar

                    ret_data.append({
                        'id': obj.id,

                        'publisher': publisher,  # 发布者
                        'publisher_date': obj.create_date,  # 发布日期。
                        'cover_picture': list(cover_picture_data) or '',  # 封面地址的URL
                        'name': obj.name,  # 产品名称
                        'price': obj.price,  # 价格
                        'user_avatar': user_avatar,

                        'reason': obj.reason,  # 推荐理由
                        'article_data': ret_data_list,
                        'create_date': obj.create_date.strftime("%Y-%m-%d"),  # 发布的日期
                        'status': obj.get_status_display(),  # 产品的动态
                        'status_code': obj.status  # 产品的动态值。

                    })
                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }

            else:
                response.code = 302
                response.msg = "产品不存在"

        elif oper_type == 'product_list':
            forms_obj = ProductSelectForm(request.GET)
            if forms_obj.is_valid():
                user_id = int(request.GET.get('user_id'))
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                order = request.GET.get('order', '-create_date')
                status = request.GET.get('status_code')
                # field_dict = {
                #     'status': '',
                #     'create_date': '',
                # }
                company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company.id

                # q = conditionCom(request, field_dict)
                # q.add(Q(**{'user_id': user_id}), Q.AND)
                # q.add(Q(**{'company_id': company_id}), Q.AND)
                # q.add(Q(**{'user_id__isnull': True,'company_id': company_id},), Q.AND)

                con = Q()
                q1 = Q()
                q1.connector = 'and'  # 满足个人发布只能看自己的
                q1.children.append(('user_id', user_id))
                q1.children.append(('company_id', company_id))
                q1.children.append(('status', status)) if status else ''

                q2 = Q()
                q2.connector = 'and' # 满足只能看公司发布的
                q2.children.append(('company_id', company_id))
                q2.children.append(('user_id__isnull', True))

                q3 = Q()
                q3.connector = 'and'  # 满足只能看公司发布的
                if status:
                    if  int(status) in [1, 3]:  # 表示搜索了上架或者被推荐了的产品。
                        q3.children.append(('status', status))
                    elif int(status) == 2: # 表示下架了产品
                        q3.children.append(('status', status))
                        q3.children.append(('status', status))


                con.add(q1, 'OR')
                con.add(q2, 'OR')
                con.add(q3, 'AND')



                print('-----con----->',con)

                objs = models.zgld_product.objects.select_related('user', 'company').filter(con).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []

                for obj in objs:
                    product_id = obj.id
                    if obj.user_id:
                        if int(obj.user_id) == int(user_id):
                            publisher = '我添加的'
                        else:
                            publisher = obj.user.username + '添加的'
                    else:
                        publisher = '企业发布'

                    picture_obj = models.zgld_product_picture.objects.filter(
                                product_id=product_id, picture_type=1
                    ).order_by('create_date')

                    picture_url = ''
                    if picture_obj:
                        picture_url = picture_obj[0].picture_url


                    ret_data.append({
                        'id': product_id,
                        'name': obj.name ,# 标题
                        'publisher': publisher,  # 发布者
                        'price': obj.price,  # 价格
                        'publisher_date': obj.create_date,  # 发布日期。
                        'cover_picture': picture_url,  # 封面地址的URL

                        'create_date': obj.create_date.strftime("%Y-%m-%d"),  # 发布的日期
                        'status': obj.get_status_display(),
                        'status_code': obj.status  # 产品的动态。

                    })
                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }
            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 添加企业的产品
class imgUploadForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "图片名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    img_data = forms.CharField(
        error_messages={
            'required': "图片内容不能为空"
        }
    )

    chunk = forms.IntegerField(
        error_messages={
            'required': "当前是第几份文件不能为空",
            'invalid': '份数必须是整数类型'
        }
    )


# 添加企业的产品
class imgMergeForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "文件名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    chunk_num = forms.IntegerField(
        error_messages={
            'required': "总份数不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )


    picture_type = forms.IntegerField(
        error_messages={
            'required': "图片不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )



@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "update":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'product_id': o_id,  # 标题    非必须
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格    非必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                # 'article_id': request.POST.get('article_id'),  # 内容    非必须
            }

            forms_obj = ProductUpdateForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                product_id = forms_obj.data.get('product_id')
                article_data_list = json.loads(request.POST.get('article_data'))
                cover_picture_list = json.loads(request.POST.get('cover_picture_id'))

                product_obj = models.zgld_product.objects.filter(id=product_id)

                product_obj.update(
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )
                exist_cover_picture_list = []
                picture_list = list(models.zgld_product_picture.objects.filter(product_id=product_id, picture_type=1).values_list('id'))
                for  p in  picture_list:
                    exist_cover_picture_list.append(p[0])

                delete_cover_picture_list = list(set(exist_cover_picture_list).difference(set(cover_picture_list)))
                print('----delete_cover_picture_list-->>',delete_cover_picture_list)

                delete_cover_picture_objs = models.zgld_product_picture.objects.filter(id__in=delete_cover_picture_list)

                if delete_cover_picture_objs: #要删除的封面图片。
                    for delete_picture_obj in delete_cover_picture_objs:
                        IMG_PATH = BASE_DIR + '/' + delete_picture_obj.picture_url
                        if os.path.exists(IMG_PATH): os.remove(IMG_PATH)
                    delete_cover_picture_objs.delete()

                product_id = product_obj[0].id
                picture_objs = models.zgld_product_picture.objects.filter(id__in=cover_picture_list)  # 更新前端传过来的封面ID绑定到数据库。
                picture_objs.update(product_id=product_id)

                now_picture_list = []
                now_article_list = []
                if article_data_list:

                    for article_data in article_data_list:
                        if 'picture_id' in article_data:
                                picture_id = article_data.get('picture_id')
                                now_picture_list.append(picture_id)

                    exist_product_picture_list = []
                    picture_list = list(models.zgld_product_picture.objects.filter(product_id=product_id, picture_type=2).values_list('id'))
                    for p in picture_list:
                        exist_product_picture_list.append(p[0])

                    delete_product_picture_list = list(set(exist_product_picture_list).difference(set(now_picture_list)))
                    print('----delete_product_picture_list-->>', delete_product_picture_list)

                    delete_product_picture_objs = models.zgld_product_picture.objects.filter(
                        id__in=delete_product_picture_list)

                    if delete_product_picture_objs:  # 要删除的产品图片。
                        for delete_picture_obj in delete_product_picture_objs:
                            IMG_PATH = BASE_DIR + '/' + delete_picture_obj.picture_url
                            if os.path.exists(IMG_PATH): os.remove(IMG_PATH)
                        delete_product_picture_objs.delete()

                    ## 比较新穿过来的文章列表和已经存在数据库的文章的ID的差级
                    for article_data in article_data_list:
                        if 'article_id' in article_data:
                                article_id = article_data.get('article_id')
                                now_article_list.append(article_id)

                    exist_article_list = []
                    article_list = models.zgld_product_article.objects.filter(product_id=product_id).values_list('id')
                    for a in article_list:
                        exist_article_list.append(a[0])

                    delete_article_list = list(set(exist_article_list).difference(set(now_article_list)))
                    print('--------delete_article_list------->>',delete_article_list)
                    delete_article_objs = models.zgld_product_article.objects.filter(id__in=delete_article_list)

                    if delete_article_objs:  # 要删除的文章内容的ID。
                        delete_article_objs.delete()


                    for article_data in article_data_list:
                        print('article_data_list 2 ------>>', article_data, type(article_data))
                        article_id = article_data.get('article_id')

                        if 'article_id' in article_data and 'title' in article_data:
                            obj = models.zgld_product_article.objects.filter(product_id=product_id,id=article_id)
                            obj.update(
                                title=article_data.get('title'),
                                type=1,
                                order=article_data.get('order')
                            )


                        elif 'article_id' in article_data and 'content' in article_data:
                            obj = models.zgld_product_article.objects.filter(product_id=product_id,id=article_id)
                            obj.update(
                                content=article_data.get('content'),
                                type=2,
                                order=article_data.get('order')
                            )


                        elif 'article_id' not  in article_data and  'title' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                title=article_data.get('title'),
                                type=1,
                                order=article_data.get('order')
                            )

                        elif 'article_id' not  in article_data and 'content' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                content=article_data.get('content'),
                                type=2,
                                order=article_data.get('order')
                            )
                        elif  'picture_id' in article_data:
                            picture_id = article_data.get('picture_id')
                            picture_obj = models.zgld_product_picture.objects.filter(id=picture_id)
                            picture_obj.update(product_id=product_id, order=article_data.get('order'))


                    response.code = 200
                    response.msg = "添加成功"
                else:
                    objs = models.zgld_product_article.objects.filter(product_id=product_id)
                    if objs:
                        objs.delete()

                    response.code = 200
                    response.msg = "添加成功"


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        #上传产品图片的接口
        elif oper_type == "add_picture":
            response = Response.ResponseObj()

            forms_obj = imgUploadForm(request.POST)
            if forms_obj.is_valid():
                img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
                timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
                img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
                chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
                expanded_name = img_name.split('.')[-1]  # 扩展名

                img_name = timestamp + "_" + str(chunk) + '.' + expanded_name

                img_save_path = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs','qiyeweixin' ,'product', 'tmp', img_name)

                img_data = base64.b64decode(img_data.encode('utf-8'))
                with open(img_save_path, 'w') as f:
                    f.write(img_data)

                response.code = 200
                response.msg = "上传成功"
            else:
                response.code = 303
                response.msg = "上传异常"
                response.data = json.loads(forms_obj.errors.as_json())

            return JsonResponse(response.__dict__)

        #产品图片合并请求
        elif  oper_type == "upload_complete":

            response = Response.ResponseObj()
            forms_obj = imgMergeForm(request.POST)
            if forms_obj.is_valid():
                img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
                timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
                chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
                expanded_name = img_name.split('.')[-1]  # 扩展名
                picture_type = forms_obj.cleaned_data.get('picture_type')  # 图片的类型  (1, '产品封面的图片'), (2, '产品介绍的图片')

                file_dir = ''
                file_dir = os.path.join(BASE_DIR,'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product')

                fileData = ''
                for chunk in range(chunk_num):
                    file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
                    file_save_path = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs','qiyeweixin' ,'product', 'tmp', file_name)
                    with open(file_save_path, 'r') as f:
                        fileData += f.read()

                    os.remove(file_save_path)

                img_path = os.path.join(file_dir, img_name)
                file_obj = open(img_path, 'ab')
                img_data = base64.b64decode(fileData)
                file_obj.write(img_data)

                product_picture_obj = models.zgld_product_picture.objects.create(picture_type=picture_type,
                                                                                     picture_url=img_path)

                response.data = {
                            'picture_type': product_picture_obj.picture_type,
                            'picture_id': product_picture_obj.id,
                            'picture_url': product_picture_obj.picture_url,
                }

                response.code = 200
                response.msg = "添加图片成功"

            else:
                response.code = 303
                response.msg = "上传异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete_picture":
            # 删除 ID
            product_id = request.POST.get('product_id')
            picture_objs = models.zgld_product_picture.objects.filter(id=o_id,product_id=product_id) # 接口

            if picture_objs:
                IMG_PATH = BASE_DIR + '/' + picture_objs[0].picture_url
                if os.path.exists(IMG_PATH): os.remove(IMG_PATH)

                picture_objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '图片ID不存在'

        # 删除文章的[标题或内容]的相关记录
        elif oper_type == "delete_article":
            # 删除 ID
            product_id = request.POST.get('product_id')
            picture_article_objs = models.zgld_product_article.objects.filter(id=o_id,product_id=product_id)
            if picture_article_objs:
                picture_article_objs.delete()
                response.code = 200
                response.msg = "删除文章字段成功"
            else:
                response.code = 302
                response.msg = '图片ID不存在'

        elif oper_type == "change_status":

            status = int(request.POST.get('status'))
            user_id =int(request.GET.get('user_id'))
            product_objs = models.zgld_product.objects.filter(id=o_id)
            print('product_objs--------->',product_objs)


            if product_objs:

                if not  product_objs[0].user_id:  # 用户ID不存在，说明它是企业发布的产品，只能被推荐和取消推荐，不能被下架和上架。
                    if int(status) in [1,3]: # 1为上架，2，为下架, 3为推荐
                        product_objs.update(
                            status=status
                        )
                        response.code = 200
                        response.msg = "修改状态成功"
                        response.data = {
                            'product_id': product_objs[0].id,
                            'status': product_objs[0].get_status_display(),
                            'status_code': product_objs[0].status
                        }
                    else:
                        response.code = 302
                        response.msg = "没有权限修改"

                elif product_objs[0].user_id == int(user_id): # 修改用户发布产品的状态

                    product_objs.update(
                        status=status
                    )
                    response.code = 200
                    response.msg = "修改状态成功"
                    response.data = {
                        'product_id': product_objs[0].id,
                        'status': product_objs[0].get_status_display(),
                        'status_code': product_objs[0].status
                    }

                else:
                    response.code = 302
                    response.msg = "没有权限修改"


            else:

                response.code = 302
                response.msg = '产品不存在'

        # 触发-删除个人产品
        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            product_objs = models.zgld_product.objects.filter(id=o_id, user_id=user_id)

            product_picture_objs = models.zgld_product_picture.objects.filter(product_id=o_id)
            product_article_objs = models.zgld_product_article.objects.filter(product_id=o_id)

            if product_objs:
                product_objs.delete()
                product_picture_objs.delete()
                product_article_objs.delete()
                response.code = 200
                response.msg = "删除成功"



            else:
                response.code = 302
                response.msg = '产品不存在'

        elif oper_type == "add":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格     必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                # 'title': request.POST.get('title'),    # 标题    非必须
                # 'content': request.POST.get('content'),  # 内容    非必须
            }

            forms_obj = ProductAddForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                article_data_list = json.loads(request.POST.get('article_data'))
                cover_picture_list = json.loads(request.POST.get('cover_picture_id'))

                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                product_obj = models.zgld_product.objects.create(
                    user_id=user_id,
                    company_id=company_id,
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )


                #封面图片绑定到产品。
                product_id = product_obj.id
                picture_objs = models.zgld_product_picture.objects.filter(id__in=cover_picture_list)
                picture_objs.update(product_id=product_id)

                if article_data_list:
                    print('article_data_list 1 ------>>', article_data_list, type(article_data_list))
                    for article_data in article_data_list:
                        print('article_data_list 2 ------>>', article_data, type(article_data))
                        if 'title' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                title=article_data.get('title'),
                                type=1,
                                order=article_data.get('order')

                            )
                        elif 'content' in article_data:
                            models.zgld_product_article.objects.create(
                                product_id=product_id,
                                content=article_data.get('content'),
                                type=2,
                                order=article_data.get('order')
                            )
                        elif 'picture_id' in article_data:
                            picture_id = article_data.get('picture_id')
                            picture_obj = models.zgld_product_picture.objects.filter(id=picture_id)
                            picture_obj.update(product_id=product_id, order=article_data.get('order'))

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)




class create_product_picture:

    def __init__(self, user_id, picture_obj, product_obj, type):
        self.response = Response.ResponseObj()
        self.user_id = user_id
        self.picture_obj = picture_obj
        self.product_obj = product_obj
        self.picture_type = type
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def comon_picture(self, p_obj, product_picture_obj):

        userid = models.zgld_userprofile.objects.get(id=self.user_id).userid
        product_picture = '/%s_%s_photo.jpg' % (product_picture_obj.id, userid)

        photo_url = 'statics/zhugeleida/imgs/qiyeweixin/product%s' % (product_picture)
        product_picture_obj.picture_url = photo_url
        product_picture_obj.save()
        IMG_PATH = os.path.join(self.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin',
                                'product') + product_picture
        with open('%s' % (IMG_PATH), 'wb') as f:
            print('---p_obj-->>', p_obj)

            for chunk in p_obj.chunks():
                f.write(chunk)

    def create_picture(self):
        if self.picture_obj:  # 封面图片存在
            for p_obj in self.picture_obj:
                product_picture_obj = models.zgld_product_picture.objects.create(picture_type=1,
                                                                                 product_id=self.product_obj.id)
                self.comon_picture(p_obj, product_picture_obj)

            return '200'
        else:
            self.response.code = 301
            self.response.msg = "封面图片不能为空"
            return '301'


def sort_article_data(data):
    ret_list = []
    for obj in data:
        if not ret_list:
            # tmp_dict[obj['order']] = obj
            ret_list.append(obj)

        else:
            for index, data in enumerate(ret_list):
                if obj['order'] < data['order']:
                    ret_list.insert(index, obj)
                    break
            else:
                ret_list.append(obj)
    return ret_list
