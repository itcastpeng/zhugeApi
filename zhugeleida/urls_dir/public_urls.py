from django.conf.urls import url

from zhugeleida.views_dir.public import img_upload

urlpatterns = [
    url(r'^img_upload$', img_upload.img_upload),
    url(r'^img_merge$', img_upload.img_merge),

]