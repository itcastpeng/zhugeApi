from django.db import models

# Create your models here.


# 权限表
class zhugedanao_quanxian(models.Model):
    path = models.CharField(verbose_name="访问路径", max_length=64)
    icon = models.CharField(verbose_name="图标", max_length=64)
    title = models.CharField(verbose_name="功能名称", max_length=64)
    pid = models.ForeignKey('self', verbose_name="父级id", null=True, blank=True)
    order_num = models.SmallIntegerField(verbose_name="按照该字段的大小排序")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    component = models.CharField(verbose_name="vue 文件路径", max_length=64, null=True, blank=True)

    class Meta:
        verbose_name_plural = "角色表"
        app_label = "zhugedanao"


# 角色表
class zhugedanao_role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    quanxian = models.ManyToManyField('zhugedanao_quanxian', verbose_name="对应权限")

    class Meta:
        verbose_name_plural = "角色表"
        app_label = "zhugedanao"

    def __str__(self):
        return "%s" % self.name


# 用户级别表
class zhugedanao_level(models.Model):
    name = models.CharField(verbose_name="级别名称", max_length=128)


# 用户信息表
class zhugedanao_userprofile(models.Model):
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态", default=1)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    username = models.CharField(verbose_name="姓名", max_length=32, null=True, blank=True)

    level_name = models.ForeignKey('zhugedanao_level', verbose_name="用户级别", default=1)
    role = models.ForeignKey("zhugedanao_role", verbose_name="角色", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    set_avator = models.CharField(verbose_name="头像图片地址", max_length=256, default='statics/imgs/setAvator.jpg')
    openid = models.CharField(verbose_name="微信公众号id", max_length=32)
    timestamp = models.CharField(verbose_name="时间戳", max_length=32, null=True, blank=True)

    sex_choices = (
        (1, '男'),
        (2, '女'),
    )
    sex = models.SmallIntegerField(choices=sex_choices, verbose_name="性别", null=True, blank=True)
    country = models.CharField(verbose_name="国家", max_length=32, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=32, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=32, null=True, blank=True)
    subscribe_time = models.CharField(verbose_name="最后关注时间", max_length=32, null=True, blank=True)



    def __str__(self):
        return self.username

    class Meta:
        app_label = "zhugedanao"


# 功能表
class zhugedanao_gongneng(models.Model):
    name = models.CharField(verbose_name="功能名称", max_length=128)
    pid = models.ForeignKey('self', verbose_name="功能父ID，为空表示主功能", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        app_label = "zhugedanao"


# 功能访问日志表
class zhugedanao_oper_log(models.Model):

    user = models.ForeignKey('zhugedanao_userprofile', verbose_name="用户")
    gongneng = models.ForeignKey('zhugedanao_gongneng', verbose_name='使用功能')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        app_label = "zhugedanao"


# 百度知道链接提交
class zhugedanao_lianjie_tijiao(models.Model):
    user = models.ForeignKey('zhugedanao_userprofile', verbose_name="用户")
    name = models.CharField(verbose_name="任务名称", max_length=128)
    url = models.TextField(verbose_name="提交链接")
    count = models.SmallIntegerField(verbose_name="提交次数", default=0)
    status_choices = (
        (1, "等待查询"),
        (2, "未收录"),
        (3, "已收录"),
    )
    status = models.SmallIntegerField(verbose_name="收录状态", choices=status_choices, default=1)
    get_task_date = models.DateTimeField(verbose_name='获取任务时间', null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


# 百度知道链接提交日志
class zhugedanao_lianjie_tijiao_log(models.Model):
    zhugedanao_lianjie_tijiao = models.ForeignKey('zhugedanao_lianjie_tijiao', verbose_name="提交的链接信息")
    ip = models.CharField(verbose_name="提交的ip", max_length=128)
    address = models.CharField(verbose_name="提交机器的ip", max_length=128)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
