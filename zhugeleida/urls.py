from django.conf.urls import url

from zhugeleida.views_dir import login, role, user,quanxian,company,tag,work_weixin_auth


urlpatterns = [
    url(r'^login$', login.login),

    # 权限操作
    url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)', quanxian.quanxian_oper),
    url(r'^quanxian', quanxian.quanxian),

    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # 公司操作
    url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    url(r'^company$', company.company),

    # 标签操作
    url(r'^tag/(?P<oper_type>\w+)/(?P<o_id>\d+)', tag.tag_oper),
    url(r'^tag$', tag.tag),

    #企业微信网页登录认证
    # url(r'^work_weixin_auth/(?P<oper_type>\w+)/(?P<o_id>\d+)', work_weixin_auth.work_weixin_auth_oper),
    url(r'^work_weixin_auth/(?P<company_id>\d+)', work_weixin_auth.work_weixin_auth),

]
