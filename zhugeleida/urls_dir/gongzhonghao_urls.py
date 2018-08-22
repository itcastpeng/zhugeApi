from django.conf.urls import url

from zhugeleida.views_dir.gongzhonghao import user_gongzhonghao_auth,article


urlpatterns = [
    # url(r'^login$', login.login),

    # 微信公招号登录认证
    url(r'^work_gongzhonghao_auth/(?P<company_id>\d+)', user_gongzhonghao_auth.user_gongzhonghao_auth),

    # 公众号文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),



]
