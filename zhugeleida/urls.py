from django.conf.urls import url, include
from zhugeleida.urls_dir  import admin_urls


urlpatterns = [

    # 雷达后台
    url(r'^admin/', include('zhugeleida.urls_dir.admin_urls')),

    # 公众号文章
    url(r'^gongzhonghao/', include('zhugeleida.urls_dir.gongzhonghao_urls')),

    # AI雷达
    url(r'^qiyeweixin/', include('zhugeleida.urls_dir.qiyeweixin_urls')),

    # 小程序
    url(r'^xiaochengxu/', include('zhugeleida.urls_dir.xiaochengxu_urls')),

    # 异步处理
    url(r'^mycelery/', include('zhugeleida.urls_dir.celery_urls')),


    url(r'^public/', include('zhugeleida.urls_dir.public_urls')),

    # boos雷达
    url(r'^boosleida/', include('zhugeleida.urls_dir.boosleida_urls'))
]
