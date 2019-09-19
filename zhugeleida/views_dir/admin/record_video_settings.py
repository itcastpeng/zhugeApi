from zhugeleida import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.record_video_verify import SelectForm
from publicFunc.condition_com import conditionCom
import json, base64


# 视频基础设置查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def record_video_settings(request):
    user_id = request.GET.get('user_id')
    company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')
        field_dict = {
            'id': '',
        }
        q = conditionCom(request, field_dict)
        objs = models.zgld_recorded_video_settings.objects.filter(
            q,
            company_id=company_id
        ).order_by(order)
        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        data_list = []
        for obj in objs:
            data_list.append({
                'id': obj.id,
                'whether_turn_on_advertisement': obj.whether_turn_on_advertisement,         # 是否打开 广告
                'ad_wallpaper': obj.ad_wallpaper,                                           # 广告图片
                'whether_business_communication': obj.whether_business_communication,       # 是否打开 商务通
                'business_address': obj.business_address,                                   # 商务通地址
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),               # 文章创建时间
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'count': count,
            'data_list': data_list,
        }
        response.note = {
            'id': 'id',
            'whether_turn_on_advertisement': '是否打开 广告',
            'ad_wallpaper': '广告图片',
            'whether_business_communication': '是否打开 商务通',
            'business_address': '商务通地址',
            'create_date': '文章创建时间',
        }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 视频基础设置
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def record_video_settings_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    company_id = models.zgld_admin_userprofile.objects.get(
        id=user_id
    ).company_id

    if request.method == "POST":

        # 修改基本设置
        if oper_type == 'update':
            whether_turn_on_advertisement = request.POST.get('whether_turn_on_advertisement')       # 开关 广告
            whether_business_communication = request.POST.get('whether_business_communication')       # 开关 商务通
            ad_wallpaper = request.POST.get('ad_wallpaper')             # 广告壁纸
            business_address = request.POST.get('business_address')     # 商务通
            code = 200
            msg = '修改成功'
            objs = models.zgld_recorded_video_settings.objects.filter(company_id=company_id)

            if objs:
                obj = objs[0]

            else:
                obj = models.zgld_recorded_video_settings.objects.create(
                    company_id=company_id
                )

            if whether_turn_on_advertisement: # 操作广告开关
                whether_turn_on_advertisement = bool(1 - obj.whether_turn_on_advertisement)
                if whether_turn_on_advertisement and ad_wallpaper:
                    code = 301
                    msg = '请上传广告图片'
                else:
                    obj.whether_turn_on_advertisement = whether_turn_on_advertisement

            if whether_business_communication: # 操作商务通开关
                whether_business_communication = bool(1 - obj.whether_business_communication)
                if whether_business_communication and business_address:
                    code = 301
                    msg = '请上传商务通地址'
                else:
                    obj.whether_business_communication = whether_business_communication
            obj.save()

            if ad_wallpaper:
                if obj.whether_turn_on_advertisement:
                    objs.ad_wallpaper=ad_wallpaper
                else:
                    code = 301
                    msg = '请先打开广告'

            if business_address:
                if obj.whether_business_communication:
                    obj.business_address=business_address
                else:
                    code = 301
                    msg = '请先打开商务通'
            obj.save()
            response.code = code
            response.msg = msg


    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


















