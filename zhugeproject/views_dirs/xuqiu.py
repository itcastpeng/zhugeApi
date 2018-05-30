from zhugeproject import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from publicFunc.condition_com import conditionCom
from zhugeproject.forms.xuqiu_verify import AddForm, UpdateForm, SelectForm
import json
from zhugeproject.public import insert_log

models_xuqiu_name = 'project_Xuqiu'
models_xuqiu_obj = getattr(models, models_xuqiu_name)

models_userprofile_name = 'project_UserProfile'
models_userprofile_obj = getattr(models, models_userprofile_name)


# cerf  token验证 需求展示模块
@csrf_exempt
@account.is_token(models_userprofile_obj)
def xuqiu_select(request):
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
                'demand_user': '__contains',  # 需求人
                'is_system': '__contains',  # 属于哪个功能
                'create_time': '',
                'is_remark': '',  # 备注
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models_xuqiu_obj.objects.filter(q).order_by(order)
            count = objs.count()
            print('objs -- -  >', objs)
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            #
            # 返回的数据
            ret_data = []
            #
            for obj in objs:
                # print('oper_user_username -->', oper_user_username)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'demand_user': obj.demand_user.username,
                    'is_system': obj.is_system.name,
                    'create_time': obj.create_time,
                    'is_remark': obj.is_remark,
                })
                print('ret - - >', ret_data)
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


#  增删改 需求表
#  csrf  token验证
@csrf_exempt
@account.is_token(models_userprofile_obj)
def xuqiu_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            user_id = request.GET.get('user_id')
            username_log = models_userprofile_obj.objects.get(id=user_id)
            form_data = {
                'o_id': o_id,
                'demand_user_id': request.POST.get('demand_user_id'),
                'is_system_id': request.POST.get('is_system_id'),
                'is_remark': request.POST.get('is_remark')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data-->', forms_obj.cleaned_data)
                models_xuqiu_obj.objects.create(**forms_obj.cleaned_data)
                remark = '{}添加新需求：{}}'.format(username_log, form_data['is_remark'])
                insert_log.xuqiu_log(request, remark)
                response.code = 200
                response.msg = "添加成功"
            else:
                remark = '{}添加新需求:{},FORM验证未通过'.format(username_log, form_data['is_remark'])
                insert_log.xuqiu_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            user_id = request.GET.get('user_id')
            username_log = models_userprofile_obj.objects.get(id=user_id)
            xuqiu_objs = models_xuqiu_obj.objects.filter(id=o_id)
            if xuqiu_objs:
                for obj in xuqiu_objs:
                    name = obj.is_remark
                    remark = '{}删除需求:{}成功,ID为{}'.format(username_log, name, o_id)
                    insert_log.xuqiu_log(request, remark)
                    xuqiu_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                remark = '{}删除需求ID失败:{},用户ID不存在'.format(username_log, o_id)
                insert_log.xuqiu_log(request, remark)

                response.code = 302
                response.msg = '需求ID不存在'

        elif oper_type == "update":
            form_data = {
                'o_id': o_id,
                'demand_user_id': request.POST.get('demand_user_id'),
                'is_system_id': request.POST.get('is_system_id'),
                'is_remark': request.POST.get('is_remark')
            }
            user_id = request.GET.get('user_id')
            username_log = models_userprofile_obj.objects.get(id=user_id)
            print('form_data -  - -- > ', form_data)
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data 0- - - > ', forms_obj.cleaned_data)
                demand_user_id = forms_obj.cleaned_data['demand_user_id']
                is_system_id = forms_obj.cleaned_data['is_system_id']
                is_remark = forms_obj.cleaned_data['is_remark']
                #  查询数据库  用户id
                user_obj = models_xuqiu_obj.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if user_obj:
                    user_obj.update(
                        demand_user_id=demand_user_id,
                        is_system_id=is_system_id,
                        is_remark=is_remark
                    )
                    remark = '{}修改需求{},ID:{}'.format(username_log, forms_obj.data['is_remark'], o_id)
                    insert_log.xuqiu_log(request, remark)

                    response.code = 200
                    response.msg = "修改成功"


                else:
                    remark = '{}修改需求{}失败ID不存在,ID为:{}'.format(username_log, forms_obj.data['is_remark'], o_id)
                    insert_log.xuqiu_log(request, remark)

                    response.code = 303
                    response.msg = '修改ID不存在'

            else:
                remark = '{}修改需求ID为{}FORM验证失败'.format(username_log, o_id)
                insert_log.xuqiu_log(request, remark)

                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        user_id = request.GET.get('user_id')
        username_log = models_userprofile_obj.objects.get(id=user_id)
        remark = '{}请求操作需求失败请求异常'.format(username_log)
        insert_log.gongneng_log(request, remark)

        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
