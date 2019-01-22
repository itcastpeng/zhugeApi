from django.conf.urls import url

from zhugeleida.views_dir.mycelery_task import mycelery,mycelery_expand


urlpatterns = [

    # 权限操作
    url(r'^user_send_action_log$', mycelery.user_send_action_log),   # 小程序访问动作日志的发送到企业微信
    url(r'^user_forward_send_activity_redPacket$', mycelery.user_forward_send_activity_redPacket),   # 关注发红包和转发文章满足就发红包
    url(r'^user_focus_send_activity_redPacket$', mycelery.user_focus_send_activity_redPacket),   # 关注发红包和转发文章满足就发红包
    url(r'^bufa_send_activity_redPacket$', mycelery.bufa_send_activity_redPacket),               # 补发红包 发红包

    url(r'^get_customer_gongzhonghao_userinfo$', mycelery.get_customer_gongzhonghao_userinfo),   # 异步获取公众号用户信息[用三方平台token]
    url(r'^binding_article_customer_relate$', mycelery.binding_article_customer_relate),         # 绑定客户和文章的关系


    url(r'^create_user_or_customer_qr_code$', mycelery.create_user_or_customer_qr_code),     # 生成小程序二维码
    url(r'^qiyeweixin_user_get_userinfo$', mycelery.qiyeweixin_user_get_userinfo),           # 获取企业用户信息
    url(r'^create_user_or_customer_poster$', mycelery.create_user_or_customer_poster),       # 生成小程序的海报


    url(r'^user_send_template_msg$', mycelery.user_send_template_msg),                               # 发送模板消息
    url(r'^user_send_gongzhonghao_template_msg$', mycelery.user_send_gongzhonghao_template_msg),     # 发送公众号的模板消息
    url(r'^get_latest_audit_status_and_release_code$', mycelery.get_latest_audit_status_and_release_code),     # 定时检测代小程序发布审核状态

    url(r'^crontab_create_user_to_customer_qrCode_poster$', mycelery.crontab_create_user_to_customer_qrCode_poster),     # 定时生成海报

    url(r'^common_send_gzh_template_msg$', mycelery_expand.common_send_gzh_template_msg),  # 发送公众号的模板消息
    url(r'^crontab_batchget_article_material$', mycelery_expand.batchget_article_material),  # 定时器获取微信公众号文章到文章模板库
    url(r'^batchget_article_material$', mycelery_expand.batchget_article_material),  # 定时器获取微信公众号文章到文章模板库
    url(r'^record_money_process$', mycelery.record_money_process),                   # 发送公众号的模板消息

    url(r'^bossLeida_acount_data_and_line_info/(?P<oper_type>\w+)', mycelery_expand.bossLeida_acount_data_and_line_info),  # 发送公众号的模板消息




]
