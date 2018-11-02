from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.followup_verify import FollowInfoAddForm, FollowInfoSelectForm
import datetime
import json

from publicFunc.condition_com import conditionCom



#分页获取用户跟进-聊天的信息
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def follow_info(request, ):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        forms_obj = FollowInfoSelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')

            field_dict = {
                'user_id': '',
                'customer_id': ''
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            customer_flowup_objs = models.zgld_user_customer_belonger.objects.filter(q).order_by(order)  # 查询出有user用户关联的信心表

            objs = models.zgld_follow_info.objects.filter(user_customer_flowup_id=customer_flowup_objs[0].id).order_by(order)

            count = objs.count()
            ret_list = []
            if objs:
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                for obj in objs:

                    ret_list.append({
                        'user_customer_flowup__customer__headimgurl':  customer_flowup_objs[0].customer.headimgurl,
                        'user_customer_flowup__user__avatar' : customer_flowup_objs[0].user.avatar,
                        'user_customer_flowup__user_id': customer_flowup_objs[0].user_id,
                        'user_customer_flowup__customer_id' :  customer_flowup_objs[0].customer_id,
                        'follow_info': obj.follow_info,
                        'create_date': obj.create_date
                    })


                response.code = 200
                response.data = {
                    'ret_data': ret_list,
                    'data_count': count,
                }

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 用户跟进信息操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def follow_info_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加用户跟进信息
        if oper_type == "add":

            print('----request.POST---->>', request.POST)
            language_data = {
                'user_id': request.GET.get('user_id'),
                'customer_id': o_id,
                'follow_info': request.POST.get('follow_info'),
            }
            forms_obj = FollowInfoAddForm(language_data)
            if forms_obj.is_valid():
                now_time = datetime.datetime.now()
                user_id =  forms_obj.cleaned_data.get('user_id')
                customer_id =  forms_obj.cleaned_data.get('customer_id')
                follow_info =  forms_obj.cleaned_data.get('follow_info')

                objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id,customer_id=customer_id)

                if objs:
                    objs.update(last_follow_time=now_time)

                    models.zgld_follow_info.objects.create(user_customer_flowup_id=objs[0].id,
                                                           follow_info=follow_info
                                                           )

                else:
                    response.code = 307
                    response.msg = "用户-客户关系表数据重复"

                    response.code = 200
                    response.msg = "添加成功"

            else:
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
