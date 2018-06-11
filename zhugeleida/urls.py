from django.conf.urls import url, include
from zhugeleida.urls_dir  import admin_urls


urlpatterns = [
    url(r'^admin/',include('zhugeleida.urls_dir.admin_urls')),
    url(r'^gongzhonghao/', include('zhugeleida.urls_dir.gongzhonghao_urls')),
    url(r'^qiyeweixin/', include('zhugeleida.urls_dir.qiyeweixin_urls')),
    url(r'^xiaochengxu/', include('zhugeleida.urls_dir.xiaochengxu_urls')),

]
