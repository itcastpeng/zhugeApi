from django.db import models

# Create your models here.

# 角色表
class RibaoRole(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('RibaoUserProfile', verbose_name='操作人', null=True, blank=True,
    related_name='role_oper_user')

    class Meta:
        verbose_name_plural = "角色表"
        app_label = "ribao"

    def __str__(self):
        return "%s" % self.name


# 用户信息表
class RibaoUserProfile(models.Model):
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态", default=1)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    username = models.CharField(verbose_name="姓名", max_length=32)
    role = models.ForeignKey("RibaoRole", verbose_name="角色", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)
    oper_user = models.ForeignKey("self", verbose_name="操作人", related_name="u_user", null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    set_avator = models.CharField(verbose_name="头像图片地址", max_length=128, default='statics/imgs/setAvator.jpg')
    def __str__(self):
        return self.username
    class Meta:
        app_label = "ribao"


# 项目管理表
class RibaoProjectManage(models.Model):
    project_name = models.CharField(verbose_name='项目名称',max_length=32)
    person_people = models.ForeignKey('RibaoUserProfile',verbose_name='开发负责人',max_length=64)
    def __str__(self):
        return self.project_name

    class Meta:
        app_label = 'ribao'


# 任务管理表
class RibaoTaskManage(models.Model):
    task_name = models.CharField(verbose_name='任务名称',max_length=64)
    detail = models.CharField(verbose_name="任务详情", max_length=128, null=True, blank=True)
    belog_task = models.ForeignKey('RibaoProjectManage',verbose_name="归属名称", max_length=32)
    director = models.ForeignKey('RibaoProjectManage', verbose_name="开发负责人",max_length=32,related_name='person')
    issuer = models.CharField( verbose_name="发布人",max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    estimated_time = models.DateTimeField(verbose_name="预计完成时间", null=True, blank=True)
    boor_urgent = models.BooleanField(verbose_name="是否加急",default=False)

    def __str__(self):
        return self.task_name

    class Meta:
        app_label = 'ribao'

    # 任务日志管理表
class RibaoTaskLog(models.Model):
    status = {
        (1,'一'),
        (2,'二'),
        (3,'三'),

    }

    belog_log = models.ForeignKey('RibaoTaskManage',verbose_name='本日志属于哪个任务',max_length=265)
    log_status = models.CharField(verbose_name='当前项目状态',max_length=64,choices=status,default=1)
    oper_user = models.ForeignKey("RibaoUserProfile", verbose_name="操作人", related_name="x_user", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建日志时间", auto_now_add=True)

    def __str__(self):
        return self.belog_log

    class Meta:
        app_label = 'ribao'













