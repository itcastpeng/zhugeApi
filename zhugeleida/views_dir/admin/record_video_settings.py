from zhugeleida import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.record_video_verify import SelectForm
from publicFunc.condition_com import conditionCom
from publicFunc.base64 import b64decode

from django.db.models import Q, Count
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
                if not ad_wallpaper:
                    code = 301
                    msg = '请上传广告图片'


            if whether_business_communication: # 操作商务通开关
                if not business_address:
                    code = 301
                    msg = '请上传商务通地址'


            if business_address and whether_business_communication:
                obj.business_address=business_address
            else:
                if not whether_business_communication:
                    code = 301
                    msg = '请先打开商务通'

            if ad_wallpaper and whether_turn_on_advertisement:
                    obj.ad_wallpaper=ad_wallpaper
            else:
                if not whether_turn_on_advertisement:
                    code = 301
                    msg = '请先打开广告'

            obj.whether_business_communication = whether_business_communication
            obj.whether_turn_on_advertisement = whether_turn_on_advertisement
            obj.save()
            response.code = code
            response.msg = msg


    else:

        # 查询所有视频名称
        if oper_type == 'query_all_video_names':
            classification_id = request.GET.get('classification_id')

            objs = models.zgld_recorded_video.objects.filter(
                company_id=company_id
            )
            if classification_id:
                objs = objs.filter(classification_id=classification_id)

            count = objs.count()
            data_list = []
            for obj in objs:
                data_list.append({
                    'id': obj.id,
                    'title': obj.title
                })

            response.code = 200
            response.msg = '查询完成'
            response.data = {
                'data_list': data_list,
                'count': count,
            }

        # 查询所有视频分类名称
        elif oper_type == 'query_all_video_category_names':
            objs = models.zgld_recorded_video_classification.objects.filter(
                company_id=company_id
            )
            count = objs.count()
            data_list = []
            for obj in objs:
                data_list.append({
                    'id': obj.id,
                    'classification_name': obj.classification_name
                })

            response.code = 200
            response.msg = '查询完成'
            response.data = {
                'data_list': data_list,
                'count': count,
            }

        # 查询视频数据管理
        elif oper_type == 'query_video_data_management':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')
                field_dict = {
                    'id': '',
                    'video_id': '',
                }
                q = conditionCom(request, field_dict)
                objs = models.zgld_video_to_customer_belonger.objects.filter(
                    q,
                    user__company_id=company_id,
                    video__user__company_id=company_id,
                ).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                data_list = []
                for obj in objs:

                    if obj.customer: #
                        phone = obj.customer.video_phone_num
                        customer_id = obj.customer_id
                        customer_name = b64decode(obj.customer.username)

                    else:
                        phone = obj.parent_customer.video_phone_num
                        customer_id = obj.parent_customer_id
                        customer_name = b64decode(obj.parent_customer.username)

                    data_list.append({
                        'id': obj.id,
                        'phone': phone,
                        'belong_id': obj.user_id,
                        'belong_name': obj.user.username,
                        'customer_id': customer_id,
                        'customer_name': customer_name,
                        'video_id': obj.video_id,
                        'video_name': obj.video.title,
                        'video_view_duration': obj.video_view_duration,
                        'video_duration_stay': obj.video_duration_stay,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),  # 查看时间
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'data_list': data_list,
                }
                response.note = {
                    'id': 'ID',
                    'phone': '电话',
                    'belong_id': '归属人ID',
                    'belong_name': '归属人名称',
                    'customer_id': '查看人ID',
                    'customer_name': '查看人名称',
                    'video_id': '查看视频ID',
                    'video_name': '查看视频名称',
                    'video_view_duration': '视频查看时长',
                    'video_duration_stay': '视频停留时长',
                    'create_date': '查看时间',
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 查询视频 脉络图
        elif oper_type == 'query_video_context_diagram':
            q = Q()
            uid = request.GET.get('uid')  # 视频所属用户ID
            q.add(Q(video_id=o_id), Q.AND)
            if uid:
                q.add(Q(user_id=uid), Q.AND)

            objs = models.zgld_video_to_customer_belonger.objects.filter(q)
            if objs:
                video_title = objs[0].video.title
                result_data = []

                belonger_objs = models.zgld_video_to_customer_belonger.objects.select_related(
                    'user'
                ).filter(q, level=0).values('user', 'user__username').annotate(Count('id')) # 首级
                count_num = 0
                for belonger_obj in belonger_objs:
                    tmp = {}
                    tmp['name'] = belonger_obj['user__username']
                    tmp['children'] = init_data(o_id, q)
                    result_data.append(tmp)

                dataList = {  # 顶端 首级
                    'name': video_title,
                    'children': result_data
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'dataList': dataList,
                    'video_title': video_title, # 视频标题
                    # 'max_person_num': max_person_num
                }
            else:
                response.code = 301
                response.msg = '该文章无查看'
                response.data = {}

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)



# 脉络图查询 调用init_data
def init_data(article_id, q, user_id=None):
    objs = models.zgld_video_to_customer_belonger.objects.select_related(
        'user', 'video', 'customer'
    ).filter(q).values(
        'customer_id',
        'customer__username'
    ).annotate(Count('id'))

    if user_id:
        objs = objs.filter(parent_customer_id=user_id)
    else:
        objs = objs.filter(parent_customer__isnull=True)
    result_data = []
    for obj in objs:
        user_id = obj['customer_id']
        username = b64decode(obj['customer__username'])
        children_data = init_data(article_id, q, user_id)
        tmp = {'name': username}
        if children_data:
            tmp['children'] = children_data
        result_data.append(tmp)
    return result_data













