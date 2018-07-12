from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from publicFunc.Response import ResponseObj
from publicFunc.account import is_token
from zhugedanao import models


@csrf_exempt
# @is_token(models.zhugedanao_userprofile)
def oper_log(request):
    response = ResponseObj()
    user_id = request.GET.get('user_id')
    gongneng_id = request.GET.get('gongneng_id')

    models.zhugedanao_oper_log.objects.create(
        user_id=user_id,
        gongneng_id=gongneng_id
    )

    response.code = 200
    response.msg = "添加成功"
    return JsonResponse(response.__dict__)