from publicFunc import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from zhugeleida.forms.public import img_upload_verify
from zhugeleida.forms.public import img_merge_verify
from django.http import HttpResponse
import datetime as dt, time, json, uuid, os, base64
from PIL import Image, ImageDraw,ImageFont
import subprocess

from zhugeleida import models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# 上传图片（分片上传）
@csrf_exempt
# @account.is_token(models.zgld_userprofile)
def img_upload(request):
    response = Response.ResponseObj()

    forms_obj = img_upload_verify.imgUploadForm(request.POST)
    if forms_obj.is_valid():

        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
        chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
        expanded_name = img_name.split('.')[-1]  # 扩展名

        img_name = timestamp + "_" + str(chunk) + '.' + expanded_name
        img_save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'tmp', img_name)
        print('img_save_path -->', img_save_path )

        with open(img_save_path, 'w') as f:
            f.write(img_data)

        response.code = 200
        response.msg = "上传成功"

    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


data_path_dict = {
    'user_photo': os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_photo')
}

# 合并图片
@csrf_exempt
# @account.is_token(models.zgld_admin_userprofile)
def img_merge(request):
    response = Response.ResponseObj()
    forms_obj = img_merge_verify.imgMergeForm(request.POST)
    if forms_obj.is_valid():
        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
        expanded_name = img_name.split('.')[-1]  # 扩展名
        company_id = request.POST.get('company_id')  # 图片的类型  (1, '产品封面的图片'), (2, '产品介绍的图片')
        img_name = timestamp + '.' + expanded_name
        img_source = forms_obj.cleaned_data.get('img_source')  # user_photo 代表用户上传的照片  user_avtor 代表用户的头像。

        print('-----img_source----->', img_source)

        file_dir = ''

        # file_dir = data_path_dict['user_photo']
        if img_source == 'user_photo':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_photo')

        elif img_source == 'user_avatar':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'user_avatar')

        elif img_source == 'cover_picture' or img_source == 'product_picture':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'product')

        elif img_source == 'feedback':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'feedback')

        elif img_source == 'website':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'website')

        elif img_source == 'wcx_head_image': # 上传小程序头像
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'wcx_head_image')

        elif img_source == 'article':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article')


        elif img_source == 'admin_qrcode':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'qr_code')

        elif  img_source == 'goods':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'goods')

        elif  img_source == 'secretKeyFile':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'secretKeyFile')

        elif img_source == 'leida_chat':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'qiyeweixin', 'chat')

        elif img_source == 'case':
            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'case')



        fileData = ''

        for chunk in range(chunk_num):

            count = 0
            while True:
                count += 1
                try:
                    if count > 5:
                        break
                    file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
                    file_save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'tmp', file_name)
                    with open(file_save_path, 'r') as f:
                        fileData += f.read()
                    print('file_save_path -->', file_save_path)
                    # os.remove(file_save_path)
                    break

                except FileNotFoundError:
                    time.sleep(0.1)

        # user_id = request.GET.get('user_id')
        img_path = os.path.join(file_dir, img_name)
        file_obj = open(img_path, 'wb')
        # print("fileData -->", fileData)
        img_data = base64.b64decode(fileData)
        # print("type(img_data) -->", type(img_data))
        file_obj.write(img_data)

        print('【1】值 os.path.getsize(img_path) ---------->>',os.path.getsize(img_path))
        user_id = request.GET.get('user_id')
        if  img_source == 'article' or  img_source == 'cover_picture':
            company_id =  models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            _img_path = setup_picture_shuiyin(img_name,img_path, company_id,'article')
            if  _img_path:
                img_path =  _img_path

        elif  img_source == 'case':
            company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            _img_path = setup_picture_shuiyin(img_name,img_path, company_id, 'case')
            if  _img_path:
                img_path =  _img_path

        response.data = {
            'picture_url': img_path,
        }
        response.code = 200
        response.msg = "添加图片成功"

    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 目录创建
def upload_generation_dir(dir_name):
    today = dt.datetime.today()
    filedir = '/%d/%d/' % (today.year, today.month)
    url_part = dir_name + filedir
    if not os.path.exists(url_part):
        os.makedirs(url_part)

    return url_part, filedir

## 给图片添加水印
def setup_picture_shuiyin(img_name,file_path,company_id,img_source):

    print('值 img_name ---->>',img_name)
    print('值 file_path ---->>',file_path)
    print('值 company_id ---->>',company_id)
    print('值 img_source ---->>',img_source)

    _file_path = BASE_DIR + '/' + file_path
    # im = Image.open('/tmp/zhangju/_20190212123822.jpg').convert('RGBA')
    print('值 BasePath --------->>', BASE_DIR)
    print('值 file_path --------->>', _file_path)
    print('值是否存在 _file_path ------->', os.path.exists(_file_path))

    # return False

    # ret = subprocess.Popen('/bin/cp  %s  /data/tmp' % (_file_path),shell=True)
    # print('------ subprocess 返回码 -------->>', ret)
    # ret.wait()
    # now_file_name = '/data/tmp/' + img_name
    ret = subprocess.Popen('du -sk  %s ' % (_file_path),shell=True)
    print('ret.stdout.read() --------->>',ret.stdout.read())

    print('【2】值 os.path.getsize(img_path) ---------->>', os.path.getsize(_file_path))

    file_size = os.path.getsize(_file_path)
    if file_size == 0:
        return False

    try:

        im = Image.open(_file_path).convert('RGBA')
        txt=Image.new('RGBA', im.size, (0,0,0,0))
        # fnt=ImageFont.truetype("c:/Windows/fonts/Tahoma.ttf", 30)
        width, height = txt.size

        x, _v = divmod(height, 100)
        font_size = 10 + x * 10

        fnt=ImageFont.truetype("/usr/share/fonts/chinese/simsun.ttc", font_size)
        d=ImageDraw.Draw(txt)
        shuiyin_name = ''
        if img_source == 'article':
            shuiyin_name = models.zgld_gongzhonghao_app.objects.get(company_id=company_id).name

        elif img_source == 'case':
            shuiyin_name = models.zgld_xiaochengxu_app.objects.get(company_id=company_id).name

        d.text((10, txt.size[1]-30), shuiyin_name,font=fnt, fill=(255,255,255,255))
        out=Image.alpha_composite(im, txt)

        print('值 txt.size[0] ---->>',txt.size[0])
        print('值 txt.size[1] ---->>',txt.size[1])

        print('值  file_path.split[0] --->' , file_path.split('.')[0])
        front_file_name = file_path.split('.')[0]
        file_name =  front_file_name + '.png'

        out.save(file_name)
        return file_name

    except OSError as e:
        print('转换报错 ---->>', e)
        return False




# 图片上传
@csrf_exempt
def ueditor_image_upload(request):

    # action为config 从服务器返回配置
    # https://github.com/bffor/python-ueditor
    # http://127.0.0.1:8001/zhugeleida/public/ueditor_img_upload?action=config
    if request.GET.get('action') == 'config':
        '''
        为uploadimage 上传图片 对图片进行处理
        config.json 配置文件 详细设置参考：http://fex.baidu.com/ueditor/#server-deploy
        '''

        # f = open('config.json', encoding='utf-8')
        # data = f.read()
        # f.close()
        # temp = json.loads(data)
        # callbackname = request.GET.get('callback')
        # # 防止XSS 过滤  callbackname只需要字母数字下划线
        # pattern = re.compile('\w+', re.U)
        # matchObj = re.findall(pattern, callbackname, flags=0)
        # callbacks = matchObj[0] + '(' + json.dumps(temp) + ')'
        # return HttpResponse(callbacks)
        from zhugeleida.views_dir.public.config import UEditorUploadSettings
        if "callback" not in request.GET:
            return JsonResponse(UEditorUploadSettings)
        else:
            return_str = "{0}({1})".format(request.GET["callback"], json.dumps(UEditorUploadSettings, ensure_ascii=False))
            return HttpResponse(return_str)



    elif request.GET.get('action') == 'uploadimage':
        img = request.FILES.get('upfile')
        name = request.FILES.get('upfile').name

        print('------request.FILES-------->>',request.FILES.get,img,name)

        allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp']
        # file_suffix = name.split(".")[-1]
        file_suffix = name.split(".")[-1]

        if file_suffix not in allow_suffix:
            return {"state": 'error', "name": name, "url": "", "size": "", "type": file_suffix}

        # 上传文件路径
        dir_name = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article')
        url_part, filedir = upload_generation_dir(dir_name)

        file_name = str(uuid.uuid1()) + "." + file_suffix
        path_file = os.path.join(url_part, file_name)
        file_url = url_part + file_name

        filenameurl = '/statics/zhugeleida/imgs/admin/article' + filedir + file_name
        with open(file_url, 'wb+') as destination:
            for chunk in img.chunks():
                destination.write(chunk)
        data = {"state": 'SUCCESS', "url": filenameurl, "title": file_name, "original": name, "type": file_suffix}

        print('-------data-------->>',data)

        return JsonResponse(data)


















