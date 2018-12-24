from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import GoodsManagementSelectForm
import json, base64
# from zhugeleida.views_dir.admin import mallManagement
from django.db.models import Q

@csrf_exempt
# @account.is_token(models.zgld_customer)
def mallManage(request):


    response = Response.ResponseObj()
    if request.method == "GET":

        # response = mallManagement.mallManagement(request, uid, goodsGroup, status, flag)

        uid = request.GET.get('uid')
        parentName_id = request.GET.get('parentName_id')
        detaileId = request.GET.get('detaileId')    # 查询详情
        u_idObjs = models.zgld_userprofile.objects.get(id=uid)
        company_id = u_idObjs.company_id

        xiaoChengXuObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxucompany_id=company_id)
        indexLunBoTu = ''
        xiaoChengXuId = ''
        if xiaoChengXuObjs:
            indexLunBoTu = xiaoChengXuObjs[0].lunbotu  # 查询首页 轮播图
            xiaoChengXuId = xiaoChengXuObjs[0].id

        otherData = []

        forms_obj = GoodsManagementSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            if detaileId:
                print('=====================xiaoChengXuObjs[0].id.....> ',xiaoChengXuId)

                objs = models.zgld_goods_management.objects.filter(company_id=company_id).filter(id=detaileId,goodsStatus__in=[1,3])
                count = objs.count()
                if objs:

                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    print('objs=========>',objs)
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

                        content = obj.content
                        if content:
                            content = json.loads(content)

                        otherData.append({
                            'id':obj.id,
                            'goodsName':obj.goodsName,
                            'parentName_id':parentGroup_id,
                            'parentName':parentGroup_name,
                            'goodsPrice':obj.goodsPrice,
                            'goodsStatus_code':obj.goodsStatus,
                            'goodsStatus':obj.get_goodsStatus_display(),
                            'xianshangjiaoyi':xianshangjiaoyi,
                            'shichangjiage':obj.shichangjiage,
                            'topLunBoTu': topLunBoTu,                       # 顶部轮播图
                            'content': content,
                            'detailePicture' : detailePicture,              # 详情图片
                            'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                            'shelvesCreateDate':obj.shelvesCreateDate.strftime('%Y-%m-%d %H:%M:%S'),
                            'DetailsDescription': obj.DetailsDescription    # 描述详情
                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                         'otherData':otherData,
                         'count' : count
                    }
                else:
                    response.code = 302
                    response.msg = '无数据'

            else:

                q1 = Q()
                q1.add(Q(**{'company_id': company_id}), Q.AND)

                if parentName_id:
                    q1.add(Q(**{'parentName_id': parentName_id}), Q.AND)

                objs = models.zgld_goods_management.objects.filter(q1).exclude(goodsStatus__in=[2,4]).order_by('-recommend_index')
                count = objs.count()

                if objs:
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]


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
                        'count': count
                    }

                else:
                    response.code = 302
                    response.msg = '无数据'


    return JsonResponse(response.__dict__)




