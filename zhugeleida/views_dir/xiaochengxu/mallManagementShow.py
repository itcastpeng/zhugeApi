from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import UpdateForm, SelectForm
import json, base64
# from zhugeleida.views_dir.admin import mallManagement


@csrf_exempt
@account.is_token(models.zgld_customer)
def mallManageShow(request):
    # response = mallManagement.mallManagement(request, uid, goodsGroup, status, flag)
    response = Response.ResponseObj()
    uid = request.GET.get('uid')
    detaileId = request.GET.get('detaileId')
    u_idObjs = models.zgld_customer.objects.filter(id=uid)
    xiaochengxu_id = u_idObjs[0].company_id
    xiaoChengXuObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu_id)
    indexLunBoTu = xiaoChengXuObjs[0].lunbotu
    otherData = []
    if detaileId:
        objs = models.zgld_goods_management.objects.filter(parentName__xiaochengxu_app_id=xiaochengxu_id).filter(id=detaileId)
        for obj in objs:
            groupObjs = models.zgld_goods_classification_management.objects.filter(id=obj.parentName_id)
            xianshangjiaoyi = '否'
            if obj.xianshangjiaoyi:
                xianshangjiaoyi = '是'
            topLunBoTu = ''
            if obj.topLunBoTu:
                topLunBoTu = json.loads(obj.topLunBoTu)
            detailePicture = ''
            if obj.detailePicture:
                detailePicture = json.loads(obj.detailePicture)
            parentGroup_id = obj.parentName_id
            parentGroup_name = obj.parentName.classificationName
            if groupObjs[0].parentClassification_id:
                parent_group_name = groupObjs[0].parentClassification.classificationName
                parentGroup_name = parent_group_name + ' > ' + parentGroup_name
            otherData.append({
                'id':obj.id,
                'goodsName':obj.goodsName,
                'parentName_id':parentGroup_id,
                'parentName':parentGroup_name,
                'goodsPrice':obj.goodsPrice,
                'inventoryNum':obj.inventoryNum,
                'goodsStatus':obj.get_goodsStatus_display(),
                'xianshangjiaoyi':xianshangjiaoyi,
                'shichangjiage':obj.shichangjiage,
                'kucunbianhao':obj.kucunbianhao,
                'topLunBoTu': topLunBoTu,                       # 顶部轮播图
                'detailePicture' : detailePicture,              # 详情图片
                'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                'shelvesCreateDate':obj.shelvesCreateDate.strftime('%Y-%m-%d %H:%M:%S'),
            })
    else:
        objs = models.zgld_goods_management.objects.filter(parentName__xiaochengxu_app_id=xiaochengxu_id)
        print(objs)
        for obj in objs:
            topLunBoTu = ''
            if obj.topLunBoTu:
                topLunBoTu = json.loads(obj.topLunBoTu)
            otherData.append({
                'id':obj.id,
                'goodsName': obj.goodsName,
                'goodsPrice': obj.goodsPrice,
                'topLunBoTu': topLunBoTu,
                'shichangjiage': obj.shichangjiage,
            })
    if indexLunBoTu:
        indexLunBoTu = json.loads(indexLunBoTu)
    response.code = 200
    response.msg = '查询成功'
    response.data = {
        'indexLunBoTu':indexLunBoTu,
        'otherData':otherData,
    }
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




