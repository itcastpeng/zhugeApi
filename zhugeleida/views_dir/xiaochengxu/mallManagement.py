from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.mallManage_verify import AddForm, UpdateForm, SelectForm
import json,os,sys

# 商城展示
@csrf_exempt
@account.is_token(models.zgld_customer)
def mallManagementShow(request):
    response = Response.ResponseObj()
    if request.method == "GET":  # 获取单个名片的信息
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            objs = models.zgld_goods_management.objects.filter(parentName__userProfile_id=user_id)
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
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = otherData
    return JsonResponse(response.__dict__)


# 商城操作
@csrf_exempt
# @account.is_token(models.zgld_customer)
def mallManagementOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    resultData = {
        'user_id':request.GET.get('user_id'),
        'o_id':o_id,
        'goodsName':request.POST.get('goodsName'),                  # 商品名称
        'parentName':request.POST.get('parentName'),                # 父级分类
        'goodsPrice':request.POST.get('goodsPrice'),                # 商品标价
        # 'salesNum':request.POST.get('salesNum'),                    # 商品销量
        'inventoryNum':request.POST.get('inventoryNum'),            # 商品库存
        'goodsStatus':request.POST.get('goodsStatus'),              # 商品状态
        # 'commissionFee':request.POST.get('commissionFee'),          # 佣金提成
        # 'createDate':request.POST.get('createDate'),                # 创建时间
        # 'shelvesCreateDate':request.POST.get('shelvesCreateDate'),  # 上架时间
        'xianshangjiaoyi':request.POST.get('xianshangjiaoyi'),      # 是否线上交易
        'shichangjiage':request.POST.get('shichangjiage'),          # 市场价格
        'kucunbianhao':request.POST.get('kucunbianhao'),            # 库存编号
    }
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
                    inventoryNum=formObjs.get('inventoryNum'),
                    xianshangjiaoyi=formObjs.get('xianshangjiaoyi'),
                    shichangjiage=formObjs.get('shichangjiage'),
                    kucunbianhao=formObjs.get('kucunbianhao'),
                    goodsStatus=formObjs.get('goodsStatus')
                )
                response.code = 200
                response.msg = '添加成功'
                response.data = {}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == 'update':
            forms_obj = UpdateForm(resultData)
            if forms_obj.is_valid():
                formObjs = forms_obj.cleaned_data
                print('formObjs------> ',formObjs)
                models.zgld_goods_management.objects.filter(id=o_id).update(
                    goodsName=formObjs.get('goodsName'),
                    parentName_id=formObjs.get('parentName'),
                    goodsPrice=formObjs.get('goodsPrice'),
                    kucunbianhao=formObjs.get('kucunbianhao'),
                    goodsStatus=formObjs.get('goodsStatus')
                )
            response.code = 200
            response.msg = '修改成功'
            response.data = {}
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




