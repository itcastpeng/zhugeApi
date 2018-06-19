from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom,action_record
from zhugeleida.forms.xiaochengxu.user_verify import UserAddForm, UserUpdateForm, UserSelectForm
import json


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_customer)
def mingpian(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('uid')  # 用户 id
            customer_id = request.GET.get('user_id')  # 客户 id

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'company__name': '__contains',
                'create_date': '',
                'last_login_date': '',

            }
            q = conditionCom(request, field_dict)

            print('order -->', order)
            print(models.zgld_userprofile.objects.all())
            objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            print('------------->>>', objs)
            ret_data = []
            for obj in objs:
                print('oper_user_username -->', obj)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'avatar': obj.avatar,
                    'company': obj.company.name,
                    'popularity': obj.popularity,
                    'praise': obj.praise,
                    'forward': obj.forward,
                })
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

            remark = '访问名片功能'
            models.zgld_accesslog.objects.create(
                user_id=user_id,
                customer_id=customer_id,
                remark=remark,
                action=1
            )
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_customer)
def mingpian_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            if oper_type == 'calling':
                remark = '拨打你的手机'
                ret_obj = action_record(request, remark)

                return JsonResponse(ret_obj.__dict__)


            elif oper_type == 'praise':  # 点赞功能，觉得你靠谱

                remark = '觉得您靠谱'
                response = Response.ResponseObj()
                user_id = request.GET.get('uid')  # 用户 id
                customer_id = request.GET.get('user_id')  # 客户 id
                action = request.GET.get('action')

                # obj = models.zgld_accesslog.objects.create(
                #     user_id=user_id,
                #     customer_id=customer_id,
                #     remark=remark,
                #     action=action
                # )

                obj = models.zgld_UpDown.objects.create(
                    user_id=user_id,         #被赞的用户
                    customer_id=customer_id, #赞或踩的客户
                    up=True
                )

                follow_objs = models.zgld_user_customer_flowup.objects.filter(user_id=user_id, customer_id=customer_id)
                if follow_objs.count() == 1:
                    obj.activity_time_id = follow_objs[0].id
                    follow_objs.update(last_activity_time=datetime.datetime.now())
                    obj.save()
                    follow_objs[0].save()
                    response.code = 200
                    response.msg = '记录日志成功'


                elif follow_objs.count() == 0:
                    flowup_create_obj = models.zgld_user_customer_flowup.objects.create(user_id=user_id,
                                                                                        customer_id=customer_id,
                                                                                        last_activity_time=datetime.datetime.now())
                    obj.activity_time_id = flowup_create_obj.id
                    obj.save()
                    response.code = 200
                    response.msg = '记录日志成功'

                else:
                    response.code = 301
                    response.msg = '用户-客户跟进信息-关系绑定表数据重复'

                return response



        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
