from django.conf.urls import url

from zhugeleida.views_dir.public import img_upload, fild_upload,websocket,open_weixin_api

urlpatterns = [
    url(r'^img_upload$', img_upload.img_upload),
    url(r'^ueditor_img_upload$', img_upload.ueditor_image_upload),
    url(r'^img_merge$', img_upload.img_merge),
    url(r'^fild_upload$', fild_upload.fild_upload),
    url(r'^websocket/(?P<oper_type>\w+)$', websocket.public_websocket),
    url(r'^create_token/(?P<oper_type>\w+)$', open_weixin_api.crate_token),

]