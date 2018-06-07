from django.conf.urls import url

from zhugeleida.views_dir.admin import  role,company,login,user,department
from zhugeleida.views_dir import chat,contact,action


urlpatterns = [
    url(r'^login$', login.login),

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

]