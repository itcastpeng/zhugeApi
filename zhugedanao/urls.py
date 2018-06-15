from django.conf.urls import url


from zhugedanao.views_dir.wechat import wechat

urlpatterns = [

    # url(r'^w_login',login.w_login),

    # 微信
    url(r'^wechat', wechat.index),

    # 获取用于登录的微信二维码
    url(r'^generate_qrcode', wechat.generate_qrcode),


]
