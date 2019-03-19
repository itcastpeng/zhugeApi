from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from bs4 import BeautifulSoup
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.diary_manage_verify import SetFocusGetRedPacketForm, diaryAddForm, diarySelectForm, diaryUpdateForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm
import requests,cv2,os
import json,datetime
from django.db.models import Q, Sum, Count
import threading





def create_video_coverURL(obj,url):

    s = requests.session()
    s.keep_alive = False  # 关闭多余连接

    res = s.get(url,stream=True)

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
    video_filename = "/diary_video_%s_%s.mp4" % (obj.id,now_time)  # amr
    video_file_dir = os.path.join('statics', 'zhugeleida','imgs','admin' ,'diary') + video_filename

    # 写入收到的视频数据
    with open(video_file_dir, 'ab') as file:
        file.write(res.content)
        file.flush()
    print('x下载的视频链接 video_file_dir ------->',video_file_dir)
    video_url = url
    _cover_picture_list = []

    img_file_dir =  get_video_pic(video_file_dir)
    _cover_picture_list.append(video_url)
    _cover_picture_list.append(img_file_dir)
    cover_picture_list = json.dumps(_cover_picture_list)
    obj.cover_picture = cover_picture_list
    obj.save()


    return img_file_dir

def get_video_pic(video_file_dir):
    cap = cv2.VideoCapture(video_file_dir)
    cap.set(1, int(cap.get(7)/2)) # 取它的中间帧
    rval, frame = cap.read() # 如果rval为False表示这个视频有问题，为True则正常
    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
    video_cover_picture_filename = "diary_video_cover_picture_%s_%s.jpg" % (1, now_time)  # amr

    video_cover_picture_file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'diary') + video_cover_picture_filename
    if rval:
        cv2.imwrite(video_cover_picture_file_dir, frame)  # 存储为图像
        os.remove(video_file_dir)
    print('视频地址 video_cover_picture_file_dir --------->',video_cover_picture_file_dir)

    cap.release()
    return  video_cover_picture_file_dir


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def diary_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        # 查询 文章-活动(任务)
        if oper_type == 'diary_list':

            print('request.GET----->', request.GET)

            forms_obj = diarySelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')
                case_id = request.GET.get('case_id')

                ## 搜索条件
                diary_id = request.GET.get('diary_id')  #
                search_activity_status = request.GET.get('status')  #
                title = request.GET.get('title')  #

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))
                if case_id:
                    q1.children.append(('case_id', case_id))

                if title:
                    q1.children.append(('title__contains', title))

                if diary_id:
                    q1.children.append(('id', diary_id))

                # now_date_time = datetime.datetime.now()
                if search_activity_status:
                    q1.children.append(('status', search_activity_status))  #


                print('-----q1---->>', q1)
                objs = models.zgld_diary.objects.select_related('company').filter(q1).order_by(order).exclude(status__in=[3])
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []

                if objs:
                    for obj in objs:
                        status = obj.status
                        status_text = obj.get_status_display()
                        content = obj.content

                        cover_picture = []
                        if obj.cover_picture:
                            cover_picture =  json.loads(obj.cover_picture)

                        poster_cover = []
                        if obj.poster_cover:
                            poster_cover = eval(obj.poster_cover)

                        ret_data.append({
                            'diary_id': obj.id,
                            'case_id': obj.case_id,
                            'company_id': obj.company_id,

                            'title': obj.title,
                            'diary_date' : obj.diary_date.strftime('%Y-%m-%d') if obj.diary_date else '',
                            'cover_picture': cover_picture,
                            'summary': obj.summary,
                            'content': content,
                            'poster_cover': poster_cover,

                            'status': status,
                            'status_text': status_text,

                            'cover_show_type' : obj.cover_show_type,
                            'cover_show_type_text' : obj.get_cover_show_type_display(),

                            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                        })

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }


            else:

                response.code = 301
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())



    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def diary_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 删除-案例
        if oper_type == "delete":
            company_id = request.GET.get('company_id')
            objs = models.zgld_diary.objects.filter(id=o_id,company_id=company_id)
            if objs:
                obj = objs[0]
                models.zgld_diary_action.objects.filter(diary_id=obj.id).delete()
                models.zgld_diary_comment.objects.filter(diary_id=obj.id).delete()
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '案例不存在'

        # 修改-案例
        elif oper_type == 'update':

            diary_id = o_id
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            case_id = request.POST.get('case_id')
            title = request.POST.get('title')
            diary_date = request.POST.get('diary_date')
            content = request.POST.get('content')
            status = request.POST.get('status')
            cover_show_type = request.POST.get('cover_show_type')  # (1,'只展示图片'),  (2,'只展示视频'),

            form_data = {
                'diary_id': diary_id,
                'company_id': company_id,
                'case_id': case_id,  # 日记列表ID
                'title': title,  # 日记标题
                'diary_date': diary_date,  # 活动名称
                'content': content,  # 日记内容
                'status': status,  # 日记状态(是否删除)
                'cover_show_type': cover_show_type,  # 展示图片封面或视频封面
            }

            forms_obj = diaryUpdateForm(form_data)
            if forms_obj.is_valid():

                diary_objs = models.zgld_diary.objects.filter(id=diary_id)


                diary_objs.update(
                    user_id = user_id,
                    case_id = case_id,
                    company_id = company_id,
                    title = title,
                    diary_date = diary_date,
                    content = content,
                    status = status,
                    cover_show_type = cover_show_type
                )

                if int(cover_show_type) == 1: # (1,'只展示图片')
                    _cover_picture = []
                    print('值 content ----->>',content)

                    soup = BeautifulSoup(content, 'html.parser')

                    img_tags = soup.find_all('img')
                    for img_tag in img_tags:
                        data_src = img_tag.attrs.get('src')
                        if data_src:
                            print(data_src)
                            _cover_picture.append(data_src)

                    diary_objs.update(
                        cover_picture=json.dumps(_cover_picture)
                    )

                case_objs = models.zgld_case.objects.filter(id=case_id)
                if case_objs:
                    case_objs.update(
                        update_date=datetime.datetime.now()
                    )

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 增加-案例
        elif oper_type == "add":
            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            case_id = request.POST.get('case_id')               # 日记列表ID
            title = request.POST.get('title')                   # 日记标题
            diary_date = request.POST.get('diary_date')         # 日记时间
            content = request.POST.get('content')               # 日记内容
            status = request.POST.get('status')                 # 日记状态(是否删除)
            cover_show_type  = request.POST.get('cover_show_type') # (1,'封面展示图片'),  (2,'封面展示视频'),
            cover_picture  = request.POST.get('cover_picture')  # 普通日记 上传(图片/视频)

            form_data = {
                'company_id' :company_id,
                'case_id' : case_id,                # 日记列表ID
                'title': title,                     # 日记标题
                'diary_date': diary_date,           # 活动名称
                'content': content,                 # 日记内容
                'status': status,                   # 日记状态(是否删除)
                'cover_show_type' : cover_show_type,# 展示图片封面或视频封面
                'cover_picture' : cover_picture,    # 图片/视频 普通日记轮播图
            }

            forms_obj = diaryAddForm(form_data)
            if forms_obj.is_valid():
                forms_data = forms_obj.cleaned_data
                models.zgld_diary.objects.create(
                    user_id=user_id,
                    company_id=forms_data.get('company_id'),
                    case_id=forms_data.get('case_id'),
                    title=forms_data.get('title'),
                    diary_date=forms_data.get('diary_date'),
                    content=forms_data.get('content'),
                    status=forms_data.get('status'),
                    cover_show_type=forms_data.get('cover_show_type'),
                    cover_picture=forms_data.get('cover_picture'),
                )

                # if int(cover_show_type) == 1:  # 获取内容图片 作为封面
                #     _cover_picture = []
                #     print('值 content cover_show_type----->>', content)
                #     soup = BeautifulSoup(content, 'html.parser')
                #
                #     img_tags = soup.find_all('img')
                #     for img_tag in img_tags:
                #         data_src = img_tag.attrs.get('src')
                #         if data_src:
                #             print(data_src)
                #             _cover_picture.append(data_src)
                #
                #     obj.cover_picture =  json.dumps(_cover_picture)
                #     obj.save()

                case_objs = models.zgld_case.objects.filter(id=case_id) # 该 日记列表 更新时间
                if case_objs:
                    case_objs.update(
                        update_date=datetime.datetime.now()
                    )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        ## 海报-设置(普通案列)
        elif oper_type == "poster_setting":
            poster_cover = request.POST.get('poster_cover')
            print('poster_cover-------> ', poster_cover)
            objs = models.zgld_diary.objects.filter(id=o_id)
            if poster_cover:
                poster_cover = json.loads(poster_cover)
            if objs:
                objs.update(poster_cover = json.dumps(poster_cover))
                response.code = 200
                response.msg = '设置日记海报成功'
            else:
                response.code = 301
                response.msg = '日记ID错误'

    return JsonResponse(response.__dict__)
