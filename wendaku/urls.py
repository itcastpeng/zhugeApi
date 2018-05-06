from django.conf.urls import url

from wendaku.views_dir import login, role, user, keshi, cilei, daanleixing, daanku, quanxian

urlpatterns = [
    # url(r'^wenku/', include('wendaku.urls')),
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

    # 科室操作
    url(r'^keshi/(?P<oper_type>\w+)/(?P<o_id>\d+)', keshi.keshi_role_oper),
    url(r'^keshi', keshi.keshi),

    # 科室操作
    url(r'^cilei/(?P<oper_type>\w+)/(?P<o_id>\d+)', cilei.cilei_oper),
    url(r'^cilei', cilei.cilei),

    # 答案类型操作
    url(r'^daanleixing/(?P<oper_type>\w+)/(?P<o_id>\d+)', daanleixing.daanleixing_oper),
    url(r'^daanleixing', daanleixing.daanleixing),

    # 答案库操作
    url(r'^daanku/(?P<oper_type>\w+)/(?P<o_id>\d+)', daanku.daanku_oper),
    url(r'^daanku', daanku.daanku),
]
