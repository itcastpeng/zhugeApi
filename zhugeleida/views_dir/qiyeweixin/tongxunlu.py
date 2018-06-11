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
            order = request.GET.get('order', '-create_date')  # 排序为【默认为】成交率; 最后跟进时间; 最后活动时间
            field_dict = {
                'customer_id': '',
                'user_id': '',
                'username': '__contains',
                'belonger__username': '__contains',  # 归属人
                'superior__username': '__contains',  # 上级人
                'expected_time': '__contains',  # 预测成交时间
                'source': '',                   # 搜索转码 或者 转发
                ''
                'create_date': '',

            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.zgld_user_customer_flowup.objects.select_related('user','customer').filter(q).order_by(order)

            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            print('=====  objs ====>', objs)

            if objs:
                for obj in objs:

                    ai_pr = 0

                    date_interval_msg = ''
                    follow_up_obj = obj.last_follow_time  # 关联的跟进表是否有记录值，没有的话说明没有跟进记录。
                    if not follow_up_obj:
                        date_interval_msg = '未跟进过'

                    elif follow_up_obj:
                        last = obj.flowup.filter(is_last_follow_time=True)[0].last_follow_time
                        now = datetime.datetime.now()
                        date_interval = (now - last).days

                        if date_interval == 0:
                            date_interval_msg = '今天新增'
                        else:
                            date_interval = date_interval - int(1)
                            date_interval_msg = '%s天前已经跟进' % (date_interval)

                    ret_data.append({
                        'customer_id': obj.id,
                        'customer_username': obj.username,
                        'openid': obj.openid,
                        'headimgurl': obj.headimgurl,
                        'expected_time': obj.expected_time,  # 预计成交时间
                        'expedted_pr': obj.expedted_pr,      # 预计成交概率
                        'ai_pr': ai_pr,                      # AI 预计成交概率
                        'belonger': obj.belonger.username,   # 所属用户
                        'source': obj.source,                # 来源
                        'flow_time': date_interval_msg,      # 跟进时间

                    })

                    print('-------for 2 ---->>', ret_data)

                #  查询成功 返回200 状态码
                print('----ret_data----->', ret_data)

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
