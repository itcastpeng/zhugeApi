from django.shortcuts import HttpResponse
import os
from django import forms
from publicFunc import Response
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import base64
BasePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


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


# 上传图片（分片上传）
@csrf_exempt
def img_upload(request):
    response = Response.ResponseObj()

    print(BasePath)

    forms_obj = imgUploadForm(request.POST)
    if forms_obj.is_valid():
        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
        chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
        expanded_name = img_name.split('.')[-1]  # 扩展名

        img_name = timestamp + "_" + str(chunk) + '.' + expanded_name

        img_save_path = "/".join([BasePath, 'statics', 'zhugeleida', 'imgs', 'tmp', img_name])
        print('img_save_path -->', img_save_path)
        print('img_data -->', img_data)
        img_data = base64.b64decode(img_data.encode('utf-8'))
        with open(img_save_path, 'wb') as f:
            f.write(img_data)

        response.code = 200
        response.msg = "上传成功"
    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


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


# 合并图片
@csrf_exempt
def img_merge(request):
    response = Response.ResponseObj()
    forms_obj = imgMergeForm(request.POST)
    if forms_obj.is_valid():
        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
        expanded_name = img_name.split('.')[-1]  # 扩展名

        img_name = timestamp + '.' + expanded_name
        img_path = "/".join(['statics', 'zhugeleida', 'imgs', 'tmp', img_name])
        img_save_path = "/".join([BasePath, img_path])
        file_obj = open(img_save_path, 'ab')
        for chunk in range(chunk_num):
            file_name = timestamp + "_" + str(chunk) + '.' + expanded_name

            file_save_path = "/".join([BasePath, 'statics', 'zhugeleida', 'imgs', 'tmp', file_name])

            with open(file_save_path, 'rb') as f:
                file_obj.write(f.read())
                # file_content += f.read()
            os.remove(file_save_path)

        #
        # with open(img_save_path, 'wb') as f:
        #     f.write(file_content)

        response.code = 200
        response.data = {
            'img_url': img_path
        }
        response.msg = "上传成功"
    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)