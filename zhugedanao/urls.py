from django.conf.urls import url

<<<<<<< HEAD
=======
from zhugedanao.views_dir.wechat import wechat
>>>>>>> upstream/dev

urlpatterns = [

    # url(r'^w_login',login.w_login),

    # 微信
    url(r'^wechat/', wechat.index),


]
