from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from zhugeproject.forms.gongneng_verify import AddForm, UpdateForm, SelectForm
from publickFunc.condition_com import conditionCom
import json
from zhugeproject.publick import xuqiu_or_gongneng_log


# 数据的展示
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def gongneng_select(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            print('验证成功')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            order = request.GET.get('order', 'id')

            field_dict = {
                'item_name':'',
                'create_time':'',
                'oper_user':'__contains',
                'is_function':'',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            # 获取所有数据
            objs = models.ProjectFunction.objects.select_related('oper_user','item_name').filter(
                q).order_by(order)
            count = objs.count()
            print('objs- --  ->',objs)
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []

            # 获取第几页的数据
            for obj in objs:
                ret_data.append({
                    'item_name': obj.item_name.item_name,
                    'create_time': obj.create_time,
                    'oper_user__username': obj.oper_user.username,
                    'is_function': obj.is_function,
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
@account.is_token(models.ProjectUserProfile)
def gongneng_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')
        username_log = models.ProjectUserProfile.objects.get(id=user_id)
        if oper_type == "add":
            print('开始入库')
            forms_obj = AddForm(request.POST)
            if forms_obj.is_valid():
                print('forms_obj.forms_obj -->',forms_obj.cleaned_data)
                models.ProjectFunction.objects.create(**forms_obj.cleaned_data)
                remark = '{}添加新功能：{}'.format(username_log, forms_obj.data['name'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 200
                response.msg = "添加成功"

            else:
                remark = '{}添加:{}新功能,FORM验证未通过'.format(username_log,forms_obj.data['name'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            objs = models.ProjectFunction.objects.filter(id=o_id)
            if objs:
                for obj in objs:
                    name = obj.name
                    print('name---->',name)
                    remark = '{}删除功能:{}成功,ID为{}'.format(username_log, name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                remark = '{}删除功能ID失败:{},功能ID不存在'.format(username_log, o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 302
                response.msg = '功能ID不存在'

        elif oper_type == "update":
            form_data = {
                'tid': o_id,
                'item_name_id':request.POST.get('item_name_id'),
                'name':request.POST.get('name')
            }
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                objs = models.ProjectFunction.objects.filter(id=o_id)
                if objs:
                    objs.update(
                        item_name_id = forms_obj.cleaned_data['item_name_id'],
                        name=forms_obj.cleaned_data['name']
                    )
                    remark = '{}修改功能{},ID:{}'.format(username_log, forms_obj.data['name'], o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    remark = '{}修改功能{}失败ID不存在,ID为:{}'.format(username_log, forms_obj.data['name'], o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    response.code = 303
                    response.msg = '修改ID不存在'
            else:
                remark = '{}修改功能ID为{}FORM验证失败}'.format(username_log, o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        user_id = request.GET.get('user_id')
        username_log = models.ProjectUserProfile.objects.get(id=user_id)
        remark = '{}请求操作功能失败请求异常'.format(username_log)
        xuqiu_or_gongneng_log.gongneng_log(request, remark)
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
