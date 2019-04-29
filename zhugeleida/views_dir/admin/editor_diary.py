from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from bs4 import BeautifulSoup
from zhugeleida.forms.admin.editor_diary_verify import diaryAddForm, diaryUpdateForm, DeleteDiaryForm, SelectForm, SubmitDiaryForm
from django.db.models import Q, Sum, Count
from publicFunc.condition_com import conditionCom
import json,datetime


@csrf_exempt
@account.is_token(models.zgld_editor)
def editor_diary(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')

        field_dict = {
            'id': '',
            'title': '__contains',
            'case_id': '',
            'status': '',
            'customer_name': '__contains',
        }
        q = conditionCom(request, field_dict)
        objs = models.zgld_editor_diary.objects.filter(q).order_by(order)
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

        status_choices = []
        for i in models.zgld_editor_diary.status_choices:
            status_choices.append({
                'id': i[0],
                'name': i[1]
            })
        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
            'data_count': count,
            'status_choices': status_choices
        }

    else:
        response.code = 301
        response.msg = "验证未通过"
        response.data = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_editor)
def editor_diary_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_obj = models.zgld_editor.objects.get(id=user_id)

    if request.method == "POST":

        form_data = {
            'diary_id':o_id,
            'company_id': user_obj.company_id,
            'case_id': request.POST.get('case_id'),  # 日记列表ID
            'title': request.POST.get('title'),  # 日记标题
            'diary_date': request.POST.get('diary_date'),  # 日记发布时间
            'content': request.POST.get('content'),  # 日记内容
            'cover_show_type': request.POST.get('cover_show_type'),  # (1,'封面展示图片'),  (2,'封面展示视频'),
            'cover_picture': request.POST.get('cover_picture')  # 普通日记 上传(图片/视频)
        }

        # 删除-日记
        if oper_type == "delete":
            delete_form_objs = DeleteDiaryForm({'diary_id':o_id})
            if delete_form_objs.is_valid():
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 301
                response.msg = json.loads(delete_form_objs.errors.as_json())

        # 修改-日记
        elif oper_type == 'update':
            forms_obj = diaryUpdateForm(form_data)
            if forms_obj.is_valid():
                forms_data = forms_obj.cleaned_data
                case_id, case_type = forms_data.get('case_id')
                content = forms_data.get('content')
                diary_objs = models.zgld_editor_diary.objects.filter(id=o_id)
                diary_objs.update(
                    user_id = user_id,
                    title = forms_data.get('title'),
                    diary_date = forms_data.get('diary_date'),
                    content = content,
                    cover_show_type = forms_data.get('cover_show_type')
                )
                cover_picture = forms_obj.cleaned_data.get('cover_picture')
                if int(case_type) == 1:  # 普通案例
                    diary_objs.update(cover_picture = json.dumps(json.loads(cover_picture)))

                else:
                    _cover_picture = []
                    soup = BeautifulSoup(content, 'html.parser')

                    img_tags = soup.find_all('img')
                    for img_tag in img_tags:
                        data_src = img_tag.attrs.get('src')
                        if data_src:
                            # 判断是否上传的图片  防止设为表情为封面
                            if 'tianyan.zhugeyingxiao.com' in data_src or 'statics' in data_src:
                                print(data_src)
                                _cover_picture.append(data_src)
                        if len(_cover_picture) >= 9:
                            break
                    diary_objs.update(cover_picture = json.dumps(_cover_picture))

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 增加-日记
        elif oper_type == "add":
            forms_obj = diaryAddForm(form_data)
            if forms_obj.is_valid():
                forms_data = forms_obj.cleaned_data
                case_id, case_type = forms_data.get('case_id')
                obj = models.zgld_editor_diary.objects.create(
                    user_id=user_id,
                    case_id=case_id,
                    title=forms_data.get('title'),
                    diary_date=forms_data.get('diary_date'),
                    content=forms_data.get('content'),
                    cover_show_type=forms_data.get('cover_show_type'),
                )
                cover_picture = forms_data.get('cover_picture')
                content = forms_data.get('content')

                if int(case_type) == 1: # 普通日记
                    obj.cover_picture = json.dumps(json.loads(cover_picture))
                    obj.save()

                else: # 时间轴日记
                    if cover_picture and len(json.loads(cover_picture)) > 0: # 如果上传了 封面
                        cover_picture = json.loads(cover_picture)
                        obj.cover_picture = json.dumps(cover_picture)
                    else:
                        _cover_picture = []
                        soup = BeautifulSoup(content, 'html.parser')

                        img_tags = soup.find_all('img')
                        for img_tag in img_tags:
                            data_src = img_tag.attrs.get('src')
                            if data_src:
                                if 'tianyan.zhugeyingxiao.com' in data_src or 'statics' in data_src:  # 判断是否上传的图片  防止设为表情为封面
                                    print(data_src)
                                    _cover_picture.append(data_src)
                            if len(_cover_picture) >= 9:
                                break

                        obj.cover_picture =  json.dumps(_cover_picture)
                    obj.save()

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        # 提交日记
        if oper_type == 'submit_diary':
            submit_form_objs = SubmitDiaryForm({'diary_id': o_id})
            if submit_form_objs.is_valid():
                response.code = 200
                response.msg = '提交成功'
            else:
                response.code = 301
                response.msg = json.loads(submit_form_objs.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'
    return JsonResponse(response.__dict__)
