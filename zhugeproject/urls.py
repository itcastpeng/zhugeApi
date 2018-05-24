
from django.conf.urls import url

# from zhugeproject.views_dirs import api ,index
from zhugeproject.views_dirs import login,user,role,system,gongneng,quanxian,xuqiu

urlpatterns = [


    # 登录
    url(r'^login', login.login,name='login'),


    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user_select),


    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role', role.role_select),


    # 项目操作
    url(r'^system/(?P<oper_type>\w+)/(?P<o_id>\d+)', system.system_oper),
    url(r'^system',system.system_select),


    # 功能操作
    url(r'^gongneng/(?P<oper_type>\w+)/(?P<o_id>\d+)', gongneng.gongneng_oper),
    url(r'^gongneng',gongneng.gongneng_select),


    # 权限操作
    url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)', quanxian.quanxian_oper),
    url(r'^quanxian',quanxian.quanxian_select),

    # 需求操作
    url(r'^xuqiu/(?P<oper_type>\w+)/(?P<o_id>\d+)', xuqiu.xuqiu_oper),
    url(r'^xuqiu', xuqiu.xuqiu_select),

]























