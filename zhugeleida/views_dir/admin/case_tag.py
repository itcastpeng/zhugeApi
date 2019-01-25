from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.case_tag_verify import CaseTagAddForm,CaseTagUpdateAddForm,CaseTagSingleAddForm
import time
import datetime
import json

from publicFunc.condition_com import conditionCom

# 文章的标签查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def case_tag(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1

        user_id = request.GET.get('user_id')
        company_id = request.GET.get('company_id')

        field_dict = {
            'tag_id': '',
            'name': '__contains', #标签搜索
        }
        q = conditionCom(request, field_dict)
        print('q -->', q)

        tag_list = models.zgld_case_tag.objects.filter(company_id=company_id).values('id','name')
        tag_data = list(tag_list)

        response.code = 200
        response.data = {
            'ret_data': tag_data,
            'data_count': tag_list.count(),
        }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 文章的标签操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def case_tag_oper(request, oper_type,o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        #加双层标签
        if oper_type == "double_add":

            user_id = request.GET.get('user_id')
            tag_data = {
                'user_id' : request.GET.get('user_id'),
                'parent_tag_name': request.POST.get('parent_tag_name'), # 一级标签
                'second_tag_name' : request.POST.get('second_tag_name')  # 二级标签
            }

            forms_obj = CaseTagAddForm(tag_data)
            if forms_obj.is_valid():

                parent_tag_name = forms_obj.cleaned_data['parent_tag_name']
                second_tag_name = forms_obj.cleaned_data['second_tag_name']


                #说明新建的一级标签
                user_tag_obj = models.zgld_case_tag.objects.create(
                    user_id=user_id,
                    name=parent_tag_name
                )

                tag_id = user_tag_obj.id
                tag_name = user_tag_obj.name

                if second_tag_name:
                    objs = models.zgld_case_tag.objects.filter(
                        name=second_tag_name, user_id=user_id
                    )
                    if objs:
                        response.msg = '不能存在相同的标签名'
                        response.code = 303
                        return JsonResponse(response.__dict__)

                    models.zgld_case_tag.objects.create(
                        user_id=user_id,
                        name=second_tag_name,
                        parent_id_id=tag_id
                    )

                response.code = 200
                response.msg = "添加成功"
                response.data = [{ 'parent_tag_id' : tag_id, 'parent_tag_name': tag_name,'second_tag_name': second_tag_name}]

            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

        #加单层标签+默认标签或者用户专属标签
        elif oper_type == "update":

            tag_name = request.POST.get('tag_name')
            company_id = request.GET.get('company_id')

            tag_data = {
                'tag_id' : o_id,
                'company_id' : company_id,
                'tag_name' : tag_name   # 标签名字
            }

            forms_obj = CaseTagUpdateAddForm(tag_data)
            if forms_obj.is_valid():
                tag_name = forms_obj.cleaned_data['tag_name']
                tag_id = forms_obj.cleaned_data['tag_id']

                #说明新建的一级标签
                case_tag_objs = models.zgld_case_tag.objects.filter(
                   id=tag_id,company_id=company_id
                )
                case_tag_objs.update(
                    name = tag_name
                )

                response.code = 200
                response.msg = "修改成功"


            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

        # 添加文章标签
        elif oper_type == "add":

            company_id = request.GET.get('company_id')
            tag_data = {
                'company_id' : company_id,
                'tag_name' : request.POST.get('tag_name')   # 二级标签
            }

            forms_obj = CaseTagSingleAddForm(tag_data)
            if forms_obj.is_valid():
                tag_name = forms_obj.cleaned_data['tag_name']

                #说明新建的一级标签
                article_tag_obj = models.zgld_case_tag.objects.create(
                    name = tag_name,
                    company_id = company_id,
                )
                tag_id = article_tag_obj.id
                tag_name = article_tag_obj.name

                response.code = 200
                response.msg = "添加成功"
                response.data = [{ 'tag_id' : tag_id, 'tag_name': tag_name}]

            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除文章标签
        elif oper_type == "delete":
            tag_id = o_id
            company_id = request.GET.get('company_id')
            tag_objs = models.zgld_case_tag.objects.filter(id=tag_id,company_id=company_id)
            if tag_objs:
                tag_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '标签ID不存在'

        else:
            response.code = 302
            response.msg = '标签ID不存在'


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


def tree_search(d_dic,tag_dic):

    for k,v in d_dic.items():

        if k[0] == tag_dic[2]:

            d_dic[k][tag_dic] = {}
            return
        else:
            if v:
                tree_search(d_dic[k],tag_dic)

def build_tree(query_set_list):

    d_dic = { }

    for tag_dic in query_set_list:

        if tag_dic[2] is None:

            d_dic[tag_dic] = {}

        else:
            tree_search(d_dic, tag_dic)

    return d_dic


