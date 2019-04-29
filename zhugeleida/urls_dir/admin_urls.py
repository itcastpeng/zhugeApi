from django.conf.urls import url

from zhugeleida.views_dir.admin import role, company, login, user, department, website, \
    home_page, product, help_doc, article, article_tag, access_rules, admin_role, admin_userprofile, plugin_mingpian, \
    plugin_report, plugin_goods, open_weixin, dai_xcx, xcx_app, open_weixin_gongzhonghao, talkGroupManagement, \
    speechDetailsManagement, mallManagement, goodsClassification, shangchengjichushezhi, open_qiyeweixin, \
    theOrderManagement, tuiKuanDingDan, employeesOrders, activity_manage, tongxunlu, money_manage, case_tag, \
    case_manage, diary_manage, comment_manage, data_statistics, editor, editor_article, editor_case, editor_diary

urlpatterns = [

    # 登录
    url(r'^login$', login.login),

    # 获取当前角色拥有的权限
    url(r'^login_rules$', login.login_rules),

    # 修改密码
    url(r'^modify_password$', login.modify_password),

    # 后台 - 首页功能 数据统计 名片状态+账号状态
    url(r'^home_page/(?P<oper_type>\w+)$', home_page.home_page_oper),
    url(r'^home_page$', home_page.home_page),

    # 后台-用户管理
    url(r'^admin_userprofile/(?P<oper_type>\w+)/(?P<o_id>\d+)$', admin_userprofile.admin_userprofile_oper),
    url(r'^admin_userprofile$', admin_userprofile.admin_userprofile),

    # 后台-角色操作
    url(r'^admin_role/(?P<oper_type>\w+)/(?P<o_id>\d+)$', admin_role.admin_role_oper),
    url(r'^admin_role$', admin_role.admin_role),
    # url(r'^admin_role_init$', admin_role.admin_role_init),

    # 后台-权限管理
    url(r'^access_rules/(?P<oper_type>\w+)/(?P<o_id>\d+)$', access_rules.access_rules_oper),
    url(r'^access_rules$', access_rules.access_rules),

    # 微信小程序通知
    url(r'^open_weixin/(?P<oper_type>\w+)$', open_weixin.open_weixin),

    # 企业微信服务商认证接入
    url(r'^open_qiyeweixin/(?P<oper_type>\w+)$', open_qiyeweixin.open_qiyeweixin),

    # 微信公众号通知+消息与事件接收
    url(r'^open_weixin_gongzhonghao/(?P<oper_type>\w+)/(?P<app_id>\w+)$',open_weixin_gongzhonghao.open_weixin_gongzhonghao_oper),
    url(r'^open_weixin_gongzhonghao/(?P<oper_type>\w+)$', open_weixin_gongzhonghao.open_weixin_gongzhonghao),

    # 小程序第三方进入认证 - 小程序授权
    url(r'^xcx_auth_process/update/(?P<oper_type>\w+)$', open_weixin.xcx_auth_process_oper),
    url(r'^xcx_auth_process$', open_weixin.xcx_auth_process),

    # 公众号第三方进入认证 - 公众号授权
    url(r'^gzh_auth_process/update/(?P<oper_type>\w+)$', open_weixin_gongzhonghao.gzh_auth_process_oper),
    url(r'^gzh_auth_process$', open_weixin_gongzhonghao.gzh_auth_process),

    # 小程序-批量上线
    url(r'^xcx_app$', xcx_app.xcx_app),

    # 代小程序发布
    url(r'^dai_xcx/(?P<oper_type>\w+)$', dai_xcx.dai_xcx_oper),

    # 客户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)$', user.user_oper),
    url(r'^user$', user.user),
    url(r'^get_audit_user$', user.get_audit_user),  # 获取审核用户列表

    # 所有客户的通讯录
    url(r'^tongxunlu/(?P<oper_type>\w+)$', tongxunlu.tongxunlu_oper),
    url(r'^tongxunlu$', tongxunlu.tongxunlu),

    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)$', role.role_oper),
    url(r'^role$', role.role),

    # 公司操作 + 验证雷达AI APP秘钥添加。
    url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)$', company.company_oper),
    url(r'^company$', company.company),

    # 验证雷达，通讯录
    url(r'^company/(?P<oper_type>\w+)$', company.author_status),

    # 部门操作
    url(r'^department/(?P<oper_type>\w+)/(?P<o_id>\d+)$', department.department_oper),
    url(r'^department$', department.department),

    # 官网编辑
    url(r'website/(?P<oper_type>\w+)/(?P<o_id>\d+)$', website.website_oper),
    url(r'website$', website.website),

    # 官网模板管理
    url(r'website_template/(?P<oper_type>\w+)/(?P<o_id>\d+)$', website.website_template_oper),
    url(r'website_template$', website.website_template),

    # 后台产品管理
    url(r'^product/(?P<oper_type>\w+)/(?P<o_id>\d+)$', product.product_oper),
    url(r'^product/(?P<oper_type>\w+)$', product.product),

    # 公众号-文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)$', article.article_oper),
    url(r'^article/(?P<oper_type>\w+)$', article.article),

    # 公众号-帮助文档管理
    url(r'^help_doc/(?P<oper_type>\w+)/(?P<o_id>\d+)$', help_doc.help_doc_oper),
    url(r'^help_doc$', help_doc.help_doc),

    # 公众号-插件名片管理
    url(r'^plugin_mingpian/(?P<oper_type>\w+)/(?P<o_id>\d+)$', plugin_mingpian.plugin_mingpian_oper),
    url(r'^plugin_mingpian$', plugin_mingpian.plugin_mingpian),

    # 公众号-插件报名管理
    url(r'^plugin_report/(?P<oper_type>\w+)/(?P<o_id>\d+)$', plugin_report.plugin_report_oper),
    url(r'^plugin_report/(?P<oper_type>\w+)$', plugin_report.plugin_report),

    # 公众号-商品管理
    url(r'^plugin_goods/(?P<oper_type>\w+)/(?P<o_id>\d+)$', plugin_goods.plugin_goods_oper),
    url(r'^plugin_goods/(?P<oper_type>\w+)$', plugin_goods.plugin_goods),

    # 文章的标签管理
    url(r'^article_tag/(?P<oper_type>\w+)/(?P<o_id>\d+)$', article_tag.article_tag_oper),
    url(r'^article_tag$', article_tag.article_tag),

    # 案例-标签管理
    url(r'^case_tag/(?P<oper_type>\w+)/(?P<o_id>\d+)$', case_tag.case_tag_oper),
    url(r'^case_tag$', case_tag.case_tag),

    # 案例管理
    url(r'^case_manage/(?P<oper_type>\w+)/(?P<o_id>\d+)$', case_manage.case_manage_oper),
    url(r'^case_manage/(?P<oper_type>\w+)$', case_manage.case_manage),

    # 日记管理
    url(r'^diary_manage/(?P<oper_type>\w+)/(?P<o_id>\d+)$', diary_manage.diary_manage_oper),
    url(r'^diary_manage/(?P<oper_type>\w+)$', diary_manage.diary_manage),

    # 评论管理
    url(r'^comment_manage/(?P<oper_type>\w+)$', comment_manage.comment_manage),

    # 话术分组管理
    url(r'^talkGroupManage/(?P<oper_type>\w+)/(?P<o_id>\d+)$', talkGroupManagement.talkGroupManageOper),
    url(r'^talkGroupManage$', talkGroupManagement.talkGroupManage),

    # 话术详情管理
    url(r'^speechDetailsManage/(?P<oper_type>\w+)/(?P<o_id>\d+)$', speechDetailsManagement.speechDetailsManageOper),
    url(r'^speechDetailsManage$', speechDetailsManagement.speechDetailsManage),

    # 商城基础设置
    url(r'^jiChuSheZhi/(?P<oper_type>\w+)$', shangchengjichushezhi.jiChuSheZhiOper),  # 商城基础操作
    url(r'^jiChuSheZhi$', shangchengjichushezhi.jiChuSheZhi),  # 商城基础查询
    # url(r'^addSmallProgram$', shangchengjichushezhi.addSmallProgram),                       # 添加小程序ID

    # 商品分类管理
    url(r'^goodsClass/(?P<oper_type>\w+)/(?P<o_id>\d+)$', goodsClassification.goodsClassOper),  # 商品分类管理操作
    url(r'^goodsClass$', goodsClassification.goodsClass),  # 商品分类管理查询

    # 商品管理
    url(r'^mallManagement/(?P<oper_type>\w+)/(?P<o_id>\d+)$', mallManagement.mallManagementOper),  # 商品管理操作
    url(r'^mallManagement$', mallManagement.mallManagement),  # 商品管理查询

    # 订单管理
    url(r'^theOrder/(?P<oper_type>\w+)/(?P<o_id>\d+)$', theOrderManagement.theOrderOper),  # 订单管理操作
    url(r'^theOrder$', theOrderManagement.theOrder),  # 订单管理查询

    # 退款单管理
    url(r'^tuiKuanDingDan/(?P<oper_type>\w+)/(?P<o_id>\d+)$', tuiKuanDingDan.tuiKuanDingDanOper),  # 退款订单管理操作
    url(r'^tuiKuanDingDan$', tuiKuanDingDan.tuiKuanDingDan),  # 退款订单管理查询

    # 员工订单管理
    url(r'^employeesOrders$', employeesOrders.employeesOrders),  # 订单管理查询
    # url(r'^theOrderOper/(?P<oper_type>\w+)/(?P<o_id>\d+)$', theOrderManagement.theOrderOper),           # 订单管理操作


    # 活动管理
    url(r'^activity_manage/(?P<oper_type>\w+)/(?P<o_id>\d+)$', activity_manage.activity_manage_oper),  # 关注领红包
    url(r'^activity_manage/(?P<oper_type>\w+)$', activity_manage.activity_manage),  # 关注领红包

    # 资金管理
    url(r'^money_manage/(?P<oper_type>\w+)$', money_manage.money_manage),

    # 微信支付回调地址[暂时搁置待删除]
    url(r'^wx_pay/(?P<oper_type>\w+)$', money_manage.wx_pay_option),

    # 数据统计
    url(r'^data_statistics/(?P<oper_type>\w+)$', data_statistics.data_statistics),
    url(r'^update_qiniu$', data_statistics.update_qiniu), # 临时 案例图片上传到七牛云


    # 管理员审核 员工提交的 文章/案例
    url(r'^editor/(?P<oper_type>\w+)/(?P<o_id>\d+)$', editor.editor_oper),
    url(r'^editor$', editor.editor),

    url(r'^editor_login$', editor.editor_login),                                                        # 员工登录

    url(r'^editor_article/(?P<oper_type>\w+)/(?P<o_id>\d+)$', editor_article.editor_article_oper),      # 员工操作文章
    url(r'^editor_article$', editor_article.editor_article),                                            # 员工查询文章

    url(r'^editor_case/(?P<oper_type>\w+)/(?P<o_id>\d+)$', editor_case.editor_case_oper),               # 员工操作案例
    url(r'^editor_case$', editor_case.editor_case),                                                     # 员工查询案例

    url(r'^editor_diary/(?P<oper_type>\w+)/(?P<o_id>\d+)$', editor_diary.editor_diary_oper),            # 员工操作日记
    url(r'^editor_diary$', editor_diary.editor_diary),                                                  # 员工查询日记

]
