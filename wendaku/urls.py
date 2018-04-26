from django.conf.urls import url

from wendaku.views_dir import login, role, user

urlpatterns = [
    # url(r'^wenku/', include('wendaku.urls')),
    url(r'^login$', login.login),

    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user)
]