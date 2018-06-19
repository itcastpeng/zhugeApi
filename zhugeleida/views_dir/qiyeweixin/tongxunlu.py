from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.qiyeweixin.tongxunlu_verify import TongxunluSelectForm
import json
import datetime


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tongxunlu(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = TongxunluSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-customer__expedted_pr')  # 排序为【默认为】成交率; 最后跟进时间; 最后活动时间
            field_dict = {
                'customer_id': '',
                'user_id': '',
                'username': '__contains',
                'belonger__username': '__contains',  # 归属人
                'superior__username': '__contains',  # 上级人
                'expected_time': '__contains',  # 预测成交时间
                'source': '',  # 搜索转码 或者 转发
                'create_date': '',

            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.zgld_user_customer_flowup.objects.select_related('user', 'customer').filter(q).order_by(order)

            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            print('=====  objs ====>', objs)
            customer_status = ''
            if objs:
                for obj in objs:
                    ai_pr = 0
                    last_interval_msg = ''
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
                                customer_status = '%s天前已跟进' % (day_interval)

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
                                day_interval = day_interval - 1
                                last_activity_msg = '%s天前' % (day_interval)

                    ret_data.append({
                        'customer_id': obj.id,
                        'customer_username': obj.customer.username,
                        'headimgurl': obj.customer.headimgurl,
                        'expected_time': obj.customer.expected_time,  # 预计成交时间
                        'expedted_pr': obj.customer.expedted_pr,  # 预计成交概率
                        # 'ai_pr': ai_pr,  # AI 预计成交概率
                        'belonger': obj.customer.belonger.username,  # 所属用户
                        'source': obj.customer.get_source_display(),  # 来源
                        'last_follow_time': last_interval_msg,  # 最后跟进时间
                        'last_activity_time':  last_activity_msg,                # 最后活动时间
                        'follow_status': customer_status,       #跟进状态

                    })

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)
