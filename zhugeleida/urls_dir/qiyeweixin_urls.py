from django.conf.urls import url

from zhugeleida.views_dir.qiyeweixin import user, quanxian, action, tag_customer, user_weixin_auth, customer, tongxunlu, \
    qr_code_auth, follow_language, follow_info,tag_list,article, talkGroupManagement, speechDetailsManagement
from zhugeleida.views_dir.qiyeweixin import chat, contact,search,mingpian,tag_user,product

urlpatterns = [

    # 权限操作
    url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)$', quanxian.quanxian_oper),
    url(r'^quanxian$', quanxian.quanxian),


    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)$', user.user_oper),
    url(r'^user$', user.user),


    # 标签 和 标签客户的操作
    url(r'^tag_customer/(?P<oper_type>\w+)/(?P<o_id>\d+)$', tag_customer.tag_customer_oper),
    url(r'^tag_customer$', tag_customer.tag_customer),

    # 标签列表和标签列表的的操作
    url(r'^tag_list/(?P<oper_type>\w+)/(?P<o_id>\d+)$', tag_list.tag_list_oper),
    url(r'^tag_list$', tag_list.tag_list),

    # 标签 和 标签用户的操作
    url(r'^tag_user/(?P<oper_type>\w+)$', tag_user.tag_user_oper),
    url(r'^tag_user$', tag_user.tag_user),

    #搜索(客户\标签)
    url(r'^search/(?P<oper_type>\w+)$', search.search),


    # 修改客户详情和客户关联信息表
    url(r'^customer/(?P<oper_type>\w+)/(?P<o_id>\d+)$', customer.customer_oper),
    url(r'^customer$', customer.customer),

    # 客户通讯录
    url(r'^tongxunlu$', tongxunlu.tongxunlu),

    # 用户跟进常用语
    url(r'follow_language/(?P<oper_type>\w+)/(?P<o_id>\d+)$', follow_language.follow_language_oper),
    url(r'follow_language$', follow_language.follow_language),

    # 用户跟进信息
    url(r'follow_info/(?P<oper_type>\w+)/(?P<o_id>\d+)$', follow_info.follow_info_oper),
    url(r'follow_info$', follow_info.follow_info),

    # 实时聊天 一对多
    url(r'^chat/(?P<oper_type>\w+)/(?P<o_id>\d+)', chat.chat_oper),
    url(r'^chat$', chat.chat),

    # 获取聊天联系人列表
    url(r'^contact/(?P<oper_type>\w+)$', contact.contact_oper),
    url(r'^contact$', contact.contact),

    # 获取访问日志动作。
    url(r'^action/(?P<oper_type>\w+)$', action.action),

    # 生成微信二维码 create_qr_code
    url(r'^qr_code_auth$', qr_code_auth.create_qr_code),

    # 企业微信网页登录认证
    url(r'^work_weixin_auth/(?P<company_id>\d+)$', user_weixin_auth.work_weixin_auth),
    url(r'^work_weixin_auth/(?P<oper_type>\w+)$', user_weixin_auth.work_weixin_auth_oper),

    #企业微信JS-SDK使用权限签名算法
    url(r'^enterprise_weixin_sign$', user_weixin_auth.enterprise_weixin_sign),

    # 访问企业微信-我的用户名片
    url(r'^mingpian/(?P<oper_type>\w+)$', mingpian.mingpian_oper),
    url(r'^mingpian$', mingpian.mingpian),

    # 企业产品操作
    url(r'^product/(?P<oper_type>\w+)/(?P<o_id>\d+)$', product.product_oper),
    url(r'^product/(?P<oper_type>\w+)$', product.product),

    # 企业微信端-文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)$', article.article_oper),
    url(r'^article/(?P<oper_type>\w+)$', article.article),

    # 话术分组管理
    url(r'^talkGroupManage$', talkGroupManagement.talkGroupManage),
    # url(r'^talkGroupManageOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', talkGroupManagement.talkGroupManageOper),

    # 话术详情管理
    url(r'^speechDetailsManage$', speechDetailsManagement.speechDetailsManage),
    # url(r'^speechDetailsManageOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', speechDetailsManagement.speechDetailsManageOper),
]
