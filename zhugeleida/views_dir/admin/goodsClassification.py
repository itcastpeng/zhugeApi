from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.goodsClass_verify import AddForm, UpdateForm, SelectForm
import json,os,sys
from django.db.models import Q

def init_data(xiaochengxu_id, pid=None, level=1):
    """
    获取权限数据
    :param pid:  权限父级id
    :return:
    """
    result_data = []
    print('level------> ',level)
    objs = models.zgld_goods_classification_management.objects.filter(
        xiaochengxu_app_id=xiaochengxu_id,
        # userProfile_id=user_id,
        parentClassification_id=pid,
        level=level
    )
    for obj in objs:
        current_data = {
            'name': obj.classificationName,
            'id': obj.id,
        }
        print('obj.id---------> ',obj.id)
        children_data = init_data(xiaochengxu_id, pid=obj.id, level=2)
        if children_data:
            current_data['children'] = children_data
        result_data.append(current_data)
    return result_data

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def goodsClassShow(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        singleUser = request.GET.get('singleUser')

        u_idObjs = models.zgld_admin_userprofile.objects.filter(id=user_id)
        xiaochengxu = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
        userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu[0].id)
        xiaochengxu_id = userObjs[0].id

        groupObjs = models.zgld_goods_classification_management.objects
        parentObjs = groupObjs.filter(parentClassification__isnull=True, xiaochengxu_app_id=xiaochengxu_id)
        parentData = []
        for parentObj in parentObjs:
            parentData.append({
                'parntId':parentObj.id,
                'parentName':parentObj.classificationName
            })
        q = Q()
        if singleUser:
            q.add(Q(parentClassification_id=singleUser), Q.AND)
        objs = groupObjs.filter( xiaochengxu_app_id=xiaochengxu_id).filter(q)
        otherData = []
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
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'parentData':parentData,
             'otherData':otherData
        }
    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def goodsClassOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        dataDict = {
            'o_id':o_id,
            'classificationName': request.POST.get('classificationName'),
            'xiaochengxu_app_id': request.POST.get('xiaochengxu_app_id', ''),
            'userProfile_id':request.GET.get('user_id'),
            'parentClassification_id':request.POST.get('parentClassification')
        }
        print('dataDict---------------> ',dataDict)
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
                objsId = objs.create(**forms_obj.cleaned_data)
                objs.filter(id=objsId.id).update(level=level)
                response.code = 200
                response.msg = '添加成功'
                response.data = {}
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())
        elif oper_type == 'update':
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
                models.zgld_goods_classification_management.objects.filter(id=formObj.get('o_id')).update(
                    classificationName=formObj.get('classificationName'),
                    parentClassification_id=parentClassification_id,
                    xiaochengxu_app_id=dataDict.get('xiaochengxu_app_id'),
                    level=level,
                )
                response.code = 200
                response.msg = '修改成功'
                response.data = {}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
                response.data = {}

        elif oper_type == 'delete':
            objs = goodsObjs = models.zgld_goods_classification_management.objects.filter(id=o_id)
            if objs:
                if goodsObjs.filter(parentClassification_id=o_id):
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