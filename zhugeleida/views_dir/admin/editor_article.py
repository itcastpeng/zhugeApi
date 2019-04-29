from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.editor_article_verify import ArticleAddForm, ArticleUpdateForm, \
    ArticleDeleteForm, SelectForm, ReportSelectForm, SubmitArticleForm
from publicFunc.condition_com import conditionCom
import json, base64
from django.db.models import Q


# 文章管理查询
@csrf_exempt
@account.is_token(models.zgld_editor)
def editor_article(request):
    user_id = request.GET.get('user_id')
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')
        field_dict = {
            'id': '',
            'status': '',
            'title': '__contains',
        }
        q = conditionCom(request, field_dict)

        tag_list = json.loads(request.GET.get('tags_list')) if request.GET.get('tags_list') else []
        if tag_list:
            q.add(Q(**{'tags__in': tag_list}), Q.AND)

        objs = models.zgld_editor_article.objects.filter(
            q,
            user_id=user_id,
        ).order_by(order)
        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        data_list = []
        id = request.GET.get('id')
        for obj in objs:
            tag_list = list(obj.tags.values('id', 'name'))

            data_list.append({
                'id': obj.id,
                'title': obj.title,  # 文章标题
                'status_code': obj.status,  # 状态
                'status': obj.get_status_display(),  # 状态
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),  # 文章创建时间
                'cover_url': obj.cover_picture,  # 封面图片链接
                'tag_list': tag_list,
                'reason_rejection': obj.reason_rejection,  # 驳回理由
            })

            if id:
                data_list[0]['summary'] = obj.summary  # 文章标题
                data_list[0]['content'] = obj.content  # 文章内容
                data_list[0]['is_auto_tagging'] = obj.is_auto_tagging  # 文章是否开启打标签
                data_list[0]['tags_time_count'] = obj.tags_time_count  # 达到几秒实现打标签
                data_list[0]['insert_ads'] = json.loads(obj.insert_ads)  # 植入广告类型

        status_choices = []
        for i in models.zgld_editor_article.status_choices:
            status_choices.append({
                'id': i[0],
                'name': i[1]
            })
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'count': count,
            'data_list': data_list,
            'status_choices': status_choices,
        }
        response.note = {
            'id': '文章ID',
            'title': '文章标题',
            'status_code': '文章状态ID',
            'status': '文章状态',
            'create_date': '文章创建时间',
            'cover_url': '封面图片链接',
            'tag_list': '标签列表',
            'summary': '文章摘要',
            'content': '文章内容',
            'is_auto_tagging': '文章是否开启打标签, 0不开启, 1开启',
            'insert_ads': '植入广告类型',
            'tags_time_count': '达到几秒实现打标签',
            'reason_rejection': '驳回理由',
        }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 编辑添加文章
@csrf_exempt
@account.is_token(models.zgld_editor)
def editor_article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        is_auto_tagging = request.POST.get('is_auto_tagging')  # (0,'不开启'),   (1,'开启'),
        tags_time_count = request.POST.get('tags_time_count')  # 达到几秒实现打标签

        article_form_data = {
            'o_id': o_id,
            'user_id': request.GET.get('user_id'),
            'title': request.POST.get('title'),
            'summary': request.POST.get('summary'),
            'content': request.POST.get('content'),
            'cover_picture': request.POST.get('cover_picture'),
        }

        # 添加文章
        if oper_type == "add":
            forms_obj = ArticleAddForm(article_form_data)
            if forms_obj.is_valid():
                title, company_id = forms_obj.cleaned_data['title']

                dict_data = {
                    'title': title,
                    'user_id': user_id,
                    'summary': forms_obj.cleaned_data['summary'],
                    'content': forms_obj.cleaned_data['content'],
                    'cover_picture': forms_obj.cleaned_data['cover_picture'].strip(),
                    'insert_ads': request.POST.get('insert_ads'),
                    'is_auto_tagging': is_auto_tagging,
                    'tags_time_count': tags_time_count
                }

                obj = models.zgld_editor_article.objects.create(**dict_data)

                insert_ads = request.POST.get('insert_ads') # 植入广告类型

                if insert_ads:
                    insert_ads = json.loads(insert_ads)
                    title = insert_ads.get('title')
                    plugin_id = insert_ads.get('id')
                    if title and plugin_id:
                        obj.plugin_report_id = plugin_id
                        obj.save()
                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    obj.tags = tags_id_list

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除文章
        elif oper_type == "delete":
            form_objs = ArticleDeleteForm({'o_id':o_id})
            if form_objs.is_valid():
                response.code = 200
                response.msg = '删除成功'
            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 修改文章
        elif oper_type == "update":
            forms_obj = ArticleUpdateForm(article_form_data)
            if forms_obj.is_valid():
                title, company_id = forms_obj.cleaned_data['title']
                dict_data = {
                    'title': title,
                    'summary': forms_obj.cleaned_data['summary'],
                    'content': forms_obj.cleaned_data['content'],
                    'cover_picture': forms_obj.cleaned_data['cover_picture'],
                    'insert_ads': request.POST.get('insert_ads'),
                    'is_auto_tagging': is_auto_tagging,
                    'tags_time_count': tags_time_count
                }

                article_id = forms_obj.cleaned_data['o_id']
                objs = models.zgld_editor_article.objects.select_related('plugin_report').filter(
                    id=article_id
                )
                objs.update(**dict_data)

                insert_ads = request.POST.get('insert_ads')  # 是否显示名片 显示报名
                if insert_ads:
                    obj = objs[0]
                    insert_ads = json.loads(insert_ads)
                    title = insert_ads.get('title')
                    plugin_id = insert_ads.get('id')
                    if title and plugin_id:
                        obj.plugin_report_id = plugin_id
                        obj.save()

                # 标签列表
                tags_id_list = json.loads(request.POST.get('tags_id_list')) if request.POST.get('tags_id_list') else []
                if tags_id_list:
                    objs[0].tags = tags_id_list

                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    elif request.method == 'GET':

        # 获取文章标签
        if oper_type == 'article_tags':
            field_dict = {
                'tag_id': '',
                'name': '__contains',  # 标签搜索
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            company_id = models.zgld_editor.objects.get(id=user_id).company_id

            tag_list = models.zgld_article_tag.objects.filter(user__company_id=company_id).values('id', 'name')
            tag_data = list(tag_list)

            response.code = 200
            response.data = {
                'ret_data': tag_data,
                'data_count': tag_list.count(),
            }

        # 查询报名插件
        elif oper_type == 'plugin_list':
            forms_obj = ReportSelectForm(request.GET)
            if forms_obj.is_valid():
                company_id = models.zgld_editor.objects.get(id=user_id).company_id
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')  #

                field_dict = {
                    'id': '',
                    'user__company_id': company_id,
                }

                q = conditionCom(request, field_dict)

                objs = models.zgld_plugin_report.objects.select_related('user').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    print('current_page -->', current_page)
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 获取所有数据
                ret_data = []

                # 获取第几页的数据
                for obj in objs:

                    read_count = obj.read_count
                    report_customer_objs = models.zgld_report_to_customer.objects.select_related('user',
                        'activity').filter(
                        activity_id=obj.id)
                    join_num = report_customer_objs.count()
                    if read_count == 0:
                        convert_pr = 0
                    else:
                        convert_pr = format(float(join_num) / float(read_count), '.2f')

                    ret_data.append({
                        'id': obj.id,
                        'belong_user_id': obj.user.id,
                        'belong_user': obj.user.username,
                        # 广告位
                        'ad_slogan': obj.ad_slogan,  # 广告语
                        'sign_up_button': obj.sign_up_button,  # 报名按钮
                        # 报名页
                        'title': obj.title,  # 活动标题
                        'read_count': read_count,  # 阅读数量
                        'join_num': join_num,  # 参与人数
                        'convert_pr': convert_pr,  # 转化率
                        # 'name_list' :name_list_data,
                        'leave_message': obj.leave_message,
                        'introduce': obj.introduce,  # 活动说明
                        'is_get_phone_code': obj.is_get_phone_code,  # 是否获取手机验证码
                        'skip_link': obj.skip_link,  # 跳转链接
                        'create_date': obj.create_date.strftime("%Y-%m-%d %H:%M")
                    })

                response.code = 200
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

        # 提交文章
        elif oper_type == 'submit_article':
            form_objs = SubmitArticleForm({'o_id':o_id})
            if form_objs.is_valid():
                response.code = 200
                response.msg = '提交成功'
            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


















