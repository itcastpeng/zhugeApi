from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^gongzhonghao/', include('zhugeleida.urls_dir.gongzhonghao_urls')),
    url(r'^qiyeweixin/', include('zhugeleida.urls_dir.qiyeweixin_urls')),
    url(r'^xiaochengxu/', include('zhugeleida.urls_dir.xiaochengxu_urls')),

]
