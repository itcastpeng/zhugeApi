from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import  user,quanxian, customer
from zhugeleida.views_dir.xiaochengxu import login,mingpian,product, prepaidManagement, theOrderManagement, tuiKuanDingDan, mallManagementShow
from zhugeleida.views_dir.xiaochengxu  import chat,website


urlpatterns = [

    # 权限操作
    url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)', quanxian.quanxian_oper),
    url(r'^quanxian', quanxian.quanxian),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    #修改客户和客户信息表
    url(r'^customer/(?P<oper_type>\w+)/(?P<o_id>\d+)', customer.customer_oper),
    url(r'^customer$', customer.customer),

    #实时聊天
    url(r'^chat/(?P<oper_type>\w+)/(?P<o_id>\d+)', chat.chat_oper),
    url(r'^chat$',chat.chat),

    #访问小程序的名片\并记录访问功能。
    url(r'^mingpian$',mingpian.mingpian),
    url(r'^mingpian/poster_html$', mingpian.mingpian_poster_html_oper),
    url(r'^mingpian/(?P<oper_type>\w+)', mingpian.mingpian_oper),

    #查看产品 + 查看竞价产品 + 转发竞价产品 + 咨询产品。
    url(r'^product/(?P<oper_type>\w+)', product.product),
    # url(r'^product/(?P<oper_type>\w+)', product.product_oper),

    #小程序登录认证 + 绑定关系 + 信息入库
    url(r'^login$', login.login),
    url(r'^login/control_mingan_info$', login.login_oper_control),
    url(r'^login/(?P<oper_type>\w+)$', login.login_oper),

    #小程序官网
    url(r'website$',website.website),

    # 小程序支付操作
    url(r'payback', prepaidManagement.payback),                                    # 回调信息
    url(r'yuZhiFu', prepaidManagement.yuZhiFu),                             # 预支付

    # 订单管理
    url(r'theOrderShow', theOrderManagement.theOrderShow),                 # 订单管理查询
    url(r'^theOrderOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', theOrderManagement.theOrderOper),           # 订单管理操作

    # 退款单管理
    url(r'tuiKuanDingDanShow', tuiKuanDingDan.tuiKuanDingDanShow),                 # 退款订单管理查询
    url(r'^tuiKuanDingDanOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', tuiKuanDingDan.tuiKuanDingDanOper),           # 退款订单管理操作

    # 员工订单管理
    # url(r'theOrderShow', theOrderManagement.theOrderShow),                 # 订单管理查询
    # url(r'^theOrderOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', theOrderManagement.theOrderOper),           # 订单管理操作

    # 查询商品
    url(r'mallManageShow', mallManagementShow.mallManageShow),                 # 订单管理查询

]
