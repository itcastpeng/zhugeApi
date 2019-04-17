from publicFunc import Response
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import datetime as dt, time, json, uuid, os, base64
from zhugeleida.views_dir.public.watermark import encryption
import qiniu

def qiniu_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'qiniu_token':

        AccessKey = '6gFyUrgwDoEgWMH-6QbZUxDnn7yy6ZggiyiuqOt3'
        SecretKey = 'sS6fCaFOIAHJfzBhRjYvYnGhzS5buAxThUUfWyfR'
        suffix = request.GET.get('suffix')  # 后缀
        q = qiniu.Auth(AccessKey, SecretKey)

        bucket_name = 'bucket_name'
        key = '{}.{}'.format(encryption(), suffix)  # 图片名称

        token = q.upload_token(bucket_name, key, 3600)
        response.code = 200
        response.msg = 'token生成完成'
        response.data = {'token': token}

    return JsonResponse(response.__dict__)























