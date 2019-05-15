from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.chat_verify import ChatSelectForm,ChatGetForm,ChatPostForm
from zhugeapi_celery_project.tasks import user_send_template_msg_to_customer, user_send_gongzhonghao_template_msg
from django.db.models import F
import json
from django.db.models import Q
import  redis
import json
from zhugeleida import models
import base64
from zhugeleida.public.common import action_record

# 获取所有的聊天信息
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat(request):
    '''
    【分页获取】- 所有的聊天信息
    :param request:
    :return:
    '''
    if request.method == 'GET':
        forms_obj = ChatSelectForm(request.GET)
        if forms_obj.is_valid():
            response = Response.ResponseObj()
            user_id = request.GET.get('user_id')
            customer_id = request.GET.get('customer_id')
            # send_type = request.GET.get('send_type')

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            objs = []
            _objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                userprofile_id=user_id,
                customer_id=customer_id,
            ).exclude(send_type=4).order_by('-create_date')

            count = _objs.count()


            company_id = ''
            if _objs:
                company_id = _objs[0].userprofile.company_id

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = _objs[start_line: stop_line]


            ret_data_list = []
            update_id_list = [] # 修改当前分页下的雷达用户已读的消息列表ID
            for obj in objs:

                customer_name = base64.b64decode(obj.customer.username)
                customer_name = str(customer_name, 'utf-8')
                content = obj.content

                if not content:
                    continue

                is_customer_new_msg = obj.is_customer_new_msg
                id = obj.id
                # update_id_list.append(id)

                if is_customer_new_msg: # 为True时
                    is_customer_already_read = 0 # 未读
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
                    'id': id,
                    'customer_id': obj.customer_id,
                    'customer_avatar': obj.customer.headimgurl,
                    'user_id': obj.userprofile_id,
                    'src': obj.customer.headimgurl,
                    'name': customer_name,
                    'dateTime': obj.create_date,
                    'send_type': obj.send_type,
                    'is_customer_already_read': is_customer_already_read,
                    'is_customer_already_read_text' : is_customer_already_read_text
                }
                base_info_dict.update(_content)

                ret_data_list.append(base_info_dict)

            ret_data_list.reverse()

            response.code = 200
            response.msg = '分页获取-全部聊天消息成功'
            response.data = {
                'ret_data':  ret_data_list,
                'data_count': count,
                'company_id' : company_id
            }
            # print('response--------->',response.data)

            # _objs.filter(id__in=update_id_list).update(
            #     is_user_new_msg=False
            # )
            _objs.update(
                is_user_new_msg=False
            )


            if not ret_data_list:
                # 没有新消息
                response.msg = '没有新消息'

            return JsonResponse(response.__dict__)


# 聊天信息 操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':
        # 用户推送消息到server端,然后入库

        if  oper_type == 'send_msg':
            print('----send_msg--->>',request.POST)
            forms_obj = ChatPostForm(request.POST)
            if forms_obj.is_valid():
                company_id =  request.GET.get('company_id')

                data = request.POST.copy()
                user_id = int(data.get('user_id'))
                customer_id = int(data.get('customer_id'))
                Content = data.get('content')
                send_type = int(data.get('send_type'))

                flow_up_obj = models.zgld_user_customer_belonger.objects.select_related('user','customer').filter(user_id=user_id, customer_id=customer_id)

                if send_type == 1 and flow_up_obj: # 用戶發消息給客戶，修改最後跟進-時間
                    flow_up_obj.update(
                        is_user_msg_num=F('is_user_msg_num') + 1,
                        last_follow_time = datetime.datetime.now()
                    )

                _content = json.loads(Content)
                info_type = _content.get('info_type')

                if info_type:
                    info_type = int(info_type)

                    if info_type == 1:
                        msg = _content.get('msg')
                        encodestr = base64.b64encode(msg.encode('utf-8'))
                        msg = str(encodestr, 'utf-8')
                        _content['msg'] = msg
                        Content = json.dumps(_content)

                    elif info_type == 3:
                        msg = '您好,请问能否告诉我您的手机号?'
                        _content['msg'] = msg
                        Content = json.dumps(_content)

                    elif info_type == 6:
                        # 创建日志-- 发送小程序
                        models.zgld_accesslog.objects.create(
                            action=23,
                            user_id=user_id,
                            customer_id=customer_id,
                            remark='发送小程序',
                        )
                        msg = '官方商城，可点击进入购买'
                        _content['msg'] = msg
                        Content = json.dumps(_content)
                        if not  company_id:
                            company_id =  flow_up_obj[0].user.company_id
                        objs = models.zgld_company.objects.filter(id=company_id)
                        if objs:
                            shopping_type =  objs[0].shopping_type
                            print('---- 购物类型 ---->>',shopping_type)

                            if shopping_type == 1: # 开启产品
                                response.code = 303
                                response.msg = '此小程序没有开启商城'

                                return JsonResponse(response.__dict__)



                '''
                content 里的字段可以自定义增加, 本着对后端的尊重请和我商量下。
                
                content = {
                    'info_type' :  1 , # 1代表发送的文字\表情\ 或 话术库里的自定义(文字表情)。
                    'msg': '这个信息是文字\表情'
                }
                
                content = {
                     'info_type' : 2 , # 2代表发送的产品咨询  
                     'product_cover_url': 'statics/zhugeleida/imgs/chat/2d49ecd2-9180-11e8-a32d-8e2edea1cc9c.png',
                     'product_name': '产品名字',
                     'product_price': '产品价格',
                }
                content = {
                     'info_type' : 3   ,   # 3代表客户要触发事件要电话号码  
                     'msg': '您好,请问能否告诉我您的手机号?|您好,请问能否加下您的微信?'
                     ......
                }
                
                content = {
                     'info_type' : 4  ,   # 4代表发送的图片|截图
                     'url': 'statics/zhugeleida/imgs/chat/xxxx.jnp'
                     ......
                }
                content = {
                     'info_type' : 5  ,   # 4代表发送的 视频
                     'url': 'statics/zhugeleida/imgs/chat/YYYY.mp4'
                     ......
                } 
                
                content = {
                     'info_type' : 6  ,   # 4代表发送的商城
                     'msg': '请点击进去购买'
                     ......
                }  
        
                '''


                models.zgld_chatinfo.objects.filter(userprofile_id=user_id,customer_id=customer_id,is_last_msg=True).update(is_last_msg=False)

                # ----------------查询最近一次该用户和该客户聊天 的 文章 判断是否为 文章聊天
                zgld_chatinfo_obj = models.zgld_chatinfo.objects.filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=2,
                    article__isnull=False
                ).order_by('-create_date')

                article_id = None
                if zgld_chatinfo_obj:
                    article_id = zgld_chatinfo_obj[0].article_id # 如果最后一次聊天有文章ID 那么是从文章过来的 (雷达首页统计数据用)
                # ----------------------------------------------------

                obj = models.zgld_chatinfo.objects.create(
                        content=Content,
                        userprofile_id=user_id,
                        customer_id=customer_id,
                        send_type=1,
                        is_user_new_msg=False,
                        msg=int(time.time()),
                        article_id=article_id
                )

                user_type = obj.customer.user_type # 客户类型
                print('user_type, info_type, customer_id, user_id-------------------> ', user_type, customer_id, user_id)
                if customer_id and user_id and user_type == 2:
                    data['customer_id'] = customer_id
                    data['user_id'] = user_id
                    print('=----------------------------------执行celery-------------=======================')
                    response_celery = user_send_template_msg_to_customer(json.dumps(data))  # 发送【小程序】模板消息
                    print('---------==================response_celery============? ', response_celery)
                elif  user_type == 1 and info_type ==  6 and customer_id and user_id: # 发送商城 的模板消息,可以点击进去
                    print('--- 【公众号发送（商城）模板消息】 user_send_gongzhonghao_template_msg --->')
                    data['customer_id'] = customer_id
                    data['user_id'] = user_id
                    data['type'] = 'gongzhonghao_template_shopping_mall'
                    data['content'] = Content
                    user_send_gongzhonghao_template_msg.delay(data)  # 发送【公众号发送模板消息】

                elif  user_type == 1 and customer_id and user_id:
                    print('--- 【公众号发送模板消息】 user_send_gongzhonghao_template_msg')
                    data['customer_id'] = customer_id
                    data['user_id'] = user_id
                    # data['type'] = 'gongzhonghao_template_chat'
                    data['type'] = 'gongzhonghao_send_kefu_msg'
                    data['content'] = data.get('content')
                    user_send_gongzhonghao_template_msg(data) # 发送【公众号发送模板消息】
                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

                # redis_user_id_key = 'message_user_id_{uid}'.format(uid=user_id)
                redis_customer_id_key = 'message_customer_id_{cid}'.format(cid=customer_id)
                redis_customer_query_info_key = 'message_customer_id_{cid}_info_num'.format(cid=customer_id)

                # rc.set(redis_user_id_key, True)
                rc.set(redis_customer_query_info_key, True) # 通知公众号文章客户消息数量变化了
                rc.set(redis_customer_id_key, True)

                response.code = 200
                response.msg = '发送成功'

    else:

        # 获取数据
        if oper_type == 'getmsg':

            forms_obj = ChatGetForm(request.GET)
            if forms_obj.is_valid():
                response = Response.ResponseObj()
                user_id = request.GET.get('user_id')
                customer_id = request.GET.get('customer_id')

                objs = models.zgld_chatinfo.objects.select_related('userprofile', 'customer').filter(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    is_user_new_msg=True

                ).order_by('-create_date')

                ret_data_list = []
                count = objs.count()

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

                response.code = 200
                response.msg = '实时获取-最新聊天信息成功'
                print('--- list(msg_obj) -->>', ret_data_list)
                ret_data_list.reverse()
                response.data = {
                    'ret_data': ret_data_list,
                    'data_count': count,
                }
                objs.update(
                    is_user_new_msg=False
                )

                if not ret_data_list:
                    # 没有新消息
                    response.msg = '没有得到实时聊天信息'

                return JsonResponse(response.__dict__)

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)