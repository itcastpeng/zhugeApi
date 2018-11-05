from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import boss_leida

urlpatterns = [

    # boos雷达数据统计
    url(r'^home_page/(?P<oper_type>\w+)$', boss_leida.home_page_oper),

]
