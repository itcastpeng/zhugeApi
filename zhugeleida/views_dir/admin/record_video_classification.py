from zhugeleida import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.record_video_verify import SelectForm, ClassificationAddForm, \
    ClassificationUpdateForm, ClassificationDeleteForm
from django.db.models import Q
import json, base64


# 视频分类查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def record_video_classification(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')
        field_dict = {
            'id': '',
            'classification_name': '__contains',
            'company_id': '',
        }
        q = conditionCom(request, field_dict)
        print(q)
        objs = models.zgld_recorded_video_classification.objects.filter(
            q,
            company_id=company_id
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
                'company_id': obj.company_id,       # 公司ID
                'company_name': obj.company.name,   # 公司名称
                'user_id': obj.user_id,             # 创建用户ID
                'login_user': obj.user.login_user,             # 创建用户名称
                'classification_name': obj.classification_name,  # 分类名称
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),  # 视频分类创建时间
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'count': count,
            'data_list': data_list,
        }
        response.note = {
            'company_id': '公司ID',
            'company_name': '公司名称',
            'user_id': '创建用户ID',
            'login_user': '创建用户名称',
            'classification_name': '分类名称',
            'create_date': '视频分类创建时间'
        }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 视频分类操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def record_video_classification_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    pub_user_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
    company_id = pub_user_obj.company_id
    if request.method == "POST":
        form_data = {
            'classification_name': request.POST.get('classification_name'),
            'o_id': o_id,
            'user_id': user_id,
            'company_id': company_id,
        }

        # 添加视频分类
        if oper_type == "add":
            forms_obj = ClassificationAddForm(form_data)
            if forms_obj.is_valid():
                classification_name = forms_obj.cleaned_data.get('classification_name')
                company_id = forms_obj.cleaned_data.get('company_id')
                models.zgld_recorded_video_classification.objects.create(
                    classification_name=classification_name,
                    user_id=user_id,
                    company_id=company_id
                )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改视频分类
        elif oper_type == 'update':
            forms_obj = ClassificationUpdateForm(form_data)
            if forms_obj.is_valid():
                classification_name = forms_obj.cleaned_data.get('classification_name')
                o_id = forms_obj.cleaned_data.get('o_id')
                models.zgld_recorded_video_classification.objects.filter(id=o_id).update(
                    classification_name=classification_name
                )
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除视频分类
        elif oper_type == 'delete':
            forms_obj = ClassificationDeleteForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data.get('o_id')
                models.zgld_recorded_video_classification.objects.filter(id=o_id).delete()
                response.code = 200
                response.msg = '删除成功'
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


















