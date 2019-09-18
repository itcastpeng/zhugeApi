from django.conf.urls import url

from zhugeleida.views_dir.gongzhonghao import user_gongzhonghao_auth,article,chat,plugin_report

from zhugeleida.views_dir.public import  websocket
urlpatterns = [
    # url(r'^login$', login.login),

    # 代公众号 - 登录认证
    url(r'^work_gongzhonghao_auth$', user_gongzhonghao_auth.user_gongzhonghao_auth),

    # 分享出去的文章链接当点击后跳转。
    url(r'^work_gongzhonghao_auth/redirect_share_url$', user_gongzhonghao_auth.user_gongzhonghao_redirect_share_url),

    # 微信公众号-JS-SDK使用权限签名算法
    url(r'^work_gongzhonghao_auth/(?P<oper_type>\w+)$', user_gongzhonghao_auth.user_gongzhonghao_auth_oper),

    # 实时聊天
    url(r'^chat/(?P<oper_type>\w+)/(?P<o_id>\d+)$', chat.chat_oper),
    url(r'^chat$', chat.chat),

    # 实时聊天
    url(r'^websocket/(?P<oper_type>\w+)$', websocket.gongzhonghao_websocket),

    # 公众号文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)$', article.article_oper),

    # 插件活动报名
    url(r'^plugin_report/(?P<oper_type>\w+)/(?P<o_id>\d+)', plugin_report.plugin_report_oper),

    # 转发出去的录播视频 跳转地址
    url(r'^forwarding_video_jump_address$', user_gongzhonghao_auth.forwarding_video_jump_address),

]
