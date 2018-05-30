from zhugeproject import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from zhugeproject.forms.system_verify import AddForm, UpdateForm, SelectForm
from publicFunc.condition_com import conditionCom
import json
from zhugeproject.public import insert_log


# 数据的展示
@csrf_exempt
@account.is_token(models.project_UserProfile)
def system(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            order = request.GET.get('order', 'id')

            field_dict = {
                'id': '',
                'item_name': '',  # 产品/项目名
                'is_section': '',  # 哪个技术部
                'finish_status': '',  # 项目状态
                'create_time': '',  # 创建时间
                'predict_time': '',  # 预计结束时间
                'over_time': '',  # 结束时间
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            # 获取所有数据
            objs = models.project_System.objects.filter(
                q).order_by(order)
            count = objs.count()
            print('objs- --  ->', objs)
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []

            # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'item_name': obj.item_name,
                    'is_section': obj.is_section,
                    'finish_status': obj.finish_status,
                    'create_time': obj.create_time,
                    'predict_time': obj.predict_time,
                    'over_time': obj.over_time,
                })

            response.code = 200
            response.data = {
                'ret_data': ret_data,
                'data_count': count
            }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


#  增删改
@csrf_exempt
@account.is_token(models.project_UserProfile)
def system_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            user_id = request.GET.get('user_id')
            username_log = models.project_UserProfile.objects.get(id=user_id)

            forms_obj = AddForm(request.POST)
            if forms_obj.is_valid():
                models.project_System.objects.create(**forms_obj.cleaned_data)

                remark = '{}添加项目：{}'.format(username_log, request.POST.get('name'))
                insert_log.gongneng_log(request, remark)

                response.code = 200
                response.msg = "添加成功"
            else:
                remark = '{}添加项目:{},FORM验证未通过'.format(username_log, request.POST.get('name'))
                insert_log.gongneng_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            username_log = models.project_UserProfile.objects.get(id=user_id)
            objs = models.project_System.objects.filter(id=o_id)
            if objs:
                for obj in objs:
                    name = obj.name
                    remark = '{}删除项目:{}成功,ID为{}'.format(username_log, name, o_id)
                    insert_log.gongneng_log(request, remark)

                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                remark = '{}删除项目ID失败:{},项目ID不存在'.format(username_log, o_id)
                insert_log.gongneng_log(request, remark)
                response.code = 302
                response.msg = '项目ID不存在'

        elif oper_type == "update":
            user_id = request.GET.get('user_id')
            username_log = models.project_UserProfile.objects.get(id=user_id)
            form_data = {
                'tid': o_id,
                'name': request.POST.get('name'),
                'finish_status': request.POST.get('finish_status'),
                'create_time': request.POST.get('create_time'),
                'predict_time': request.POST.get('predict_time'),
                'over_time': request.POST.get('over_time'),
            }
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                objs = models.project_System.objects.filter(id=o_id)
                if objs:
                    objs.update(
                        name=forms_obj.cleaned_data['name'],
                        finish_status=forms_obj.cleaned_data['finish_status'],
                        create_time=forms_obj.cleaned_data['create_time'],
                        predict_time=forms_obj.cleaned_data['predict_time'],
                        over_time=forms_obj.cleaned_data['over_time'],
                    )
                    remark = '{}修改项目{},ID:{}'.format(username_log, form_data['name'], o_id)
                    insert_log.gongneng_log(request, remark)

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    remark = '{}修改项目{}失败ID不存在,ID为:{}'.format(username_log, form_data['name'], o_id)
                    insert_log.gongneng_log(request, remark)

                    response.code = 303
                    response.msg = '修改ID不存在'
            else:
                remark = '{}修改项目ID为:{}FORM验证失败'.format(username_log, o_id)
                insert_log.gongneng_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        user_id = request.GET.get('user_id')
        username_log = models.project_UserProfile.objects.get(id=user_id)
        remark = '{}请求操作用户失败请求异常'.format(username_log)
        insert_log.gongneng_log(request, remark)
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
