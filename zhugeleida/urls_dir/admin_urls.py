from django.conf.urls import url

from zhugeleida.views_dir.admin import  role,company,login,user,department,website,\
    home_page,product,article,article_tag, access_rules, admin_role,admin_userprofile,plugin_mingpian,plugin_report



urlpatterns = [
    url(r'^login$', login.login),

    url(r'^home_page$',home_page.home_page),
    url(r'^home_page/(?P<oper_type>\w+)', home_page.home_page_oper),

    # 后台用户操作
    url(r'^admin_userprofile/(?P<oper_type>\w+)/(?P<o_id>\d+)', admin_userprofile.admin_userprofile_oper),
    url(r'^admin_userprofile', admin_userprofile.admin_userprofile),

    # 后台-角色操作
    url(r'^admin_role/(?P<oper_type>\w+)/(?P<o_id>\d+)', admin_role.admin_role_oper),
    url(r'^admin_role', admin_role.admin_role),

    # 后台-权限管理
    url(r'^access_rules/(?P<oper_type>\w+)/(?P<o_id>\d+)', access_rules.access_rules_oper),
    url(r'^access_rules', access_rules.access_rules),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),

    # 公司操作
    url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    url(r'^company$', company.company),
    #验证雷达，通讯录
    url(r'^company/(?P<oper_type>\w+)', company.author_status),


    #部门操作
    url(r'^department/(?P<oper_type>\w+)/(?P<o_id>\d+)', department.department_oper),
    url(r'^department$', department.department),

    #官网编辑
    url(r'website/(?P<oper_type>\w+)/(?P<o_id>\d+)',website.website_oper),
    url(r'website$',website.website),

    #后台产品管理
    url(r'^product/(?P<oper_type>\w+)/(?P<o_id>\d+)', product.product_oper),
    url(r'^product/(?P<oper_type>\w+)/', product.product),

    #公众号-文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),
    url(r'^article/(?P<oper_type>\w+)/', article.article),

    #公众号-插件名片管理
    url(r'^plugin_mingpian/(?P<oper_type>\w+)/(?P<o_id>\d+)', plugin_mingpian.plugin_mingpian_oper),
    url(r'^plugin_mingpian$', plugin_mingpian.plugin_mingpian),

    # 公众号插件报名管理
    url(r'^plugin_report/(?P<oper_type>\w+)/(?P<o_id>\d+)', plugin_report.plugin_report_oper),
    url(r'^plugin_report$', plugin_report.plugin_report),

    # 公众号-商品管理
    url(r'^plugin_goods/(?P<oper_type>\w+)/(?P<o_id>\d+)', product.product_oper),
    url(r'^plugin_goods/(?P<oper_type>\w+)/', product.product),

    # 文章的标签管理
    url(r'^tag/(?P<oper_type>\w+)$', article_tag.article_tag_oper),
    url(r'^tag$', article_tag.article_tag),


]