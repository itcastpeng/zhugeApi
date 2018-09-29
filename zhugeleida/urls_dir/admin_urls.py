from django.conf.urls import url

from zhugeleida.views_dir.admin import role, company, login, user, department, website, \
    home_page, product, article, article_tag, access_rules, admin_role, admin_userprofile, plugin_mingpian, \
    plugin_report, plugin_goods, open_weixin,dai_xcx,xcx_app, open_weixin_gongzhonghao, talkGroupManagement, \
    speechDetailsManagement, mallManagement, goodsClassification, shangchengjichushezhi

urlpatterns = [
    url(r'^login$', login.login),
    url(r'^login_rules$', login.login_rules),
    url(r'^modify_password$', login.modify_password),

    url(r'^home_page$', home_page.home_page),
    url(r'^home_page/(?P<oper_type>\w+)', home_page.home_page_oper),

    # 后台用户操作
    url(r'^admin_userprofile/(?P<oper_type>\w+)/(?P<o_id>\d+)', admin_userprofile.admin_userprofile_oper),
    url(r'^admin_userprofile', admin_userprofile.admin_userprofile),

    # 后台-角色操作
    url(r'^admin_role/(?P<oper_type>\w+)/(?P<o_id>\d+)', admin_role.admin_role_oper),
    url(r'^admin_role', admin_role.admin_role),

    # 后台-权限管理
    url(r'^access_rules/(?P<oper_type>\w+)/(?P<o_id>\d+)$', access_rules.access_rules_oper),
    url(r'^access_rules', access_rules.access_rules),

    # 微信小程序通知
    url(r'^open_weixin/(?P<oper_type>\w+)', open_weixin.open_weixin),

    # 微信公众号通知
    url(r'^open_weixin_gongzhonghao/(?P<oper_type>\w+)', open_weixin_gongzhonghao.open_weixin_gongzhonghao),

    # 小程序第三方进入认证
    url(r'^xcx_auth_process/update/(?P<oper_type>\w+)$', open_weixin.xcx_auth_process_oper),
    url(r'^xcx_auth_process$', open_weixin.xcx_auth_process),

    # 公众号第三方进入认证
    url(r'^gzh_auth_process/update/(?P<oper_type>\w+)$', open_weixin_gongzhonghao.gzh_auth_process_oper),
    url(r'^gzh_auth_process$', open_weixin_gongzhonghao.gzh_auth_process),

    # 小程序-批量上线
    url(r'^xcx_app$', xcx_app.xcx_app),

    # 代小程序发布
    url(r'^dai_xcx/(?P<oper_type>\w+)$', dai_xcx.dai_xcx_oper),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),

    # 公司操作 + 验证雷达AI APP秘钥添加。
    url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    url(r'^company$', company.company),

    # 验证雷达，通讯录
    url(r'^company/(?P<oper_type>\w+)', company.author_status),

    # 部门操作
    url(r'^department/(?P<oper_type>\w+)/(?P<o_id>\d+)', department.department_oper),
    url(r'^department$', department.department),

    # 官网编辑
    url(r'website/(?P<oper_type>\w+)/(?P<o_id>\d+)', website.website_oper),
    url(r'website$', website.website),

    # 官网模板管理
    url(r'website_template/(?P<oper_type>\w+)/(?P<o_id>\d+)', website.website_template_oper),
    url(r'website_template$', website.website_template),

    # 后台产品管理
    url(r'^product/(?P<oper_type>\w+)/(?P<o_id>\d+)', product.product_oper),
    url(r'^product/(?P<oper_type>\w+)/', product.product),

    # 公众号-文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),
    url(r'^article/(?P<oper_type>\w+)/', article.article),

    # 公众号-插件名片管理
    url(r'^plugin_mingpian/(?P<oper_type>\w+)/(?P<o_id>\d+)', plugin_mingpian.plugin_mingpian_oper),
    url(r'^plugin_mingpian$', plugin_mingpian.plugin_mingpian),

    # 公众号插件报名管理
    url(r'^plugin_report/(?P<oper_type>\w+)/(?P<o_id>\d+)', plugin_report.plugin_report_oper),
    url(r'^plugin_report$', plugin_report.plugin_report),

    # 公众号-商品管理
    url(r'^plugin_goods/(?P<oper_type>\w+)/(?P<o_id>\d+)', plugin_goods.plugin_goods_oper),
    url(r'^plugin_goods/(?P<oper_type>\w+)/', plugin_goods.plugin_goods),

    # 文章的标签管理
    url(r'^article_tag/(?P<oper_type>\w+)/(?P<o_id>\d+)$', article_tag.article_tag_oper),
    url(r'^article_tag$', article_tag.article_tag),

    # 话术分组管理
    url(r'^talkGroupManageShow', talkGroupManagement.talkGroupManageShow),
    url(r'^talkGroupManageOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', talkGroupManagement.talkGroupManageOper),

    # 话术详情管理
    url(r'^speechDetailsManageShow', speechDetailsManagement.speechDetailsManageShow),
    url(r'^speechDetailsManageOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', speechDetailsManagement.speechDetailsManageOper),

    # 小程序 - 商品分类管理
    url(r'goodsClassShow', goodsClassification.goodsClassShow),  # 商品分类管理查询
    url(r'^goodsClassOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', goodsClassification.goodsClassOper),  # 商品分类管理操作

    # 小程序 - 商品管理
    url(r'mallManagementShow', mallManagement.mallManagementShow),  # 商品管理查询
    url(r'^mallManagementOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', mallManagement.mallManagementOper),  # 商品管理操作

    # 小程序 - 商城基础设置
    url(r'^jiChuSheZhiOper/(?P<oper_type>\w+)$', shangchengjichushezhi.jiChuSheZhiOper),  # 商品基础设置

]
