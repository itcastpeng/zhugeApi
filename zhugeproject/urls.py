
from django.conf.urls import url

# from zhugeproject.views_dirs import api ,index
from zhugeproject.views_dirs import login,index,user_profile

urlpatterns = [

    # 登录
    url(r'^login', login.login,name='login'),
    url(r'^index',index.index,name='index'),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user_profile.user_operate),
    url(r'^user', user_profile.user_profile),

    # # 权限操作
    # url(r'^quanxian/(?P<oper_type>\w+)/(?P<o_id>\d+)', quanxian.quanxian_oper),
    # url(r'^quanxian', quanxian.quanxian),

    # # 角色操作
    # url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    # url(r'^role$', role.role),


]























