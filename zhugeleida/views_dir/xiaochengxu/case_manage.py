from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.case_manage_verify import SetFocusGetRedPacketForm, CaseAddForm, CaseSelectForm, CaseUpdateForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm,CollectionDiaryForm,BrowseCaseSelectForm


import json,datetime
from django.db.models import Q,F, Sum, Count

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
                company_id = forms_obj.cleaned_data.get('company_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-update_date')

                ## 搜索条件
                search_tag_id = request.GET.get('search_tag_id')  #
                case_id = request.GET.get('case_id')  #
                search_activity_status = request.GET.get('status')  #
                customer_name = request.GET.get('customer_name')  #


                q1 = Q()
                q1.connector = 'and'
                q1.children.append(('company_id', company_id))

                if customer_name:
                    q1.children.append(('customer_name__contains', customer_name))

                if case_id:
                    q1.children.append(('id', case_id))


                    ##记录客户查看单个案例的操作
                    models.zgld_diary_action.objects.create(
                        case_id=case_id,customer_id=customer_id,action=3
                    )

                    ## 记录单个案例浏览量
                    case_objs = models.zgld_case.objects.filter(id=case_id)
                    if case_objs:
                        case_objs.update(
                            read_count=F('read_count') + 1
                        )


                # now_date_time = datetime.datetime.now()
                if search_activity_status:
                    q1.children.append(('status', search_activity_status))  #

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
                                _history_tags_record =  customer_objs[0].history_tags_record
                                history_tags_record = json.loads(_history_tags_record)

                                history_tags_record =  history_tags_record[0:13]
                                recode_tag_name = []
                                for recode_tag_name_dict in history_tags_record:
                                    recode_tag_name.append(recode_tag_name_dict['name'])

                                if tag_name  in recode_tag_name:
                                    index_num = tag_name.index(recode_tag_name)
                                    history_tags_record.remove(index_num)

                                history_tags_record.append( {
                                    'id': search_tag_id,
                                    'name' : tag_name
                                })
                                customer_objs.update(
                                    history_tags_record=json.dumps(history_tags_record)
                                )


                print('-----q1---->>', q1)
                objs = models.zgld_case.objects.select_related('company').filter(q1).order_by(order).exclude(status=3)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                if objs:
                    last_diary_data = ''
                    is_open_comment = ''
                    is_open_comment_text = ''
                    gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
                    if gongzhonghao_app_objs:
                        is_open_comment = gongzhonghao_app_objs[0].is_open_comment
                        is_open_comment_text = gongzhonghao_app_objs[0].get_is_open_comment_display()

                    for obj in objs:

                        status = obj.status
                        status_text = obj.get_status_display()

                        cover_picture = obj.cover_picture
                        if cover_picture:
                            cover_picture =  json.loads(cover_picture)

                        _case_id = obj.id

                        ## 查找出最新更新的日记
                        if not case_id: # 当满足 不是查询单个的情况
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

                                    # 'is_praise_diary': is_praise_diary,
                                    # 'is_praise_diary_text': is_praise_diary_text,

                                    'title': diary_obj.title,
                                    'diary_date': diary_obj.diary_date.strftime('%Y-%m-%d') if diary_obj.diary_date else '', #'%Y-%m-%d %H:%M:%S'
                                    'cover_picture': _cover_picture,
                                    'content': _content,


                                    'status': _status,
                                    'status_text': _status_text,

                                    'cover_show_type': diary_obj.cover_show_type,
                                    'cover_show_type_text': diary_obj.get_cover_show_type_display(),

                                    'create_date': diary_obj.create_date.strftime('%Y-%m-%d %H:%M:%S') if diary_obj.create_date else '',
                                }

                        tag_list = list(obj.tags.values('id', 'name'))
                        diary_up_down_objs = models.zgld_diary_action.objects.filter(case_id=obj.id,
                                                                                     customer_id=customer_id, action=4)
                        if diary_up_down_objs:
                            is_praise_diary = 1
                            is_praise_diary_text = '已经赞过此日记'
                        else:
                            is_praise_diary = 0
                            is_praise_diary_text = '没有赞过此日记'

                        case_up_down_objs = models.zgld_diary_action.objects.filter(action=2, case_id=obj.id,
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

                        ret_data.append({
                            'case_id': _case_id,
                            'case_name': obj.case_name,
                            'company_id': obj.company_id,
                            'customer_name': obj.customer_name,

                            'headimgurl': obj.headimgurl,
                            'cover_picture' : cover_picture,

                            'read_count': obj.read_count,  #
                            'comment_count': obj.comment_count,  #
                            'up_count': obj.up_count,  #

                            'is_praise_diary': is_praise_diary,
                            'is_praise_diary_text': is_praise_diary_text,

                            'is_open_comment' : is_open_comment,
                            'is_open_comment_text' :is_open_comment_text,

                            'is_collection_case' : is_collection_case,
                            'is_collection_case_text' : is_collection_case_text,

                            'status': status,
                            'status_text': status_text,
                            'tag_list' : tag_list,

                            'case_type': obj.case_type,
                            'case_type_text': obj.get_case_type_display(),

                            'last_diary_data' : last_diary_data, # 最后日记的内容
                            'update_date': obj.update_date.strftime('%Y-%m-%d %H:%M:%S') if obj.update_date else '',
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
                    response.code = 302
                    response.msg = '数据不存在'


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
                objs = models.zgld_diary_action.objects.select_related('case','customer').filter(q1).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line : stop_line]

                ret_data = []
                for obj in  objs:

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

    elif  request.method == "POST":

        ## 收藏案例
        if  oper_type == 'collection_case':
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

                case_up_down_objs = models.zgld_diary_action.objects.filter(action=2, case_id=case_id,customer_id=customer_id)
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
                    case_up_down_obj =  models.zgld_diary_action.objects.create(**create_data)
                    response.data = {
                        'status' : case_up_down_obj.status,
                        'status_text': '已收藏此案例'
                    }
                    response.code = 200
                    response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())



        ##点赞案例
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
                    'customer_id' :customer_id,
                    'status' : 1,
                    'action' : 4  # 点赞
                }
                case_objs = models.zgld_case.objects.filter(id=case_id)
                diary_up_down_objs = models.zgld_diary_action.objects.filter(action=4,case_id=case_id,customer_id=customer_id)
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
                        case_objs.update( #点赞
                            up_count=F('up_count') + 1
                        )
                    response.data = {
                        'up_count': case_objs[0].up_count,
                        'is_praise_diary' : 1,
                        'is_praise_diary_text' : '已赞此案例'
                    }
                    response.code = 200
                    response.msg = "记录成功"
            else:

                print('-------未能通过------->>', forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


