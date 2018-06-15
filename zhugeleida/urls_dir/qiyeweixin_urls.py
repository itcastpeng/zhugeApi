from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import user, quanxian, action, tag_customer, user_weixin_auth, customer, tongxunlu, \
    qr_code_auth, follow_language, follow_info,tag_list
from zhugeleida.views_dir.qiyeweixin import chat, contact,search

urlpatterns = [
    # url(r'^login$', login.login),

    # 权限操作
    url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)', quanxian.quanxian_oper),
    url(r'^quanxian', quanxian.quanxian),

    # # 角色操作
    # url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    # url(r'^role$', role.role),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # # 公司操作
    # url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    # url(r'^company$', company.company),

    # 标签和标签用户的操作
    url(r'^tag_customer/(?P<oper_type>\w+)/(?P<o_id>\d+)', tag_customer.tag_customer_oper),
    url(r'^tag_customer$', tag_customer.tag_customer),

    # 标签列表和标签列表的的操作
    url(r'^tag_list/(?P<oper_type>\w+)/(?P<o_id>\d+)', tag_list.tag_list_oper),
    url(r'^tag_list$', tag_list.tag_list),

    #搜索(客户\标签)
    url(r'^search/(?P<oper_type>\w+)$', search.search),


    # 修改客户详情和客户关联信息表
    url(r'^customer/(?P<oper_type>\w+)/(?P<o_id>\d+)', customer.customer_oper),
    url(r'^customer$', customer.customer),

    # 客户通讯录
    url(r'^tongxunlu$', tongxunlu.tongxunlu),

    # 用户跟进常用语
    url(r'follow_language$', follow_language.follow_language),
    url(r'follow_language/(?P<oper_type>\w+)/(?P<o_id>\d+)', follow_language.follow_language_oper),

    # 用户跟进信息
    url(r'follow_info$', follow_info.follow_info),
    url(r'follow_info/(?P<oper_type>\w+)/(?P<o_id>\d+)', follow_info.follow_info_oper),

    # 实时聊天 一对多
    url(r'^chat/(?P<oper_type>\w+)/(?P<o_id>\d+)', chat.chat_oper),
    url(r'^chat$', chat.chat),

    # 获取聊天联系人列表
    url(r'^contact$', contact.contact),

    # 获取访问日志动作。
    url(r'^action/(?P<oper_type>\w+)', action.action),

    # 生成微信二维码 create_qr_code
    url(r'^qr_code_auth$', qr_code_auth.qr_code_auth),

    # 企业微信网页登录认证
    url(r'^work_weixin_auth/(?P<company_id>\d+)', user_weixin_auth.work_weixin_auth),

]
