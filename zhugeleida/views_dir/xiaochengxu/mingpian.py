from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom, action_record
from zhugeleida.forms.xiaochengxu.user_verify import UserAddForm, UserUpdateForm, UserSelectForm
import json
from django.db.models import Q
from django.db.models import F


# 展示单个的名片信息
@csrf_exempt
@account.is_token(models.zgld_customer)
def mingpian(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('uid')  # 用户 id
            customer_id = request.GET.get('customer_id')

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'company__name': '__contains',
            }

            q = conditionCom(request, field_dict)
            q.add(Q(**{'id': user_id}), Q.AND)

            global remark
            accesslog_obj = models.zgld_accesslog.objects.filter(user_id=user_id, action=1)
            action_count = accesslog_obj.count()
            if action_count == 0:
                remark = '首次查看你的名片,沟通从此刻开始'
            elif action_count == 2:
                remark = '查看你的名片第%s次,把握深度交流的机会' % (action_count)
            elif action_count == 3:
                remark = '查看你的名片第%s次,建议标注重点客户' % (action_count)
            elif action_count > 4:
                remark = '查看你的名片第%s次,成交在望' % (action_count)

            action_record(request, remark)
            models.zgld_userprofile.objects.filter(id=user_id).update(popularity=F('popularity') + 1)  # 查看的个数加1

            objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = {}
            is_up_down = ''
            for obj in objs:
                up_down_obj = models.zgld_up_down.objects.filter(user_id=obj.id,customer_id=customer_id)
                if up_down_obj:
                    is_up_down = up_down_obj[0].up

                ret_data = {
                    'id': obj.id,
                    'username': obj.username,
                    'avatar': obj.avatar,
                    'company': obj.company.name,
                    'address': obj.company.address or '',
                    'position': obj.position,
                    'email': obj.email or '',
                    'wechat': obj.wechat or '',  # 微信号
                    'mingpian_phone': obj.mingpian_phone or '',  # 名片手机号
                    'create_date': obj.create_date,  # 创建时间
                    'popularity': obj.popularity,    # 被查看多少次。
                    'praise': obj.praise,            # 点赞多少次
                    'forward': obj.forward,          # 转发多少次
                    'is_up_down' : is_up_down or False,
                    'sign' : obj.sign,               # 签名
                    # 'photo' : [
                    #     {id:1,img_url}
                    # ]

                }

            # 查询成功 返回200 状态码
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


# 展示全部的名片、记录各种动作到日志中
@csrf_exempt
@account.is_token(models.zgld_customer)
def mingpian_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        forms_obj = UserSelectForm(request.GET)

        if forms_obj.is_valid():
            if oper_type == 'calling':
                remark = '拨打您的手机'
                response = action_record(request, remark)

            if oper_type == 'save_phone':
                remark = '保存了您的电话,可以考虑拜访'
                response = action_record(request, remark)

            elif oper_type == 'praise':  # 点赞功能，觉得你靠谱
                user_id = request.GET.get('uid')  # 用户 id
                customer_id = request.GET.get('user_id')  # 客户 id

                updown_obj = models.zgld_up_down.objects.filter(
                    user_id=user_id,  # 被赞的用户
                    customer_id=customer_id,  # 赞或踩的客户
                )

                if not updown_obj:
                    updown_obj = models.zgld_up_down.objects.create(
                        user_id=user_id,  # 被赞的用户
                        customer_id=customer_id,  # 赞或踩的客户
                        up=True
                    )
                    remark = '觉得您非常靠谱'
                    response = action_record(request, remark)
                    models.zgld_userprofile.objects.filter(id=user_id).update(praise=F('praise') + 1)

                else:
                    praise_status = updown_obj[0].up
                    if praise_status == True:
                        remark = '取消了给你的靠谱评价'
                        updown_obj.update(up=False)
                        response = action_record(request, remark)
                        models.zgld_userprofile.objects.filter(id=user_id).update(praise=F('praise') - 1)

                    elif praise_status == False:
                        remark = '觉得您非常靠谱'
                        updown_obj.update(up=True)
                        response = action_record(request, remark)
                        models.zgld_userprofile.objects.filter(id=user_id).update(praise=F('praise') + 1)


            elif oper_type == 'forward':
                user_id = request.GET.get('uid')  # 用户 id

                remark = '转发了你的名片,你的人脉圈正在裂变'
                response = action_record(request, remark)
                models.zgld_userprofile.objects.filter(id=user_id).update(forward=F('forward') + 1)



        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

        if oper_type == "all":  # 获取所有的名片
            print('---request.GET-->>',request.GET)
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
                }

                q = conditionCom(request, field_dict)

                objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    source_obj = models.zgld_user_customer_belonger.objects.get(user_id=obj.id,
                                                                                customer_id=customer_id)

                    ret_data.append({
                        'id': obj.id,
                        'username': obj.username,
                        'source': source_obj.get_source_display(),
                        'avatar': obj.avatar,
                        'company': obj.company.name,
                        'position': obj.position,
                        'email': obj.email or '',
                        'mingpian_phone': obj.mingpian_phone or '',  # 名片手机号

                        'create_date': obj.create_date,              # 创建时间

                    })
                    #  查询成功 返回200 状态码
                print('---ret_data---->>',ret_data)

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

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
