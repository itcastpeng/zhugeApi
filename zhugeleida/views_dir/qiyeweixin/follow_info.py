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

            customer_flowup_objs = models.zgld_user_customer_flowup.objects.filter(q).order_by(order)  # 查询出有user用户关联的信心表
            objs = models.zgld_follow_info.objects.filter(user_customer_flowup_id=customer_flowup_objs[0].id).order_by(order)
            print('----objs -->>>>',objs[0].create_date)
            count = objs.count()
            ret_list = []
            if objs:
                if length != 0:
                    print('current_page -->', current_page)
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                for obj in objs:


                    # ret_list  = 'user_customer_flowup__customer__headimgurl',
                    #                                 'user_customer_flowup__user__avatar',
                    #                                 'user_customer_flowup__user__username',
                    #                                  'user_customer_flowup__user_id',
                    #                                  'user_customer_flowup__customer_id',
                    #                                 'follow_info', 'create_date')

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
