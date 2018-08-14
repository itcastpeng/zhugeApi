from django.conf.urls import url


from zhugedanao.views_dir.wechat import wechat
from zhugedanao.views_dir import oper_log
from zhugedanao.views_dir import tongji_data
from zhugedanao.views_dir import lianjie_tijiao

urlpatterns = [

    # url(r'^w_login',login.w_login),

    # 微信
    url(r'^wechat$', wechat.index),

    # 判断是否登录
    url(r'^wechat_login$', wechat.wechat_login),

    # 获取用于登录的微信二维码
    url(r'^generate_qrcode$', wechat.generate_qrcode),

    # 记录使用日志
    url(r'^oper_log$', oper_log.oper_log),

    # 微信公众号获取统计数据
    url(r'^tongji_data$', tongji_data.tongji_data),

    # 需求管理
    url(r'^lianjie_tijiao/(?P<oper_type>\w+)/(?P<o_id>\d+)', lianjie_tijiao.lianjie_tijiao_oper),
    url(r'^lianjie_tijiao', lianjie_tijiao.lianjie_tijiao),

]
