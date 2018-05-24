from django.db import models


# 用户表
class ProjectUserProfile(models.Model):
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    username = models.CharField(verbose_name="姓名", max_length=32)
    role = models.ForeignKey("ProjectRole", verbose_name="角色", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = "zhugeproject"

# 权限表
class ProjectQuanXian(models.Model):
    quanxian_name = models.CharField(verbose_name='权限名称',max_length=64)
    path = models.CharField(verbose_name="权限URL", max_length=64)
    create_time = models.DateField(verbose_name='创建时间',null=True,blank=True)

    class Meta:
        app_label = "zhugeproject"

# 多对多 权限对角色
class ProjectRoleQuanxian(models.Model):
    quanxian = models.ForeignKey('ProjectQuanXian',verbose_name='权限',null=True,blank=True)
    role = models.ForeignKey('ProjectRole',verbose_name='角色',null=True,blank=True)

# 角色表
class ProjectRole(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


    class Meta:
        verbose_name_plural = "角色表"
        app_label = "zhugeproject"

    def __str__(self):
        return "%s" % self.name

# 多对多  用户对产品/项目
class Chanpin_User(models.Model):
    projectuserprofile = models.ForeignKey(to='ProjectUserProfile',verbose_name='用户')
    projectsystem = models.ForeignKey(to='ProjectSystem',verbose_name='产品/项目')

    choies_status = (
        (1,'正常'),
        (2,'非正常')
    )
    xiangmu_status = models.BooleanField(verbose_name='状态',choices=choies_status,default=1)

# 产品/项目表
class ProjectSystem(models.Model):
    name = models.CharField(verbose_name='产品/项目名',max_length=32)

    choices_status = (
        (1,'开发阶段'),
        (2,'修复阶段'),
        (3,'上线阶段'),
        (4,'迭代阶段')
    )
    finish_status = models.SmallIntegerField(verbose_name='项目状态',choices=choices_status,default=1)
    create_time = models.DateField(verbose_name='创建时间',auto_now_add=True)
    predict_time = models.DateField(verbose_name='预计结束时间', null=True, blank=True)
    over_time = models.DateField(verbose_name='结束时间', null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"

#  功能表
class ProjectFunction(models.Model):
    item_name =  models.ForeignKey('ProjectSystem',verbose_name='产品/项目名',max_length=32)
    create_time = models.DateField(verbose_name='创建时间',auto_now_add=True)
    name = models.CharField(verbose_name='功能名称',max_length=128,null=True, blank = True)

    class Meta:
        app_label = "zhugeproject"

# 工作日志表
class ProjectWork_Log(models.Model):
    name = models.ForeignKey('ProjectUserProfile',verbose_name='创建日志的人',null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    remark = models.TextField(verbose_name='日志备注',max_length=256,null=True, blank=True)
    is_system = models.ForeignKey('ProjectFunction',verbose_name='属于哪个功能',null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"

# 需求表(BUG)表
class ProjectNeed_Demand(models.Model):
    demand_user = models.ForeignKey('ProjectUserProfile',verbose_name='需求人')
    is_system = models.ForeignKey('ProjectFunction', verbose_name='属于哪个功能')
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)
    is_remark = models.TextField(verbose_name='需求简介', max_length=256, null=True, blank=True)


    class Meta:
        app_label = "zhugeproject"

# 需求log日志
class ProjectDemand_Log(models.Model):
    name = models.ForeignKey('ProjectUserProfile', verbose_name='创建日志的人', null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    is_system = models.ForeignKey('ProjectNeed_Demand', verbose_name='属于哪个需求', null=True, blank=True)
    is_remark = models.TextField(verbose_name='日志备注', max_length=256, null=True, blank=True)

    class Meta:
        app_label = "zhugeproject"









