from django.shortcuts import HttpResponse
import os
from django import forms
from publicFunc import Response
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import base64
# BasePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from zhugeleida import models
from publicFunc import account

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

    img_source =  forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid':  "必须是字符串"
        }
    )



# 上传图片（分片上传）
@csrf_exempt
# @account.is_token(models.zgld_userprofile)
def img_upload(request):
    response = Response.ResponseObj()

    forms_obj = imgUploadForm(request.POST)
    if forms_obj.is_valid():

        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
        chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
        expanded_name = img_name.split('.')[-1]  # 扩展名

        img_name = timestamp + "_" + str(chunk) + '.' + expanded_name
        img_save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'tmp', img_name)
        print('img_save_path -->', img_save_path )

        with open(img_save_path, 'w') as f:
            f.write(img_data)

        response.code = 200
        response.msg = "上传成功"

    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 合并图片 Form 验证
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
    img_source =  forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid':  "必须是字符串"
        }
    )


# 合并图片
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def img_merge(request):
    response = Response.ResponseObj()
    forms_obj = imgMergeForm(request.POST)
    if forms_obj.is_valid():
        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
        expanded_name = img_name.split('.')[-1]  # 扩展名
        picture_type = request.POST.get('picture_type')  # 图片的类型  (1, '产品封面的图片'), (2, '产品介绍的图片')
        img_name = timestamp + '.' + expanded_name
        img_source = forms_obj.cleaned_data.get('img_source')  # user_photo 代表用户上传的照片  user_avtor 代表用户的头像。
        print('-----img_source----->', img_source)

        file_dir = ''
        if img_source == 'user_photo':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_photo')
            #
            # user_id = request.GET.get('user_id')
            # img_path = "/".join(['statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_photo' , img_name])
            # img_save_path = "/".join([BasePath, img_path])
            # file_obj = open(img_save_path, 'ab')
            # for chunk in range(chunk_num):
            #     file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            #
            #     file_save_path = "/".join([BasePath, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_photo', 'tmp' , file_name])
            #
            #     with open(file_save_path, 'rb') as f:
            #         file_obj.write(f.read())
            #         # file_content += f.read()
            #     os.remove(file_save_path)
            #     obj = models.zgld_user_photo.objects.create(user_id=user_id,photo_url=img_path,photo_type=1)  # 用户上传照片
            #     response.data = {
            #         'picture_id': obj.id,
            #         'picture_url': obj.photo_url,
            #     }

        elif img_source == 'user_avatar':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_avatar')

        elif img_source == 'cover_picture' or img_source == 'product_picture':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product')

            # user_id = request.GET.get('user_id')
            # img_path = "/".join(['statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product', img_name])
            # img_save_path = "/".join([BasePath, img_path])
            # file_obj = open(img_save_path, 'ab')
            # for chunk in range(chunk_num):
            #     file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            #
            #     file_save_path = "/".join(
            #         [BasePath, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product', 'tmp', file_name])
            #
            #     with open(file_save_path, 'rb') as f:
            #         file_obj.write(f.read())
            #
            #     os.remove(file_save_path)
            #
            #     if img_source == 'cover_picture':
            #         obj = models.zgld_product_picture.objects.create(picture_url=img_path,
            #                                                          picture_type=1)  # 封面头像
            #     elif  img_source == 'product_picture':
            #         obj = models.zgld_product_picture.objects.create(picture_url=img_path,
            #                                                          picture_type=2)  # 产品图片
            #     response.data = {
            #         'picture_id': obj.id,
            #         'picture_url': obj.picture_url,
            #     }

        fileData = ''
        for chunk in range(chunk_num):
            file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            file_save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'tmp', file_name)
            with open(file_save_path, 'r') as f:
                fileData += f.read()

            os.remove(file_save_path)

        # user_id = request.GET.get('user_id')
        img_path = os.path.join(file_dir, img_name)
        # img_save_path = os.path.join(BasePath, img_path)
        file_obj = open(img_path, 'ab')
        img_data = base64.b64decode(fileData)
        file_obj.write(img_data)
        # obj = models.zgld_user_photo.objects.create(user_id=user_id, photo_url=img_path,photo_type=2)   # 用户名片头像

        response.data = {
            'picture_url': img_path,
        }
        response.code = 200
        response.msg = "添加图片成功"

    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)