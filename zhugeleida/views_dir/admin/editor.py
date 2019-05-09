from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.editor_verify import AddForm, UpdateForm, SelectForm, LoginForm, AuditArticleForm, \
    AuditCaseForm, AuditDiaryForm
from publicFunc.condition_com import conditionCom
from zhugeleida.public.common import create_qrcode
from zhugeleida.views_dir.gongzhonghao.user_gongzhonghao_auth import create_gongzhonghao_yulan_auth_url
from django.db.models import F
from bs4 import BeautifulSoup
import json, base64, datetime, random

# 员工管理查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def editor(request):
    response = Response.ResponseObj()
    form_objs = SelectForm(request.GET)
    if form_objs.is_valid():
        user_id = request.GET.get('user_id')
        current_page = form_objs.cleaned_data['current_page']
        length = form_objs.cleaned_data['length']
        company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
        field_dict = {
            'id': '',
            'user_name': '__contains',
            'create_date': '',
        }

        q = conditionCom(request, field_dict)
        objs = models.zgld_editor.objects.filter(q, is_delete=False, company_id=company_id).order_by('-create_date')
        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        data_list = []
        for obj in objs:
            data_list.append({
                'id':obj.id,
                'status_id': obj.status,
                'status': obj.get_status_display(),
                'phone': obj.phone,
                'position': obj.position,
                'user_name': obj.user_name,
                'login_user': obj.login_user,
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'data_list': data_list,
            'count': count,
        }
        response.note = {
            'data_list':{
                'status_id': '该员工状态ID',
                'status': '员工状态',
                'phone': '电话',
                'position': '职位',
                'user_name': '备注名',
                'login_user': '登录用户名',
            },
            'count':'总数',
        }

    else:
        response.code = 301
        response.msg = json.loads(form_objs.errors.as_json())
    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def editor_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
    company_id = user_obj.company_id


    if request.method == "POST":
        editor_data = {
            'company_id': user_obj.company_id,  # 公司ID
            'login_user': request.POST.get('login_user'),  # 登录账号
            'user_name': request.POST.get('user_name'),  # 备注
            'password': request.POST.get('password'),  # 密码
            'phone': request.POST.get('phone'),  # 电话
            'position': request.POST.get('position'),  # 职位
        }

        audit_data = {
            'status': request.POST.get('status'),
            'reason_rejection': request.POST.get('reason_rejection')# 驳回理由
        }

        # 添加员工(编辑)
        if oper_type == "add":
            forms_obj = AddForm(editor_data)
            if forms_obj.is_valid():
                models.zgld_editor.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = '创建成功'
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除员工
        elif oper_type == "delete":
            objs = models.zgld_editor.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                if obj.company_id == user_obj.company_id:
                    objs.update(
                        is_delete=True
                    )
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 301
                    response.msg = '权限不足'
            else:
                response.code = 302
                response.msg = '客户不存在'

        # 修改员工
        elif oper_type == "update":
            editor_data['o_id'] = o_id
            forms_obj = UpdateForm(editor_data)
            if forms_obj.is_valid():
                objs = models.zgld_editor.objects.filter(id=o_id)
                if objs:
                    form_cleaned_data = forms_obj.cleaned_data
                    objs.update(
                        # login_user=form_cleaned_data.get('login_user'),
                        user_name=form_cleaned_data.get('user_name'),
                        position=form_cleaned_data.get('position'),
                        phone=form_cleaned_data.get('phone'),
                    )
                    response.code = 200
                    response.msg = '修改成功'

                else:
                    response.code = 301
                    response.msg = '该用户不存在'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 审核文章
        elif oper_type == 'audit_article':
            form_objs = AuditArticleForm(audit_data)
            if form_objs.is_valid():
                status = form_objs.cleaned_data.get('status')
                obj = models.zgld_editor_article.objects.get(id=o_id)
                if status == 4:
                    if not models.zgld_article.objects.filter(title=obj.title, company_id=company_id).exclude(status=3):

                        article_obj = models.zgld_article.objects.create(
                            user_id=user_id,
                            company_id=user_obj.company_id,
                            title=obj.title,
                            summary=obj.summary,
                            status=1,  # 未发状态
                            source=1,  # 原创作品
                            content=obj.content,
                            cover_picture=obj.cover_picture,  # 封面
                            insert_ads=obj.insert_ads,  # 插入广告类型 记录
                            plugin_report_id=obj.plugin_report_id,  # 报名插件ID
                            is_auto_tagging=obj.is_auto_tagging,  # 是否打标签
                            tags_time_count=obj.tags_time_count,  # 实现几秒打标签
                        )
                        tags_list = [i.get('id') for i in obj.tags.all().values('id')]
                        print('i-------------> ', tags_list)
                        article_obj.tags = tags_list

                        data = {
                            'company_id': user_obj.company_id,
                            'article_id': article_obj.id,
                            'uid': '',
                            'pid': '',
                            'level': 1,

                        }
                        print('--------------------------------------------->', user_obj.company_id)
                        if models.zgld_xiaochengxu_app.objects.filter(company_id=user_obj.company_id):
                            auth_url_ret = create_gongzhonghao_yulan_auth_url(data)
                            authorize_url = auth_url_ret.data.get('authorize_url')

                            qrcode_data = {
                                'url': authorize_url,
                                'article_id': obj.id,
                            }
                            response_ret = create_qrcode(qrcode_data)
                            pre_qrcode_url = response_ret.data.get('pre_qrcode_url')
                            article_obj.qrcode_url = pre_qrcode_url

                            article_obj.save()

                        response.code = 200
                        response.msg = '该文章已被审核'
                    else:
                        status = 2
                        response.code = 301
                        response.msg = '标题重复'
                else:
                    response.code = 200
                    response.msg = '该文章已驳回'
                obj.reason_rejection = audit_data.get('reason_rejection')
                obj.status = status
                obj.save()

            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 审核案例
        elif oper_type == 'audit_case':
            form_objs = AuditCaseForm(audit_data)
            if form_objs.is_valid():
                status = form_objs.cleaned_data.get('status')
                obj = models.zgld_editor_case.objects.get(id=o_id)
                if status == 4: # 通过
                    if not models.zgld_case.objects.filter(case_name=obj.case_name,  company_id=company_id):
                        tags_list = [i.get('id') for i in obj.tags.all().values('id')]
                        tags_objs = models.zgld_case_tag.objects.filter(id__in=tags_list)
                        tags_objs.update(
                            use_number=F('use_number') + 1
                        )
                        case_obj = models.zgld_case.objects.create(
                            user_id=user_id,
                            company_id=company_id,
                            case_name=obj.case_name,
                            customer_name=obj.customer_name,
                            headimgurl=obj.headimgurl,
                            cover_picture=obj.cover_picture,
                            status=2,
                            become_beautiful_cover=obj.become_beautiful_cover,
                            case_type=obj.case_type
                        )
                        case_obj.tags = tags_list
                        case_obj.save()
                        response.code = 200
                        response.msg = '审核已通过'
                    else:
                        status = 2
                        response.code = 301
                        response.msg = '案例名称已存在'
                else:
                    response.code = 200
                    response.msg = '本案例已驳回'

                obj.reason_rejection = audit_data.get('reason_rejection')
                obj.status = status
                obj.save()
            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 审核日记
        elif oper_type == 'audit_diary':
            form_objs = AuditDiaryForm(audit_data)
            if form_objs.is_valid():
                status = form_objs.cleaned_data.get('status')
                obj = models.zgld_editor_diary.objects.get(id=o_id)
                case_obj = models.zgld_editor_case.objects.get(id=obj.case_id)
                if case_obj.status == 4:
                    if status == 4:  # 通过
                        if not models.zgld_diary.objects.filter(title=obj.title, company_id=company_id):

                            objs = models.zgld_case.objects.filter(
                                case_name=obj.case.case_name,
                                company_id=company_id
                            )

                            diary_obj = models.zgld_diary.objects.create(
                                user_id=user_id,
                                company_id=company_id,
                                case_id=objs[0].id,
                                title=obj.title,
                                diary_date=obj.diary_date,
                                content=obj.content,
                                status=1,
                                cover_show_type=obj.cover_show_type
                            )
                            case_type = int(obj.case.case_type)

                            cover_picture = obj.cover_picture
                            print('cover_picture-------> ', cover_picture)
                            if case_type == 1:  # 普通日记
                                diary_obj.cover_picture = json.dumps(json.loads(cover_picture))
                                diary_obj.save()

                            else:  # 时间轴日记
                                if cover_picture and len(json.loads(cover_picture)) > 0:  # 如果上传了 封面
                                    cover_picture = json.loads(cover_picture)
                                    diary_obj.cover_picture = json.dumps(cover_picture)
                                else:
                                    _cover_picture = []
                                    soup = BeautifulSoup(obj.content, 'html.parser')

                                    img_tags = soup.find_all('img')
                                    for img_tag in img_tags:
                                        data_src = img_tag.attrs.get('src')
                                        if data_src:
                                            if 'tianyan.zhugeyingxiao.com' in data_src or 'statics' in data_src:  # 判断是否上传的图片  防止设为表情为封面
                                                print(data_src)
                                                _cover_picture.append(data_src)
                                        if len(_cover_picture) >= 9:
                                            break

                                    diary_obj.cover_picture = json.dumps(_cover_picture)
                                diary_obj.save()

                            case_objs = models.zgld_case.objects.filter(id=obj.case_id)  # 该 日记列表 更新时间
                            if case_objs:
                                case_objs.update(
                                    update_date=datetime.datetime.now()
                                )
                            response.code = 200
                            response.msg = '审核已通过'

                        else:
                            status = 2
                            response.code = 301
                            response.msg = '该日记名称已存在'
                    else:
                        response.code = 200
                        response.msg = '本案例已驳回'
                    obj.reason_rejection = audit_data.get('reason_rejection')
                    obj.status = status
                    obj.save()
                else:
                    response.code = 301
                    response.msg = '请先审核该日记案例'
            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 生成账号
        elif oper_type == 'generate_account':
            num = 1
            msg = '生成成功'
            account = ''
            while True:
                num += 1
                if num >= 50:
                    msg = '网络异常请稍后重试'
                    break

                account = random.randint(10000000000, 99999999999)
                objs = models.zgld_editor.objects.filter(login_user=account)
                if objs:
                    continue
                else:
                    break

            response.code = 200
            response.msg = msg
            response.data = {
                'account': account
            }


    elif request.method == 'GET':
        status_choices = []
        for i in models.zgld_editor_article.status_choices: # 可选状态
            if i[0] != 1:
                status_choices.append({
                    'id': i[0],
                    'name': i[1]
                })

        # 查询提交的文章
        if oper_type == 'get_article':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'title': '__contains',
                }
                q = conditionCom(request, field_dict)

                status = request.GET.get('status')
                if not status:
                    status = [2, 3, 4]
                else:
                    status = [status]
                print('status, q-------------> ', status, q, company_id, )
                objs = models.zgld_editor_article.objects.filter(
                    q,
                    status__in=status,
                    user__company_id=company_id,
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
                    })

                    if id:
                        data_list[0]['summary'] = obj.summary  # 文章标题
                        data_list[0]['content'] = obj.content  # 文章内容
                        data_list[0]['is_auto_tagging'] = obj.is_auto_tagging  # 文章是否开启打标签
                        data_list[0]['tags_time_count'] = obj.tags_time_count  # 达到几秒实现打标签
                        data_list[0]['insert_ads'] = json.loads(obj.insert_ads)  # 植入广告类型

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'data_list': data_list,
                    'status_choices': status_choices,
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 查询提交的案例
        elif oper_type == 'get_case':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'title': '__contains',
                }
                q = conditionCom(request, field_dict)

                status = request.GET.get('status')
                if not status:
                    status = [2, 3, 4]
                else:
                    status = [status]

                objs = models.zgld_editor_case.objects.filter(
                    q,
                    user__company_id=user_obj.company_id,
                    status__in=status
                ).order_by(order)

                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    cover_picture = obj.cover_picture
                    if cover_picture:
                        cover_picture = json.loads(cover_picture)

                    become_beautiful_cover = []
                    if obj.become_beautiful_cover:
                        become_beautiful_cover = json.loads(obj.become_beautiful_cover)

                    poster_cover = []
                    if obj.poster_cover:
                        poster_cover = json.loads(obj.poster_cover)

                    tag_list = list(obj.tags.values('id', 'name'))
                    ret_data.append({
                        'case_id': obj.id,
                        'case_name': obj.case_name,
                        'customer_name': obj.customer_name,
                        'headimgurl': obj.headimgurl,
                        'cover_picture': cover_picture,
                        'status': obj.status,
                        'status_text': obj.get_status_display(),
                        'tag_list': tag_list,
                        'case_type': obj.case_type,
                        'poster_cover': poster_cover,
                        'become_beautiful_cover': become_beautiful_cover,
                        'case_type_text': obj.get_case_type_display(),
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'status_choices': status_choices
                }

        # 查询提交的日记
        elif oper_type == 'get_diary':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')

                field_dict = {
                    'id': '',
                    'title': '__contains',
                    'case_id': '',
                    'customer_name': '__contains',
                }
                q = conditionCom(request, field_dict)

                status = request.GET.get('status')
                if not status:
                    status = [2, 3, 4]
                else:
                    status = [status]
                objs = models.zgld_editor_diary.objects.filter(
                    q,
                    user__company_id=company_id,
                    status__in=status
                ).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                id = request.GET.get('id')
                for obj in objs:
                    cover_picture = []
                    if obj.cover_picture:
                        cover_picture = json.loads(obj.cover_picture)

                    poster_cover = []
                    if obj.poster_cover:
                        poster_cover = json.loads(obj.poster_cover)

                    ret_data.append({
                        'diary_id': obj.id,
                        'case_id': obj.case_id,
                        'title': obj.title,
                        'status': obj.status,
                        'status_text': obj.get_status_display(),
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                    })
                    if id:
                        ret_data[0]['diary_date'] = obj.diary_date.strftime('%Y-%m-%d') if obj.diary_date else ''
                        ret_data[0]['cover_picture'] = cover_picture
                        ret_data[0]['content'] = obj.content
                        ret_data[0]['cover_show_type'] = obj.cover_show_type
                        ret_data[0]['cover_show_type_text'] = obj.get_cover_show_type_display()
                        ret_data[0]['poster_cover'] = poster_cover
                        ret_data[0]['summary'] = obj.summary
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'status_choices': status_choices
                }

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)







# 编辑登录
@csrf_exempt
def editor_login(request):
    response = Response.ResponseObj()
    form_objs = LoginForm(request.POST)
    if form_objs.is_valid():
        obj = form_objs.cleaned_data.get('login_user')

        gzh_notice_qrcode = ''
        gzh_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=obj.company_id)
        if gzh_objs:
            gzh_notice_qrcode = gzh_objs[0].gzh_notice_qrcode

        response.code = 200
        response.msg = '登录成功'
        response.data = {
            'login_user':obj.login_user,
            'token':obj.token,
            'company_id':obj.company_id,
            'company__name':obj.company.name,
            'user_id':obj.id,
            'weChatQrCode':obj.company.weChatQrCode,
            'gzh_notice_qrcode':gzh_notice_qrcode,
        }
        response.note = {
            'login_user': '登录用户',
            'token': '用户token',
            'company_id': '公司ID',
            'company__name': '公司名称',
            'user_id': '用户ID',
        }

    else:
        response.code = 301
        response.msg = json.loads(form_objs.errors.as_json())

    return JsonResponse(response.__dict__)






