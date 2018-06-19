from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.qiyeweixin.user_verify import UserAddForm, UserUpdateForm, UserSelectForm
import json
from django.db.models import Q

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def mingpian(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():

            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'company__name': '__contains',
                'create_date': '',
                'last_login_date': '',
            }
            user_id = request.GET.get('user_id')
            q = conditionCom(request, field_dict)
            q.add(Q(**{'id': user_id}), Q.AND)

            objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
            count = objs.count()
            # 返回的数据
            print('-----objs---q----->>>', objs,q)

            ret_data = []
            for obj in objs:
                print('oper_user_username -->', obj)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'company': obj.company.name,
                    'position': obj.position,
                    'username': obj.username,
                    'avatar': obj.avatar,
                    'phone': obj.phone,
                    'email': obj.email or '',
                    'qr_code': obj.qr_code,
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
