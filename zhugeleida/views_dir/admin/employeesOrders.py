from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import UpdateForm, SelectForm
import json, base64, datetime, time
from django.db.models import Q, Sum, Count


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def employeesOrders(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        q = Q()
        yewuyuan = request.GET.get('yewuyuan')
        startCreateTime =  request.GET.get('startCreateTime')
        stopCreateTime = request.GET.get('stopCreateTime')
        if yewuyuan:
            q.add(Q(yewuUser__username__contains=yewuyuan), Q.AND)
        if startCreateTime and stopCreateTime:
            stopCreateTime = stopCreateTime.replace('00:00:00', '23:59:59')
            q.add(Q(createDate__gte=startCreateTime) & Q(createDate__lte=stopCreateTime), Q.AND)
        print('q--------------> ',q)
        objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(q).values('yewuUser_id', 'yewuUser__username').annotate(Count('id'), Sum('yingFuKuan'))
        objsCount = objs.count()
        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]
        otherData = []
        for obj in objs:
            otherData.append({
                'yewuUser_id':obj['yewuUser_id'],
                'yewuUser__username':obj['yewuUser__username'],
                'id__count':obj['id__count'],
                'yingFuKuan__sum':obj['yingFuKuan__sum']
            })
        response.msg = '查询成功'
        response.code = 200
        response.data = {'otherData':otherData}
    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)





