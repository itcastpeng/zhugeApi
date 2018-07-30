from django.conf.urls import url

from zhugeleida.views_dir.admin import  role,company,login,user,department,website,\
    home_page,product,article,article_tag, access_rules, admin_role,admin_userprofile



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

    #部门操作
    url(r'^department/(?P<oper_type>\w+)/(?P<o_id>\d+)', department.department_oper),
    url(r'^department$', department.department),

    #官网编辑
    url(r'edit_website$',website.website),

    #后台产品管理
    url(r'^product/(?P<oper_type>\w+)/(?P<o_id>\d+)', product.product_oper),
    url(r'^product/(?P<oper_type>\w+)/', product.product),

    url(r'^article/(?P<oper_type>\w+)/', article.article),

    # 文章的标签管理
    url(r'^tag/(?P<oper_type>\w+)$', article_tag.article_tag_oper),
    url(r'^tag$', article_tag.article_tag),


]