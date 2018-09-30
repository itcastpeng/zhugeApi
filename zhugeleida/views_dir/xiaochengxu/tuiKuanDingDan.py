from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.tuiKuanDingDan_verify import AddForm, SelectForm
import json, base64


@csrf_exempt
@account.is_token(models.zgld_customer)
def tuiKuanDingDanShow(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    user_id = request.GET.get('user_id')
    u_id = request.GET.get('u_id')
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']

        if u_id:
            u_idObjs = models.zgld_userprofile.objects.filter(id=u_id)
            xiaochengxu_id = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)

            objs = models.zgld_shangcheng_dingdan_guanli.objects.select_related('shangpinguanli').filter(
                shangpinguanli__parentName__xiaochengxu_app__xiaochengxuApp=xiaochengxu_id
            )
        else:
            objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(shouHuoRen_id=user_id)
        objsCount = objs.count()
        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]
        otherData = []
        for obj in objs:
            username = ''
            yewu = ''
            if obj.yewuUser:
                decode_username = base64.b64decode( obj.yewuUser.username)
                username = str(decode_username, 'utf-8')
                yewu = obj.yewuUser_id
            shouhuorenusername = ''
            if obj.shouHuoRen_id:
                decode_username = base64.b64decode(obj.shouHuoRen.username)
                shouhuorenusername = str(decode_username, 'utf-8')
            shangpinguanli = obj.shangpinguanli
            otherData.append({
                'goodsName' : shangpinguanli.goodsName,
                'goodsPrice':shangpinguanli.goodsPrice,
                'countPrice':obj.countPrice,
                'yingFuKuan':obj.yingFuKuan,
                'youhui':obj.yongJin,
                'yewuyuan_id':yewu,
                'yewuyuan':username,
                'yongjin':obj.yongJin,
                'peiSong':obj.peiSong,
                'shouHuoRen_id':obj.shouHuoRen_id,
                'shouHuoRen':shouhuorenusername,
                'status':obj.get_theOrderStatus_display(),
                'createDate':obj.createDate.strftime('%Y-%m-%d %H:%M:%S')
            })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'otherData':otherData,
                'objsCount':objsCount,
            }
    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)





@csrf_exempt
@account.is_token(models.zgld_customer)
def tuiKuanDingDanOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':
        if oper_type == 'add':
            otherData = {
                'orderNumber':request.POST.get('orderNumber'),
                'tuiKuanYuanYin':request.POST.get('tuiKuanYuanYin'),
            }
            forms_obj = AddForm(otherData)
            if forms_obj.is_valid():
                print('验证通过')
                formObjs = forms_obj.cleaned_data
                models.zgld_shangcheng_tuikuan_dingdan_management.objects.create(
                    orderNumber_id=formObjs.get('orderNumber'),
                    tuiKuanYuanYin=formObjs.get('tuiKuanYuanYin')
                )
                response.code = 200
                response.msg = '添加退款订单成功！'
                response.data = ''
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)




