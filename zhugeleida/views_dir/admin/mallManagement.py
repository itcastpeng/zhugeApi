from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.mallManage_verify import AddForm, UpdateForm, SelectForm
import json,os,sys
from django.db.models import Q


def mallManagement(request, user_id, goodsGroup, status, flag):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            q = Q()
            print('goodsGroup--> ',goodsGroup, 'status---> ',status)
            if goodsGroup:
                q.add(Q(parentName_id=goodsGroup), Q.AND)
            if status:
                q.add(Q(goodsStatus=status), Q.AND)
            if flag == 'admin':
                u_idObjs = models.zgld_admin_userprofile.objects.get(id=user_id)
            else:
                u_idObjs = models.zgld_customer.objects.get(id=user_id)
            objs = models.zgld_goods_management.objects.filter(q).filter(parentName__xiaochengxu_app__xiaochengxucompany_id=u_idObjs.company_id)
            otherData = []
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            for obj in objs:
                groupObjs = models.zgld_goods_classification_management.objects.filter(id=obj.parentName_id)
                parentGroup_id = obj.parentName_id
                parentGroup_name = obj.parentName.classificationName
                if groupObjs[0].parentClassification_id:
                    parent_group_name = groupObjs[0].parentClassification.classificationName
                    parentGroup_name = parent_group_name + ' > ' + parentGroup_name

                xianshangjiaoyi = '否'
                if obj.xianshangjiaoyi:
                    xianshangjiaoyi = '是'
                topLunBoTu = ''
                if obj.topLunBoTu:
                    topLunBoTu = json.loads(obj.topLunBoTu)
                detailePicture = ''
                if obj.detailePicture:
                    detailePicture = json.loads(obj.detailePicture)
                otherData.append({
                    'id':obj.id,
                    'goodsName':obj.goodsName,
                    'parentName_id':parentGroup_id,
                    'parentName':parentGroup_name,
                    'goodsPrice':obj.goodsPrice,
                    # 'inventoryNum':obj.inventoryNum,
                    'goodsStatus':obj.get_goodsStatus_display(),
                    'xianshangjiaoyi':xianshangjiaoyi,
                    'shichangjiage':obj.shichangjiage,
                    # 'kucunbianhao':obj.kucunbianhao,
                    'topLunBoTu': topLunBoTu,  # 顶部轮播图
                    'detailePicture' : detailePicture,  # 详情图片
                    'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                    'shelvesCreateDate':obj.shelvesCreateDate.strftime('%Y-%m-%d %H:%M:%S'),
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = otherData
    return response

# 商城展示
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def mallManagementShow(request):
    user_id = request.GET.get('user_id')
    goodsGroup = request.GET.get('goodsGroup')
    status = request.GET.get('status')
    flag = 'admin'
    response = mallManagement(request, user_id, goodsGroup, status, flag)
    return JsonResponse(response.__dict__)

def updateInitData(result_data,xiaochengxu_id, pid=None):   # 更新查询 分类接口
    objs = models.zgld_goods_classification_management.objects.filter(
        xiaochengxu_app_id=xiaochengxu_id,
        id=pid,
    )
    for obj in objs:
        parent = updateInitData(result_data, xiaochengxu_id, pid=obj.parentClassification_id)
        result_data.append(obj.id)
    return result_data

# 商城操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def mallManagementOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    resultData = {
        'user_id':request.GET.get('user_id'),
        'o_id':o_id,
        'goodsName':request.POST.get('goodsName'),                    # 商品名称
        'parentName':request.POST.get('parentName'),                  # 父级分类
        'goodsPrice':request.POST.get('goodsPrice'),                  # 商品标价
        # 'inventoryNum':request.POST.get('inventoryNum'),              # 商品库存
        'goodsStatus':request.POST.get('goodsStatus'),                # 商品状态
        'xianshangjiaoyi':request.POST.get('xianshangjiaoyi'),        # 是否线上交易
        'shichangjiage':request.POST.get('shichangjiage'),            # 市场价格
        # 'kucunbianhao':request.POST.get('kucunbianhao'),              # 库存编号
        'topLunBoTu':request.POST.get('topLunBoTu'),                  # 顶部轮播图
        'detailePicture':request.POST.get('detailePicture'),          # 详情图片
    }
    print('resultData---------------->',resultData)
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        if oper_type == 'add':
            forms_obj = AddForm(resultData)
            if forms_obj.is_valid():
                print('验证通过')
                formObjs = forms_obj.cleaned_data
                models.zgld_goods_management.objects.create(
                    goodsName=formObjs.get('goodsName'),
                    parentName_id=formObjs.get('parentName'),
                    goodsPrice=formObjs.get('goodsPrice'),
                    # inventoryNum=formObjs.get('inventoryNum'),
                    xianshangjiaoyi=formObjs.get('xianshangjiaoyi'),
                    shichangjiage=formObjs.get('shichangjiage'),
                    # kucunbianhao=formObjs.get('kucunbianhao'),
                    goodsStatus=formObjs.get('goodsStatus'),
                    topLunBoTu=resultData.get('topLunBoTu'),  # 顶部轮播图
                    detailePicture=resultData.get('detailePicture'),  # 详情图片
                )
                response.code = 200
                response.msg = '添加成功'
                response.data = {}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'Beforeupdate':
            goodsObjs = models.zgld_goods_management.objects.filter(id=o_id)
            u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
            userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=u_idObjs[0].company_id)
            xiaochengxu_id = userObjs[0].id
            objs = models.zgld_goods_classification_management.objects.filter(id=goodsObjs[0].parentName_id)
            result_data = []
            parentData = updateInitData(result_data, xiaochengxu_id, objs[0].parentClassification_id)
            parentData.append(goodsObjs[0].parentName_id)
            response.code = 200
            response.msg = '查询成功'
            response.data = parentData


        elif oper_type == 'update':
            forms_obj = UpdateForm(resultData)
            if forms_obj.is_valid():
                print('======================')
                formObjs = forms_obj.cleaned_data
                print('formObjs------> ',formObjs)
                print("formObjs.get('xianshangjiaoyi')==========> ",formObjs.get('xianshangjiaoyi'))
                print("formObjs.get('goodsPrice')==============> ",formObjs.get('goodsPrice'))
                models.zgld_goods_management.objects.filter(id=o_id).update(
                    goodsName=formObjs.get('goodsName'),
                    parentName_id=formObjs.get('parentName'),
                    goodsPrice=formObjs.get('goodsPrice'),
                    # kucunbianhao=formObjs.get('kucunbianhao'),
                    goodsStatus=formObjs.get('goodsStatus'),
                    topLunBoTu=resultData.get('topLunBoTu'),  # 顶部轮播图
                    detailePicture=resultData.get('detailePicture'),  # 详情图片
                    xianshangjiaoyi=formObjs.get('xianshangjiaoyi'),
                )
                response.code = 200
                response.msg = '修改成功'
                response.data = {}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == 'delete':
            objs = models.zgld_goods_management.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = '删除成功'
                response.data = {}
            else:
                response.code = 301
                response.msg = '删除ID不存在！'
    else:
        if oper_type == 'goodsStatus': # 查询商品状态
            objs = models.zgld_goods_management
            otherData = []
            for status in objs.status_choices:
                otherData.append({
                    'id':status[0],
                    'name':status[1]
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = otherData
        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)




