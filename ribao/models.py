from django.db import models

# Create your models here.


# 角色表
class Role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('UserProfile', verbose_name='操作人', null=True, blank=True,
    related_name='role_oper_user')

    class Meta:
        verbose_name_plural = "角色表"
        app_label = "ribao"

    def __str__(self):
        return "%s" % self.name


# 用户信息表
class UserProfile(models.Model):
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态", default=1)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    username = models.CharField(verbose_name="姓名", max_length=32)
    role = models.ForeignKey("Role", verbose_name="角色", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)
    oper_user = models.ForeignKey("self", verbose_name="操作人", related_name="u_user", null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    set_avator = models.CharField(verbose_name="头像图片地址", max_length=128, default='statics/imgs/setAvator.jpg')

    def __str__(self):
        return self.username

    class Meta:
        app_label = "ribao"
