from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from bs4 import BeautifulSoup
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.diary_manage_verify import SetFocusGetRedPacketForm, diaryAddForm, diarySelectForm,ReviewDiaryForm,DiaryReviewSelectForm
from django.db.models import F,Q
import json,datetime
from django.db.models import Q, Sum, Count
import base64

@csrf_exempt
@account.is_token(models.zgld_customer)
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

                    diary_objs = models.zgld_diary.objects.filter(id=diary_id)
                    if diary_objs:
                        diary_objs.update( # 阅读次数
                            read_count=F('read_count') + 1
                        )


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
                            'diary_date' : obj.diary_date.strftime('%Y-%m-%d %H:%M:%S') if obj.diary_date else '',
                            'cover_picture': cover_picture,
                            'content': content,

                            'status': status,
                            'status_text': status_text,

                            'read_count' : obj.read_count, #
                            'comment_count' : obj.comment_count, #
                            'up_count' : obj.up_count, #


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

    elif request.method == "POST":
        pass




    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def diary_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 评论日记
        if oper_type == 'review_diary':

            from_customer_id = request.GET.get('user_id')
            content = request.POST.get('content')

            request_data_dict = {
                'diary_id': o_id,
                'content': content,  # 文章所属用户的ID
                'customer_id': from_customer_id,  # 文章所属用户的ID
            }

            forms_obj = ReviewDiaryForm(request_data_dict)
            if forms_obj.is_valid():

                encodestr = base64.b64encode(content.encode('utf-8'))
                msg = str(encodestr, 'utf-8')

                create_data = {
                    'diary_id': o_id,
                    'content': msg,
                    'from_customer_id': from_customer_id
                }
                obj = models.zgld_diary_comment.objects.create(**create_data)
                response.code = 200
                response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    elif request.method == 'GET':

        ## 文章评论列表展示
        if oper_type == 'diary_id_review_list':

            user_id = request.GET.get('user_id')
            form_data = {
                'diary_id' : o_id
            }
            forms_obj = DiaryReviewSelectForm(form_data)

            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                objs = models.zgld_diary_comment.objects.select_related('from_customer','to_customer').filter(diary_id=o_id).order_by('-create_date')

                count = objs.count()
                if objs:

                    # if length != 0:
                    #     start_line = (current_page - 1) * length
                    #     stop_line = start_line + length
                    #     objs = objs[start_line: stop_line]

                    ret_data = []
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
                            'from_customer_id': obj.from_customer_id,
                            'from_customer_name': customer_name,
                            'from_customer_headimgurl': obj.from_customer.headimgurl,
                            'content': content,
                            'create_time' : obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }

                else:
                    response.code = 302
                    response.msg = '没有数据'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)
