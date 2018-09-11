from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import boss_leida

urlpatterns = [
    # 文章的标签管理
    # url(r'^article_tag/(?P<oper_type>\w+)/(?P<o_id>\d+)$', article_tag.article_tag_oper),
    # url(r'^article_tag$', article_tag.article_tag),

    # boos雷达数据统计
    url(r'^home_page/(?P<oper_type>\w+)$', boss_leida.home_page_oper),
    # url(r'^boss_leida$', boss_leida.home_page),



]
