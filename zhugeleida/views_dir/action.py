from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.action_verify import ActionSelectForm


from zhugeleida import models


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def action(request):
    '''
     分页获取访问日志信息
    :param request:
    :return:
    '''
    if request.method == 'GET':

        forms_obj = ActionSelectForm(request.GET)
        if forms_obj.is_valid():
            response = Response.ResponseObj()
            user_id = request.GET.get('user_id')

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            access_log_objs = models.zgld_accesslog.objects.select_related(
                'user',
                'customer'
            ).filter(
                user_id=user_id

            ).order_by('-create_date')
            print(access_log_objs)

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                access_log_objs = access_log_objs[start_line: stop_line]

            ret_data_list = []
            for obj in access_log_objs:
                ret_data_list.append({
                    'user_id': obj.user_id,
                    'customer_id': obj.customer_id,
                    'log': obj.customer.username + obj.remark,
                    'create_date': obj.create_date,
                })

            response.code = 200
            response.msg = '查询日志记录成功'
            response.data = ret_data_list


            return JsonResponse(response.__dict__)

