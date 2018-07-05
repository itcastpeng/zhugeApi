
from zhugeleida import models
from publicFunc import Response

import datetime
import json
from zhugeapi_celery_project import tasks


# 记录访问日志，例如访问某个功能（名片，产品，官网...）
# 创建客户与用户之间的关系

def action_record(data,remark):
    response = Response.ResponseObj()
    user_id = data.get('uid')  # 用户 id
    customer_id = data.get('user_id')  # 客户 id
    action = data.get('action')

    # 创建访问日志
    obj = models.zgld_accesslog.objects.create(
        user_id=user_id,
        customer_id=customer_id,
        remark=remark,
        action=action
    )

    # 查询客户与用户是否已经建立关系
    follow_objs = models.zgld_user_customer_flowup.objects.select_related('user', 'customer').filter(
        user_id=user_id,
        customer_id=customer_id
    )
    if follow_objs:  # 已经有关系了
        flowup_obj = follow_objs[0]
        obj.activity_time_id = flowup_obj.id
        follow_objs.update(last_activity_time=datetime.datetime.now())
        obj.save()
        # follow_objs[0].save()
        response.code = 200
        response.msg = '记录日志成功'


    else: # 没有对应关系，要创建对应关系
        flowup_obj = models.zgld_user_customer_flowup.objects.create(
            user_id=user_id,
            customer_id=customer_id,
            last_activity_time=datetime.datetime.now()
        )
        obj.activity_time_id = flowup_obj.id
        obj.save()
        response.code = 200
        response.msg = '记录日志成功'

    company_id = flowup_obj.user.company_id
    customer_name = flowup_obj.customer.username
    #
    data['content'] = customer_name + remark
    data['agentid'] = models.zgld_app.objects.get(
        id=company_id,
        name='AI雷达'
    ).agent_id

    tasks.user_send_action_log.delay(json.dumps(data))
    # user_send_action_log(data)  #发送企业微信的消息提醒

    return response


