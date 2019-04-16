
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.case_manage_verify import CaseSelectForm
from zhugeleida.public.common import action_record
import json, datetime
from django.db.models import Q, F, Sum, Count


# 查询公共函数 搜索需要
def case_manage_public(request, is_search=None, tag_list=None): # is_search 是否为搜索 如果为搜索不记录日志 tag_list搜索传进标签列表
    response = Response.ResponseObj()
    forms_obj = CaseSelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-update_date')
        # case_id = request.GET.get('case_id')                # 案例ID 相当于查询详情

        company_id = request.GET.get('company_id')  # 公司ID
        customer_id = request.GET.get('user_id')  # 客户ID
        u_id = request.GET.get('u_id')  # 查询谁的小程序 用户ID
        exclude_id = request.GET.get('exclude_id')  # 排除哪个ID

        ## 搜索条件
        search_tag_id = request.GET.get('search_tag_id')  # 案例标签
        customer_name = request.GET.get('customer_name')  # 按个人查询全部文章

        field_dict = {
            'company_id': '',
            'customer_name': '',  # 发布某个客户的名称
            'status': '',  # 案列状态(1已发、2未发、3删除)
        }
        q = conditionCom(request, field_dict)

        if tag_list: # 搜索时展示 搜索到所有标签下 案例日记
            q.add(Q(tags__in=tag_list), Q.AND)

        # 如果有案例标签 则记录热门搜索的标签
        if search_tag_id:
            q.add(Q(tags=search_tag_id), Q.AND)

            case_tag_objs = models.zgld_case_tag.objects.filter(id=search_tag_id)
            if case_tag_objs:
                case_tag_objs.update(
                    search_amount=F('search_amount') + 1
                )

        print('q -->', q)
        objs = models.zgld_case.objects.filter(
            q,
            status=1
        ).order_by(order).exclude(status=3)

        objs_exc_case_obj = objs.exclude(case_type=1)

        count = 0
        data_list = []
        if not objs:
            response.code = 302
            response.msg = '数据不存在'

        else:
            # is_open_comment = ''        # 是否可以评论 ID
            # is_open_comment_text = ''   # 是否可以评论 内容
            # gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            # if gongzhonghao_app_objs:
            #     is_open_comment = gongzhonghao_app_objs[0].is_open_comment
            #     is_open_comment_text = gongzhonghao_app_objs[0].get_is_open_comment_display()

            stop = datetime.datetime.today()
            zgld_diary_q = Q()
            if search_tag_id:
                zgld_diary_q.add(Q(case__tags=search_tag_id), Q.AND)
            if customer_name:
                zgld_diary_q.add(Q(case__customer_name=customer_name), Q.AND)
            if tag_list:
                zgld_diary_q.add(Q(case__tags__in=tag_list), Q.AND) # 搜索查询
            diary_objs = models.zgld_diary.objects.filter(
                zgld_diary_q,
                company_id=company_id,
                diary_date__lte=stop,  # 添加日记时 会选择发布日期 发布日期小于今天才展示
                status=1,
            ).exclude(case__case_type=2).exclude(id=exclude_id) # 相关文章 排除自己 只有普通日记排除

            count = diary_objs.count() + objs_exc_case_obj.count()  # 列表页总数

            # # 时间轴日记列表页
            for obj in objs_exc_case_obj:

                cover_picture = []
                if obj.cover_picture:
                    cover_picture = json.loads(obj.cover_picture)
                diary_give_like = models.zgld_diary_action.objects.filter(case_id=obj.id).count()

                is_give_like = False
                # 判断是否点赞
                is_give_like_obj = models.zgld_diary_action.objects.filter(
                    case_id=obj.id,
                    customer_id=customer_id,
                    action=1
                )
                if is_give_like_obj:
                    is_give_like = True

                data_list.append({
                    'diary_list_id': obj.id,
                    'cover_picture': cover_picture,
                    'case_name': obj.case_name,  # 日记名称(时间轴案例 为日记列表名称)
                    'customer_name': obj.customer_name,  # 客户名称
                    'customer_headimgurl': obj.headimgurl,  # 客户头像
                    'diary_give_like': diary_give_like,  # 点赞数量
                    'case_type': 2,  # 日记类型(1普通/2时间轴)
                    'is_give_like': is_give_like,  # 是否点赞
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            # 普通日记列表页
            for diary_obj in diary_objs:
                # tag_list = list(diary_obj.case.tags.values('id', 'name'))  # 标签列表
                # case_type = int(diary_obj.case.case_type) # 日记类型
                # print('case_type------> ', case_type)
                # if case_type == 1:
                # 判断是否点赞
                is_give_like = False
                is_give_like_obj = models.zgld_diary_action.objects.filter(
                    diary_id=diary_obj.id,
                    customer_id=customer_id,
                    action=1
                )
                if is_give_like_obj:
                    is_give_like = True
                cover_picture = []
                if diary_obj.cover_picture:  # 封面（取第一张）
                    cover_picture = json.loads(diary_obj.cover_picture)
                diary_give_like = models.zgld_diary_action.objects.filter(diary_id=diary_obj.id).count()
                diary_list_id = diary_obj.id
                case_name = diary_obj.title
                customer = diary_obj.case.customer_name
                headimgurl = diary_obj.case.headimgurl

                data_list.append({
                    'diary_list_id': diary_list_id,
                    'cover_picture': cover_picture,  # 如果为图片取第一张 / 如果是视频 就取视频
                    'case_name': case_name,  # 案例名称(普通案例 为标题)
                    'customer_name': customer,  # 客户名称
                    'customer_headimgurl': headimgurl,  # 客户头像
                    'diary_give_like': diary_give_like,  # 点赞数量
                    'case_type': 1,  # 日记类型(1普通/2时间轴)
                    'is_give_like': is_give_like,  # 是否点赞
                    'cover_show_type': diary_obj.cover_show_type,  # 封面类型 视频/图片
                    'create_date': diary_obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                data_list = data_list[start_line: stop_line]

            # 按时间排序
            data_list = sorted(data_list, key=lambda x: x['create_date'], reverse=True)
        print('len(data_list)------->', len(data_list))
        #  查询成功 返回200 状态码

        # 记录该客户 点击查看日记首页日志
        data = {
            'action': 21,
            'customer_id': customer_id,
            'user_id': u_id
        }
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': data_list,
            'data_count': count,
            'data': data,
        }
        response.note = {
            'diary_list_id': '(普通日记为日记ID/时间轴日记为日记列表ID)',
            'cover_picture': '封面图片',
            'case_name': '日记名称(时间轴日记为日记列表名称/普通日记为日记标题)',
            'customer_name': '客户名称',
            'customer_headimgurl': '客户头像',
            'diary_give_like': '点赞数量',
            'case_type': '日记类型(1普通/2时间轴)',
            'cover_show_type': '封面类型 视频/图片',
            'is_give_like': '是否点赞',
        }

    else:
        response.code = 301
        response.msg = "验证未通过"
        response.data = json.loads(forms_obj.errors.as_json())
    return response


# 记录该客户 点击查看日记首页日志(访问动能)
def record_view_log(data):
    customer_id = data.get('customer_id')
    u_id = data.get('user_id')
    log_count = models.zgld_accesslog.objects.filter(**data).count()
    num = int(log_count) + 1
    if int(log_count) == 0:
        remark = '首次查看您的日记首页, 沟通从此刻开始'
    elif int(log_count) == 1:
        remark = '查看您的日记首页/第{}次, 把握深度交流的机会'.format(num)
    elif int(log_count) == 2:
        remark = '查看您的日记首页/第{}次, 建议标注重点客户'.format(num)
    else:
        remark = '查看您的日记首页/第{}次, 成交在望'.format(num)
    # models.zgld_accesslog.objects.create(
    #     action=21,
    #     user_id=u_id,
    #     customer_id=customer_id,
    #     remark=remark
    # )
    data['uid'] = u_id
    data['user_id'] = customer_id
    data['action'] = 21
    print('--------------------------------------==============================================', data)
    action_record(data, remark)  # 记录访问动作

@csrf_exempt
@account.is_token(models.zgld_customer)
def case_manage(request):
    response = case_manage_public(request)
    print(response.data.get('data'))
    record_view_log(response.data.get('data'))
    return JsonResponse(response.__dict__)


