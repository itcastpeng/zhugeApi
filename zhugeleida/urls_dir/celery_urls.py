from django.conf.urls import url

from zhugeleida.views_dir.mycelery import mycelery


urlpatterns = [

    # 权限操作
    url(r'^user_send_action_log', mycelery.user_send_action_log),   # 小程序访问动作日志的发送到企业微信
    url(r'^create_user_or_customer_qr_code', mycelery.create_user_or_customer_qr_code),     # 生成小程序二维码
    url(r'^user_send_template_msg', mycelery.user_send_template_msg),     # 发送模板消息



]
