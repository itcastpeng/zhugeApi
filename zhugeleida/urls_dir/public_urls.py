from django.conf.urls import url

from zhugeleida.views_dir.public import img_upload, fild_upload,websocket,open_weixin_api,myself_tools

urlpatterns = [

    # 图片分片上传与合并
    url(r'^img_upload$', img_upload.img_upload),
    url(r'^img_merge$', img_upload.img_merge),

    # 百度编辑器上传图片
    url(r'^ueditor_img_upload$', img_upload.ueditor_image_upload),

    # 上传文件
    url(r'^fild_upload$', fild_upload.fild_upload),

    # 后台扫码登录
    url(r'^websocket/(?P<oper_type>\w+)$', websocket.public_websocket),
    # url(r'^create_token/(?P<oper_type>\w+)$', open_weixin_api.crate_token),
    url(r'^myself_tools/(?P<oper_type>\w+)$',myself_tools.tools_oper) #内部工具的链接
]