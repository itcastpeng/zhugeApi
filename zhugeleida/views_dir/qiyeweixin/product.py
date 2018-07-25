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
BasePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


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


                    user_photo_obj = models.zgld_user_photo.objects.filter(user_id=user_id, photo_type=2).order_by('-create_date')

                    if user_photo_obj:
                        user_avatar =  user_photo_obj[0].photo_url

                    else:
                        # if obj.avatar.startswith("http"):
                        #     user_avatar = obj.avatar
                        # else:
                        user_avatar =  obj.avatar


                    ret_data.append({
                        'id': obj.id,
                        'publisher': publisher,  # 发布者
                        'publisher_date': obj.create_date,  # 发布日期。

                        'name': obj.name,  # 产品名称
                        'price': obj.price,  # 价格
                        'user_avatar': user_avatar,

                        'reason': obj.reason,  # 推荐理由
                        'content': json.loads(obj.content),
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

                    content = {
                        'cover_data': json.loads(obj.content).get('cover_data')

                    }

                    ret_data.append({
                        'id': product_id,
                        'name': obj.name ,# 标题
                        'publisher': publisher,  # 发布者
                        'price': obj.price,  # 价格
                        'publisher_date': obj.create_date,  # 发布日期。
                        'content': content,  # 封面地址的URL

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
                'content': request.POST.get('content'),  # 推荐理由 非必须
                # 'article_id': request.POST.get('article_id'),  # 内容    非必须
            }

            forms_obj = ProductUpdateForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                product_id = forms_obj.cleaned_data.get('product_id')
                content = forms_obj.cleaned_data.get('content')
                print('--------forms_obj------->>',content,forms_obj.cleaned_data)
                product_obj = models.zgld_product.objects.filter(id=product_id)

                product_obj.update(
                    name=forms_obj.cleaned_data.get('name'),
                    price=forms_obj.cleaned_data.get('price'),
                    reason=forms_obj.cleaned_data.get('reason'),
                    content = content
                )


                #
                # product_obj.save()

                response.code = 200
                response.msg = "添加成功"



            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "add":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),  # 产品名称 必须
                'price': request.POST.get('price'),  # 价格     必须
                'reason': request.POST.get('reason'),  # 推荐理由 非必须
                # 'title': request.POST.get('title'),    # 标题    非必须
                # 'content': request.POST.get('content'),  # 内容    非必须
            }

            print(request.POST)
            forms_obj = ProductAddForm(form_data)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                content = request.POST.get('content')


                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                product_obj = models.zgld_product.objects.create(
                    user_id=user_id,
                    company_id=company_id,
                    name=forms_obj.data.get('name'),
                    price=forms_obj.data.get('price'),
                    reason=forms_obj.data.get('reason'),
                )

                # 封面图片数据绑定到产品。
                product_obj.content = content
                product_obj.save()

                response.code = 200
                response.msg = "添加成功"



            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

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

            if product_objs:
                product_objs.delete()
                response.code = 200
                response.msg = "删除成功"



            else:
                response.code = 302
                response.msg = '产品不存在'





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
