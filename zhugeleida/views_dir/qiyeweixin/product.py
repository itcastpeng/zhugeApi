from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.qiyeweixin.product_verify import ProductAddForm
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = ProductAddForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'company__name': '__contains',
                'create_date': '',
                'last_login_date': '',

            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            print('order -->', order)
            print(models.zgld_userprofile.objects.all())
            objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            print('------------->>>', objs)
            ret_data = []
            for obj in objs:
                print('oper_user_username -->', obj)
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'username': obj.username,
                    'role_name': obj.role.name,
                    'role_id': obj.role.id,
                    'create_date': obj.create_date,
                    'last_login_date': obj.last_login_date,
                    'status': obj.get_status_display()
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


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def product_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        if oper_type == "add":
            print('-----1--->>>', request.POST)
            form_data = {
                'user_id' : request.GET.get('user_id'),
                'name': request.POST.get('name'),        # 产品名称 必须
                'price': request.POST.get('price'),      # 价格     必须
                'reason': request.POST.get('reason'),    # 推荐理由 非必须
                'title': request.POST.get('title'),      # 标题    非必须
                'content': request.POST.get('content'),  # 内容    非必须
            }

            forms_obj = ProductAddForm(form_data)
            if forms_obj.is_valid():
                user_id =request.GET.get('user_id')
                cover_picture = request.FILES.get('cover_picture')  # 1代表产品封面 2 代表产品介绍
                introduce_picture = request.FILES.get('introduce_picture')

                print('----cover_picture----->>>>',type(cover_picture),cover_picture)

                if cover_picture:

                    for p in cover_picture:
                        print('-------cover_picture p ---------------->>>', p)
                        with open('xxx.jpg', 'wb') as f:
                            for chunk in p.chunks():
                                f.write(chunk)


                company_id = models.zgld_userprofile.objects.get(id=user_id).company_id
                product_obj = models.zgld_product.objects.create(
                      user_id=user_id,
                      company_id=company_id,
                      name=forms_obj.data.get('name'),
                      price=forms_obj.data.get('price'),
                      reason = forms_obj.data.get('reason'),
                      title = forms_obj.data.get('title'),
                      content = forms_obj.data.get('content')
                )
                create_picture_obj = create_product_picture(user_id,cover_picture,product_obj,1)
                create_picture_obj.create_picture()

            return JsonResponse(response.__dict__)


        elif oper_type == "add_picture":
            print('----111---->>>', request.POST)
            upload_file = request.FILES['file']

            task = request.POST.get('task_id')      # 获取文件唯一标识符
            chunk = request.POST.get('chunk', 0)    # 获取该分片在所有分片中的序号
            filename = '/%s%s' % (task, chunk)      # 构成该分片唯一标识符
            IMG_PATH_FILES = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin','product') + filename
            with open(IMG_PATH_FILES, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

        elif oper_type == "delete":
            # 删除 ID
            user_objs = models.zgld_userprofile.objects.filter(id=o_id)
            if user_objs:
                user_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '用户ID不存在'

        elif oper_type == "update":
            # 获取ID 用户名 及 角色
            form_data = {
                'user_id': o_id,
                'username': request.POST.get('username'),
                'role_id': request.POST.get('role_id'),
            }
            print(request.POST)
            forms_obj = UserUpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                user_id = forms_obj.cleaned_data['user_id']
                username = forms_obj.cleaned_data['username']
                role_id = forms_obj.cleaned_data['role_id']
                #  查询数据库  用户id
                user_obj = models.zgld_userprofile.objects.filter(
                    id=user_id
                )
                #  更新 数据
                if user_obj:
                    user_obj.update(
                        username=username, role_id=role_id
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    elif request.method == "GET":

        if  oper_type == "upload_complete":
            target_filename = request.GET.get('filename')  # 获取上传文件的文件名
            task = request.GET.get('task_id')              # 获取文件的唯一标识符
            picture_type = request.GET.get('picture_type')
            IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product')
            chunk = 0          #分片序号
            file_tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            print('===target_filename===>>',target_filename)

            file_type = target_filename.split('.')[1]
            target_filename = '%s/%s.%s' %  (IMG_PATH,file_tag,file_type)

            with open(target_filename, 'wb') as target_file:   # 创建新文件
                while True:
                    try:
                        filename = '%s%d' % (task, chunk)
                        source_file = open('%s/%s' % (IMG_PATH, filename), 'rb')     # 按序打开每个分片
                        target_file.write(source_file.read())                        # 读取分片内容写入新文件
                        source_file.close()
                    except IOError:
                        break
                    chunk += 1
                    os.remove('%s/%s' % (IMG_PATH,filename))  #删除该分片，节约空间
            picture_url = 'statics/zhugeleida/imgs/qiyeweixin/product/%s.%s' % (file_tag,file_type)

            product_picture_obj = models.zgld_product_picture.objects.create(picture_type=picture_type,picture_url=picture_url)

            response.code = 200
            response.msg = "添加图片成功"
            response.data = {
                'ret_data':
                    {
                        'picture_id': product_picture_obj.id,
                        'picture_url': product_picture_obj.picture_url,
                    }
            }


    return JsonResponse(response.__dict__)


class create_product_picture:

    def __init__(self,user_id,picture_obj,product_obj,type):
        self.response = Response.ResponseObj()
        self.user_id = user_id
        self.picture_obj = picture_obj
        self.product_obj = product_obj
        self.picture_type = type
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def comon_picture(self,p_obj,product_picture_obj):

        userid = models.zgld_userprofile.objects.get(id=self.user_id).userid
        product_picture = '/%s_%s_photo.jpg' % (product_picture_obj.id, userid)

        photo_url = 'statics/zhugeleida/imgs/qiyeweixin/product%s' % (product_picture)
        product_picture_obj.picture_url = photo_url
        product_picture_obj.save()
        IMG_PATH = os.path.join(self.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'qiyeweixin',
                                'product') + product_picture
        with open('%s' % (IMG_PATH), 'wb') as f:
            print('---p_obj-->>',p_obj)

            for chunk in p_obj.chunks():
                f.write(chunk)


    def create_picture(self):
        if self.picture_obj:  # 封面图片存在
            for p_obj in self.picture_obj:
                product_picture_obj = models.zgld_product_picture.objects.create(picture_type=1, product_id=self.product_obj.id)
                self.comon_picture(p_obj,product_picture_obj)

            return '200'
        else:
            self.response.code = 301
            self.response.msg = "封面图片不能为空"
            return '301'


