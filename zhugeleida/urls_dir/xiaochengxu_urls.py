from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import  user,quanxian,tag_customer,user_weixin_auth,customer
from zhugeleida.views_dir.xiaochengxu import login,mingpian,product
from zhugeleida.views_dir.xiaochengxu  import chat


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
    url(r'^mingpian/(?P<oper_type>\w+)', mingpian.mingpian_oper),

    #查看产品 + 查看竞价产品 + 转发竞价产品 + 咨询产品。
    url(r'^product/(?P<oper_type>\w+)/', product.product),

    # url(r'^product/(?P<oper_type>\w+)', product.product_oper),

    #小程序登录认证
    url(r'^login$', login.login)


]
