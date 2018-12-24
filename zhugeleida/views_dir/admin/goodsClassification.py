from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.goodsClass_verify import AddForm, UpdateForm, SelectForm
import json,os,sys
from django.db.models import Q


# 商品分级 查询
def init_data(company_id, pid=None, level=1):
    result_data = []
    print('level------> ',level)
    objs = models.zgld_goods_classification_management.objects.filter(
        company_id=company_id,
        # userProfile_id=user_id,
        parentClassification_id=pid,
        level=level
    )
    for obj in objs:
        current_data = {
            'label': obj.classificationName,
            'value': obj.id,
        }
        # print('obj.id---------> ',obj.id)
        children_data = init_data(company_id, pid=obj.id, level=2)
        if children_data:
            current_data['children'] = children_data

        result_data.append(current_data)

    return result_data

# 商城商品查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def goodsClass(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        singleUser = request.GET.get('singleUser')   # 单独查询父级 参数
        company_id = request.GET.get('company_id')   #

        # Objs = models.zgld_shangcheng_jichushezhi.objects.select_related(
        #     'xiaochengxuApp__company'
        # ).filter(xiaochengxucompany_id=company_id)
        #
        # if Objs:

        # jichushezhi_id = Objs[0].id
        parentData = init_data(company_id)
        groupObjs = models.zgld_goods_classification_management.objects

        q = Q()
        if singleUser:
            q.add(Q(parentClassification_id=singleUser), Q.AND)

        objs = groupObjs.filter(company_id=company_id).filter(q).order_by('-createDate')

        objsCount = objs.count()
        otherData = []
        if objs:

            for obj in objs:
                countNum = models.zgld_goods_management.objects.filter(parentName_id=obj.id).count()
                classificationName = ''
                parentClassification_id = ''
                if obj.parentClassification_id:
                    parentClassification_id = obj.parentClassification_id
                    classificationName = obj.parentClassification.classificationName

                otherData.append({
                    'groupId':obj.id,
                    'groupName':obj.classificationName,
                    'groupParentId':parentClassification_id,
                    'groupParent':classificationName,
                    'countNum':countNum
                })

            response.data = {
                'parentData':parentData,
                'otherData':otherData,
                'objsCount':objsCount
            }
            response.code = 200
            response.msg = '查询成功'

        else:
            response.code = 302
            response.msg = '无数据'



    return JsonResponse(response.__dict__)


# 判断分组是否会死关联
def updateInitData(result_data,company_id, pid=None, o_id=None):   # o_id 判断是否会关联自己 如果o_id 在 result_data里会return
    objs = models.zgld_goods_classification_management.objects.filter(
        company_id =company_id,
        id=pid,
    )
    for obj in objs:
        result_data.append(obj.id)
        if o_id:
            if int(o_id) == int(obj.id):
                return result_data

        parent = updateInitData(result_data, company_id, pid=obj.parentClassification_id, o_id=o_id)

    return result_data

# 商城商品操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def goodsClassOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    company_id = request.GET.get('company_id')

    # u_idObjs = models.zgld_admin_userprofile.objects.get(id=user_id)                            # 查询 admin用户
    # xiaochengxu_id = models.zgld_xiaochengxu_app.objects.filter(company_id=u_idObjs.company_id) # 查询小程序ID
    # userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu_id)  #商城基础设置

    if request.method == "POST":
        dataDict = {
            'o_id':o_id,
            'classificationName': request.POST.get('classificationName'),
            # 'xiaochengxu_app_id': request.POST.get('xiaochengxu_app_id'),
            'userProfile_id':request.GET.get('user_id'),
            'parentClassification_id':request.POST.get('parentClassification')
        }

        # 添加商品分类
        if oper_type == 'add':
            forms_obj = AddForm(dataDict)
            if forms_obj.is_valid():
                print('==验证成功==')
                parentClassName_id = forms_obj.cleaned_data.get('parentClassification_id')
                level = 1
                if parentClassName_id:
                    level = 2
                    parentClassNameObjs = models.zgld_goods_classification_management.objects.filter(id=parentClassName_id)
                    if not parentClassNameObjs:
                        response.code = 301
                        response.msg = '无此父级'
                        return JsonResponse(response.__dict__)
                objs = models.zgld_goods_classification_management.objects
                # objsId = objs.create(**forms_obj.cleaned_data)
                objForm = forms_obj.cleaned_data
                objsId = objs.create(
                    company_id=company_id,
                    classificationName=objForm.get('classificationName'),
                    parentClassification_id=objForm.get('parentClassification_id'),
                    # mallSetting_id=userObjs[0].id,
                )
                objs.filter(id=objsId.id).update(level=level)
                response.code = 200
                response.msg = '添加成功'
                response.data = {}
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())

        # 修改前查询商品分类
        elif oper_type == 'Beforeupdate':
            result_data = []
            objs = models.zgld_goods_classification_management.objects.filter(id=o_id)
            if objs:
                parentData = updateInitData(result_data, company_id , objs[0].parentClassification_id)
                response.code = 200
                response.msg = '查询成功'
                response.data = parentData
            else:
                response.code = 301
                response.msg = '分组ID错误'

        # 确认修改商品分类
        elif oper_type == 'update':
            # 判断是否会关联自己
            result_data = []
            if dataDict.get('parentClassification_id'):
                if int(dataDict.get('o_id')) == int(dataDict.get('parentClassification_id')):
                    response.code = 301
                    response.msg = '不可关联自己'
                    return JsonResponse(response.__dict__)
                objs = models.zgld_goods_classification_management.objects.filter(id=dataDict.get('parentClassification_id'))
                parentData = updateInitData(result_data, company_id, objs[0].parentClassification_id, o_id)
                if int(o_id) in parentData:
                    response.code = 301
                    response.msg = '不可关联自己'
                    return JsonResponse(response.__dict__)

            forms_obj = UpdateForm(dataDict)
            if forms_obj.is_valid():
                print('==验证成功==')
                parentClassName_id = forms_obj.cleaned_data.get('parentClassification_id')
                if parentClassName_id:
                    parentClassNameObjs = models.zgld_goods_classification_management.objects.filter(
                        id=parentClassName_id)
                    if not parentClassNameObjs:
                        response.code = 301
                        response.msg = '无此父级'
                        return JsonResponse(response.__dict__)
                formObj = forms_obj.cleaned_data
                parentClassification_id = formObj.get('parentClassification_id')
                level = 1
                if parentClassification_id:
                    level = 2
                models.zgld_goods_classification_management.objects.filter(id=o_id).update(
                    classificationName=formObj.get('classificationName'),
                    parentClassification_id=parentClassification_id,
                    level=level,
                )
                response.code = 200
                response.msg = '修改成功'
                response.data = {}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
                response.data = {}

        # 删除商品分类
        elif oper_type == 'delete':
            groupObjs = models.zgld_goods_classification_management.objects
            objs = groupObjs.filter(id=o_id)
            if objs:
                if groupObjs.filter(parentClassification_id=o_id):
                    response.code = 301
                    response.msg = '含有子级,请先移除'
                else:
                    objs.delete()
                    response.code = 200
                    response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = '删除ID不存在！'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)