from django.http import JsonResponse
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
from publickFunc import Response, account
from zhugeproject.publick import xuqiu_or_gongneng_log
from zhugeproject import models


@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    username = request.POST.get('username')
    pwd = request.POST.get('password')
    user_id = request.GET.get('user_id')
    username_log = models.ProjectUserProfile.objects.get(id=user_id)
    print('username -- pwd ---->',username,pwd)
    user_obj = models.ProjectUserProfile.objects.filter(username=username,password=account.str_encrypt(pwd))
    if user_obj:
        token = user_obj[0].token
        if not token:
            token = str(ObjectId())
            user_obj.update(token=token)
        remark = '{}登录了,'.format(username_log)
        xuqiu_or_gongneng_log.gongneng_log(request, remark)
        response.code = 200
        response.msg = '登陆成功'
        response.data = {
            'token':token
        }
    else:
        response.code = 305
        response.msg = '登陆失败,用户名或密码错误'
    return JsonResponse(response.__dict__)




















