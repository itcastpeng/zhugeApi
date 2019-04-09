from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.diary_manage_verify import PraiseDiaryForm, diarySelectForm, \
    ReviewDiaryForm, DiaryReviewSelectForm, SelectForm, CollectionDiaryForm
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
from publicFunc.base64 import b64encode, b64decode
from zhugeleida.public.common import action_record


# 记录查询日志 (动能日志/ diary_manage调用)
def record_view_log(data):
    diary_name = data.get('diary_name')
    u_id = data.get('user_id')
    customer_id = data.get('customer_id')
    log_count = models.zgld_accesslog.objects.filter(
        customer_id=customer_id,
        user=u_id,
        action=22
    ).count()
    num = int(log_count) + 1
    if int(log_count) == 0:
        remark = '首次查看您的日记{diary_name}, 沟通从此刻开始'.format(diary_name=diary_name)
    elif int(log_count) == 1:
        remark = '查看您的日记{diary_name}/第{log_count}次, 把握深度交流的机会'.format(
            diary_name=diary_name,
            log_count=num
        )
    elif int(log_count) == 2:
        remark = '查看您的日记{diary_name}/第{log_count}次, 建议标注重点客户'.format(
            diary_name=diary_name,
            log_count=num
        )
    else:
        remark = '查看您的日记{diary_name}/第{log_count}次, 成交在望'.format(
            diary_name=diary_name,
            log_count=num
        )

    # models.zgld_accesslog.objects.create(
    #     action=22,
    #     user_id=u_id,
    #     customer_id=customer_id,
    #     remark=remark
    # )
    data['uid'] = u_id
    data['user_id'] = customer_id
    data['action'] = 22
    action_record(data, remark)  # 记录访问动作

# 查询日记
@csrf_exempt
@account.is_token(models.zgld_customer)
def diary_manage(request):
    response = Response.ResponseObj()
    forms_obj = diarySelectForm(request.GET)
    if forms_obj.is_valid():
        print('-=------------------------------------验证通过')
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')

        u_id = request.GET.get('u_id')
        case_id = request.GET.get('case_id')    # 列表ID 判断日记类型 时间轴展示所有数据/普通展示详情
        user_id = request.GET.get('user_id')    # 客户ID
        timeline_id = request.GET.get('timeline_id')    # 时间轴日记ID  (传此参数 查询时间轴详情 内容)

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
        if timeline_id:
            objs = models.zgld_diary.objects.filter(id=timeline_id).order_by(order)
            objs.update(  # 阅读次数
                read_count=F('read_count') + 1
            )

            models.zgld_diary_action.objects.create(
                action=3,
                customer_id=user_id,
                diary_id=timeline_id
            ) # 创建浏览日志

            obj = objs[0]
            cover_picture = []
            if obj.cover_picture:  # 封面（取第一张）
                cover_picture = json.loads(obj.cover_picture)

            is_diary_give_like = False # 是否点赞
            zgld_diary_action_obj = models.zgld_diary_action.objects.filter(
                action=1,
                customer_id=user_id,
                diary_id=obj.id
            )
            if zgld_diary_action_obj:
                is_diary_give_like = True

            is_collection = False   # 是否收藏
            is_collection_obj = models.zgld_diary_action.objects.filter(
                action=2,
                customer_id=user_id,
                diary_id=obj.id
            )
            if is_collection_obj:
                is_collection = True
            diary_name = obj.title # 记录动能日志
            data_list = {
                'cover_picture': cover_picture,
                'customer_headimgurl': obj.case.headimgurl,
                'customer_name': obj.case.customer_name,
                'title': obj.title,
                'content': obj.content,
                'read_count': obj.read_count,               # 阅读数量
                'up_count': obj.up_count,                   # 点赞数量
                'comment_count': obj.comment_count,         # 评论数量
                'case_type': 2,                             # 日记类型
                'is_diary_give_like': is_diary_give_like,   # 是否点赞
                'cover_show_type': obj.cover_show_type,     # 封面类型
                'is_collection': is_collection,             # 是否收藏
                'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            }
            response.note = {
                'cover_picture': '封面',
                'customer_headimgurl': '头像',
                'customer_name': '客户名称',
                'title': '日记标题',
                'content': '日记内容',
                'read_count': '阅读数量',
                'up_count': '点赞数量',
                'comment_count': '评论数量',
                'case_type': '日记类型',
                'is_diary_give_like': '是否点赞',
                'create_date': '创建时间',
            }
        else:
            # 普通日记
            if case_type == 1:

                # 普通日记 阅读量增加
                diary_objs = models.zgld_diary.objects.filter(id=case_id)

                diary_objs.update(  # 阅读次数
                    read_count=F('read_count') + 1
                )
                models.zgld_diary_action.objects.create(
                    action=3,
                    customer_id=user_id,
                    diary_id=case_id
                )

                diary_obj = diary_objs[0]

                # 该客户的 普通案例总数
                customer_name = diary_obj.case.customer_name
                case_type_one = diary_objs.filter(
                    case__customer_name=customer_name,
                    case__case_type=1
                ).count()
                # 该客户的 时间轴案例总数
                case_type_two = models.zgld_case.objects.filter(
                    customer_name=customer_name,
                    case_type=2
                ).count()
                customer_count = case_type_one + case_type_two

                # 是否点赞
                is_diary_give_like = False
                zgld_diary_action_obj = models.zgld_diary_action.objects.filter(
                    action=1,
                    customer_id=user_id,
                    diary_id=diary_obj.id
                )
                if zgld_diary_action_obj:
                    is_diary_give_like = True

                # 是否收藏
                is_collection= False
                zgld_diary_action_obj = models.zgld_diary_action.objects.filter(
                    action=2,
                    customer_id=user_id,
                    diary_id=diary_obj.id
                )
                if zgld_diary_action_obj:
                    is_collection = True

                cover_picture = ''
                if diary_obj.cover_picture:  # 封面（取第一张）
                    cover_picture = json.loads(diary_obj.cover_picture)

                customer_name = diary_obj.case.customer_name
                customer_headimgurl = diary_obj.case.headimgurl
                content = diary_obj.content
                diary_name = diary_obj.title # 记录动能日志
                data_list = {
                    'cover_picture': cover_picture,
                    'customer_headimgurl': customer_headimgurl,
                    'customer_name': customer_name,
                    'title': diary_obj.title,
                    'content': content,
                    'read_count': diary_obj.read_count,                 # 阅读数量
                    'up_count': diary_obj.up_count,                     # 点赞数量
                    'comment_count': diary_obj.comment_count,           # 评论数量
                    'is_diary_give_like': is_diary_give_like,           # 是否点赞
                    'case_type': 1,                                     # 日记类型
                    'is_collection': is_collection,                     # 是否收藏
                    'cover_show_type': diary_obj.cover_show_type,       # 封面类型
                    'customer_count': customer_count,                   # 客户发布案例总数
                    'create_date': diary_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                }

                response.note = {
                    'cover_picture': '轮播图',
                    'customer_headimgurl': '客户头像',
                    'customer_name': '客户名称',
                    'content': '日记内容',
                    'title': '日记标题',
                    'up_count': '点赞数量',
                    'comment_count': '评论数量',
                    'read_count': '阅读数量',
                    'case_type': '日记类型',
                    'create_date': '创建时间',
                    'is_diary_give_like': '是否点赞',
                }

            # 时间轴
            else:

                # 时间轴 阅读量增加
                zgld_case_objs = models.zgld_case.objects.filter(id=case_id)
                diary_name = ''
                customer_name = ''          # 客户名称
                create_date = ''            # 创建时间
                become_beautiful_cover = '' # 变美图片
                customer_headimgurl = ''    # 客戶头像
                is_collection = False       # 是否收藏
                if models.zgld_diary_action.objects.filter(case_id=case_id, customer_id=user_id, action=2):
                    is_collection = True
                tag_list = []
                if zgld_case_objs:
                    zgld_case_obj = zgld_case_objs[0]
                    diary_name = zgld_case_obj.case_name
                    tag_list = list(zgld_case_obj.tags.values('id', 'name'))  # 标签列表
                    customer_name = zgld_case_obj.customer_name
                    create_date = zgld_case_obj.create_date.strftime('%Y-%m-%d')
                    become_beautiful_cover = json.loads(zgld_case_obj.become_beautiful_cover)
                    customer_headimgurl = zgld_case_obj.headimgurl
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
                ).order_by(order)

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

                    is_diary_give_like = False
                    zgld_diary_action_obj = models.zgld_diary_action.objects.filter(
                        action=1,
                        customer_id=user_id,
                        diary_id=obj.id
                    )
                    if zgld_diary_action_obj:
                        is_diary_give_like = True

                    diary_give_like = models.zgld_diary_action.objects.filter(diary_id=obj.id, action=1).count() # 点赞数量统计

                    content = obj.content  # 获取简介
                    content_tag = ''
                    flag = False
                    for ch in content:  # 判断是否为中文 否则有样式
                        if u'\u4e00' <= ch <= u'\u9fff':
                            if '微软雅黑' in ch:
                                continue
                            flag = True
                            content_tag += ch
                        else:
                            if flag == True:
                                break

                    if len(obj.title) >= 50:
                        summary = content_tag[:50]
                    elif len(content) >= 30:
                        summary = content_tag[:30]
                    else:
                        summary = content_tag[:10]

                    result_data.append({
                        'timeline_id': obj.id,      # 时间轴详情ID
                        'cover_picture': cover_picture,
                        'diary_date': obj.diary_date.strftime('%Y-%m-%d'), # 发布时间
                        'summary': summary,
                        'title': obj.title,
                        'diary_give_like': diary_give_like,     # 点赞数量
                        'diary_read_num': obj.read_count,       # 阅读数量
                        'cover_show_type': obj.cover_show_type, # 阅读数量
                        'comment_count': obj.comment_count,     # 评论数量
                        'case_type': 2,                         # 日记类型
                        'is_diary_give_like': is_diary_give_like,# 是否点赞
                    })
                top_data = {
                    'become_beautiful_cover': become_beautiful_cover,
                    'customer_name': customer_name,
                    'tag_list': tag_list,
                    'create_date': create_date,
                    'is_collection': is_collection,
                    'customer_headimgurl': customer_headimgurl,
                    'count': count,
                }
                data_list = {
                    'result_data': result_data,
                    'top_data':top_data,
                }
                response.note = {
                    'become_beautiful_cover': '变美图片',
                    'customer_headimgurl': '客户头像',
                    'customer_name': '客户名称',
                    'result_data': {
                        'cover_picture': '封面图片',
                        'diary_date': '发布时间',
                        'title': '日记标题',
                        'content': '日记内容',
                        'diary_give_like': '点赞数量',
                        'diary_read_num': '阅读数量',
                        # 'comment_count': '评论数量',
                    },
                    'create_date': '创建时间',
                    'tag_list': '标签',
                    'case_type': '日记类型',
                    'count': '该时间轴 日记总数 /可做分页',
                }


        # 记录该客户 点击查看日记详情日志 (动能记录)
        data = {
            'action': 22,
            'customer_id': user_id,
            'user_id': u_id,
            'diary_name': diary_name
        }
        print('***记录日志********record_view_log********记录日志*****************record_view_log******************记录日志', user_id, diary_name)
        record_view_log(data)

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': data_list,
            'data_count': count
        }

    else:
        print('------json.loads(forms_obj.errors.as_json())---------------', json.loads(forms_obj.errors.as_json()))
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
        case_type = int(request.GET.get('case_type'))

        if case_type == 1:
            poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                user_customer_belonger_id=user_customer_belonger_id,
                diary_id=case_id
            )
            case_objs = models.zgld_diary.objects.get(id=case_id)
        else:
            poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                user_customer_belonger_id=user_customer_belonger_id,
                case_id=case_id
            )
            case_objs = models.zgld_case.objects.get(id=case_id)

        qr_code = ''
        if poster_belonger_objs:
            poster_belonger_obj = poster_belonger_objs[0]
            qr_code = poster_belonger_obj.qr_code

        poster_cover = []
        if case_objs.poster_cover:
            poster_cover = json.loads(case_objs.poster_cover)


        poster_company_logo = models.zgld_xiaochengxu_app.objects.get(company_id=company_id).poster_company_logo
        len_poster_cover = len(poster_cover)

        ret_data = {
            'poster_company_logo' :poster_company_logo,
            'qr_code_url': qr_code,
            'poster_cover' : poster_cover,
            'len_poster_cover' : len_poster_cover
        }
        print('ret_data ------>>',ret_data)

        return render(request, 'poster_case.html', locals())


# 企业用户生成小程序二维码 和 小程序客户生成和自己的企业用户对应的小程序二维码。
@csrf_exempt
def create_user_customer_case_poster_qr_code(data):
    response = ResponseObj()
    user_id = data.get('user_id')
    customer_id = data.get('customer_id')
    user_customer_belonger_id = data.get('user_customer_belonger_id') # 关系绑定表ID
    case_id = data.get('case_id')
    case_type = int(data.get('case_type'))
    company_id = data.get('company_id')

    # 判断案例关系是否存在   区分普通案例和时间轴
    case_type_q = Q()
    if case_type == 1:
        case_type_q.add(Q(diary_id=case_id), Q.AND)
    else:
        case_type_q.add(Q(case_id=case_id), Q.AND)

    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/diary_manage/poster_html?' \
          'user_id={user_id}&uid={uid}&case_id={case_id}&company_id={company_id}&' \
          'user_customer_belonger_id={user_customer_belonger_id}&case_type={case_type}'.format(
        user_id=customer_id, uid=user_id, case_id=case_id,company_id=company_id,
        user_customer_belonger_id=user_customer_belonger_id, case_type=case_type)

    # poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
    #     case_type_q,
    #     user_customer_belonger_id=user_customer_belonger_id,
    # )
    #
    # if poster_belonger_objs:
    #     poster_belonger_obj = poster_belonger_objs[0]
    #     qr_code =  poster_belonger_obj.qr_code          # 关系二维码

        # poster_url =  poster_belonger_obj.poster_url    # 判断 二维码海报截图是否存在 不存在异步创建

    # 生成海报截图
    data_dict = {
        'user_id': user_id,
        'customer_id': customer_id,
        'poster_url': url,
        'user_customer_belonger_id': user_customer_belonger_id,
        'case_id': case_id,
        'case_type': case_type
    }
    tasks.create_user_or_customer_small_program_poster.delay(json.dumps(data_dict))

    qr_code = ''
    # if not qr_code: # 海报二维码不存在 生成
    xiaochengxu_app_objs = models.zgld_xiaochengxu_app.objects.filter(company_id=company_id)
    if xiaochengxu_app_objs:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        path = '/pages/detail/detail?uid=%s&case_id=%s&source=1&case_type=%s' % (user_id, case_id, case_type)  # 小程序路由
        user_qr_code = '/case_%s_customer_%s_user_%s_%s_qrcode.jpg' % (case_id, customer_id, user_id, now_time)

        get_qr_data = {}
        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

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

        if not qr_ret.content:
            rc.delete('xiaochengxu_token')
            response.code = 301
            response.msg = "生成小程序二维码未验证通过"

        else:
            IMG_PATH = os.path.join(BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'xiaochengxu', 'qr_code') + user_qr_code
            with open('%s' % (IMG_PATH), 'wb') as f:
                f.write(qr_ret.content)

            if customer_id:
                qr_code = 'statics/zhugeleida/imgs/xiaochengxu/qr_code%s' % user_qr_code

                case_poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                    case_type_q,
                    user_customer_belonger_id=user_customer_belonger_id,
                )

                if case_poster_belonger_objs:
                    case_poster_belonger_objs.update(
                        qr_code=qr_code
                    )

                else:
                    if case_type == 1:
                        models.zgld_customer_case_poster_belonger.objects.create(
                            user_customer_belonger_id=user_customer_belonger_id,
                            diary_id=case_id,
                            qr_code=qr_code
                        )
                    else:
                        models.zgld_customer_case_poster_belonger.objects.create(
                            user_customer_belonger_id=user_customer_belonger_id,
                            case_id=case_id,
                            qr_code=qr_code
                        )

            response.data = {'qr_code': qr_code}
            response.code = 200
            response.msg = "生成小程序二维码成功"

    else:
        response.data = {'qr_code': qr_code}
        response.code = 200
        response.msg = "存在二维码"
    return response


# 日记其他操作
@csrf_exempt
@account.is_token(models.zgld_customer)
def diary_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    customer_id = request.GET.get('user_id')

    if request.method == "POST":
        # 点赞
        if oper_type == 'praise_case':
            customer_id = request.GET.get('user_id')
            case_id = o_id  # 日记ID
            case_type = request.GET.get('case_type')  # 日记类型
            diary_id = request.GET.get('diary_id')  # 时间轴详情ID
            if case_type:
                case_type = int(case_type)

            form_data = {
                'case_id': case_id,
                'customer_id': customer_id,
                'diary_id': diary_id,
                'case_type': case_type,
            }
            print('============================================')
            forms_obj = CollectionDiaryForm(form_data)
            if forms_obj.is_valid():
                formData = forms_obj.cleaned_data
                print('验证通过----')
                # 时间轴日记详情点赞
                if diary_id:
                    diary_id = formData.get('diary_id')
                    objs = models.zgld_diary_action.objects.filter(
                        action=1,
                        diary_id=diary_id,
                        customer_id=formData.get('customer_id')
                    )
                    if objs:
                        objs.delete()
                        response.msg = '已取消点赞'

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
                            zgld_diary_action_objs.delete()
                            response.msg = '已取消点赞'

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
                            zgld_diary_action_objs.delete()
                            response.msg = '已取消点赞'

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

        # 评论日记
        elif oper_type == 'review_diary':

            from_customer_id = request.GET.get('user_id')
            comments = request.POST.get('comments')
            # reply_comment = request.POST.get('reply_comment') # 回复评论(评论别人的评论)

            request_data_dict = {
                'diary_id': o_id,
                'comments': comments,                 # 评论内容
                'customer_id': from_customer_id,      # 文章所属用户的ID
                # 'reply_comment': reply_comment,      # 回复评论
            }

            forms_obj = ReviewDiaryForm(request_data_dict)
            if forms_obj.is_valid():
                cleaned_data = forms_obj.cleaned_data
                msg = b64encode(cleaned_data.get('comments'))
                diary_id, objs = cleaned_data.get('diary_id')
                create_data = {
                    'diary_id': diary_id,
                    'content': msg,
                    'from_customer_id': from_customer_id,
                    # 'reply_comment_id': reply_comment
                }

                objs.update(  # 评论次数
                    comment_count=F('comment_count') + 1
                )

                models.zgld_diary_comment.objects.create(**create_data)
                response.code = 200
                response.msg = "评论成功"
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 收藏日记
        elif oper_type == 'collect_diary':
            case_id = o_id
            case_type = int(request.POST.get('case_type'))
            if case_type == 1:
                objs = models.zgld_diary_action.objects.filter(
                    diary_id=case_id,
                    customer_id=customer_id,
                    action=2
                )
                if objs:
                    objs.delete()
                    response.msg = '已取消收藏'
                else:
                    models.zgld_diary_action.objects.create(
                        diary_id=case_id,
                        customer_id=customer_id,
                        action=2
                    )
                    response.msg = '收藏成功'
            else:
                objs = models.zgld_diary_action.objects.filter(
                    case_id=case_id,
                    customer_id=customer_id,
                    action=2
                )
                if objs:
                    objs.delete()
                    response.msg = '已取消收藏'
                else:
                    models.zgld_diary_action.objects.create(
                        case_id=case_id,
                        customer_id=customer_id,
                        action=2
                    )
                    response.msg = '收藏成功'

            response.code = 200

    elif request.method == 'GET':


        ## 查询评论
        if oper_type == 'diary_review_list':

            company_id = request.GET.get('company_id')
            customer_id = request.GET.get('user_id')
            form_data = {
                'diary_id': o_id
            }
            forms_obj = DiaryReviewSelectForm(form_data)

            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                q = Q()
                q.add(Q(is_audit_pass=1) | Q(from_customer_id=customer_id) & Q(is_audit_pass__isnull=False), Q.AND)
                print('q-----> ', q)
                objs = models.zgld_diary_comment.objects.select_related(
                    'from_customer',
                ).filter(
                    diary_id=o_id,
                    diary__case__company_id=company_id
                ).filter(
                    q
                ).order_by('-create_date')
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    customer_name = b64decode(obj.from_customer.username)
                    content = b64decode(obj.content)
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
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # (我-我的足迹)
        elif oper_type == 'browse_case_list_record':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                order = request.GET.get('order', '-create_date')
                customer_id = request.GET.get('user_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                company_id = request.GET.get('company_id')
                ## 搜索条件
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                q.add(Q(action=3) & Q(customer_id=customer_id), Q.AND)

                objs = models.zgld_diary_action.objects.select_related('case', 'customer').filter(q).order_by(order)
                count = objs.count()
                ret_data = []
                case_objs = objs.filter(case__company_id=company_id).exclude(case_id__isnull=True)
                diary_objs = objs.filter(diary__case__company_id=company_id).exclude(diary_id__isnull=True)

                start_line = 0
                stop_line = 10
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    diary_objs = diary_objs[start_line: stop_line]
                    case_objs = case_objs[start_line: stop_line]

                for obj in case_objs:
                    cover_picture = []
                    if obj.case.cover_picture:
                        cover_picture = json.loads(obj.case.cover_picture)

                    ret_data.append({
                        'case_type': 2, # 时间轴
                        'diary_id':obj.case_id,
                        'case_name':obj.case.case_name,
                        'cover_picture':cover_picture,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                    })

                for obj in diary_objs:

                    cover_picture = []
                    if obj.diary.cover_picture:
                        cover_picture = json.loads(obj.diary.cover_picture)
                    cover_show_type = obj.diary.cover_show_type
                    ret_data.append({
                        'case_type': 1,  # 普通案例
                        'diary_id': obj.diary_id,
                        'case_name': obj.diary.title,
                        'cover_picture': cover_picture,
                        'cover_show_type': cover_show_type,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                    })

                # 按时间排序
                ret_data = sorted(ret_data, key=lambda x: x['create_date'], reverse=True)

                ret_data = ret_data[start_line: stop_line]

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }
                response.note = {
                    'case_type': '案例类型',  # 普通案例
                    'diary_id': '案例ID/日记ID',
                    'case_name': '案例名称/日记名称',
                    'cover_picture': '封面图',
                    'create_date':'创建时间',
                    'cover_show_type':'封面类型',
                }
            else:
                response.code = 301
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())

        # (我-收藏日记)
        elif oper_type == 'collection_case':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                order = request.GET.get('order', '-create_date')
                customer_id = request.GET.get('user_id')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                company_id = request.GET.get('company_id')

                ## 搜索条件
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                q.add(Q(action=2) & Q(customer_id=customer_id), Q.AND)

                objs = models.zgld_diary_action.objects.select_related('case', 'customer').filter(q).order_by(order)
                count = objs.count()
                ret_data = []
                case_objs = objs.filter(case__company_id=company_id).exclude(case_id__isnull=True)
                diary_objs = objs.filter(diary__case__company_id=company_id).exclude(diary_id__isnull=True)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    diary_objs = diary_objs[start_line: stop_line]
                    case_objs = case_objs[start_line: stop_line]

                for obj in case_objs:
                    cover_picture = []
                    if obj.case.cover_picture:
                        cover_picture = json.loads(obj.case.cover_picture)
                    ret_data.append({
                        'case_type': 2,  # 时间轴
                        'diary_id': obj.case_id,
                        'case_name': obj.case.case_name,
                        'cover_picture': cover_picture,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                    })

                for obj in diary_objs:
                    cover_picture = ''
                    if obj.diary.cover_picture:
                        cover_picture = json.loads(obj.diary.cover_picture)
                    cover_show_type = obj.diary.cover_show_type
                    ret_data.append({
                        'case_type': 1,  # 普通案例
                        'diary_id': obj.diary_id,
                        'case_name': obj.diary.title,
                        'cover_picture': cover_picture,
                        'cover_show_type': cover_show_type,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if obj.create_date else '',
                    })

                # 按时间排序
                ret_data = sorted(ret_data, key=lambda x: x['create_date'], reverse=True)

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }
                response.note = {
                    'case_type': '案例类型',  # 普通案例
                    'diary_id': '案例ID/日记ID',
                    'case_name': '案例名称/日记名称',
                    'cover_picture': '封面图',
                    'create_date': '创建时间',
                    'cover_show_type': '封面类型'
                }
            else:
                response.code = 301
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())

        ## 小程序-案例-生成关系二维码
        elif oper_type == 'xcx_case_poster':
            customer_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            uid = request.GET.get('uid')             # 用户ID

            case_id = request.GET.get('case_id')     # 日记ID
            case_type = request.GET.get('case_type') # 案例类型

            # 获取 logo
            poster_company_logo = ''
            xiaochengxu_obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
            if xiaochengxu_obj.poster_company_logo:
                poster_company_logo = xiaochengxu_obj.poster_company_logo


            # 判断该用户和客户是否绑定关系
            user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.filter(
                customer_id=customer_id,
                user_id=uid
            )

            user_customer_belonger_id = ''
            if user_customer_belonger_objs:
                user_customer_belonger_id = user_customer_belonger_objs[0].id

            case_type = int(case_type)
            if case_type == 1: # 普通案例
                objs = models.zgld_diary.objects.filter(id=case_id)
            else:
                objs = models.zgld_case.objects.filter(id=case_id)

            if objs:
                obj = objs[0]
                poster_cover = []
                if obj.poster_cover:  # 海报图片
                    poster_cover = json.loads(obj.poster_cover)

                _data = {
                    'user_id': uid,
                    'customer_id': customer_id,
                    'case_id': case_id,
                    'company_id': company_id,
                    'case_type': case_type,
                    'user_customer_belonger_id': user_customer_belonger_id, # 关系绑定表ID
                }

                _response = create_user_customer_case_poster_qr_code(_data)

                qr_code = ''
                if _response.code == 200:
                    qr_code = _response.data.get('qr_code')

                ret_data = {
                    'case_id': case_id,
                    'poster_cover': poster_cover,
                    'poster_company_logo': poster_company_logo,
                    'qr_code': qr_code
                }

                response.data = ret_data
                response.note = {
                    'case_id': '案例ID',
                    'poster_cover': '海报封面',
                    'poster_company_logo': '海报公司log',
                    'qr_code': '小程序关系二维码'
                }

                response.code = 200
                response.msg = "返回成功"
            else:
                response.code = 301
                response.msg = "案例不存在"

        ## 小程序获取 案例海报截图
        elif oper_type == 'xcx_get_case_poster_screenshots':
            customer_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            company_id = request.GET.get('company_id')
            case_type = int(request.GET.get('case_type'))
            case_id = request.GET.get('case_id')

            user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.filter(
                customer_id=customer_id,
                user_id=uid
            )
            user_customer_belonger_id = ''
            if user_customer_belonger_objs:
                user_customer_belonger_id = user_customer_belonger_objs[0].id

            case_type_q = Q()
            if case_type == 1:
                case_type_q.add(Q(diary_id=case_id), Q.AND)
            else:
                case_type_q.add(Q(case_id=case_id), Q.AND)

            poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                case_type_q,
                user_customer_belonger_id=user_customer_belonger_id,
            )

            poster_url = ''
            if poster_belonger_objs:
                poster_belonger_obj = poster_belonger_objs[0]
                poster_url = poster_belonger_obj.poster_url
                if not poster_url:
                    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/diary_manage/poster_html?' \
                          'user_id={user_id}&uid={uid}&case_id={case_id}&company_id={company_id}&' \
                          'user_customer_belonger_id={user_customer_belonger_id}&case_type={case_type}'.format(
                        user_id=customer_id, uid=uid, case_id=case_id, company_id=company_id,
                        user_customer_belonger_id=user_customer_belonger_id, case_type=case_type)

                    data_dict = {
                        'user_id': uid,
                        'poster_url': url,
                        'customer_id': customer_id,
                        'user_customer_belonger_id': user_customer_belonger_id,
                        'case_id': case_id,
                        'case_type': case_type
                    }
                    print('data_dict---data_dict---> ', data_dict)
                    tasks.create_user_or_customer_small_program_poster(json.dumps(data_dict))
                    poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                        case_type_q,
                        user_customer_belonger_id=user_customer_belonger_id,
                    )
                    if poster_belonger_objs:
                        poster_belonger_obj = poster_belonger_objs[0]

                poster_url = poster_belonger_obj.poster_url

            ret_data = {
                'poster_url': poster_url,
            }
            response.data = ret_data
            response.note = {
                'poster_url': '海报图片',
            }
            response.code = 200
            response.msg = "返回成功"

    return JsonResponse(response.__dict__)
