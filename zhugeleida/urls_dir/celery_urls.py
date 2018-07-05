from django.conf.urls import url

from zhugeleida.views_dir.mycelery import mycelery


urlpatterns = [

    # 权限操作
    url(r'^user_send_action_log', mycelery.user_send_action_log),
    url(r'^create_user_or_customer_qr_code', mycelery.create_user_or_customer_qr_code),



]
