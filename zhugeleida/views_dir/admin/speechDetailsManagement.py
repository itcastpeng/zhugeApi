from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.adminSpeechDetailsmanage import AddForm, UpdateForm
import json
from django.db.models import Q


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def speechDetailsManage(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        groupSearch = request.GET.get('groupSearch')
        order = request.GET.get('order', '-createDate')
        field_dict = {
            'id': '',
            'talkGroupName': '__contains',
            'create_date': '',
        }
        q = conditionCom(request, field_dict)
        print('q -->', q)
        # q.add(Q(talkGroupName_id=user_id), Q.AND)
        companyName_id = request.GET.get('companyName_id')
        objs = models.zgld_speech_details_management.objects.filter(q).order_by(order).filter(talkGroupName_id__companyName=companyName_id)
        if groupSearch:
            if groupSearch == 'groupSearch':
                objs = objs.filter(talkGroupName_id__isnull=True)
            else:
                objs = objs.filter(talkGroupName_id=groupSearch)
        objsCount = objs.count()
        otherList = []
        for obj in objs:
            sendNum = 0
            if obj.sendNum:
                sendNum = obj.sendNum
            talkGroupNameId = ''
            groupName = ''
            if obj.talkGroupName:
                groupName = obj.talkGroupName.groupName
                talkGroupNameId = obj.talkGroupName.id
            username = ''
            if obj.userProfile:
                username = obj.userProfile.username
            otherList.append({
                'o_id':obj.id,
                'p_id':talkGroupNameId,
                'contentWords': obj.contentWords,  # 分组名
                'sendNum': sendNum,  # 用户
                'talkGroupName': groupName,  # 公司名
                'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),  # 创建时间
                'username':username,
                'user_id':user_id,
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'otherList': otherList,
            'objsCount': objsCount,
        }
        # else:
        #     response.code = 402
        #     response.msg = "请求异常"
        #     response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def speechDetailsManageOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        form_data = {
            'o_id':o_id,
            'contentWords': request.POST.get('contentWords'),
            'userProfile': request.GET.get('user_id'),  # 归属用户
            'talkGroupName': request.POST.get('talkGroupName'),
        }
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                obj = models.zgld_speech_details_management.objects.create(
                    contentWords=forms_obj.cleaned_data.get('contentWords'),
                    talkGroupName_id=forms_obj.cleaned_data.get('talkGroupName'),
                    userProfile_id=forms_obj.cleaned_data.get('userProfile'),
                )
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update":
            # 获取需要修改的信息
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                objs = models.zgld_speech_details_management.objects.filter(id=o_id)
                #  更新 数据
                if objs:
                    objs.update(
                        contentWords=forms_obj.cleaned_data.get('contentWords'),
                        talkGroupName_id=forms_obj.cleaned_data.get('talkGroupName'),
                        userProfile_id=forms_obj.cleaned_data.get('userProfile')
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = '修改ID不存在'
            else:
                print("验证不通过")
                print('forms_obj.errors.as_json() -->', forms_obj.errors.as_json())
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        if oper_type == "delete":
            # 删除 ID
            objs = models.zgld_speech_details_management.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
        else:
            response.code = 402
            response.msg = '请求异常'
    return JsonResponse(response.__dict__)
