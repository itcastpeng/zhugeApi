from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.diary_manage_verify import PraiseDiaryForm, diarySelectForm, \
    ReviewDiaryForm, DiaryReviewSelectForm, BrowseCaseSelectForm, CollectionDiaryForm
from django.db.models import F, Q
import json, datetime, base64,requests
from publicFunc.condition_com import conditionCom
from zhugeapi_celery_project import tasks
from zhugeleida.views_dir.conf import Conf
from zhugeapi_celery_project import tasks
from publicFunc.Response import ResponseObj
from zhugeleida.views_dir.admin.dai_xcx import create_authorizer_access_token
from django.shortcuts import render
import os, redis, requests


# 记录查询日志 (动能日志/ diary_manage调用)
def record_view_log(data):
    u_id = data.get('user_id')
    customer_id = data.get('customer_id')
    log_count = models.zgld_accesslog.objects.filter(**data).count()
    if int(log_count) == 0:
        remark = '首次查看您的日记详情, 沟通从此刻开始'
    elif int(log_count) == 1:
        remark = '查看您的日记详情/第{}次, 把握深度交流的机会'.format(log_count)
    elif int(log_count) == 2:
        remark = '查看您的日记详情/第{}次, 建议标注重点客户'.format(log_count)
    else:
        remark = '查看您的日记详情/第{}次, 成交在望'.format(log_count)

    models.zgld_accesslog.objects.create(
        action=22,
        user_id=u_id,
        customer_id=customer_id,
        remark=remark
    )


# 查询日记
@csrf_exempt
@account.is_token(models.zgld_customer)
def diary_manage(request):
    response = Response.ResponseObj()
    forms_obj = diarySelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')

        u_id = request.GET.get('u_id')
        case_id = request.GET.get('case_id')    # 列表ID 判断日记类型 时间轴展示所有数据/普通展示详情
        user_id = request.GET.get('user_id')    # 客户ID

        case_type = int(request.GET.get('case_type')) # 日记类型(1普通/2时间轴)

        ## 搜索条件
        field_dict = {
            'company_id': '',
            'id': '',
            'title__contains': '',  # 日记标题 模糊匹配
        }
        q = conditionCom(request, field_dict)

        data_list = []
        count = 0

        # 普通日记
        if case_type == 1:

            # 普通日记 阅读量增加
            diary_objs = models.zgld_diary.objects.filter(id=case_id)
            if diary_objs:
                diary_objs.update(  # 阅读次数
                    read_count=F('read_count') + 1
                )
                models.zgld_diary_action.objects.create(
                    action=3,
                    customer_id=user_id,
                    diary_id=case_id
                )

                for diary_obj in diary_objs:

                    cover_picture = ''
                    if diary_obj.cover_picture:  # 封面（取第一张）
                        cover_picture = json.loads(diary_obj.cover_picture)

                    customer_name = diary_obj.case.customer_name
                    customer_headimgurl = diary_obj.case.headimgurl
                    content = diary_obj.content
                    data_list.append({
                        'cover_picture': cover_picture,
                        'customer_headimgurl': customer_headimgurl,
                        'customer_name': customer_name,
                        'title': diary_obj.title,
                        'content': content,
                        'read_count': diary_obj.read_count,                 # 阅读数量
                        'up_count': diary_obj.up_count,                     # 点赞数量
                        'comment_count': diary_obj.comment_count,           # 评论数量
                        'create_date': diary_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    })

            response.note = {
                'cover_picture': '轮播图',
                'customer_headimgurl': '客户头像',
                'customer_name': '客户名称',
                'content': '日记内容',
                'title': '日记标题',
                'up_count': '点赞数量',
                'comment_count': '评论数量',
                'read_count': '阅读数量',
                'create_date': '创建时间',
            }

        # 时间轴
        else:

            # 时间轴 阅读量增加
            zgld_case_objs = models.zgld_case.objects.filter(id=case_id)

            customer_name = ''          # 客户名称
            create_date = ''            # 创建时间
            become_beautiful_cover = '' # 变美图片
            if zgld_case_objs:
                zgld_case_obj = zgld_case_objs[0]
                customer_name = zgld_case_obj.customer_name
                create_date = zgld_case_obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                become_beautiful_cover = json.loads(zgld_case_obj.become_beautiful_cover)

                zgld_case_objs.update(
                    read_count=F('read_count') + 1
                )
                models.zgld_diary_action.objects.create(
                    action=3,
                    customer_id=user_id,
                    case_id=case_id
                )

            objs = models.zgld_diary.objects.filter(
                case_id=case_id,
                diary_date__lte=datetime.datetime.today(), # 添加日记时 会选择发布日期 发布日期小于今天才展示
            ).order_by('-diary_date')

            count = objs.count()
            result_data = []

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            for obj in objs:
                cover_picture = ''
                if obj.cover_picture:  # 封面
                    cover_picture = json.loads(obj.cover_picture)

                diary_give_like = models.zgld_diary_action.objects.filter(diary_id=obj.id, action=1).count() # 点赞数量统计

                result_data.append({
                    'cover_picture': cover_picture,
                    'diary_date': obj.diary_date.strftime('%Y-%m-%d %H:%M:%S'), # 发布时间
                    'title': obj.title,
                    'content': obj.content,
                    'diary_give_like': diary_give_like,     # 点赞数量
                    'diary_read_num': obj.read_count,       # 阅读数量
                    'comment_count': obj.comment_count,     # 评论数量
                })

            data_list = {
                'become_beautiful_cover': become_beautiful_cover,
                'customer_name': customer_name,
                'result_data': result_data,
                'create_date': create_date,
                'count': count,
            }
            response.note = {
                'become_beautiful_cover': '变美图片',
                'customer_name': '客户名称',
                'result_data': {
                    'cover_picture': '封面图片',
                    'diary_date': '发布时间',
                    'title': '日记标题',
                    'content': '日记内容',
                    'diary_give_like': '点赞数量',
                    'diary_read_num': '阅读数量',
                    'comment_count': '评论数量',
                },
                'create_date': '创建时间',
                'count': '该时间轴 日记总数 /可做分页',
            }

        # 记录该客户 点击查看日记详情日志 (动能记录)
        data = {
            'action': 22,
            'customer_id': user_id,
            'user_id': u_id
        }
        record_view_log(data)

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': data_list,
            'data_count': count
        }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)






# 生成海报相关信息页面用于截图使用
@csrf_exempt
def diary_poster_html(request):

    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        customer_id = request.GET.get('customer_id')
        user_customer_belonger_id = request.GET.get('user_customer_belonger_id')
        case_id = request.GET.get('case_id')
        company_id = request.GET.get('company_id')

        poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
            user_customer_belonger_id=user_customer_belonger_id, case_id=case_id)

        print('值 user_customer_belonger_id ---->',user_customer_belonger_id)
        print('值 case_id ---->', case_id)

        qr_code = ''
        if poster_belonger_objs:
            poster_belonger_obj = poster_belonger_objs[0]
            qr_code = poster_belonger_obj.qr_code

        case_objs = models.zgld_case.objects.filter(id=case_id)
        poster_cover = []
        if case_objs:
            poster_cover = case_objs[0].poster_cover
            if poster_cover:
                poster_cover = json.loads(poster_cover)
            else:
                poster_cover = ''

        poster_company_logo = models.zgld_xiaochengxu_app.objects.get(company_id=company_id).poster_company_logo

        ret_data = {
            'poster_company_logo' :poster_company_logo,
            'qr_code_url': qr_code,
            'poster_cover' : poster_cover
        }
        print('ret_data ------>>',ret_data)

        return render(request, 'poster_case.html', locals())


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@csrf_exempt
def create_user_customer_case_poster_qr_code(data):
    response = ResponseObj()

    user_id = data.get('user_id')
    customer_id = data.get('customer_id')
    user_customer_belonger_id = data.get('user_customer_belonger_id')
    case_id = data.get('case_id')
    company_id = data.get('company_id')

    poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(user_customer_belonger_id=user_customer_belonger_id,case_id=case_id)
    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/diary_manage/poster_html?user_id=%s&uid=%s&case_id=%s&company_id=%s&user_customer_belonger_id=%s' % (
        customer_id, user_id, case_id,company_id,user_customer_belonger_id)

    qr_code = ''
    if poster_belonger_objs:
        poster_belonger_obj = poster_belonger_objs[0]
        qr_code =  poster_belonger_obj.qr_code
        poster_url =  poster_belonger_obj.poster_url

        if not  poster_url:
            data_dict = {
                'user_id': user_id,
                'customer_id': customer_id,
                'poster_url': url,
                'user_customer_belonger_id': user_customer_belonger_id,
                'case_id': case_id

            }
            tasks.create_user_or_customer_small_program_poster.delay(json.dumps(data_dict))


    if  qr_code:
        response.data = {'qr_code': qr_code}
        print('海报存在二维码 ------>>',qr_code)
        response.code = 200
        response.msg = "存在二维码"

    else:
        print('海报不存在二维码 ------>>', qr_code)

        xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)

        if xiaochengxu_app_objs:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            path = '/pages/detail/detail?uid=%s&case_id=%s&source=1' % (user_id, case_id)
            user_qr_code = '/case_%s_customer_%s_user_%s_%s_qrcode.jpg' % (case_id, customer_id, user_id, now_time)

            get_qr_data = {}
            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

            # userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
            # company_id = userprofile_obj.company_id

            authorizer_refresh_token = xiaochengxu_app_objs[0].authorizer_refresh_token
            authorizer_appid = xiaochengxu_app_objs[0].authorization_appid

            key_name = '%s_authorizer_access_token' % (authorizer_appid)

            authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

            if not authorizer_access_token:
                data = {
                    'key_name': key_name,
                    'authorizer_refresh_token': authorizer_refresh_token,
                    'authorizer_appid': authorizer_appid,
                    'company_id': company_id
                }
                authorizer_access_token_ret = create_authorizer_access_token(data)
                authorizer_access_token = authorizer_access_token_ret.data  # 调用生成 authorizer_access_token 授权方接口调用凭据, 也简称为令牌。

            get_qr_data['access_token'] = authorizer_access_token

            post_qr_data = {'path': path, 'width': 430}

            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            qr_ret = s.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

            # qr_ret = requests.post(Conf['qr_code_url'], params=get_qr_data, data=json.dumps(post_qr_data))

            if not qr_ret.content:
                rc.delete('xiaochengxu_token')
                response.msg = "生成小程序二维码未验证通过"

                return response

            # print('-------qr_ret---->', qr_ret.text)

            IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'qr_code') + user_qr_code
            with open('%s' % (IMG_PATH), 'wb') as f:
                f.write(qr_ret.content)

            user_obj = ''
            if customer_id:
                user_obj = models.zgld_user_customer_belonger.objects.get(user_id=user_id, customer_id=customer_id)
                qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code


                print('----celery生成用户-客户对应的小程序二维码成功-->>',
                      'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code)

                # # 一并生成案例海报

                data_dict = {
                    'user_id': user_id,
                    'customer_id': customer_id,
                    'poster_url': url,
                    'user_customer_belonger_id' : user_customer_belonger_id,
                    'case_id' : case_id

                }

                if qr_code:
                    case_poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                        user_customer_belonger_id=user_customer_belonger_id,
                        case_id=case_id
                    )
                    if case_poster_belonger_objs:
                        case_poster_belonger_objs.update(
                            qr_code=qr_code
                        )

                    else:
                        models.zgld_customer_case_poster_belonger.objects.create(
                            user_customer_belonger_id=user_customer_belonger_id,
                            case_id=case_id,
                            qr_code=qr_code
                        )

                tasks.create_user_or_customer_small_program_poster.delay(json.dumps(data_dict))


            response.data = {'qr_code': qr_code}
            response.code = 200
            response.msg = "生成小程序二维码成功"

    return response


# 日记其他操作
@csrf_exempt
@account.is_token(models.zgld_customer)
def diary_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 评论日记
        if oper_type == 'review_diary':

            from_customer_id = request.GET.get('user_id')
            content = request.POST.get('content')

            request_data_dict = {
                'diary_id': o_id,
                'content': content,  # 文章所属用户的ID
                'customer_id': from_customer_id,  # 文章所属用户的ID
            }

            forms_obj = ReviewDiaryForm(request_data_dict)
            if forms_obj.is_valid():

                encodestr = base64.b64encode(content.encode('utf-8'))
                msg = str(encodestr, 'utf-8')

                create_data = {
                    'diary_id': o_id,
                    'content': msg,
                    'from_customer_id': from_customer_id
                }
                models.zgld_diary_comment.objects.create(**create_data)
                diary_objs = models.zgld_diary.objects.filter(id=o_id)
                if diary_objs:
                    diary_objs.update(
                        comment_count=F('comment_count') + 1
                    )
                ## 记录单个案例浏览量
                case_objs = models.zgld_case.objects.filter(id=diary_objs[0].case_id)
                if case_objs:
                    case_objs.update(
                        comment_count=F('comment_count') + 1
                    )

                response.code = 200
                response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        ## 点赞日记
        elif oper_type == 'praise_diary':
            customer_id = request.GET.get('user_id')
            # status = request.POST.get('status')

            request_data_dict = {
                'diary_id': o_id,
                'status': 1,  # 文章所属用户的ID

            }

            forms_obj = PraiseDiaryForm(request_data_dict)
            if forms_obj.is_valid():

                create_data = {
                    'diary_id': o_id,
                    'customer_id': customer_id,
                    'status': 1,
                    'action': 1  # 点赞
                }
                diary_objs = models.zgld_diary.objects.filter(id=o_id)
                diary_up_down_objs = models.zgld_diary_action.objects.filter(action=1, diary_id=o_id,
                                                                             customer_id=customer_id)
                if diary_up_down_objs:
                    diary_up_down_objs.update(
                        status=1
                    )
                    response.code = 302
                    response.msg = "已经点过赞了"
                    response.data = {
                        'up_count': diary_objs[0].up_count,
                        'is_praise_diary': 1,
                        'is_praise_diary_text': '已赞过此日记'
                    }
                else:
                    models.zgld_diary_action.objects.create(**create_data)

                    if diary_objs:
                        diary_objs.update(
                            up_count=F('up_count') + 1
                        )
                    response.data = {
                        'up_count': diary_objs[0].up_count,
                        'is_praise_diary': 1,
                        'is_praise_diary_text': '已赞此案例'
                    }
                    response.code = 200
                    response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 浏览案例记录(我-我的足迹)
        elif oper_type == 'browse_case_list_record':
            print('request.GET----->', request.GET)

            forms_obj = BrowseCaseSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                order = request.GET.get('order', '-create_date')
                customer_id = request.GET.get('user_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('customer_id', customer_id))
                q1.children.append(('action', 3))

                print('-----q1---->>', q1)
                objs = models.zgld_diary_action.objects.select_related('case', 'customer').filter(q1).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    status = obj.case.status
                    status_text = obj.case.get_status_display()

                    cover_picture = obj.case.cover_picture
                    if cover_picture:
                        cover_picture = json.loads(cover_picture)

                    _case_id = obj.case_id
                    ## 查找出最新更新的日记
                    last_diary_data = ''
                    diary_objs = models.zgld_diary.objects.filter(case_id=_case_id).order_by('-create_date')
                    if diary_objs:

                        diary_obj = diary_objs[0]
                        _status = diary_obj.status
                        _status_text = diary_obj.get_status_display()
                        _cover_picture = diary_obj.cover_picture
                        _content = diary_obj.content

                        if _cover_picture:
                            _cover_picture = json.loads(_cover_picture)
                        # if _content:
                        #     _content = json.loads(_content)

                        last_diary_data = {
                            'diary_id': diary_obj.id,
                            'case_id': diary_obj.case_id,
                            'company_id': diary_obj.company_id,

                            'title': diary_obj.title,
                            'diary_date': diary_obj.diary_date.strftime(
                                '%Y-%m-%d %H:%M:%S') if diary_obj.diary_date else '',
                            'cover_picture': _cover_picture,
                            'content': _content,

                            'status': _status,
                            'status_text': _status_text,

                            'cover_show_type': diary_obj.cover_show_type,
                            'cover_show_type_text': diary_obj.get_cover_show_type_display(),

                            'create_date': diary_obj.create_date.strftime('%Y-%m-%d') if diary_obj.create_date else '',
                        }

                    tag_list = list(obj.case.tags.values('id', 'name'))
                    ret_data.append({
                        'case_id': _case_id,
                        'company_id': obj.case.company_id,
                        'customer_name': obj.case.customer_name,

                        'headimgurl': obj.case.headimgurl,
                        'cover_picture': cover_picture,

                        'status': status,
                        'status_text': status_text,
                        'tag_list': tag_list,

                        'last_diary_data': last_diary_data,  # 最后日记的内容

                        'create_date': obj.create_date.strftime('%Y-%m-%d') if obj.create_date else '',
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

        # 收藏(我-我的收藏)
        elif oper_type == 'collection_case_list_record':
            print('request.GET----->', request.GET)

            forms_obj = BrowseCaseSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)

                order = request.GET.get('order', '-create_date')
                customer_id = request.GET.get('user_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('customer_id', customer_id))
                q1.children.append(('action', 2))  # (2, '收藏日记'),
                q1.children.append(('status', 1))  # (1, '已点赞|已收藏')

                print('-----q1---->>', q1)
                objs = models.zgld_diary_action.objects.select_related('case', 'customer').filter(q1).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    status = obj.case.status
                    status_text = obj.case.get_status_display()

                    cover_picture = obj.case.cover_picture
                    if cover_picture:
                        cover_picture = json.loads(cover_picture)

                    _case_id = obj.case_id
                    ## 查找出最新更新的日记
                    last_diary_data = ''
                    diary_objs = models.zgld_diary.objects.filter(case_id=_case_id).order_by('-create_date')
                    if diary_objs:

                        diary_obj = diary_objs[0]
                        _status = diary_obj.status
                        _status_text = diary_obj.get_status_display()
                        _cover_picture = diary_obj.cover_picture
                        _content = diary_obj.content

                        if _cover_picture:
                            _cover_picture = json.loads(_cover_picture)

                        last_diary_data = {
                            'diary_id': diary_obj.id,
                            'case_id': diary_obj.case_id,
                            'company_id': diary_obj.company_id,

                            'title': diary_obj.title,
                            'diary_date': diary_obj.diary_date.strftime(
                                '%Y-%m-%d %H:%M:%S') if diary_obj.diary_date else '',
                            'cover_picture': _cover_picture,
                            'content': _content,

                            'status': _status,
                            'status_text': _status_text,

                            'cover_show_type': diary_obj.cover_show_type,
                            'cover_show_type_text': diary_obj.get_cover_show_type_display(),

                            'create_date': diary_obj.create_date.strftime(
                                '%Y-%m-%d %H:%M:%S') if diary_obj.create_date else '',
                        }

                    tag_list = list(obj.case.tags.values('id', 'name'))
                    ret_data.append({
                        'case_id': _case_id,
                        'company_id': obj.case.company_id,
                        'customer_name': obj.case.customer_name,

                        'headimgurl': obj.case.headimgurl,
                        'cover_picture': cover_picture,

                        'status': status,
                        'status_text': status_text,
                        'tag_list': tag_list,

                        'last_diary_data': last_diary_data,  # 最后日记的内容

                        'create_date': obj.create_date.strftime('%Y-%m-%d') if obj.create_date else '',
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

    elif request.method == 'GET':

        ## 文章评论列表展示
        if oper_type == 'diary_review_list':

            customer_id = request.GET.get('user_id')
            form_data = {
                'diary_id': o_id
            }
            forms_obj = DiaryReviewSelectForm(form_data)

            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                objs = models.zgld_diary_comment.objects.select_related('from_customer', 'to_customer').filter(diary_id=o_id).filter(Q(is_audit_pass=1) | Q(from_customer=customer_id)).order_by('-create_date')

                count = objs.count()
                if objs:

                    # if length != 0:
                    #     start_line = (current_page - 1) * length
                    #     stop_line = start_line + length
                    #     objs = objs[start_line: stop_line]

                    ret_data = []
                    for obj in objs:

                        try:
                            username = base64.b64decode(obj.from_customer.username)
                            customer_name = str(username, 'utf-8')
                            print('----- 解密b64decode username----->', username)
                        except Exception as e:
                            print('----- b64decode解密失败的 customer_id 是 | e ----->', obj.from_customer_id, "|", e)
                            customer_name = '客户ID%s' % (obj.from_customer_id)

                        _content = base64.b64decode(obj.content)
                        content = str(_content, 'utf-8')
                        print('----- 解密b64decode 内容content----->', content)

                        ret_data.append({
                            'from_customer_id': obj.from_customer_id,
                            'from_customer_name': customer_name,
                            'from_customer_headimgurl': obj.from_customer.headimgurl,
                            'content': content,
                            'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }

                else:
                    response.code = 302
                    response.msg = '没有数据'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 收藏案例
        elif oper_type == 'collection_case':
            customer_id = request.GET.get('user_id')
            case_id = request.POST.get('case_id')
            status = request.POST.get('status')

            request_data_dict = {
                'case_id': case_id,
                'status': status,  # 文章所属用户的ID
            }

            forms_obj = CollectionDiaryForm(request_data_dict)
            if forms_obj.is_valid():

                create_data = {
                    'case_id': case_id,
                    'customer_id': customer_id,
                    'status': status,
                    'action': 2  # 收藏
                }

                case_up_down_objs = models.zgld_diary_action.objects.filter(action=2, case_id=case_id,
                    customer_id=customer_id)
                if case_up_down_objs:

                    case_up_down_objs.update(
                        status=status
                    )
                    case_up_down_obj = case_up_down_objs[0]
                    status = case_up_down_obj.status
                    status_text = case_up_down_obj.get_status_display()

                    response.data = {
                        'status': status,
                        'status_text': status_text
                    }
                    response.code = 200
                    response.msg = "记录成功"

                else:
                    case_up_down_obj = models.zgld_diary_action.objects.create(**create_data)
                    response.data = {
                        'status': case_up_down_obj.status,
                        'status_text': '已收藏此案例'
                    }
                    response.code = 200
                    response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

            ## 点赞案例

        # 时间轴日记列表 和 普通日记 点赞
        elif oper_type == 'praise_case':
            customer_id = request.GET.get('user_id')
            case_id = o_id                                  # 日记ID
            case_type = request.GET.get('case_type')        # 日记类型
            diary_id = request.GET.get('diary_id')          # 时间轴详情ID
            if case_type:
                case_type = int(case_type)

            form_data = {
                'case_id': case_id,
                'customer_id': customer_id,
                'diary_id': diary_id,
                'case_type': case_type,
            }
            forms_obj = CollectionDiaryForm(form_data)
            if forms_obj.is_valid():
                formData = forms_obj.cleaned_data

                # 时间轴日记详情点赞
                if diary_id:
                    diary_id = formData.get('diary_id')
                    objs = models.zgld_diary_action.objects.filter(
                        action=1,
                        diary_id=diary_id,
                        customer_id=formData.get('customer_id')
                    )
                    if objs:
                        response.msg = '已赞过此日记'

                    else:
                        models.zgld_diary_action.objects.create(
                            action=1,
                            diary_id=diary_id,
                            customer_id=formData.get('customer_id')
                        )
                        response.msg = '点赞成功'
                else:
                    # 普通日记点赞
                    if case_type == 1:
                        zgld_diary_action_objs = models.zgld_diary_action.objects.filter(
                            action=1,
                            diary_id=formData.get('case_id'),
                            customer_id=formData.get('customer_id')
                        )
                        if zgld_diary_action_objs:
                            response.msg = '已赞过此日记'

                        else:
                            models.zgld_diary_action.objects.create(
                                action=1,
                                diary_id=formData.get('case_id'),
                                customer_id=formData.get('customer_id')
                            )
                            response.msg = '点赞成功'

                    # 时间轴列表点赞
                    else:
                        zgld_diary_action_objs = models.zgld_diary_action.objects.filter(
                            action=1,
                            case_id=formData.get('case_id'),
                            customer_id=formData.get('customer_id')
                        )
                        if zgld_diary_action_objs:
                            response.msg = '已赞过此日记列表'

                        else:
                            models.zgld_diary_action.objects.create(
                                action=1,
                                case_id=formData.get('case_id'),
                                customer_id=formData.get('customer_id')
                            )
                            response.msg = '点赞成功'

                response.code = 200

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



        ## 小程序-案例-海报内容
        elif oper_type == 'xcx_case_poster':
            customer_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            company_id = request.GET.get('company_id')
            case_id = request.GET.get('case_id')

            ret_data = []
            app_obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
            poster_company_logo = app_obj.poster_company_logo

            print('值customer_id------>>', customer_id)
            print('值customer_id------>>', customer_id)
            user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,
                user_id=uid)

            user_customer_belonger_id = ''
            if user_customer_belonger_objs:
                user_customer_belonger_id = user_customer_belonger_objs[0].id
            print('user_customer_belonger_objs ------->>', user_customer_belonger_objs)
            objs = models.zgld_diary.objects.filter(id=case_id)
            if objs:
                case_objs = models.zgld_case.objects.filter(id=objs[0].case_id)
                if case_objs:
                    poster_cover = case_objs[0].poster_cover

                    if poster_cover:
                        poster_cover = json.loads(poster_cover)
                    else:
                        poster_cover = []

                    _data = {
                        'user_id': uid,
                        'customer_id': customer_id,
                        'case_id': case_id,
                        'company_id': company_id,
                        'user_customer_belonger_id': user_customer_belonger_id
                    }
                    print('_data ------>>', _data)

                    _response = create_user_customer_case_poster_qr_code(_data)

                    qr_code = ''
                    if _response.code == 200:
                        qr_code = _response.data.get('qr_code')

                    ret_data.append(
                        {
                            'case_id': case_id,
                            'poster_cover': poster_cover,
                            'poster_company_logo': poster_company_logo or '',
                            'qr_code': qr_code or ''
                        }
                    )

                    response.data = ret_data
                    response.note = {
                        'case_id': '案例ID',
                        'poster_cover': '海报封面',
                        'poster_company_logo': '海报公司log'
                    }

                    response.code = 200
                    response.msg = "返回成功"


            else:
                response.code = 301
                response.msg = "案例不存在"

            ## 小程序获取案例海报截图


        elif oper_type == 'xcx_get_case_poster_screenshots':
            customer_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            company_id = request.GET.get('company_id')
            case_id = request.GET.get('case_id')

            ret_data = []

            user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,
                user_id=uid)

            user_customer_belonger_id = ''
            if user_customer_belonger_objs:
                user_customer_belonger_id = user_customer_belonger_objs[0].id

            _data = {
                'user_id': uid,
                'customer_id': customer_id,
                'case_id': case_id,
                'company_id': company_id,
                'user_customer_belonger_id': user_customer_belonger_id
            }

            poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                user_customer_belonger_id=user_customer_belonger_id, case_id=case_id)

            poster_url = ''
            if poster_belonger_objs:
                poster_belonger_obj = poster_belonger_objs[0]
                poster_url = poster_belonger_obj.poster_url
                source = 1  # 生成 扫码的海报
                if not poster_url:
                    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/diary_manage/poster_html?user_id=%s&uid=%s&case_id=%s&company_id=%s&user_customer_belonger_id=%s&source=%s' % (
                        customer_id, uid, case_id, company_id, user_customer_belonger_id, source)

                    data_dict = {
                        'user_id': uid,
                        'poster_url': url,
                        'customer_id': customer_id,
                        'user_customer_belonger_id': user_customer_belonger_id,
                        'case_id': case_id

                    }
                    tasks.create_user_or_customer_small_program_poster(json.dumps(data_dict))

                    # _response = create_user_customer_case_poster_qr_code(_data)
                    poster_url = poster_belonger_obj.poster_url

            ret_data.append(
                {
                    'case_id': case_id,
                    'poster_url': poster_url,

                }
            )

            response.data = ret_data
            response.note = {
                'case_id': '案例ID',
                'poster_cover': '海报封面',
                'poster_company_logo': '海报公司log'
            }

            response.code = 200
            response.msg = "返回成功"

    return JsonResponse(response.__dict__)
