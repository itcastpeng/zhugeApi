from zhugeproject import models
from publickFunc import Response
from publickFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from publickFunc.condition_com import conditionCom
from zhugeproject.forms.quanxian_verify import AddForm, UpdateForm ,SelectForm
import json
from zhugeproject.publick import xuqiu_or_gongneng_log

models_name = 'ProjectQuanXian'
models_obj = getattr(models, models_name)
# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def quanxian_select(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_time')
            field_dict = {
                'id': '',
                'quanxian_name': '__contains',
                'create_time': '',
                'path':'',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.ProjectQuanXian.objects.filter(q).order_by(order)
            count = objs.count()
            print('objs -- -  >', objs)
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            #
            # # 返回的数据
            ret_data = []

            for obj in objs:
                # print('oper_user_username -->', oper_user_username)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'username': obj.quanxian_name,
                    'create_time': obj.create_time,
                    'path': obj.path,
                    # 'status': obj.get_status_display()
                })
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.ProjectUserProfile)
def quanxian_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            form_data = {
                'o_id': o_id,
                'path': request.POST.get('path'),
                'quanxian_name':request.POST.get('quanxian_name')
            }
            print("form_data -->", form_data)
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                del forms_obj.cleaned_data['o_id']
                print('forms_obj.cleaned_data-->', forms_obj.cleaned_data)
                models_obj.objects.filter(**forms_obj.cleaned_data)

                remark = '{}添加新权限：{}'.format(username_log, form_data['quanxian_name'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)
                response.code = 200
                response.msg = "添加成功"

            else:
                remark = '{}添加新权限:{},FORM验证未通过'.format(username_log, form_data['quanxian_name'])
                xuqiu_or_gongneng_log.gongneng_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            # 删除 ID
            objs = models_obj.objects.filter(id=o_id)
            if objs:
                for obj in objs:
                    name = obj.quanxian_name
                    remark = '{}删除权限:{}成功,ID为{}'.format(username_log, name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                remark = '{}删除权限ID失败:{},用户ID不存在'.format(username_log, o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)

                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":

            # 获取ID 用户名 及 角色
            form_data = {
                'o_id': o_id,
                'path': request.POST.get('path'),
                'quanxian_name': request.POST.get('quanxian_name'),
            }
            user_id = request.GET.get('user_id')
            username_log = models.ProjectUserProfile.objects.get(id=user_id)
            print('form_data --> ', form_data)

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                quanxian_name = forms_obj.cleaned_data['quanxian_name']
                path = forms_obj.cleaned_data['path']

                #  查询数据库  用户id
                user_obj = models_obj.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if user_obj:
                    user_obj.update(
                        quanxian_name=quanxian_name,
                        path=path,

                    )
                    remark = '{}修改权限{},ID:{}'.format(username_log, quanxian_name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    remark = '{}修改权限{}失败ID不存在,ID为:{}'.format(username_log, quanxian_name, o_id)
                    xuqiu_or_gongneng_log.gongneng_log(request, remark)

                    response.code = 303
                    response.msg = '修改ID不存在'

            else:
                remark = '{}修改权限ID为{}FORM验证失败'.format(username_log, o_id)
                xuqiu_or_gongneng_log.gongneng_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        user_id = request.GET.get('user_id')
        username_log = models.ProjectUserProfile.objects.get(id=user_id)
        remark = '{}请求操作权限失败请求异常'.format(username_log)
        xuqiu_or_gongneng_log.gongneng_log(request, remark)

        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
