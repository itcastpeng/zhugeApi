from django.conf.urls import url

from ribao.views_dir import login, role, user,renwuguanli,xiangmuguanli,renwurizhi

urlpatterns = [

    # 登录
    url(r'^login$', login.login),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user$', user.user),


    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),


    # 项目管理操作
    url(r'^xiangmuguanli/(?P<oper_type>\w+)/(?P<o_id>\d+)', xiangmuguanli.xiangmuguanli_oper),
    url(r'^xiangmuguanli$', xiangmuguanli.xiangmuguanli),

    # 任务管理操作
    url(r'^renwuguanli/(?P<oper_type>\w+)/(?P<o_id>\d+)', renwuguanli.renwuguanli_oper),
    url(r'^renwuguanli$', renwuguanli.renwuguanli),

    # 任务日志操作
    url(r'^renwurizhi/(?P<oper_type>\w+)/(?P<o_id>\d+)', renwurizhi.renwurizhi_oper),
    url(r'^renwurizhi$', renwurizhi.renwurizhi),
]
