from django.conf.urls import url

from zhugeleida.views_dir.mycelery import mycelery


urlpatterns = [

    # 权限操作
    url(r'^user_send_action_log', mycelery.user_send_action_log),   # 小程序访问动作日志的发送到企业微信
    url(r'^create_user_or_customer_qr_code', mycelery.create_user_or_customer_qr_code),     # 生成小程序二维码
    url(r'^create_user_or_customer_poster', mycelery.create_user_or_customer_poster),     # 生成小程序的海报


    url(r'^user_send_template_msg', mycelery.user_send_template_msg),     # 发送模板消息
    url(r'^user_send_gongzhonghao_template_msg', mycelery.user_send_gongzhonghao_template_msg),     # 发送公众号的模板消息
    url(r'^get_latest_audit_status_and_release_code$', mycelery.get_latest_audit_status_and_release_code),     # 定时检测代小程序发布审核状态



]
