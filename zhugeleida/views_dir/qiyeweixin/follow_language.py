from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.followup_verify import FollowLanguageAddForm, FollowLanguageSelectForm, \
    FollowInfoAddForm, FollowInfoSelectForm

import json

from publicFunc.condition_com import conditionCom
from django.db.models import Q


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def follow_language(request, ):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = FollowLanguageSelectForm(request.GET)
        if forms_obj.is_valid():
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            user_id = forms_obj.cleaned_data['user_id']
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')

            field_dict = {
                'user_id': '',
            }
            q = conditionCom(request, field_dict)
            q.add(Q(**{'user_id__isnull': True}), Q.OR)

            print('q -->', q)

            objs = models.zgld_follow_language.objects.filter(q).order_by(order)  # 查询出有user用户关联的跟进常用语
            count = objs.count()

            if length != 0:
                print('current_page -->', current_page)
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            language_list = []


            if objs:
                for obj in objs:
                    language_list.append(
                        {'language_id': obj.id, 'user_id': obj.user_id, 'language': obj.custom_language})

            response.code = 200
            response.data = {
                'data_count': objs.count(),
                'ret_data': {
                    'user_id': user_id,
                    'follow_language_data': language_list,

                },
            }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def follow_language_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add":

            print('----request.POST---->>', request.POST)
            language_data = {
                'user_id': request.GET.get('user_id'),
                'custom_language': request.POST.get('custom_language'),
            }
            forms_obj = FollowLanguageAddForm(language_data)
            if forms_obj.is_valid():
                obj = models.zgld_follow_language.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {
                    'language_id': obj.id,
                }

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('------delete o_id --------->>', o_id)
            user_id = request.GET.get('user_id')

            language_objs = models.zgld_follow_language.objects.filter(id=o_id, user_id=user_id)
            if language_objs:
                language_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = 'ID不存在或者不允许删除'



    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
