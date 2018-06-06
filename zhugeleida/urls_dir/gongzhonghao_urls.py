from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import login


urlpatterns = [
    url(r'^login$', login.login),


]
