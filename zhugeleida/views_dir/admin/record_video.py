from zhugeleida import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from django.db.models import Q
from zhugeleida.forms.admin.record_video_verify import SelectForm, VideoAddForm, VideoUpdateForm, VideoDeleteForm
import json, base64


# 文章管理查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def record_video(request):
    user_id = request.GET.get('user_id')
    company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')
        field_dict = {
            'id': '',
            'company_id': '',
            'classification_id': '',
            'user_id': '',
            'title': '__contains',
            'abstract': '__contains',
        }
        q = conditionCom(request, field_dict)
        objs = models.zgld_recorded_video.objects.filter(
            q,
            company_id=company_id,
        ).order_by(order)
        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        data_list = []
        for obj in objs:
            data_list.append({
                'id': obj.id,
                'classification_id': obj.classification_id,                         # 分类ID
                'classification_name': obj.classification.classification_name,      # 分类名称
                'company_id': obj.company_id,                                       # 公司ID
                'company_name': obj.company.name,                                   # 公司名称
                'user_id': obj.user_id,                                             # 创建人ID
                'user_name': obj.user.login_user,                                   # 创建人名称
                'title': obj.title,                                                 # 视频标题
                'abstract': obj.abstract,                                           # 视频摘要
                'video_url': obj.video_url,                                         # 封面链接
                'cover_photo': obj.cover_photo,                                     # 封面图片
                'expert_introduction': obj.expert_introduction,                     # 专家介绍
                'textual_interpretation': obj.textual_interpretation,               # 文字解读

                'whether_authority_expert': obj.whether_authority_expert,           # 是否打开权威专家
                'whether_consult_online': obj.whether_consult_online,               # 是否打开在线咨询
                'whether_previous_video': obj.whether_previous_video,               # 是否打开往期视频
                'whether_text_interpretation': obj.whether_text_interpretation,     # 是否打开文字解读
                'whether_verify_phone': obj.whether_verify_phone,                   # 是否验证短信
                'whether_writer_number': obj.whether_writer_number,                 # 是否写手机号
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),       # 文章创建时间
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'count': count,
            'data_list': data_list,
        }
        response.note = {
            'classification_id': '分类ID',
            'classification_name': '分类名称',
            'company_id': '公司ID',
            'company_name': '公司名称',
            'user_id': '创建人ID',
            'user_name': '创建人名称',
            'title': '视频标题',
            'video_url': '视频链接',
            'abstract': '视频摘要',
            'cover_photo': '封面图片',
            'expert_introduction': '专家介绍',
            'textual_interpretation': '文字解读',
            'whether_authority_expert':'是否打开权威专家',
            'whether_consult_online': '是否打开在线咨询',
            'whether_previous_video': '是否打开往期视频',
            'whether_text_interpretation': '是否打开文字解读',
            'whether_verify_phone': '是否验证短信',
            'whether_writer_number': '是否写手机号',
            'create_date': '文章创建时间'
        }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 编辑添加文章
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def record_video_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    company_id = models.zgld_admin_userprofile.objects.get(
        id=user_id
    ).company_id

    if request.method == "POST":

        form_data = {
            'user_id': user_id,
            'company_id': company_id,
            'o_id': o_id,

            'classification': request.POST.get('classification'),                                   # 分类ID
            'video_url':request.POST.get('video_url'),                                              # 视频链接
            'title':request.POST.get('title'),                                                      # 标题
            'abstract':request.POST.get('abstract'),                                                # 摘要
            'cover_photo':request.POST.get('cover_photo'),                                          # 封面图片
            'expert_introduction':request.POST.get('expert_introduction'),                          # 专家介绍
            'textual_interpretation':request.POST.get('textual_interpretation'),                    # 文字解读

            'whether_writer_number':request.POST.get('whether_writer_number', 0),                      # 是否写手机号
            'whether_verify_phone':request.POST.get('whether_verify_phone', 0),                        # 是否验证短信
            'whether_consult_online':request.POST.get('whether_consult_online', 0),                    # 是否打开在线咨询
            'whether_authority_expert':request.POST.get('whether_authority_expert', 0),                # 是否打开权威专家
            'whether_text_interpretation':request.POST.get('whether_text_interpretation', 0),          # 是否打开文字解读
            'whether_previous_video':request.POST.get('whether_previous_video', 0)                     # 是否打开往期视频
        }

        # 添加文章
        if oper_type == "add":
            forms_obj = VideoAddForm(form_data)
            if forms_obj.is_valid():
                form_clean_data = forms_obj.cleaned_data
                models.zgld_recorded_video.objects.create(
                    company_id=company_id,
                    user_id=user_id,
                    classification_id=form_clean_data.get('classification'),
                    video_url=form_clean_data.get('video_url'),
                    title = form_clean_data.get('title'),
                    abstract = form_clean_data.get('abstract'),
                    cover_photo = form_clean_data.get('cover_photo'),
                    expert_introduction = form_clean_data.get('expert_introduction'),
                    textual_interpretation = form_clean_data.get('textual_interpretation'),
                    whether_writer_number = form_clean_data.get('whether_writer_number'),
                    whether_verify_phone = form_clean_data.get('whether_verify_phone'),
                    whether_consult_online = form_clean_data.get('whether_consult_online'),
                    whether_authority_expert = form_clean_data.get('whether_authority_expert'),
                    whether_text_interpretation = form_clean_data.get('whether_text_interpretation'),
                    whether_previous_video = form_clean_data.get('whether_previous_video'),
                )
                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改文章
        elif oper_type == "update":
            forms_obj = VideoUpdateForm(form_data)
            if forms_obj.is_valid():
                form_clean_data = forms_obj.cleaned_data
                o_id = form_clean_data.get('o_id')

                objs = models.zgld_recorded_video.objects.filter(id=o_id)
                objs.update(
                    classification_id=form_clean_data.get('classification'),
                    video_url=form_clean_data.get('video_url'),
                    title=form_clean_data.get('title'),
                    abstract=form_clean_data.get('abstract'),
                    cover_photo=form_clean_data.get('cover_photo'),
                    expert_introduction=form_clean_data.get('expert_introduction'),
                    textual_interpretation=form_clean_data.get('textual_interpretation'),
                    whether_writer_number=form_clean_data.get('whether_writer_number'),
                    whether_verify_phone=form_clean_data.get('whether_verify_phone'),
                    whether_consult_online=form_clean_data.get('whether_consult_online'),
                    whether_authority_expert=form_clean_data.get('whether_authority_expert'),
                    whether_text_interpretation=form_clean_data.get('whether_text_interpretation'),
                    whether_previous_video=form_clean_data.get('whether_previous_video'),
                )

                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除文章
        elif oper_type == "delete":
            form_objs = VideoDeleteForm({'o_id': o_id})
            if form_objs.is_valid():
                o_id = form_objs.cleaned_data.get('o_id')
                models.zgld_recorded_video.objects.filter(id=o_id).delete()

                response.code = 200
                response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())


    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


















