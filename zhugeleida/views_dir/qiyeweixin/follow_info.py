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
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')

            field_dict = {
                'user_id': '',
                'customer_id': ''
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.zgld_user_customer_flowup.objects.filter(q).order_by(order)  # 查询出有user用户关联的信心表
            count = objs.count()
            if count == 1:
                objs = objs[0].zgld_follow_info_set.all()
                if length != 0:
                    print('current_page -->', current_page)
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                    ret_data  = objs.values('user_customer_flowup__customer__headimgurl',
                                                    'user_customer_flowup__user__avatar',
                                                    'user_customer_flowup__user__username',
                                                     'user_customer_flowup__user_id',
                                                     'user_customer_flowup__customer_id',
                                                    'follow_info', 'create_date')
                    ret_data_list  = list(ret_data)
                    ret_data_list.reverse()
                    response.code = 200
                    response.data = {
                        'ret_data': ret_data_list,
                        'data_count': objs.count(),
                    }
            else:
                response.code = 307
                response.msg = "用户客户关联数据重复"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def follow_info_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
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
                follow_data = {
                    "user_id": forms_obj.cleaned_data.get('user_id'),
                    "customer_id": forms_obj.cleaned_data.get('customer_id'),
                }
                obj = models.zgld_user_customer_flowup.objects.filter(**follow_data)
                obj_num = obj.count()

                if obj_num == 0:  # 判断关系表是否有记录。
                    follow_data['last_follow_time'] = now_time
                    models.zgld_user_customer_flowup.objects.create(**follow_data)

                elif obj_num == 1:
                    obj.update(last_follow_time=now_time)

                else:
                    response.code = 307
                    response.msg = "用户-客户关系表数据重复"

                if response.code != 307:
                    print('______obj.id______>>', obj[0].id, forms_obj.cleaned_data['follow_info'])
                    models.zgld_follow_info.objects.create(user_customer_flowup_id=obj[0].id,
                                                           follow_info=forms_obj.cleaned_data['follow_info'])
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
