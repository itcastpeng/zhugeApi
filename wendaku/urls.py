from django.conf.urls import url

from wendaku.views_dir import login

urlpatterns = [
    # url(r'^wenku/', include('wendaku.urls')),
    url(r'login', login.login),

]
