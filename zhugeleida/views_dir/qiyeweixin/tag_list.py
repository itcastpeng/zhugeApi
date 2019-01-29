from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.tag_list_verify import TagListAddForm, TagListUpdateForm, TagListSelectForm
import time
import datetime
import json
from publicFunc.condition_com import conditionCom
from django.db.models import Q


# 查询标签和所属的用户
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_list(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        field_dict = {
            'id': '',
            'name': '__contains',
        }
        q = conditionCom(request, field_dict)
        print('q -->', q)
        user_id = request.GET.get('user_id')
        customer_id = request.GET.get('customer_id')
        tag_type = request.GET.get('tag_type')

        # tag_values = models.zgld_tag.objects.filter(Q(user_id=user_id) | Q(user_id__isnull=True)).values_list('id', 'name', 'tag_parent_id','user_id')
        tag_values = models.zgld_tag.objects.filter(Q(user_id=user_id) | Q(user_id__isnull=True)).filter(
            Q(tag_type=tag_type) | Q(tag_type__isnull=True)).values_list('id', 'name', 'tag_parent_id', 'user_id')

        tag_dict = {}
        ret_data = []
        date_list = list(tag_values)

        for obj in date_list:
            if obj[2] == None and obj[3] == None:
                tag_dict['tags'] = []
                tag_dict['name'] = obj[1]

                for tag in date_list:
                    customr_obj = models.zgld_tag.objects.filter(id=tag[0])[0].tag_customer.filter(id=customer_id)
                    if customr_obj:
                        tag_flag = True
                    else:
                        tag_flag = False

                    if tag[2] == obj[0]:
                        tag_dict['name'] = obj[1]
                        tag_dict['tags'].append({'id': tag[0], 'name': tag[1], 'is_select': tag_flag})
                        # tag_dict[obj[0]].append({tag[0]})

                ret_data.append(tag_dict)
                tag_dict = {}

        response.msg = "请求成功"
        response.code = 200
        response.data = {
            'ret_data': ret_data,
            'tag_count': len(ret_data)
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


# 标签列表和标签列表的的操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_list_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 为客户新增加标签，然后绑定到这个客户。
        if oper_type == "add_tag":

            tag_data = {
                'name': request.POST.get('name'),
                'tag_type': request.POST.get('tag_type'),
                'user_id': request.GET.get('user_id')
            }

            forms_obj = TagListAddForm(tag_data)
            if forms_obj.is_valid():
                customer_id = o_id
                if customer_id:
                    obj = models.zgld_tag.objects.create(**forms_obj.cleaned_data)
                    parent_id = models.zgld_tag.objects.filter(name='自定义')[0].id
                    obj.tag_parent_id = parent_id
                    obj.tag_customer = [customer_id]
                    obj.save()
                    response.code = 200
                    response.msg = "添加成功"
                else:
                    response.code = 302
                    response.msg = "标签关联客户不能为空"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 清空标签
        elif oper_type == 'delete_tag':
            user_id = request.GET.get('user_id')

            objs = models.zgld_tag.objects.filter(id=o_id, user_id=user_id)

            if objs:
                objs.delete()

            response.code = 200
            response.msg = "删除成功"

        # 操作tag，为客户添加多个标签
        elif oper_type == "customer_tag":

            tag_list = json.loads(request.POST.get('tag_list'))
            customer_obj = models.zgld_customer.objects.get(id=o_id)

            if customer_obj:
                customer_obj.zgld_tag_set = tag_list
                response.code = 200
                response.msg = "添加成功"
            else:
                response.code = 302
                response.msg = "标签关联客户不能为空"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
