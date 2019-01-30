from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from bs4 import BeautifulSoup
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.diary_manage_verify import SetFocusGetRedPacketForm, diaryAddForm, diarySelectForm, diaryUpdateForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm

import json,datetime
from django.db.models import Q, Sum, Count

@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def diary_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        # 查询 文章-活动(任务)
        if oper_type == 'diary_list':

            print('request.GET----->', request.GET)

            forms_obj = diarySelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                ## 搜索条件
                diary_id = request.GET.get('diary_id')  #
                search_activity_status = request.GET.get('status')  #
                title = request.GET.get('title')  #

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))

                if title:
                    q1.children.append(('title__contains', title))

                if diary_id:
                    q1.children.append(('id', diary_id))

                # now_date_time = datetime.datetime.now()
                if search_activity_status:
                    q1.children.append(('status', search_activity_status))  #


                print('-----q1---->>', q1)
                objs = models.zgld_diary.objects.select_related('company').filter(q1).order_by(order).exclude(status__in=[3])
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if objs:

                    for obj in objs:
                        status = obj.status
                        status_text = obj.get_status_display()
                        cover_picture = obj.cover_picture
                        content = obj.content

                        if cover_picture:
                            cover_picture =  json.loads(cover_picture)
                        if content:
                            content = json.loads(content)

                        ret_data.append({
                            'diary_id': obj.id,
                            'case_id': obj.case_id,
                            'company_id': obj.company_id,

                            'title': obj.title,
                            'diary_date' : obj.diary_date.strftime('%Y-%m-%d') if obj.diary_date else '',
                            'cover_picture': cover_picture,
                            'content': content,

                            'status': status,
                            'status_text': status_text,

                            'cover_show_type' : obj.cover_show_type,
                            'cover_show_type_text' : obj.get_cover_show_type_display(),

                            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                        })

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



    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def diary_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 删除-案例
        if oper_type == "delete":

            company_id = request.GET.get('company_id')
            objs = models.zgld_diary.objects.filter(id=o_id,company_id=company_id)

            if objs:
                objs.update(
                    status=3
                )
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '案例不存在'

        # 修改-案例
        elif oper_type == 'update':

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            diary_id = o_id
            case_id = request.POST.get('case_id')
            title = request.POST.get('title')
            summary = request.POST.get('summary')
            diary_date = request.POST.get('diary_date')
            cover_picture = request.POST.get('cover_picture')  # 文章ID
            content = request.POST.get('content')

            status = request.POST.get('status')
            cover_show_type = request.POST.get('cover_show_type')  # (1,'只展示图片'),  (2,'只展示视频'),

            form_data = {

                'case_id': case_id,
                'company_id': company_id,

                'title': title,
                'summary' : summary,
                'diary_date': diary_date,  # 活动名称
                'cover_picture': cover_picture,  # 活动名称
                'content': content,  # 活动名称

                'status': status,
                'cover_show_type': cover_show_type,
            }

            forms_obj = diaryUpdateForm(form_data)
            if forms_obj.is_valid():

                diary_objs = models.zgld_diary.objects.filter(id=diary_id)
                # if cover_show_type == 1: # (1,'只展示图片'), (2,'只展示视频'),
                #     _content = json.loads(content)
                #     soup = BeautifulSoup(_content, 'lxml')
                #
                #     img_tags = soup.find_all('img')
                #     for img_tag in img_tags:
                #         data_src = img_tag.attrs.get('src')
                #         if data_src:
                #             print(data_src)

                diary_objs.update(
                    user_id = user_id,
                    case_id = case_id,
                    company_id = company_id,

                    title = title,
                    summary=summary,

                    diary_date = diary_date,
                    cover_picture = cover_picture,
                    content = content,

                    status = status,
                    cover_show_type = cover_show_type
                )



                case_objs = models.zgld_case.objects.filter(id=case_id)
                if case_objs:
                    case_objs.update(
                        update_date=datetime.datetime.now()
                    )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 增加-案例
        elif oper_type == "add":


            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')

            case_id = request.POST.get('case_id')

            title = request.POST.get('title')
            summary = request.POST.get('summary')

            diary_date = request.POST.get('diary_date')
            cover_picture = request.POST.get('cover_picture')  # 文章ID
            content = request.POST.get('content')

            status = request.POST.get('status')
            cover_show_type  = request.POST.get('cover_show_type') # (1,'只展示图片'),  (2,'只展示视频'),


            form_data = {

                'case_id' : case_id,
                'company_id' :company_id,

                'title': title,
                'summary': summary,

                'diary_date': diary_date,  # 活动名称
                'cover_picture': cover_picture,  # 活动名称
                'content': content,  # 活动名称

                'status': status,
                'cover_show_type' : cover_show_type,
            }

            forms_obj = diaryAddForm(form_data)
            if forms_obj.is_valid():

                # if cover_show_type == 1:  # (1,'只展示图片'), (2,'只展示视频'),
                    # _content = json.loads(content)
                    # _cover_picture = json.loads(cover_picture)
                    # soup = BeautifulSoup(_content, 'lxml')
                    #
                    # img_tags = soup.find_all('img')
                    # for img_tag in img_tags:
                    #     data_src = img_tag.attrs.get('src')
                    #     if data_src:
                    #         print(data_src)

                models.zgld_diary.objects.create(
                    user_id=user_id,
                    case_id=case_id,
                    company_id=company_id,

                    title=title,
                    summary=summary,
                    diary_date=diary_date,
                    cover_picture=cover_picture,
                    content=content,

                    status=status,
                    cover_show_type=cover_show_type
                )
                case_objs = models.zgld_case.objects.filter(id=case_id)
                if case_objs:
                    case_objs.update(
                        update_date=datetime.datetime.now()
                    )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)
