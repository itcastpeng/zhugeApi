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


# 查询标签和所属的用户
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_list(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        order = request.GET.get('order', '-create_date')

        field_dict = {
            'id': '',
            'name': '__contains',
        }
        q = conditionCom(request, field_dict)
        print('q -->', q)

        objs = models.zgld_tag.objects.filter(q).order_by(order)

        tag_values = models.zgld_tag.objects.values_list('id', 'name', 'tag_parent_id')
        tag_dict = {}
        ret_data = []
        date_list = list(tag_values)
        for obj in date_list:
            if obj[2] == None:

                tag_dict['tags'] = []
                for tag in date_list:
                    if tag[2] == obj[0]:
                        tag_dict['name']  = obj[1]
                        tag_dict['tags'].append({ 'id': tag[0],'name': tag[1]})
                        # tag_dict[obj[0]].append({tag[0]})

                ret_data.append(tag_dict)
                tag_dict = {}

        response.code = 200
        response.data = {
            'ret_data': ret_data,
            'tag_count': len(ret_data),
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_list_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add_tag":   # 为客户新增加标签，然后绑定到这个客户。

            tag_data = {
                'name': request.POST.get('name'),
                'user_id': request.GET.get('user_id')
            }

            forms_obj = TagListAddForm(tag_data)
            if forms_obj.is_valid():
                customer_id = o_id
                if customer_id:
                    obj = models.zgld_tag.objects.create(**forms_obj.cleaned_data)
                    parent_id = models.zgld_tag.objects.filter(name='其他')[0].id
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

        elif oper_type == "customer_tag":  # 操作tag，为客户添加多个标签
            tag_data = {
                'name': request.POST.get('name'),
                'user_id': request.GET.get('user_id')
            }

            forms_obj = TagListAddForm(tag_data)
            if forms_obj.is_valid():
                tag_list = request.POST.get('tag_list')
                customer_obj = models.zgld_customer.objects.get(id=o_id)
                # tag_objs = models.zgld_tag.objects.filter(id__in=tag_list)
                if customer_obj:
                    customer_obj.zgld_tag_set = tag_list
                    response.code = 200
                    response.msg = "添加成功"
                else:
                    response.code = 302
                    response.msg = "标签关联客户不能为空"

        # elif oper_type == "delete":
        #     print('------delete o_id --------->>',o_id)
        #     tag_objs = models.zgld_tag.objects.filter(id=o_id)
        #     if tag_objs:
        #         tag_objs.delete()
        #         response.code = 200
        #         response.msg = "删除成功"
        #     else:
        #         response.code = 302
        #         response.msg = '标签ID不存在'
        #
        # elif oper_type == "update":
        #     form_data = {
        #         'tag_id': o_id,
        #         'name': request.POST.get('name'),
        #     }
        #     print(form_data)
        #     forms_obj = TagCustomerUpdateForm(form_data)
        #
        #     if forms_obj.is_valid():
        #         name = forms_obj.cleaned_data['name']
        #         tag_id = forms_obj.cleaned_data['tag_id']
        #         print(tag_id)
        #         tag_objs = models.zgld_tag.objects.filter(
        #             id=tag_id
        #         )
        #         if tag_objs:
        #             customer_list = request.POST.getlist('user_list')
        #             if customer_list:
        #                 tag_customer_obj = models.zgld_tag.objects.get(id=tag_id)
        #                 tag_customer_obj.tag_customer =  customer_list
        #
        #             tag_objs.update(
        #                 name=name
        #             )
        #             response.code = 200
        #             response.msg = "修改成功"
        #         else:
        #             response.code = 302
        #             response.msg = '标签ID不存在'
        #     else:
        #         response.code = 303
        #         response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)