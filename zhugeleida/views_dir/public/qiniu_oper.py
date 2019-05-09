from publicFunc import Response
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import datetime as dt, time, json, uuid, os, base64
from zhugeleida.views_dir.public.watermark import encryption
import qiniu, requests
from publicFunc.account import randon_str
from qiniu import put_file

# 内部调用
def qiniu_get_token(img_path):
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    key = randon_str()
    policy = {  # 指定上传文件的格式 等

    }
    token = q.upload_token(bucket_name)  # 可以指定key 图片名称
    # token = q.upload_token(bucket_name, None, 3600, policy)  # 可以指定key 图片名称
    # print('qiniu_url------qiniu_url------------qiniu_url-----------qiniu_url---------qiniu_url---------> ')
    # ret, info = put_file(token, None, mime_type="text/js", file_path=img_path)
    # print('ret.content-==========2@@@@@@@@@@@@@@@@@@@@!!!!!!!!!!!!!!!!!!##################$$$$$$$$$$$$$$$$$$$$$+=====》', ret)

    # ret, info = put_file(token, key, img_path)
    qiniu_url = 'https://up-z1.qiniup.com/'
    data = {
        'token': token,
    }
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
    }
    files = {
        'file': open(img_path, 'rb')
    }
    ret = requests.post(qiniu_url, data=data, files=files, headers=headers)

    return ret

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

if __name__ == '__main__':
    ret = qiniu_get_token('1.jpg')
    print('ret------> ', ret)





















