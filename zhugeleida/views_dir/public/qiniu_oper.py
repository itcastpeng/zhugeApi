from publicFunc import Response
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import datetime as dt, time, json, uuid, os, base64
from zhugeleida.views_dir.public.watermark import encryption
import qiniu

def qiniu_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'qiniu_token':
        SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
        AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
        q = qiniu.Auth(AccessKey, SecretKey)
        bucket_name = 'bjhzkq_tianyan'
        token = q.upload_token(bucket_name)
        response.code = 200
        response.msg = 'token生成完成'
        response.data = {
            'token': token,
        }

    return JsonResponse(response.__dict__)























