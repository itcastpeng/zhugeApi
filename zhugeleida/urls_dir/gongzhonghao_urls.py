from django.conf.urls import url

from zhugeleida.views_dir.gongzhonghao import user_gongzhonghao_auth


urlpatterns = [
    # url(r'^login$', login.login),

    # 微信公招号登录认证
    url(r'^work_gongzhonghao_auth/(?P<company_id>\d+)', user_gongzhonghao_auth.user_gongzhonghao_auth),



]
