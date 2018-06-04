from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.customer_verify import CustomerAddForm,  Customer_information_UpdateForm,Customer_UpdateForm , CustomerSelectForm
import json
from zhugeleida import models

from queue import Queue

GLOBAL_MQ = {

}


@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat(request):
    if request.method == 'POST':

        #获取用户发过来的数据
        print('=======>>>',request.POST)
        data = request.POST.copy()
        send_to_id = data.get('to')
        send_from_id = data.get('from')
        msg = data.get('msg')
        print('--- msg ->>',msg)

        #判断队列里是否有这个用户名,如果没有新建一个队列
        if send_to_id not in GLOBAL_MQ:
            GLOBAL_MQ[send_to_id] = Queue()

        data['timestamp'] = time.strftime("%Y-%m-%d %X", time.localtime())
        if int(data['send_type']) == 1: # user to customer 发送消息
            info_chat_create_obj = models.zgld_chatinfo.objects.create(msg = msg)
            info_chat_get_obj = models.zgld_chatinfo.objects.get(id=info_chat_create_obj.id)
            info_chat_get_obj.userprofile_id = send_to_id
            info_chat_get_obj.customer_id = send_from_id
            info_chat_get_obj.send_type = 1
            info_chat_create_obj.save()
            info_chat_get_obj.save()

        elif int(data['send_type']) == 2:  # customer to user 发送消息
            info_chat_create_obj = models.zgld_chatinfo.objects.create(
                msg = msg
            )
            info_chat_get_obj = models.zgld_chatinfo.objects.get(id=info_chat_create_obj.id)
            info_chat_get_obj.customer_id = send_to_id
            info_chat_get_obj.userprofile_id = send_from_id
            info_chat_get_obj.send_type = 2
            info_chat_create_obj.save()
            info_chat_get_obj.save()

        GLOBAL_MQ[send_to_id].put(data)
        print('----GLOBAL_MQ[send_to]---->>', GLOBAL_MQ[send_to_id].qsize())

        return HttpResponse(GLOBAL_MQ[send_to_id].qsize())

    else:
        #因为队列里目前存的是字符串所以我们需要先给他转换为字符串
        request_user = str(request.GET.get('user_id'))
        msg_lists = []
        #判断是否在队列里
        if request_user in GLOBAL_MQ:
            #判断有多少条消息
            stored_msg_nums = GLOBAL_MQ[request_user].qsize()
            print('@@@@@@@ stored_msg_nums 2 ==========>',GLOBAL_MQ[request_user].qsize(),'\n')
            try:
                #如果没有新消息
                if stored_msg_nums == 0:
                    print ("\033[41;1m没有消息等待,15秒.....\033[0m")
                    msg_lists.append(GLOBAL_MQ[request_user].get(timeout=15))
                '''
                    如果队列里面有没有消息,get就会阻塞,等待有新消息之后会继续往下走,这里如果阻塞到这里了,等有新消息过来之后,把消息加入到
                    msg_lists中后,for循环还是不执行的因为,这个stored_msg_mums是在上面生成的变量下面for调用这个变量的时候他还是为0
                    等返回之后再取得时候,现在stored_msg_nums不是0了,就执行执行for循环了,然后发送数据
                '''
            except Exception as e:
                print ('error:',e)
                print ("\033[43;1等待已超时......15秒.....\033[0m")

            # 把消息循环加入到列表中并发送
            for i in range(stored_msg_nums):
                msg_lists.append(GLOBAL_MQ[request_user].get())
            print('---msg_lists---->>',msg_lists[0]['msg'])

        else:
            #创建一个新队列给这个用户
            GLOBAL_MQ[str(request.POST.get('user_id'))] = Queue()

        return HttpResponse(json.dumps(msg_lists))

@csrf_exempt
@account.is_token(models.zgld_userprofile)
def chat_oper(request,oper_type,o_id):
    response = Response.ResponseObj()
    if request.method == "GET":

        if oper_type == 'getmsg':

            customer_id = request.GET.get('customer_id')
            userprofile_id = request.GET.get('user_id')
            order = request.GET.get('order', '-create_date')
            chat_info_list  = list(models.zgld_chatinfo.objects.select_related('userprofile','customer').filter(userprofile_id=userprofile_id, customer_id=customer_id).values('id','userprofile_id','userprofile__name','customer_id',
                                                                                        'customer__username', 'send_type',
                                                                                        'msg','create_date',).order_by(order))

            response.code = 200
            response.data = {
                'ret_data': chat_info_list,
                'data_count': 20,
            }
            return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


