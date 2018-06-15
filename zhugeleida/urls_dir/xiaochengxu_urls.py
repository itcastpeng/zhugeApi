from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import  user,quanxian,tag_customer,user_weixin_auth,customer
from zhugeleida.views_dir.xiaochengxu import login,mingpian
from zhugeleida.views_dir.xiaochengxu  import chat


urlpatterns = [
    # url(r'^login$', login.login),

    # 权限操作
    url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)', quanxian.quanxian_oper),
    url(r'^quanxian', quanxian.quanxian),

    # 角色操作
    # url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    # url(r'^role$', role.role),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # # 公司操作
    # url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    # url(r'^company$', company.company),

    # 标签操作
    # url(r'^tag/(?P<oper_type>\w+)/(?P<o_id>\d+)', tag.tag_oper),
    # url(r'^tag$', tag.tag_user),

    #修改客户和客户信息表
    url(r'^customer/(?P<oper_type>\w+)/(?P<o_id>\d+)', customer.customer_oper),
    url(r'^customer$', customer.customer),

    #实时聊天
    url(r'^chat/(?P<oper_type>\w+)/(?P<o_id>\d+)', chat.chat_oper),
    url(r'^chat$',chat.chat),

    #获取联系人列表
    # url(r'^contact$',contact.contact),

    #访问小程序的名片
    url(r'^mingpian$',mingpian.mingpian),


    #小程序登录认证
    url(r'^login$', login.login)


]
