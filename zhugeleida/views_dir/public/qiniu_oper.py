from publicFunc import Response
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import datetime as dt, time, json, uuid, os, base64
from zhugeleida.views_dir.public.watermark import encryption
import qiniu
from publicFunc.account import randon_str


# 内部调用
def qiniu_get_token():
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    key = randon_str()
    token = q.upload_token(bucket_name)  # 可以指定key 图片名称
    return token
# 前端请求
def qiniu_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'qiniu_token':
        SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
        AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
        q = qiniu.Auth(AccessKey, SecretKey)
        bucket_name = 'bjhzkq_tianyan'
        token = q.upload_token(bucket_name)  # 可以指定key 图片名称
        response.code = 200
        response.msg = 'token生成完成'
        response.data = {
            'token': token,
        }

    return JsonResponse(response.__dict__)























