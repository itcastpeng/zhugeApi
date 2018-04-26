from django.conf.urls import url

from wendaku.views_dir import login,role

urlpatterns = [
    # url(r'^wenku/', include('wendaku.urls')),
    url(r'^login$', login.login),

    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),



]
