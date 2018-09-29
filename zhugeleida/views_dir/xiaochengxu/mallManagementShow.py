from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import UpdateForm, SelectForm
import json, base64
from zhugeleida.views_dir.admin import mallManagement


@csrf_exempt
@account.is_token(models.zgld_customer)
def mallManageShow(request):
    user_id = request.GET.get('user_id')
    goodsGroup = request.GET.get('goodsGroup')
    status = request.GET.get('status')
    flag = 'xiaochengxu'
    response = mallManagement.mallManagement(request, user_id, goodsGroup, status, flag)
    return JsonResponse(response.__dict__)





# @csrf_exempt
# @account.is_token(models.zgld_customer)
# def theOrderOper(request, oper_type, o_id):
#     response = Response.ResponseObj()
#     if request.method == 'POST':
#         if oper_type == 'update':
#             otherData = {
#                 'o_id': o_id,
#                 # 'countPrice': obj.countPrice,
#                 'yingFuKuan': request.POST.get('yingFuKuan'),
#                 'youhui': request.POST.get('youhui'),
#                 'yewuyuan_id': request.POST.get('yewuyuan_id'),
#                 'yongjin': request.POST.get('yongjin'),
#                 'peiSong': request.POST.get('peiSong'),
#                 'shouHuoRen_id': request.POST.get('shouHuoRen_id'),
#             }
#             forms_obj = UpdateForm(otherData)
#             if forms_obj.is_valid():
#                 print('验证通过')
#                 print(forms_obj.cleaned_data)
#                 dingDanId = forms_obj.cleaned_data.get('o_id')
#                 models.zgld_shangcheng_dingdan_guanli.objects.filter(
#                     id=dingDanId
#                 ).update(
#                     yingFuKuan=otherData.get('yingFuKuan'),
#                     youHui=otherData.get('youhui'),
#                     yewuUser_id=otherData.get('yewuyuan_id'),
#                     yongJin=otherData.get('yongjin'),
#                     peiSong=otherData.get('peiSong'),
#                     shouHuoRen_id=otherData.get('shouHuoRen_id')
#                 )
#                 response.code = 200
#                 response.msg = '修改成功'
#                 response.data = ''
#             else:
#                 response.code = 301
#                 response.msg = json.loads(forms_obj.errors.as_json())
#
#     else:
#         response.code = 402
#         response.msg = "请求异常"
#
#     return JsonResponse(response.__dict__)




