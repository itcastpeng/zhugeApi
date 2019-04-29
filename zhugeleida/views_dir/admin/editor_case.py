from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.editor_case_manage_verify import CaseAddForm, CaseUpdateForm, CaseDeleteForm, \
    CaseSelectForm, SubmitCaseForm
import json, datetime
from publicFunc.condition_com import conditionCom


@csrf_exempt
@account.is_token(models.zgld_editor)
def editor_case(request):
    response = Response.ResponseObj()
    forms_obj = CaseSelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')
        field_dict = {
            'id': '',
            'status': '',
            'customer_name': '__contains',
        }
        q = conditionCom(request, field_dict)

        objs = models.zgld_editor_case.objects.filter(q).order_by(order)
        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        ret_data = []
        for obj in objs:
            cover_picture = obj.cover_picture
            if cover_picture:
                cover_picture =  json.loads(cover_picture)

            become_beautiful_cover = []
            if obj.become_beautiful_cover:
                become_beautiful_cover = json.loads(obj.become_beautiful_cover)

            poster_cover = []
            if obj.poster_cover:
                poster_cover = json.loads(obj.poster_cover)

            tag_list = list(obj.tags.values('id', 'name'))
            ret_data.append({
                'case_id': obj.id,
                'case_name' : obj.case_name,
                'customer_name': obj.customer_name,
                'headimgurl': obj.headimgurl,
                'cover_picture' : cover_picture,
                'status': obj.status,
                'status_text':  obj.get_status_display(),
                'tag_list': tag_list,
                'case_type': obj.case_type,
                'poster_cover': poster_cover,
                'become_beautiful_cover': become_beautiful_cover,
                'case_type_text': obj.get_case_type_display(),
                # 'update_date': obj.update_date.strftime('%Y-%m-%d %H:%M:%S') if obj.update_date else '',
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
            })

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
            'data_count': count,
        }
        response.note = {
            'case_id': '案例ID',
            'case_name': '案例名称',
            'customer_name': '客户昵称',
            'headimgurl': '客户头像',
            'cover_picture': '案例封面图',
            'status': '案例当前状态ID',
            'status_text': '案例当前状态',
            'tag_list': '分类列表',
            'case_type': '案例类型ID',
            'poster_cover': '海报',
            'become_beautiful_cover': '变美图片',
            'case_type_text': '案例类型',
            'update_date':  '更新时间',
            'create_date':  '创建时间',
        }

    else:

        response.code = 301
        response.msg = "验证未通过"
        response.data = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_editor)
def editor_case_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_obj = models.zgld_editor.objects.get(id=user_id)
    company_id = user_obj.company_id

    if request.method == "POST":

        form_data = {
            'case_id':o_id,
            'case_name': request.POST.get('case_name'),  # 案例名称
            'company_id': company_id,  # 公司ID
            'customer_name':  request.POST.get('customer_name'),  # 客户名称
            'headimgurl':request.POST.get('headimgurl'),  # 客户头像
            'case_type': request.POST.get('case_type'),  # 判断是普通案例/时间轴案例
            'tags_id_list': request.POST.get('tags_id_list'),  # 标签列表
            'cover_picture': request.POST.get('cover_picture'),  # 封面图片
            'become_beautiful_cover': request.POST.get('become_beautiful_cover'),  # 变美图片
        }

        # 增加-案例
        if oper_type == "add":

            """
            普通案例： 列表页 不加 变美过程 封面图片
            时间轴案例: 创建列表页 加 变美过程 封面图片
            """

            forms_obj = CaseAddForm(form_data)
            if forms_obj.is_valid():
                form_data = forms_obj.cleaned_data
                obj = models.zgld_editor_case.objects.create(
                    user_id=user_id,
                    case_name=form_data.get('case_name'),
                    customer_name=form_data.get('customer_name'),
                    headimgurl=form_data.get('headimgurl'),
                    cover_picture=form_data.get('cover_picture'),
                    become_beautiful_cover=form_data.get('become_beautiful_cover'),
                    case_type=form_data.get('case_type')
                )
                obj.tags = form_data.get('tags_id_list')
                obj.save()

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改-案例
        elif oper_type == 'update':
            forms_obj = CaseUpdateForm(form_data)
            if forms_obj.is_valid():
                form_data = forms_obj.cleaned_data
                objs = models.zgld_editor_case.objects.filter(
                    id=form_data.get('case_id')
                )
                if objs:
                    objs.update(
                        case_name=form_data.get('case_name'),
                        customer_name=form_data.get('customer_name'),
                        headimgurl=form_data.get('headimgurl'),
                        cover_picture=form_data.get('cover_picture'),
                        case_type=form_data.get('case_type'),
                        become_beautiful_cover=form_data.get('become_beautiful_cover')
                    )
                    objs[0].tags = forms_obj.cleaned_data.get('tags_id_list')
                    objs[0].save()

                    response.code = 200
                    response.msg = "修改成功"

                else:
                    response.code = 302
                    response.msg = "案例不存在"
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除-案例
        elif oper_type == "delete":
            delete_form_obj = CaseDeleteForm({'case_id': o_id})
            if delete_form_obj.is_valid():
                response.code = 200
                response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = json.loads(delete_form_obj.errors.as_json())

    else:

        # 获取分类标签
        if oper_type == 'get_case_tags':
            objs = models.zgld_case_tag.objects.filter(
                company_id=company_id
            ).order_by('-use_number')

            data_list = []
            for obj in objs:
                data_list.append({
                    'id': obj.id,
                    'name': obj.name
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'data_list': data_list
            }

        # 提交案例
        elif oper_type == 'submit_case':
            submit_form_objs = SubmitCaseForm({'case_id':o_id})
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
