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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from django.db.models import Q
# cerf  token验证 用户展示模块
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

                    cover_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id, picture_type=1).order_by(
                                   'create_date').values_list('id','picture_url')

                    product_picture_data = models.zgld_product_picture.objects.filter(product_id=obj.id, picture_type=2).values('id','order','picture_url')

                    article_data = models.zgld_product_article.objects.filter(product_id=obj.id).values('id','order','content','title')

                    article_picture_list = []
                    article_picture_list.extend(product_picture_data)
                    article_picture_list.extend(article_data)


                    print('---article_picture_list-->>',article_picture_list)

                    # article_content_data = models.zgld_product_article.objects.filter(type=2).values_list('id','order','content')
                    ret_data_list = sort_article_data(list(article_picture_list))

                    ret_data.append({
                        'id': obj.id,

                        'publisher': publisher,             # 发布者
                        'publisher_date': obj.create_date,  # 发布日期。
                        'cover_picture': list(cover_picture_data) or '',  # 封面地址的URL
                        'name': obj.name,                  # 产品名称
                        'price': obj.price,                  # 价格
                        'reason': obj.reason,                  # 推荐理由
                        'article_data' : ret_data_list,

                        # 'title': obj.title,                  # 标题
                        # 'content': obj.content,                  # 内容
                        # 'product_picture': list(product_picture_data) or '',  # 介绍产品的图片

                        'create_date': obj.create_date.strftime("%Y-%m-%d"),  # 发布的日期
                        'status': obj.get_status_display(),    # 产品的动态
                        'status_code': obj.status              # 产品的动态值。

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
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                order = request.GET.get('order', '-create_date')
                field_dict = {
                    'status': '',
                    'create_date': '',
                }

                q = conditionCom(request, field_dict)
                print('q -->', q)
                print('order -->', order)

                objs = models.zgld_product.objects.select_related('user', 'company').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    if obj.user_id:
                        if int(obj.user_id) == int(user_id):
                            publisher = '我添加的'
                        else:
                            publisher = obj.user.username + '添加的'
                    else:
                        publisher = '企业发布'

                    picture_url = models.zgld_product_picture.objects.filter(product_id=obj.id, picture_type=1).order_by('create_date')[0].picture_url

                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,  # 标题
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


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "update":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'product_id': o_id,
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格     必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                'title': request.POST.get('title'),  # 标题    非必须
                'content': request.POST.get('content'),  # 内容    非必须
            }

            forms_obj = ProductUpdateForm(form_data)
            if forms_obj.is_valid():
                user_id = forms_obj.data['user_id']
                product_id = forms_obj.data['product_id']
                picture_ids_list = json.loads(request.POST.get('picture_ids'))
                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id

                product_obj = models.zgld_product.objects.filter(id=product_id)
                product_obj.update(
                    user_id=user_id,
                    company_id=company_id,
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                    title=forms_obj.data.get('title'),
                    content=forms_obj.data.get('content')
                )

                product_id = product_obj[0].id
                picture_obj = models.zgld_product_picture.objects.filter(id__in=picture_ids_list)
                picture_obj.update(product_id=product_id)

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

            return JsonResponse(response.__dict__)

        elif oper_type == "add_picture":

            upload_file = request.FILES['file']

            task = request.POST.get('task_id')  # 获取文件唯一标识符
            chunk = request.POST.get('chunk', 0)  # 获取该分片在所有分片中的序号
            filename = '/%s%s' % (task, chunk)  # 构成该分片唯一标识符
            IMG_PATH_FILES = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product') + filename
            with open(IMG_PATH_FILES, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

        elif oper_type == "delete_picture":
            # 删除 ID
            picture_objs = models.zgld_product_picture.objects.filter(id=o_id)
            if picture_objs:
                picture_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '图片ID不存在'

        # 触发-下架产品的动作
        elif oper_type == "shelves":
            # 出发-发布动作。
            product_objs = models.zgld_product.objects.filter(id=o_id)
            if product_objs:
                product_objs.update(
                    status=2
                )
                response.code = 200
                response.msg = "修改下架状态成功"
                response.data = {
                    'status': product_objs[0].get_status_display(),
                    'status_code': product_objs[0].status
                }
            else:
                response.code = 302
                response.msg = '产品不存在'

        # 触发-发布产品的动作
        elif oper_type == "publish":
            # 出发-发布动作。
            product_objs = models.zgld_product.objects.filter(id=o_id)
            if product_objs:
                product_objs.update(
                    status=1
                )
                response.code = 200
                response.msg = "修改发布状态成功"
                response.data = {
                    'status': product_objs[0].get_status_display(),
                    'status_code': product_objs[0].status
                }
            else:
                response.code = 302
                response.msg = '产品不存在'

        # 触发-推荐产品的动作
        elif oper_type == "recommend":
            # 出发-发布动作。
            product_objs = models.zgld_product.objects.filter(id=o_id)
            if product_objs:
                product_objs.update(
                    status=3
                )
                response.code = 200
                response.msg = "修改推荐状态成功"
                response.data = {
                    'status': product_objs[0].get_status_display(),
                    'status_code': product_objs[0].status
                }
            else:
                response.code = 302
                response.msg = '产品不存在'

        # 触发-删除公司产品
        elif oper_type == "delete":
            # 删除 ID
            product_objs = models.zgld_product.objects.filter(id=o_id)
            if product_objs:
                product_objs.delete()
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
                'title': request.POST.get('title'),    # 标题    非必须
                'content': request.POST.get('content'),  # 内容    非必须
            }

            forms_obj = ProductAddForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                picture_ids_list = json.loads(request.POST.get('picture_ids'))

                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                product_obj = models.zgld_product.objects.create(
                    user_id=user_id,
                    company_id=company_id,
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )

                models.zgld_product_article.objects.create(
                    title=forms_obj.data.get('title'),
                    content=forms_obj.data.get('content')
                )

                product_id = product_obj.id
                picture_obj = models.zgld_product_picture.objects.filter(id__in=picture_ids_list)

                print('----picture_ids_list--->>', picture_ids_list, product_id, picture_obj)
                picture_obj.update(product_id=product_id)

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    elif request.method == "GET":

        if oper_type == "upload_complete":
            target_filename = request.GET.get('filename')  # 获取上传文件的文件名
            task = request.GET.get('task_id')  # 获取文件的唯一标识符
            picture_type = request.GET.get('picture_type')  # 图片的类型。
            IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product')
            chunk = 0  # 分片序号
            file_tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            print('===target_filename===>>', target_filename)

            file_type = target_filename.split('.')[1]
            target_filename = '%s/%s.%s' % (IMG_PATH, file_tag, file_type)

            with open(target_filename, 'wb') as target_file:  # 创建新文件
                while True:
                    try:
                        filename = '%s%d' % (task, chunk)
                        source_file = open('%s/%s' % (IMG_PATH, filename), 'rb')  # 按序打开每个分片
                        target_file.write(source_file.read())  # 读取分片内容写入新文件
                        source_file.close()
                    except IOError:
                        break
                    chunk += 1
                    os.remove('%s/%s' % (IMG_PATH, filename))  # 删除该分片，节约空间
            picture_url = 'statics/zhugeleida/imgs/qiyeweixin/product/%s.%s' % (file_tag, file_type)

            product_picture_obj = models.zgld_product_picture.objects.create(picture_type=picture_type,
                                                                             picture_url=picture_url)

            response.code = 200
            response.msg = "添加图片成功"
            response.data = {
                'ret_data':
                    {
                        'picture_id': product_picture_obj.id,
                        'picture_url': product_picture_obj.picture_url,
                    }
            }

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
            for index,data  in  enumerate(ret_list):
                if  obj['order'] < data['order']:
                    ret_list.insert(index,obj)
                    break
            else:
                ret_list.append(obj)
    return  ret_list

