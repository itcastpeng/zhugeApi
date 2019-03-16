from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.case_manage_verify import SetFocusGetRedPacketForm, CaseAddForm, CaseSelectForm, \
    CaseUpdateForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm, QueryFocusCustomerSelectForm, CollectionDiaryForm, \
    BrowseCaseSelectForm
from publicFunc.Response import ResponseObj
from zhugeleida.views_dir.admin.dai_xcx import create_authorizer_access_token

import json, datetime, os, redis, requests
from django.db.models import Q, F, Sum, Count
from zhugeleida.views_dir.conf import Conf
from zhugeapi_celery_project import tasks


@csrf_exempt
@account.is_token(models.zgld_customer)
def case_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        # 查询案例
        if oper_type == 'case_list':

            print('request.GET----->', request.GET)

            forms_obj = CaseSelectForm(request.GET)
            if forms_obj.is_valid():
                print('----forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                customer_id = request.GET.get('user_id')
                u_id = request.GET.get('u_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-update_date')

                ## 搜索条件
                search_tag_id = request.GET.get('search_tag_id')    # 案例标签
                case_id = request.GET.get('case_id')                # 案例ID 相当于查询详情
                search_activity_status = request.GET.get('status')  # 案列状态(1已发、2未发、3删除)
                customer_name = request.GET.get('customer_name')    # 发布某个客户的名称

                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))

                if customer_name:
                    q1.children.append(('customer_name__contains', customer_name))

                if search_activity_status:
                    q1.children.append(('status', search_activity_status))  #

                # 如果有案例标签 则记录 热门搜索的标签--
                if search_tag_id:
                    tag_ids_list = []
                    tag_ids_list.append(int(search_tag_id))
                    q1.children.append(('tags__in', tag_ids_list))  #

                    ## 记录热门搜索的想项目 和 历史搜索记录
                    if search_tag_id:

                        _case_objs = models.zgld_case_tag.objects.filter(id=search_tag_id)
                        if _case_objs:
                            tag_name = _case_objs[0].name
                            _case_objs.update(
                                search_amount=F('search_amount') + 1
                            )

                            customer_objs = models.zgld_customer.objects.filter(id=customer_id)
                            if customer_objs:
                                _history_tags_record = customer_objs[0].history_tags_record
                                history_tags_record = json.loads(_history_tags_record)

                                history_tags_record = history_tags_record[0:13]
                                recode_tag_name = []
                                for recode_tag_name_dict in history_tags_record:
                                    recode_tag_name.append(recode_tag_name_dict['name'])




                                if tag_name in recode_tag_name:
                                    print('值 recode_tag_name----->>', recode_tag_name)
                                    print('值 tag_name----->>', tag_name)

                                    index_num = recode_tag_name.index(tag_name)
                                    print('值 index_num---->',index_num)
                                    print('值 history_tags_record ---->',history_tags_record)

                                    del history_tags_record[index_num]

                                history_tags_record.append({
                                    'id': search_tag_id,
                                    'name': tag_name
                                })
                                customer_objs.update(
                                    history_tags_record=json.dumps(history_tags_record)
                                )

                print('-----q1---->>', q1)
                objs = models.zgld_case.objects.select_related('company').filter(q1).order_by(order).exclude(status=3)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if not objs:
                    response.code = 302
                    response.msg = '数据不存在'

                else:
                    # last_diary_data = ''
                    is_open_comment = ''        # 是否开启了自动打标签 ID
                    is_open_comment_text = ''   # 是否开启了自动打标签 内容
                    gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                    if gongzhonghao_app_objs:
                        is_open_comment = gongzhonghao_app_objs[0].is_open_comment
                        is_open_comment_text = gongzhonghao_app_objs[0].get_is_open_comment_display()

                    if case_id:
                        print('case_id------------> ', case_id)
                        diary_objs = models.zgld_diary.objects.filter(id=case_id)
                        # 查询详情记录操作
                        if diary_objs:
                            ##记录客户查看单个案例的操作
                            models.zgld_diary_action.objects.create(
                                case_id=diary_objs[0].case_id, customer_id=customer_id, action=3
                            )

                            ## 记录单个案例浏览量
                            case_objs = models.zgld_case.objects.filter(id=case_id)
                            if case_objs:
                                case_objs.update(
                                    read_count=F('read_count') + 1
                                )

                    else:
                        case_id_list = []
                        [case_id_list.append(i.id) for i in objs]
                        diary_objs = models.zgld_diary.objects.filter(case_id__in=case_id_list)


                    count = diary_objs.count()
                    for diary_obj in diary_objs:

                        ## 查询详情
                        _case_id = diary_obj.id
                        # if not case_id:  # 当满足 不是查询单个的情况
                        _cover_picture = diary_obj.cover_picture
                        if _cover_picture:
                            _cover_picture = json.loads(_cover_picture)

                        last_diary_data = {
                            'diary_id': diary_obj.id,
                            'case_id': diary_obj.case_id,

                            'company_id': diary_obj.company_id,

                            'title': diary_obj.title,
                            'diary_date': diary_obj.diary_date.strftime(
                                '%Y-%m-%d') if diary_obj.diary_date else '',

                            'cover_picture': _cover_picture,
                            'content': diary_obj.content,

                            'status': diary_obj.status,
                            'status_text': diary_obj.get_status_display(),

                            'cover_show_type': diary_obj.cover_show_type,
                            'cover_show_type_text': diary_obj.get_cover_show_type_display(),

                            'create_date': diary_obj.create_date.strftime(
                                '%Y-%m-%d %H:%M:%S') if diary_obj.create_date else '',
                        }

                        cover_picture = ''
                        if diary_obj.case.cover_picture:
                            cover_picture = json.loads(diary_obj.case.cover_picture)


                        tag_list = list(diary_obj.case.tags.values('id', 'name'))  # 标签列表
                        diary_up_down_objs = models.zgld_diary_action.objects.filter(case_id=_case_id,
                                                                                     customer_id=customer_id, action=4)
                        if diary_up_down_objs:
                            is_praise_diary = 1
                            is_praise_diary_text = '已经赞过此日记'
                        else:
                            is_praise_diary = 0
                            is_praise_diary_text = '没有赞过此日记'

                        case_up_down_objs = models.zgld_diary_action.objects.filter(action=2, case_id=_case_id,
                                                                                    customer_id=customer_id)
                        if case_up_down_objs:
                            case_up_down_obj = case_up_down_objs[0]
                            status_ = case_up_down_obj.status
                            status_text_ = case_up_down_obj.get_status_display()
                            is_collection_case = status_
                            is_collection_case_text = status_text_
                        else:
                            is_collection_case = 0
                            is_collection_case_text = '没有收藏此案例'

                        become_beautiful_cover = diary_obj.case.become_beautiful_cover     # 变美封面
                        if become_beautiful_cover:
                            become_beautiful_cover = json.loads(become_beautiful_cover)
                        else:
                            become_beautiful_cover = ''
                        print('diary_obj.case.poster_cover------> ', diary_obj.case.poster_cover)
                        if diary_obj.case.poster_cover:
                            poster_cover = json.loads(diary_obj.case.poster_cover)
                        else:
                            poster_cover = []

                        ret_data.append({
                            'case_id': _case_id,
                            'case_name': diary_obj.case.case_name,                              # 案例名称
                            'company_id': diary_obj.case.company_id,                            # 公司ID
                            'customer_name': diary_obj.case.customer_name,                      # 客户名称
                            'headimgurl': diary_obj.case.headimgurl,                            # 客户头像
                            'cover_picture': cover_picture,                                     # 封面图片URL
                            'read_count': diary_obj.case.read_count,                            # 阅读数量
                            'comment_count': diary_obj.case.comment_count,                      # 被评论数量
                            'up_count': diary_obj.case.up_count,                                # 点赞次数
                            'is_praise_diary': is_praise_diary,                                 # 是否赞过该日记 ID
                            'is_praise_diary_text': is_praise_diary_text,                       # 是否赞过该日记 内容
                            'is_open_comment': is_open_comment,                                 # 是否开启了自动打标签 ID
                            'is_open_comment_text': is_open_comment_text,                       # 是否开启了自动打标签 内容
                            'become_beautiful_cover': become_beautiful_cover,                   # 变美封面
                            'is_collection_case': is_collection_case,                           # 是否收藏该案例ID
                            'is_collection_case_text': is_collection_case_text,                 # 是否收藏该案例内容
                            'status': diary_obj.case.status,                                    # 日记状态ID
                            'status_text': diary_obj.case.get_status_display(),                 # 日记状态内容
                            'tag_list': tag_list,                                               # 标签列表
                            'poster_cover' : poster_cover,                                      # 海报封面图片URL
                            'case_type': diary_obj.case.case_type,                              # 案例类型ID
                            'case_type_text': diary_obj.case.get_case_type_display(),           # 案例类型内容
                            'last_diary_data': last_diary_data,                                 # 最后日记的内容
                            'update_date': diary_obj.case.update_date.strftime('%Y-%m-%d %H:%M:%S') if diary_obj.case.update_date else '', # 日记最后修改时间
                            'create_date': diary_obj.case.create_date.strftime('%Y-%m-%d %H:%M:%S') if diary_obj.case.create_date else '', # 创建时间
                        })

                    # 记录该客户 点击查看日记首页日志
                    data = {
                        'action': 21,
                        'customer_id': customer_id,
                        'user_id': u_id
                    }
                    log_count = models.zgld_accesslog.objects.filter(**data).count()
                    if int(log_count) == 0:
                        remark = '首次查看您的日记首页, 沟通从此刻开始'
                    elif int(log_count) == 1:
                        remark = '查看您的日记首页/第{}次, 把握深度交流的机会'.format(log_count)
                    elif int(log_count) == 2:
                        remark = '查看您的日记首页/第{}次, 建议标注重点客户'.format(log_count)
                    else:
                        remark = '查看您的日记首页/第{}次, 成交在望'.format(log_count)

                    models.zgld_accesslog.objects.create(
                        action=21,
                        user_id=u_id,
                        customer_id=customer_id,
                        remark=remark
                    )

                    #  查询成功 返回200 状态码
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,

                    }

            else:

                response.code = 301
                response.msg = "验证未通过"
                response.data = json.loads(forms_obj.errors.as_json())

        # 浏览案例记录
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

        # 浏览案例记录
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


        ## 小程序-案例-海报内容
        elif oper_type == 'xcx_case_poster':
            customer_id = request.GET.get('user_id')
            uid = request.GET.get('uid')
            company_id = request.GET.get('company_id')
            case_id = request.GET.get('case_id')

            ret_data = []
            app_obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
            poster_company_logo = app_obj.poster_company_logo

            print('值customer_id------>>',customer_id)
            print('值customer_id------>>',customer_id)
            user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,user_id=uid)

            user_customer_belonger_id = ''
            if user_customer_belonger_objs:
                user_customer_belonger_id = user_customer_belonger_objs[0].id
            print('user_customer_belonger_objs ------->>',user_customer_belonger_objs)
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
                    print('_data ------>>',_data)

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

            user_customer_belonger_objs = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id,user_id=uid)

            user_customer_belonger_id = ''
            if user_customer_belonger_objs:
                user_customer_belonger_id = user_customer_belonger_objs[0].id

            _data = {
                'user_id': uid,
                'customer_id': customer_id,
                'case_id': case_id,
                'company_id': company_id,
                'user_customer_belonger_id' : user_customer_belonger_id
            }

            poster_belonger_objs = models.zgld_customer_case_poster_belonger.objects.filter(
                user_customer_belonger_id=user_customer_belonger_id, case_id=case_id)

            poster_url = ''
            if poster_belonger_objs:
                poster_belonger_obj = poster_belonger_objs[0]
                poster_url = poster_belonger_obj.poster_url
                source = 1 # 生成 扫码的海报
                if not  poster_url:
                    url = 'http://api.zhugeyingxiao.com/zhugeleida/xiaochengxu/diary_manage/poster_html?user_id=%s&uid=%s&case_id=%s&company_id=%s&user_customer_belonger_id=%s&source=%s' % (
                        customer_id, uid, case_id, company_id,user_customer_belonger_id, source)

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
                    'poster_url' : poster_url,

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



    elif request.method == "POST":

        ## 收藏案例
        if oper_type == 'collection_case':
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
        elif oper_type == 'praise_case':
            customer_id = request.GET.get('user_id')
            case_id = request.POST.get('case_id')

            request_data_dict = {
                'case_id': case_id,
                'status': 1,

            }

            forms_obj = CollectionDiaryForm(request_data_dict)
            if forms_obj.is_valid():

                create_data = {
                    'case_id': case_id,
                    'customer_id': customer_id,
                    'status': 1,
                    'action': 4  # 点赞
                }
                case_objs = models.zgld_case.objects.filter(id=case_id)
                diary_up_down_objs = models.zgld_diary_action.objects.filter(action=4, case_id=case_id,
                                                                             customer_id=customer_id)
                if diary_up_down_objs:
                    diary_up_down_objs.update(
                        status=1
                    )
                    response.data = {
                        'up_count': case_objs[0].up_count,
                        'is_praise_diary': 1,
                        'is_praise_diary_text': '已赞过此案例了'
                    }
                    response.code = 302
                    response.msg = "已经点过赞了"

                else:
                    models.zgld_diary_action.objects.create(**create_data)

                    if case_objs:
                        case_objs.update(  # 点赞
                            up_count=F('up_count') + 1
                        )
                    response.data = {
                        'up_count': case_objs[0].up_count,
                        'is_praise_diary': 1,
                        'is_praise_diary_text': '已赞此案例'
                    }
                    response.code = 200
                    response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


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
