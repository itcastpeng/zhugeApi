from django.conf.urls import url

from zhugedanao.views_dir import login

urlpatterns = [

    url(r'^w_login',login.w_login)

]
