from django.conf.urls import url

from zhugeleida.views_dir.admin import login


urlpatterns = [
    url(r'^login$', login.login),


]
