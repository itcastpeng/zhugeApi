from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.tag_user_verify import TagUserAddForm,TagUserUpdateForm
import time
import datetime
import json
from django.db.models import Q
from publicFunc.condition_com import conditionCom

# 标签 和 标签用户的查询
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_user(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1

        user_id = request.GET.get('user_id')
        tag_type = request.GET.get('tag_type')

        field_dict = {
            'tag_id': '',
            'name': '__contains',
        }
        q = conditionCom(request, field_dict)
        print('q -->', q)
        if tag_type:        # (1, '微信公众号'),  (2, '微信小程序'),
            q.add(Q(**{'tag_type': tag_type}), Q.AND)

        tag_list = models.zgld_userprofile.objects.get(id=user_id).zgld_user_tag_set.filter(q).values('id','name')


        response.code = 200
        response.data = {
            'user_id': user_id,
            'ret_data': list(tag_list),
            'data_count': tag_list.count(),
        }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)



# 标签 和 标签用户的操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_user_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加用户标签
        if oper_type == "add":

            user_id = request.GET.get('user_id')
            tag_data = {
                'user_id' : request.GET.get('user_id'),
                'name': request.POST.get('name'),
            }

            forms_obj = TagUserAddForm(tag_data)
            if forms_obj.is_valid():

                name = forms_obj.cleaned_data['name']
                user_tag_obj = models.zgld_user_tag.objects.create(
                    user_id=user_id,
                    name=name
                )
                tag_id = user_tag_obj.id
                tag_name = user_tag_obj.name

                response.code = 200
                response.msg = "添加成功"
                response.data = [{ 'id' : tag_id, 'name':tag_name }]

            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除用户标签
        elif oper_type == "delete":
            tag_id = request.POST.get('id')
            user_id = request.GET.get('user_id')
            tag_objs = models.zgld_user_tag.objects.filter(id=tag_id,user_id=user_id)
            if tag_objs:
                tag_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '标签ID不存在'

        # 保存用户标签
        elif oper_type == "save":

            user_id =  request.GET.get('user_id')
            tag_list =  json.loads(request.POST.get('tag_list'))

            tag_objs = models.zgld_user_tag.objects.filter(id__in=tag_list,user_id=user_id)
            if tag_objs:
                obj = models.zgld_userprofile.objects.get(id=user_id)
                obj.zgld_user_tag_set = tag_objs
                response.code = 200
                response.msg = "保存成功"

            else:
                response.code = 301
                response.msg = "标签不存在"

        else:
            response.code = 302
            response.msg = '标签ID不存在'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
