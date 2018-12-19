from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from django.db.models import Max, Avg, F, Q, Min, Count, Sum
from zhugeleida.forms.admin.tongxunlu_verify import TongxunluSelectForm, TongxunluUserListSelectForm,TongxunluUserList
import json
import datetime
from django.db.models import Q
import base64
from zhugeleida.forms.chat_verify import ChatSelectForm,ChatGetForm,ChatPostForm

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def tongxunlu(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        forms_obj = TongxunluSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            uid = forms_obj.cleaned_data.get('uid')
            order = request.GET.get('order')
            if not order:
                order =  '-create_date'
            # -expedted_pr 预计成交率 | -last_activity_time 最后活动时间 | -last_follow_time 最后跟进时间  排序为【默认为】成交率; 最后跟进时间; 最后活动时间

            q1 = Q()
            q1.connector = 'AND'
            q1.children.append(('user_id', uid))

            user_type = request.GET.get('user_type')  # (1, '扫码'), (2, '转发'), (3, '搜索'), (4, '公众号文章'),
            if user_type:  # 搜索进来
                q1.add(Q(**{'customer__user_type': user_type}), Q.AND)

            objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(q1).order_by(order)

            count = objs.count()
            if objs:

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 返回的数据
                ret_data = []
                for obj in objs:

                    last_interval_msg = ''
                    customer_status = '未跟进过'

                    last_follow_time = obj.last_follow_time  # 关联的跟进表是否有记录值，没有的话说明没有跟进记录。
                    if not last_follow_time:
                        last_interval_msg = ''
                        customer_status = '未跟进过'

                    elif last_follow_time:
                        now = datetime.datetime.now()
                        day_interval = (now - last_follow_time).days
                        if int(day_interval) == 0:
                            last_interval_msg = '今天'
                            customer_status = '今天跟进'

                        else:
                            if int(day_interval) == 1:
                                last_interval_msg = '昨天'
                                customer_status = '昨天已跟进'
                            else:
                                day_interval = day_interval - 1
                                last_interval_msg = '%s天前' % (day_interval)
                                customer_status = last_follow_time.strftime('%Y-%m-%d')

                    last_activity_msg = ''
                    last_activity_time = obj.last_activity_time  # 关联的跟进表是否有记录值，没有的话说明没有跟进记录。
                    if not last_activity_time:
                        last_activity_msg = ''

                    elif last_activity_time:
                        now = datetime.datetime.now()
                        day_interval = (now - last_activity_time).days
                        if int(day_interval) == 0:
                            last_activity_msg = '今天'
                        else:
                            if day_interval == 1:
                                last_activity_msg = '昨天'
                            else:
                                last_activity_msg = last_activity_time.strftime('%Y-%m-%d')

                    try:
                        username = base64.b64decode(obj.customer.username)
                        customer_name = str(username, 'utf-8')
                        print('----- 解密b64decode username----->', username)
                    except Exception as e:
                        print('----- b64decode解密失败的 customer_id 是 | e ----->', obj.customer_id, "|", e)
                        customer_name = '客户ID%s' % (obj.customer_id)


                    if obj.source == 4:
                        source_text = '文章'
                    else:
                        source_text = obj.get_source_display()

                    ret_data.append({
                        'id': obj.id,
                        'customer_id': obj.customer_id,
                        'customer_username': customer_name,
                        'headimgurl': obj.customer.headimgurl,
                        'expected_time': obj.expected_time,  # 预计成交时间
                        'expedted_pr': obj.expedted_pr,  # 预计成交概率
                        'customer_source': obj.customer.user_type,
                        'customer_source_text': obj.customer.get_user_type_display(),

                        'is_subscribe': obj.customer.is_subscribe,  # 用户是否订阅该公众号
                        'is_subscribe_text': obj.customer.get_is_subscribe_display(),
                        'source': obj.source,  # 来源
                        'source_text': source_text,  # 来源
                        'last_follow_time': last_interval_msg,  # 最后跟进时间
                        'last_activity_time': last_activity_msg,  # 最后活动时间
                        'follow_status': customer_status,  # 跟进状态
                        'create_date': obj.create_date,  # 跟进状态
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

    return JsonResponse(response.__dict__)


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def tongxunlu_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":

        ## 查询雷达用户列表
        if oper_type == 'quey_user_list':

            forms_obj = TongxunluUserList(request.GET)
            if forms_obj.is_valid():

                company_id = forms_obj.cleaned_data.get('company_id')
                user_objs_list = models.zgld_user_customer_belonger.objects.select_related('user').filter(
                    user__company_id=company_id).values('user_id', 'user__username').annotate(
                    user__sum=Count('user_id'))
                count = len(list(user_objs_list))

                print('---- list(user_objs_list) --->>', list(user_objs_list))
                if count > 0:

                    # 返回的数据
                    ret_data = []
                    for obj in user_objs_list:
                        user_id = obj.get('user_id')
                        user__username = obj.get('user__username')
                        user_num = obj.get('user__sum')
                        gongzhonghao_customer_num = models.zgld_user_customer_belonger.objects.select_related(
                            'customer').filter(user_id=user_id, customer__user_type=1).count()

                        xiaochengxu_customer_num = user_num - gongzhonghao_customer_num

                        ret_data.append({
                            'user_id': user_id,
                            'username': user__username,
                            'total_customer_num': user_num,
                            'xiaochengxu_customer_num' : xiaochengxu_customer_num,
                            'gongzhonghao_customer_num' : gongzhonghao_customer_num
                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }


                else:
                    response.code = 301
                    response.msg = '没有数据'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        ## 内部使用工具 删除绑定的关系-处理成唯一性
        elif oper_type == 'myself_delete_binding_relate':

            customer_list = list(
                set(models.zgld_user_customer_belonger.objects.all().values_list('customer_id', flat=True)))
            customer_count = len(customer_list)

            if customer_count > 0:
                print('----- 客户集合列表------>', customer_list)
                for customer_id in customer_list:
                    objs = models.zgld_user_customer_belonger.objects.filter(customer_id=customer_id).order_by(
                        'create_date')
                    if objs:
                        print('------- 正在处理 customer_id------》', customer_id)

                        i = 0
                        for obj in objs:
                            user_id = obj.user_id
                            if i == 0:
                                print('----- 【没有删除】 customer_id : %s | uid : %s ----->>' % (customer_id, user_id))
                                i = i + 1
                                continue

                            i = i + 1
                            print('----- 【已删除】 customer_id : %s | uid : %s ----->>' % (customer_id, user_id))
                            obj.delete()

            else:

                print('-- customer_list 为空---->>', customer_list)


        ## 展示聊天历史信息
        elif oper_type == 'chat_info':

            forms_obj = ChatSelectForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('uid')
                customer_id = request.GET.get('customer_id')
                # send_type = request.GET.get('send_type')

                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                ).order_by('-create_date')

                count = objs.count()

                objs.update(
                    is_user_new_msg=False
                )

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data_list = []
                for obj in objs:

                    customer_name = base64.b64decode(obj.customer.username)
                    customer_name = str(customer_name, 'utf-8')
                    content = obj.content

                    if not content:
                        continue

                    is_customer_new_msg = obj.is_customer_new_msg

                    if is_customer_new_msg:  # 为True时
                        is_customer_already_read = 0  # 未读
                        is_customer_already_read_text = '未读'
                    else:
                        is_customer_already_read = 1  # 已读
                        is_customer_already_read_text = '已读'

                    _content = json.loads(content)
                    info_type = _content.get('info_type')
                    if info_type:
                        info_type = int(info_type)

                        if info_type == 1:
                            msg = _content.get('msg')
                            msg = base64.b64decode(msg)
                            msg = str(msg, 'utf-8')
                            _content['msg'] = msg

                    base_info_dict = {
                        'customer_id': obj.customer_id,
                        'customer_avatar': obj.customer.headimgurl,
                        'user_id': obj.userprofile_id,
                        'src': obj.customer.headimgurl,
                        'name': customer_name,
                        'dateTime': obj.create_date,
                        'send_type': obj.send_type,
                        'is_customer_already_read': is_customer_already_read,
                        'is_customer_already_read_text': is_customer_already_read_text
                    }
                    base_info_dict.update(_content)

                    ret_data_list.append(base_info_dict)

                ret_data_list.reverse()

                response.code = 200
                response.msg = '分页获取-全部聊天消息成功'
                response.data = {
                    'ret_data': ret_data_list,
                    'data_count': count,
                }


    elif request.method == "POST":

        #更改所属客户关系
        if oper_type == 'change_customer_ownership':

            user_id = request.GET.get('user_id')

            customer_id_list = request.POST.get('customer_id_list')
            old_uid = request.POST.get('old_uid')
            new_uid = request.POST.get('new_uid')
            company_id =  request.POST.get('company_id')
            type =  request.POST.get('type')

            form_data = {
                'company_id' : company_id,
                'customer_id_list' : customer_id_list,
                'old_uid' : old_uid,
                'new_uid' : new_uid,
                'type' : type,
            }

            forms_obj = TongxunluUserListSelectForm(form_data)

            if forms_obj.is_valid():

                ## 工作交接
                if type == 'all_customer':
                    customer_objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
                        user_id=old_uid,user__company_id=company_id)

                    for obj in customer_objs:

                        _customer_id =obj.customer_id
                        validate_customer_objs = models.zgld_user_customer_belonger.objects.filter(user_id=new_uid,customer_id=_customer_id)
                        chat_objs = models.zgld_chatinfo.objects.filter(customer_id=_customer_id, userprofile_id=old_uid)  #

                        if validate_customer_objs:
                            obj.delete() # 删除旧数据
                            chat_objs.update(
                                userprofile_id=new_uid,
                                is_last_msg=False
                            )

                        else:
                            chat_objs.update(
                                userprofile_id=new_uid
                            )

                            obj.userprofile_id=new_uid
                            obj.save()


                        response.code = 200
                        response.msg = '交接成功'

                    else:
                        response.code = 301
                        response.msg = '没有数据'
                else:

                    customer_id_list = forms_obj.cleaned_data.get('customer_id_list')
                    company_id = forms_obj.cleaned_data.get('company_id')
                    customer_objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(customer_id__in=customer_id_list,user__company_id=company_id)
                    if customer_objs:
                        for obj in customer_objs:

                            _customer_id = obj.customer_id
                            validate_customer_objs = models.zgld_user_customer_belonger.objects.filter(user_id=new_uid,
                                                                                                       customer_id=_customer_id) ##

                            chat_objs = models.zgld_chatinfo.objects.filter(customer_id=_customer_id, userprofile_id=old_uid) #

                            if validate_customer_objs:  # 此用户的新对接人已经有绑定关系
                                obj.delete()            # 删除旧用户的绑定数据
                                chat_objs.update(
                                    userprofile_id=new_uid,
                                    is_last_msg=False
                                )
                                response.code = 200
                                response.msg = '改变成功'

                            else:

                                obj.userprofile_id = new_uid
                                obj.save()
                                # 返回的数据
                                chat_objs.update(
                                    userprofile_id=new_uid
                                )
                    else:
                        response.code = 301
                        response.msg = '没有数据'

            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())




    return JsonResponse(response.__dict__)
