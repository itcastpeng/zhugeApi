from django.conf.urls import url

from zhugedanao.views_dir import login, wechat

urlpatterns = [

    url(r'^w_login',login.w_login),

    # 微信
    url(r'^wechat/', wechat.index),


]
