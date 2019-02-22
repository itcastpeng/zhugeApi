from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from bs4 import BeautifulSoup
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.diary_manage_verify import SetFocusGetRedPacketForm, PraiseDiaryForm, diarySelectForm, \
    ReviewDiaryForm, DiaryReviewSelectForm
from django.db.models import F, Q
import json, datetime, base64,requests


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
                case_id = request.GET.get('case_id')

                ## 搜索条件
                diary_id = request.GET.get('diary_id')  #
                title = request.GET.get('title')  #
                user_id = request.GET.get('user_id')  #

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))

                if title:
                    q1.children.append(('title__contains', title))

                if diary_id:

                    q1.children.append(('id', diary_id))

                    diary_objs = models.zgld_diary.objects.filter(id=diary_id)
                    if diary_objs:
                        diary_objs.update(  # 阅读次数
                            read_count=F('read_count') + 1
                        )

                if case_id:
                    q1.children.append(('case_id', case_id))

                q1.children.append(('status__in', [1]))  #
                print('-----q1---->>', q1)
                objs = models.zgld_diary.objects.select_related('company').filter(q1).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if objs:
                    first_diary_date = models.zgld_diary.objects.filter(q1).order_by('create_date')[0].diary_date

                    for obj in objs:

                        diary_up_down_objs = models.zgld_diary_action.objects.filter(diary_id=obj.id,
                                                                                     customer_id=user_id, action=1)
                        if diary_up_down_objs:
                            is_praise_diary = 1
                            is_praise_diary_text = '已经赞过此日记'
                        else:
                            is_praise_diary = 0
                            is_praise_diary_text = '没有赞过此日记'

                        status = obj.status
                        status_text = obj.get_status_display()
                        cover_picture = obj.cover_picture
                        content = obj.content

                        interval_days = (obj.diary_date - first_diary_date).days

                        if cover_picture:
                            cover_picture = json.loads(cover_picture)
                        # if content:
                        #     content = json.loads(content)

                        ret_data.append({
                            'diary_id': obj.id,
                            'case_id': obj.case_id,
                            'company_id': obj.company_id,

                            'is_praise_diary': is_praise_diary,
                            'is_praise_diary_text': is_praise_diary_text,

                            'title': obj.title,
                            'summary': obj.summary,
                            'diary_date': obj.diary_date.strftime('%Y-%m-%d') if obj.diary_date else '',
                            'cover_picture': cover_picture,
                            'content': content,

                            'interval_days': interval_days,

                            'status': status,
                            'status_text': status_text,

                            'read_count': obj.read_count,  #
                            'comment_count': obj.comment_count,  #
                            'up_count': obj.up_count,  #

                            'cover_show_type': obj.cover_show_type,
                            'cover_show_type_text': obj.get_cover_show_type_display(),

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



# 生成海报相关信息页面用于截图使用
@csrf_exempt
def diary_poster_html(request):

    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        customer_id = request.GET.get('customer_id')
        user_customer_belonger_id = request.GET.get('user_customer_belonger_id')
        case_id = request.GET.get('case_id')
        company_id = request.GET.get('company_id')

        poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
            user_customer_belonger_id=user_customer_belonger_id, case_id=case_id)
        url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/diary_manage/poster_html?user_id=%s&uid=%s&case_id=%s' % (
            customer_id, user_id, case_id)

        qr_code = ''
        if poster_belonger_objs:
            poster_belonger_obj = poster_belonger_objs[0]
            qr_code = poster_belonger_obj.qr_code
        case_objs = models.zgld_case.objects.filter(id=case_id)
        poster_cover = []
        if case_objs:
            poster_cover = case_objs[0].poster_cover
            if poster_cover:
                poster_cover = json.loads(poster_cover)
            else:
                poster_cover = ''

        poster_company_logo = models.zgld_xiaochengxu_app.objects.get(company_id=company_id).poster_company_logo

        ret_data = {
            'poster_company_logo' :poster_company_logo,
            'qr_code_url': qr_code,
            'poster_cover' :poster_cover
        }

        return render(request, 'poster_case.html', locals())



@csrf_exempt
@account.is_token(models.zgld_customer)
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
                models.zgld_diary_comment.objects.create(**create_data)
                diary_objs = models.zgld_diary.objects.filter(id=o_id)
                if diary_objs:
                    diary_objs.update(
                        comment_count=F('comment_count') + 1
                    )
                ## 记录单个案例浏览量
                case_objs = models.zgld_case.objects.filter(id=diary_objs[0].case_id)
                if case_objs:
                    case_objs.update(
                        comment_count=F('comment_count') + 1
                    )

                response.code = 200
                response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        ## 点赞日记
        elif oper_type == 'praise_diary':
            customer_id = request.GET.get('user_id')
            # status = request.POST.get('status')

            request_data_dict = {
                'diary_id': o_id,
                'status': 1,  # 文章所属用户的ID

            }

            forms_obj = PraiseDiaryForm(request_data_dict)
            if forms_obj.is_valid():

                create_data = {
                    'diary_id': o_id,
                    'customer_id': customer_id,
                    'status': 1,
                    'action': 1  # 点赞
                }
                diary_objs = models.zgld_diary.objects.filter(id=o_id)
                diary_up_down_objs = models.zgld_diary_action.objects.filter(action=1, diary_id=o_id,
                                                                             customer_id=customer_id)
                if diary_up_down_objs:
                    diary_up_down_objs.update(
                        status=1
                    )
                    response.code = 302
                    response.msg = "已经点过赞了"
                    response.data = {
                        'up_count': diary_objs[0].up_count,
                        'is_praise_diary': 1,
                        'is_praise_diary_text': '已赞过此日记'
                    }
                else:
                    models.zgld_diary_action.objects.create(**create_data)

                    if diary_objs:
                        diary_objs.update(
                            up_count=F('up_count') + 1
                        )
                    response.data = {
                        'up_count': diary_objs[0].up_count,
                        'is_praise_diary': 1,
                        'is_praise_diary_text': '已赞此案例'
                    }
                    response.code = 200
                    response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



    elif request.method == 'GET':

        ## 文章评论列表展示
        if oper_type == 'diary_review_list':

            customer_id = request.GET.get('user_id')
            form_data = {
                'diary_id': o_id
            }
            forms_obj = DiaryReviewSelectForm(form_data)

            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                objs = models.zgld_diary_comment.objects.select_related('from_customer', 'to_customer').filter(diary_id=o_id).filter(Q(is_audit_pass=1) | Q(from_customer=customer_id)).order_by('-create_date')

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
                            'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
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
