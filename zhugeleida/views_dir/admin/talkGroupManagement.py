from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.adminTalkGroupManage import AddForm, UpdateForm, SelectForm
import json

# 话术分组管理查询
# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def talkGroupManage(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-createDate')
            field_dict = {
                'id': '',
                'groupName': '__contains',
                'create_date': '',
                'userProfile': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            companyName_id = request.GET.get('companyName_id')
            objs = models.zgld_talk_group_management.objects.filter(q).order_by(order).filter(companyName_id=companyName_id)
            objsCount = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            otherList = []
            for obj in objs:
                companyName = ''
                if obj.companyName:
                    companyName = obj.companyName.name
                otherList.append({
                    'o_id': obj.id,
                    'groupName': obj.groupName,                 # 分组名
                    'userProfile': obj.userProfile.username,    # 用户
                    'companyName': companyName,                 # 公司名
                    'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S') # 创建时间
                })

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'otherList': otherList,
                'objsCount': objsCount,
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  话术分组管理操作
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def talkGroupManageOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        form_data = {
            'o_id': o_id,
            'groupName': request.POST.get('groupName'),         # 话术分组名称
            'userProfile': request.POST.get('userProfile'),     # 归属用户
            'companyName': request.POST.get('companyName'),
        }
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                models.zgld_talk_group_management.objects.create(
                    groupName=forms_obj.cleaned_data.get('groupName'),
                    userProfile_id=forms_obj.cleaned_data.get('userProfile'),
                    companyName_id=forms_obj.cleaned_data.get('companyName'),
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
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data.get('o_id')
                objs = models.zgld_talk_group_management.objects.filter(id=o_id)
                #  更新 数据
                if objs:
                    objs.update(
                        groupName=forms_obj.cleaned_data.get('groupName'),
                        userProfile=forms_obj.cleaned_data.get('userProfile'),
                        companyName=forms_obj.cleaned_data.get('companyName')
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

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
            objs = models.zgld_talk_group_management.objects.filter(id=o_id)
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
