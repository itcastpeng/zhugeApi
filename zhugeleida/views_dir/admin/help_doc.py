
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.help_doc_verify import ArticleAddForm,ArticleSelectForm, ArticleUpdateForm

import json, base64
from django.db.models import Q, Count

# 文章管理查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def help_doc(request,oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
            # 获取参数 页数 默认1

       if oper_type == 'help_doc_list':

            forms_obj = ArticleSelectForm(request.GET)
            if forms_obj.is_valid():

                user_id = request.GET.get('user_id')
                article_id = request.GET.get('article_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                q = Q()
                if article_id:
                    q.add(Q(**{'id': article_id}), Q.AND)

                objs = models.zgld_help_doc.objects.filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 获取所有数据
                ret_data = []
                # 获取第几页的数据
                for obj in objs:

                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,       # 文章标题
                        'content': obj.content,  # 用户的头像
                        'create_date': obj.create_date,      #文章创建时间
                    })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
            return JsonResponse(response.__dict__)


    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def help_doc_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加文章
        if oper_type == "add":

            article_data = {

                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
            }

            forms_obj = ArticleAddForm(article_data)

            if forms_obj.is_valid():

                user_id = request.GET.get('user_id')

                dict_data = {
                    'user_id': user_id,
                    'title' :forms_obj.cleaned_data['title'],
                    'content' :forms_obj.cleaned_data['content']
                }

                models.zgld_help_doc.objects.create(**dict_data)
                response.code = 200
                response.msg = "添加成功"

            else:

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除文章
        elif oper_type == "delete":

            article_objs = models.zgld_help_doc.objects.filter(id=o_id)

            if article_objs:
               article_objs.delete()
               response.code = 200
               response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '文章不存在'

        # 修改文章
        elif oper_type == "update":
            article_data = {
                'article_id' : o_id,
                'title': request.POST.get('title'),
                'content': request.POST.get('content')
            }

            forms_obj = ArticleUpdateForm(article_data)
            if forms_obj.is_valid():
                dict_data = {
                    'title': forms_obj.cleaned_data['title'],
                    'content': forms_obj.cleaned_data['content']
                }
                user_id = request.GET.get('user_id')
                article_id = forms_obj.cleaned_data['article_id']
                obj = models.zgld_help_doc.objects.filter(
                    id=article_id
                )
                obj.update(**dict_data)

                response.code = 200
                response.msg = '修改成功'


            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = '请求异常'


    return JsonResponse(response.__dict__)




