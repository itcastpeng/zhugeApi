from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.qiyeweixin.mingpian_verify import MingPianPhoneUpdateForm, MingPianInfoUpdateForm, UserSelectForm
import json
from django.db.models import Q
import os


# 展示企业微信的用户名片的个性签名,标签,
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def mingpian(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')  # 用户 id
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'company__name': '__contains',
            }
            q = conditionCom(request, field_dict)
            q.add(Q(**{'id': user_id}), Q.AND)

            objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                tag_data = models.zgld_userprofile.objects.get(id=user_id).zgld_user_tag_set.values('id', 'name')
                photo_data = models.zgld_user_photo.objects.filter(user_id=user_id).values_list('id','photo_url')
                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,  # 姓名| 管理员可以修改
                    'avatar': obj.avatar,
                    'company': obj.company.name,  # 公司名 | 管理员可以修改
                    'area': obj.company.area or '',
                    'address': obj.company.address or '',
                    'position': obj.position,  # 职位 | 管理员可以修改
                    'telephone': obj.telephone or '',
                    'email': obj.email or '',
                    'country': obj.get_country_display() or '',

                    'wechat': obj.wechat or '',  # 微信号
                    'wechat_phone': obj.wechat_phone or '',  # 微信绑定的手机号 | 管理员可以修改
                    'is_show_phone': obj.is_show_phone,  # 默认显示名片中的手机号，
                    'mingpian_phone': obj.mingpian_phone or '',  # 名片手机号
                    'sign': obj.sign,                     # 签名
                    'photo' : list(photo_data),
                    'tag' :   list(tag_data),
                    'create_date': obj.create_date,  # 创建时间

                })

            # 查询成功 返回200 状态码
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


# 展示企业微信的用户名片
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def mingpian_oper(request, oper_type):
    response = Response.ResponseObj()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if request.method == "POST":

        if oper_type == 'save_phone':

            forms_obj = MingPianPhoneUpdateForm(request.POST)
            if forms_obj.is_valid():

                user_id = request.GET.get('user_id')
                mingpian_phone = request.POST.get('mingpian_phone')
                is_show_phone = request.POST.get('is_show_phone')
                objs = models.zgld_userprofile.objects.filter(id=user_id)

                if objs:
                    objs.update(mingpian_phone=mingpian_phone, is_show_phone=is_show_phone)

                    response.code = 200
                    response.msg = '保存成功'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'save_info':

            forms_obj = MingPianInfoUpdateForm(request.POST)

            if forms_obj.is_valid():

                print('----forms_obj.data--->>', forms_obj.data)

                user_id = request.GET.get('user_id')
                wechat = forms_obj.data.get('wechat')
                mingpian_phone = forms_obj.data.get('mingpian_phone')
                telephone = forms_obj.data.get('telephone')
                email = forms_obj.data.get('email')
                country = forms_obj.data.get('country')
                area = forms_obj.data.get('area')
                address = forms_obj.data.get('address')

                objs = models.zgld_userprofile.objects.filter(id=user_id)
                print('-----objs--->>', objs)
                objs.update(
                    mingpian_phone=mingpian_phone,
                    wechat=wechat,
                    telephone=telephone,
                    email=email,
                    country=country,
                )
                if objs[0].company_id:  # 后台一定要先将用户外键到公司的ID。在修改公司地址。
                    company_obj = models.zgld_company.objects.filter(id=objs[0].company_id)
                    company_obj.update(area=area, address=address)

                response.code = 200
                response.msg = '保存成功'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'save_sign':

            user_id = request.GET.get('user_id')
            mingpian_sign = request.POST.get('sign')

            objs = models.zgld_userprofile.objects.filter(id=user_id)

            if objs:
                objs.update(sign=mingpian_sign)
                response.code = 200
                response.msg = '保存成功'

        elif oper_type == "upload_photo":

            upload_file = request.FILES['file']
            task = request.POST.get('task_id')  # 获取文件唯一标识符
            chunk = request.POST.get('chunk', 0)  # 获取该分片在所有分片中的序号
            filename = '/%s%s' % (task, chunk)  # 构成该分片唯一标识符

            IMG_PATH_FILES = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'user_photo','tmp') + filename
            with open(IMG_PATH_FILES, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

        elif oper_type == 'delete_photo':
            print('--------->>',request.POST)
            user_id = request.GET.get('user_id')
            photo_id = request.POST.get('photo_id')

            objs = models.zgld_user_photo.objects.filter(id=photo_id,user_id=user_id)

            if objs:
                IMG_PATH = BASE_DIR  + '/' + objs[0].photo_url
                print('-----IMG_PATH--->>',IMG_PATH)
                if os.path.exists(IMG_PATH):os.remove(IMG_PATH)
                objs.delete()
                response.code = 200
                response.msg = '删除成功'
            else:
                response.code = 302
                response.msg = '删除数据不存在'


    elif request.method == "GET":
        if oper_type == 'show_photo':
            user_id = request.GET.get('user_id')
            photo_query_list = models.zgld_user_photo.objects.filter(user_id=user_id).values('id', 'photo_url')
            models.zgld_user_photo.objects.filter(user_id=1)
            response.code = 200
            response.msg = '获取成功'
            response.data = {
                'ret_data': list(photo_query_list),
                'user_id': user_id,
            }

        elif oper_type == "upload_complete":
            user_id = request.GET.get('user_id')
            target_filename = request.GET.get('filename')   # 获取上传文件的文件名
            task = request.GET.get('task_id')               # 获取文件的唯一标识符

            IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'user_photo')
            TEMP_IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'user_photo', 'tmp')
            chunk = 0  # 分片序号
            file_tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            print('===target_filename===>>', target_filename)

            file_type = target_filename.split('.')[1]
            target_filename = '%s/%s.%s' % (IMG_PATH, file_tag, file_type)

            with open(target_filename, 'wb') as target_file:  # 创建新文件
                while True:
                    try:
                        filename = '%s%d' % (task, chunk)
                        source_file = open('%s/%s' % (TEMP_IMG_PATH, filename), 'rb')  # 按序打开每个分片
                        target_file.write(source_file.read())  # 读取分片内容写入新文件
                        source_file.close()
                    except IOError:
                        break
                    chunk += 1
                    os.remove('%s/%s' % (TEMP_IMG_PATH, filename))  # 删除该分片，节约空间



            photo_url = 'statics/zhugeleida/imgs/xiaochengxu/user_photo/%s.%s' % (file_tag, file_type)
            photo_obj = models.zgld_user_photo.objects.create(user_id=user_id,photo_url=photo_url)

            response.code = 200
            response.msg = "添加图片成功"
            response.data = {
                'ret_data':
                    {
                        'photo_id': photo_obj.id,
                        'photo_url': photo_obj.photo_url,
                    }
            }


    return JsonResponse(response.__dict__)
