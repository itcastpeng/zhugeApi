from django.db import models


# 用户表
class project_userprofile(models.Model):
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态", default=1)

    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    username = models.CharField(verbose_name="姓名", max_length=32)
    role = models.ForeignKey("project_role", verbose_name="角色", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    set_avator = models.CharField(verbose_name="头像图片地址", max_length=128, default='statics/imgs/setAvator.jpg')

    def __str__(self):
        return self.username

    class Meta:
        app_label = "zhugeproject"


# 权限表
class project_quanxian(models.Model):
    path = models.CharField(verbose_name="访问路径", max_length=64)
    icon = models.CharField(verbose_name="图标", max_length=64)
    title = models.CharField(verbose_name="功能名称", max_length=64)
    pid = models.ForeignKey('self', verbose_name="父级id", null=True, blank=True)
    order_num = models.SmallIntegerField(verbose_name="按照该字段的大小排序")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    component = models.CharField(verbose_name="vue 文件路径", max_length=64, null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"


# 多对多 权限对角色
class project_role_to_quanxian(models.Model):
    quanxian = models.ForeignKey(to='project_quanxian', verbose_name='权限')
    role = models.ForeignKey(to='project_role', verbose_name='角色')

    class Meta:
        app_label = "zhugeproject"


# 角色表
class project_role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        app_label = "zhugeproject"

    def __str__(self):
        return "%s" % self.name


# 产品/项目表
class project_xiangmu(models.Model):
    name = models.CharField(verbose_name='产品/项目名', max_length=32)

    choices_status = (
        (1, '开发阶段'),
        (2, '维护阶段'),
    )
    finish_status = models.SmallIntegerField(verbose_name='项目状态', choices=choices_status, default=1)
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)
    predict_time = models.DateField(verbose_name='预计结束时间', null=True, blank=True)
    over_time = models.DateField(verbose_name='结束时间', null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"


# 多对多  用户对产品/项目
class project_chanpin_to_user(models.Model):
    user = models.ForeignKey(to='project_userprofile', verbose_name='用户')
    xiangmu = models.ForeignKey(to='project_xiangmu', verbose_name='产品/项目')

    choies_status = (
        (1, '正常'),
        (2, '异常')
    )
    xiangmu_status = models.BooleanField(verbose_name='状态', choices=choies_status, default=1)

    class Meta:
        app_label = "zhugeproject"


#  功能表
class project_goneneng(models.Model):
    item_name = models.ForeignKey('project_xiangmu', verbose_name='产品/项目名', max_length=32)
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)
    name = models.CharField(verbose_name='功能名称', max_length=128, null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"


# 操作日志表
class project_caozuo_log(models.Model):
    oper_type_choices = (
        (1, "增加"),
        (2, "删除"),
        (3, "修改"),
        (4, "查询"),
    )
    oper_type = models.SmallIntegerField(verbose_name="操作类型", choices=oper_type_choices)
    user = models.ForeignKey('project_userprofile', verbose_name='创建人', null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    remark = models.TextField(verbose_name='日志备注', max_length=256, null=True, blank=True)
    quanxian = models.ForeignKey('project_quanxian', verbose_name='属于哪个权限', null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"


# 需求表(BUG)表
class project_xuqiu(models.Model):
    demand_user = models.ForeignKey('project_userprofile', verbose_name='需求人')
    is_system = models.ForeignKey('project_goneneng', verbose_name='属于哪个功能')
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)
    is_remark = models.TextField(verbose_name='需求简介', max_length=256, null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"


# 需求日志表
class project_xuqiu_log(models.Model):
    name = models.ForeignKey('project_userprofile', verbose_name='创建日志的人', null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    is_system = models.ForeignKey('project_xuqiu', verbose_name='属于哪个需求', null=True, blank=True)
    is_remark = models.TextField(verbose_name='日志备注', max_length=256, null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"
