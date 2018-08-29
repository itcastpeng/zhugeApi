from django.conf.urls import url

from zhugeleida.views_dir.gongzhonghao import user_gongzhonghao_auth,article


urlpatterns = [
    # url(r'^login$', login.login),

    # 代公众号 - 登录认证
    url(r'^work_gongzhonghao_auth$', user_gongzhonghao_auth.user_gongzhonghao_auth),
    url(r'^work_gongzhonghao_auth/(?P<oper_type>\w+)$', user_gongzhonghao_auth.user_gongzhonghao_auth_oper),

    #代公众号-生成公众号认证URl
    # url(r'^create_gongzhonghao_auth_url/(?P<company_id>\d+)', user_gongzhonghao_auth.create_gongzhonghao_auth_url),

    # 公众号文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),



]
