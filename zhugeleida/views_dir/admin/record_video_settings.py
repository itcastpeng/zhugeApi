from zhugeleida import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
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
            'company_id': '',
            'classification_id': '',
            'user_id': '',
            'title': '__contains',
            'abstract': '__contains',
        }
        q = conditionCom(request, field_dict)
        objs = models.zgld_recorded_video.objects.filter(
            q,
            company_id=company_id,
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
                'classification_id': obj.classification_id,                         # 分类ID
                'classification_name': obj.classification.classification_name,      # 分类名称
                'company_id': obj.company_id,                                       # 公司ID
                'company_name': obj.company.name,                                   # 公司名称
                'user_id': obj.user_id,                                             # 创建人ID
                'user_name': obj.user.login_user,                                   # 创建人名称
                'title': obj.title,                                                 # 视频标题
                'abstract': obj.abstract,                                           # 视频摘要
                'cover_photo': obj.cover_photo,                                     # 封面图片
                'expert_introduction': obj.expert_introduction,                     # 专家介绍
                'textual_interpretation': obj.textual_interpretation,               # 文字解读

                'whether_authority_expert': obj.whether_authority_expert,           # 是否打开权威专家
                'whether_consult_online': obj.whether_consult_online,               # 是否打开在线咨询
                'whether_previous_video': obj.whether_previous_video,               # 是否打开往期视频
                'whether_text_interpretation': obj.whether_text_interpretation,     # 是否打开文字解读
                'whether_verify_phone': obj.whether_verify_phone,                   # 是否验证短信
                'whether_writer_number': obj.whether_writer_number,                 # 是否写手机号
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),       # 文章创建时间
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'count': count,
            'data_list': data_list,
        }
        response.note = {
            'classification_id': '分类ID',
            'classification_name': '分类名称',
            'company_id': '公司ID',
            'company_name': '公司名称',
            'user_id': '创建人ID',
            'user_name': '创建人名称',
            'title': '视频标题',
            'abstract': '视频摘要',
            'cover_photo': '封面图片',
            'expert_introduction': '专家介绍',
            'textual_interpretation': '文字解读',
            'whether_authority_expert':'是否打开权威专家',
            'whether_consult_online': '是否打开在线咨询',
            'whether_previous_video': '是否打开往期视频',
            'whether_text_interpretation': '是否打开文字解读',
            'whether_verify_phone': '是否验证短信',
            'whether_writer_number': '是否写手机号',
            'create_date': '文章创建时间'
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

        objs = models.zgld_recorded_video_settings.objects.filter(company_id=company_id)

        # 打开/关闭 广告
        if oper_type == "turn_ads_on_or_off":
            if objs:
                obj = objs[0]
                obj.whether_turn_on_advertisement = bool(1 - obj.whether_turn_on_advertisement)
                obj.save()
            else:
                models.zgld_recorded_video_settings.objects.create(
                    company_id=company_id,
                    whether_turn_on_advertisement=1
                )
            response.code = 200
            response.msg = '设置完成'

        # 打开/关闭 商务通
        elif oper_type == 'turn_on_or_off_commerce_link':
            if objs:
                obj = objs[0]
                obj.whether_business_communication = bool(1 - obj.whether_business_communication)
                obj.save()
            else:
                models.zgld_recorded_video_settings.objects.create(
                    company_id=company_id,
                    whether_business_communication=1
                )
            response.code = 200
            response.msg = '设置完成'

        # 修改基本设置
        elif oper_type == 'update':
            turn_on_or_off = request.POST.get('turn_on_or_off')         # 开关 广告/商务通
            ad_wallpaper = request.POST.get('ad_wallpaper')             # 广告壁纸
            business_address = request.POST.get('business_address')     # 商务通
            code = 200
            msg = '修改成功'

            if ad_wallpaper:
                if objs[0].whether_turn_on_advertisement:
                    objs.update(ad_wallpaper=ad_wallpaper)
                else:
                    code = 301
                    msg = '请先打开广告'

            if business_address:
                if objs[0].whether_business_communication:
                    objs.update(business_address=business_address)
                else:
                    code = 301
                    msg = '请先打开商务通'


            response.code = code
            response.msg = msg


    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


















