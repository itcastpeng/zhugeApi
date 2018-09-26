
from zhugeleida import models
from publicFunc import Response

import datetime
import json
from zhugeapi_celery_project import tasks
import base64
import qrcode
from django.conf import settings
import os

def action_record(data,remark):
    response = Response.ResponseObj()
    user_id = data.get('uid')  # 用户 id
    customer_id = data.get('user_id')  # 客户 id
    article_id = data.get('article_id')  # 客户 id
    action = data.get('action')

    print('----- customer_id |  user_id | action ----->>',customer_id,user_id,action)

    if action in [0]: # 只发消息，不用记录日志。
        customer_name = models.zgld_customer.objects.get(id=customer_id).username
        company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id

        customer_name = base64.b64decode(customer_name)
        customer_name = str(customer_name, 'utf-8')

        data['content'] = '%s%s' % (customer_name, remark)
        # data['agentid'] = models.zgld_app.objects.get(id=company_id, name='AI雷达').agent_id
        data['agentid'] = models.zgld_app.objects.get(company_id=company_id, app_type=1).agent_id

        tasks.user_send_action_log.delay(json.dumps(data))
        response.code = 200
        response.msg = '发送消息提示成功'

    elif action in [14,15,16]:
        # 创建访问日志
        models.zgld_accesslog.objects.create(
            user_id=user_id,
            article_id=article_id,
            customer_id=customer_id,
            remark=remark,
            action=action
        )

        customer_name = models.zgld_customer.objects.get(id=customer_id).username
        company_id = models.zgld_userprofile.objects.filter(id=user_id)[0].company_id

        customer_name = base64.b64decode(customer_name)
        customer_name = str(customer_name, 'utf-8')
        print('------ 客户姓名 + 访问日志信息------->>', customer_name, remark)

        data['content'] = '%s%s' % (customer_name, remark)
        # data['agentid'] = models.zgld_app.objects.get(id=company_id, name='AI雷达').agent_id
        data['agentid'] = models.zgld_app.objects.get(company_id=company_id, app_type=1).agent_id
        print('------------ [公众号] 传给tasks.celery的 json.dumps 数据 ------------------>>', json.dumps(data))

        tasks.user_send_action_log.delay(json.dumps(data))
        response.code = 200
        response.msg = '发送消息提示成功'


    else:
        # 创建访问日志
        models.zgld_accesslog.objects.create(
            user_id=user_id,
            customer_id=customer_id,
            remark=remark,
            action=action
        )

        # 查询客户与用户是否已经建立关系
        follow_objs = models.zgld_user_customer_belonger.objects.select_related('user', 'customer').filter(
            user_id=user_id,
            customer_id=customer_id
        )
        now_time = datetime.datetime.now()
        if follow_objs:  # 已经有关系了
            follow_obj = follow_objs[0]
            follow_objs.update(
                last_activity_time=now_time
               )

            company_id = follow_obj.user.company_id
            customer_name = follow_obj.customer.username

            customer_name = base64.b64decode(customer_name)
            customer_name = str(customer_name, 'utf-8')
            print('------ 客户姓名 + 访问日志信息------->>', customer_name, remark)

            data['content'] = '%s%s' % (customer_name,remark)
            # data['agentid'] = models.zgld_app.objects.get(company_id=company_id, name='AI雷达').agent_id
            data['agentid'] = models.zgld_app.objects.get(company_id=company_id, app_type=1).agent_id

            print('------------ 传给tasks.celery的 json.dumps 数据 ------------------>>',json.dumps(data))
            ret = tasks.user_send_action_log.delay(json.dumps(data))
            print('--- 记录_动作日志_log ret -->', ret)
            response.code = 200
            response.msg = '记录日志成功'

    return response


def create_qrcode(data):
    url = data.get('url')
    article_id = data.get('article_id')

    response = Response.ResponseObj()
    qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.show()

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'gongzhonghao', 'article')

    qr_code_name = '/article_%s_%s_qrCode.jpg' % (article_id, now_time)
    path_qr_code_name = BASE_DIR + qr_code_name
    qr_url = 'statics/zhugeleida/imgs/gongzhonghao/article%s' % (qr_code_name)

    img.save(path_qr_code_name)
    response.data = {'pre_qrcode_url': qr_url}
    response.code = 200
    response.msg = '生成文章体验二维码成功'
    print('---------生成文章体验二维码成功--------->>', qr_url)

    return response

def create_scan_code_userinfo_qrcode(data):
    url = data.get('url')
    admin_uid = data.get('admin_uid')

    response = Response.ResponseObj()
    qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.show()

    now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    BASE_DIR = os.path.join(settings.BASE_DIR, 'statics', 'zhugeleida', 'imgs', 'admin', 'qr_code')

    qr_code_name = '/admin_uid_%s_%s_qrCode.jpg' % (admin_uid, now_time)
    path_qr_code_name = BASE_DIR + qr_code_name
    qr_url = 'statics/zhugeleida/imgs/admin/qr_code%s' % (qr_code_name)

    img.save(path_qr_code_name)
    response.data = {'qrcode_url': qr_url}
    response.code = 200
    response.msg = '生成文章体验二维码成功'
    print('---------生成文章体验二维码成功--------->>', qr_url)


    return response


## 把秒数换换成 时|分|秒
def  conversion_seconds_hms(seconds):

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time = 0
    if not h and not m and s:
        print("%s秒" % (s))
        time = "%s秒" % (s)
    elif not h and m and s:
        print("%s分%s秒" % (m, s))
        time = "%s分%s秒" % (m, s)

    elif h and m and s:
        print("%s时%s分%s秒" % (h, m, s))
        time = "%s时%s分%s秒" % (h, m, s)
    return time

