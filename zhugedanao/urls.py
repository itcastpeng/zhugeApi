from django.conf.urls import url


from zhugedanao.views_dir.wechat import wechat
from zhugedanao.views_dir import oper_log

urlpatterns = [

    # url(r'^w_login',login.w_login),

    # 微信
    url(r'^wechat$', wechat.index),

    # 判断是否登录
    url(r'^wechat_login$', wechat.wechat_login),

    # 获取用于登录的微信二维码
    url(r'^generate_qrcode$', wechat.generate_qrcode),

    url(r'^oper_log$', oper_log.oper_log),

]
