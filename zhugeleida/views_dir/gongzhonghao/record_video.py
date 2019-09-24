from zhugeleida import models
from publicFunc import account, Response
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.gongzhonghao.record_video_verify import SelectForm
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.public.pub import pub_create_link_repost_video, verify_phone_number
import json, datetime



# 录播视频操作
@csrf_exempt
@account.is_token(models.zgld_customer)
def record_video_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":

        # 更新手机号
        if oper_type == 'update_phone':
            phone_num = request.POST.get('phone_num')
            if verify_phone_number(phone_num):
                models.zgld_customer.objects.filter(id=user_id).update(video_phone_num=phone_num)
                response.code = 200
                response.msg = '更新手机号完成'
            else:
                response.code = 301
                response.msg = '手机号验证失败'
    else:

        # 查询录播视频
        if oper_type == 'get_video':
            uid = request.GET.get('uid')  # 用户ID
            is_previous_video = request.GET.get('is_previous_video')  # 是否为往期视频
            user_id = request.GET.get('user_id')
            company_id = models.zgld_customer.objects.get(id=user_id).company_id
            response = Response.ResponseObj()
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')
                field_dict = {
                    'id': '',
                    'classification_id': '',
                }
                video_id = request.GET.get('id')
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

                settings_objs = models.zgld_recorded_video_settings.objects.filter(company_id=company_id)

                setting_data = {
                    'whether_turn_on_advertisement': 0,  # 是否打开广告
                    'ad_wallpaper': '',  # 广告图片
                    'whether_business_communication': 0,  # 是否打开商务通
                    'business_address': ''  # 商务通图片
                }
                if settings_objs:
                    settings_obj = settings_objs[0]
                    setting_data['whether_turn_on_advertisement'] = settings_obj.whether_turn_on_advertisement
                    setting_data['ad_wallpaper'] = settings_obj.ad_wallpaper
                    setting_data['whether_business_communication'] = settings_obj.whether_business_communication
                    setting_data['business_address'] = settings_obj.business_address

                data_list = []
                for obj in objs:
                    # share_url = pub_create_link_repost_video(uid, obj.id, company_id, user_id)

                    data = {
                        'id': obj.id,
                        'classification_id': obj.classification_id,                     # 分类ID
                        'classification_name': obj.classification.classification_name,  # 分类名称
                        'company_id': obj.company_id,                                   # 公司ID
                        'company_name': obj.company.name,                               # 公司名称
                        'user_id': obj.user_id,                                         # 创建人ID
                        'user_name': obj.user.login_user,                               # 创建人名称
                        'title': obj.title,                                             # 视频标题
                        'abstract': obj.abstract,                                       # 视频摘要
                        'cover_photo': obj.cover_photo,                                 # 封面图片
                        'video_url': obj.video_url,                                     # 封面链接

                        'expert_introduction': obj.expert_introduction,                 # 专家介绍
                        'textual_interpretation': obj.textual_interpretation,           # 文字解读
                        'whether_authority_expert': obj.whether_authority_expert,       # 是否打开权威专家
                        'whether_consult_online': obj.whether_consult_online,           # 是否打开在线咨询
                        'whether_previous_video': obj.whether_previous_video,           # 是否打开往期视频
                        'whether_text_interpretation': obj.whether_text_interpretation, # 是否打开文字解读
                        'whether_verify_phone': obj.whether_verify_phone,               # 是否验证短信
                        'whether_writer_number': obj.whether_writer_number,             # 是否写手机号
                        # 'share_url': share_url,                                         # 转发链接
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),   # 文章创建时间
                    }
                    is_phone = False
                    if video_id:
                        if models.zgld_customer.objects.get(id=user_id).video_phone_num:
                            is_phone = True

                    data['is_phone'] = is_phone
                    data_list.append(data)

                if is_previous_video and video_id: # 记录转载
                    video_belonger_data = {
                        'video_id': video_id,
                        'user_id': uid,
                        'customer_id': user_id,
                    }
                    models.zgld_video_to_customer_belonger.objects.create(**video_belonger_data)

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'data_list': data_list,
                    'video_settings': setting_data
                }
                response.note = {
                    'data_list': [
                        {
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
                            'whether_authority_expert': '是否打开权威专家',
                            'whether_consult_online': '是否打开在线咨询',
                            'whether_previous_video': '是否打开往期视频',
                            'whether_text_interpretation': '是否打开文字解读',
                            'whether_verify_phone': '是否验证短信',
                            'whether_writer_number': '是否写手机号',
                            'create_date': '文章创建时间'
                        }
                    ],
                    'count': '总数',
                    'video_settings': {
                        'whether_turn_on_advertisement': '是否打开广告',
                        'ad_wallpaper': '广告图片',
                        'whether_business_communication': '是否打开商务通',
                        'business_address': '商务通图片'
                    }
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)

