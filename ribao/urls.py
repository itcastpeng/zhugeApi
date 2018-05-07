from django.conf.urls import url

from ribao.views_dir import login, role, user,task

urlpatterns = [

    # 登录
    url(r'^login$', login.login),

    # 用户操作
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),


    # 角色操作
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role', role.role),


    # 任务管理操作
    url(r'^task/(?P<oper_type>\w+)/(?P<o_id>\d+)', task.task_oper),
    url(r'^task', task.task),

    # 项目管理操作
    # url(r'^project/(?P<oper_type>\w+)/(?P<o_id>\d+)', project.project_oper),
    # url(r'^project', project.project),

]
