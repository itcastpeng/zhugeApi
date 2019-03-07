from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserSelectForm
import json
from django.db.models import Q, Count, Sum


# cerf  token验证
# 雷达后台首页 数据统计
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = request.GET.get('user_id')
            order = request.GET.get('order', '-create_date')

            field_dict = {
                'id': '',
            }
            q = conditionCom(request, field_dict)

            print('------q------>>',q)

            # 获取用户信息
            admin_userobj = models.zgld_userprofile.objects.get(id=user_id)
            company_id = admin_userobj.company_id

            objs = models.zgld_userprofile.objects.filter(
                q,
                company_id=company_id,
            )
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]


            ret_data = []
            read_count = 0
            forward_count = 0

            for obj in objs:
                copy_nickname = models.ZgldUserOperLog.objects.filter(user_id=obj.id).count()  # 复制昵称次数

                read_count_obj = models.zgld_article_to_customer_belonger.objects.values('user_id').annotate(
                    read_count=Sum('read_count'), forward_count=Sum('forward_count')).filter(user_id=obj.id) # 点击量 转发量
                if read_count_obj:
                    read_count = read_count_obj[0].get('read_count')
                    forward_count = read_count_obj[0].get('forward_count')

                phone_call_num = models.zgld_accesslog.objects.filter(user_id=obj.id, action=10).count() # 拨打电话次数

                #  ----------------------------用戶主动发送消息--------------------------
                data_list = []
                [data_list.append({'customer_id':i.get('customer_id'), 'article_id':i.get('article_id')}) for i in
                 models.zgld_chatinfo.objects.filter(userprofile_id=obj.id, send_type=2, article__isnull=False).values('customer_id', 'article_id').distinct()]

                user_active_send_num = 0
                for i in data_list:
                    objs = models.zgld_chatinfo.objects.filter(
                        customer_id=i.get('customer_id'),
                        article_id=i.get('article_id'),
                        userprofile_id=obj.id).order_by('-create_date')
                    if objs:
                        if int(objs[0].send_type) == 2:
                            user_active_send_num += 1
                # ---------------------------------------------------------------------



                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'copy_nickname':copy_nickname,
                    'read_count':read_count,
                    'forward_count':forward_count,
                    'phone_call_num':phone_call_num,
                    'user_active_send_num':user_active_send_num,
                })



            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'count': count,
            }

            response.note = {
                'username': '咨询用户名称',
                'copy_nickname': '复制昵称次数',
                'read_count': '点击量',
                'forward_count': '转发量',
                'phone_call_num': '拨打电话次数',
                'user_active_send_num': '客户主动发送消息数量',
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)







@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def data_statistics_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "GET":
        pass


    else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
#

