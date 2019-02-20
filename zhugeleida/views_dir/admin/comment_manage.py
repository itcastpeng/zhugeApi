from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from bs4 import BeautifulSoup
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.comment_manage_verify import SetFocusGetRedPacketForm, commentAddForm, commentSelectForm, commentUpdateForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm

import json,datetime,base64
from django.db.models import Q, Sum, Count

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def comment_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        # 查询 文章-活动(任务)
        if oper_type == 'diary' or  oper_type == 'article':

            print('request.GET----->', request.GET)

            forms_obj = commentSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                ## 搜索条件
                is_audit_pass = request.GET.get('is_audit_pass')  #是否通过审核

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('from_customer__company_id', company_id))

                # now_date_time = datetime.datetime.now()
                q1.children.append(('is_audit_pass', is_audit_pass))  #


                print('-----q1---->>', q1)
                objs = ''
                count = ''
                if oper_type == 'article':
                    objs = models.zgld_article_comment.objects.select_related('article','from_customer').filter(q1).order_by(order)
                    count = objs.count()
                elif oper_type == 'diary':
                    objs = models.zgld_diary_comment.objects.select_related('diary','from_customer').filter(q1).order_by(order)
                    count = objs.count()

                ret_data = []
                if objs:

                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    for obj in objs:

                        try:
                            username = base64.b64decode(obj.from_customer.username)
                            customer_name = str(username, 'utf-8')
                            print('----- 解密b64decode username----->', username)
                        except Exception as e:
                            print('----- b64decode解密失败的 customer_id 是 | e ----->', obj.from_customer_id, "|", e)
                            customer_name = '客户ID%s' % (obj.from_customer_id)

                        _content = base64.b64decode(obj.content)
                        content = str(_content, 'utf-8')
                        print('----- 解密b64decode 内容content----->', content)

                        ret_data.append({
                            'id' : obj.id,
                            'from_customer_id': obj.from_customer_id,
                            'from_customer_name': customer_name,
                            'from_customer_headimgurl': obj.from_customer.headimgurl,
                            'title' : obj.article.title,
                            'cover_picture' : obj.article.cover_picture,

                            'content': content,
                            'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }


            else:

                response.code = 301
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())

    elif  request.method == "POST":

        # 删除-评论
        if oper_type == "delete":

            company_id = request.GET.get('company_id')
            _type = request.POST.get('type')
            ids_list = request.POST.get('ids_list')
            if ids_list:
                ids_list = json.loads(ids_list)

            objs = ''
            if _type == 'diary':
                objs = models.zgld_diary_comment.objects.filter(id__in=ids_list, from_customer__company_id=company_id)

            elif _type == 'article':
                objs = models.zgld_article_comment.objects.filter(id__in=ids_list, from_customer__company_id=company_id)

            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '案例不存在'

        # 修改-案例
        elif oper_type == 'audit_pass':

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            _type = request.POST.get('type')
            ids_list = request.POST.get('ids_list')
            if ids_list:
                ids_list = json.loads(ids_list)

            objs = ''
            if _type == 'diary':
                objs = models.zgld_diary_comment.objects.filter(id__in=ids_list, from_customer__company_id=company_id)
                if objs:
                    print('diary 数据存在 ------->',request.POST)
                    objs.update(
                        is_audit_pass=1
                    )
                    response.code = 200
                    response.msg = "审核成功"

            elif _type == 'article':
                objs = models.zgld_article_comment.objects.filter(id__in=ids_list, from_customer__company_id=company_id)
                if objs:
                    print('article 数据存在 ------->', request.POST)
                    objs.update(
                        is_audit_pass=1
                    )

                    response.code = 200
                    response.msg = "审核成功"

            else:
                response.code = 302
                response.msg = "数据不存在"

        ## 评论是否开启
        elif oper_type == 'setting_open_comment':
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            is_open_comment = request.POST.get('is_open_comment')


            objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            if objs and is_open_comment:
                objs.update(
                    is_open_comment=is_open_comment
                )
                response.code = 200
                response.msg = "设置成功"

            else:
                response.code = 200
                response.msg = "公众号不存在"


    return JsonResponse(response.__dict__)

