from django.db import models


# Create your models here.

# 权限表
class QuanXian(models.Model):
	path = models.CharField(verbose_name="访问路径", max_length=64)
	icon = models.CharField(verbose_name="图标", max_length=64)
	title = models.CharField(verbose_name="功能名称", max_length=64)
	pid = models.ForeignKey('self', verbose_name="父级id", null=True, blank=True)
	order_num = models.SmallIntegerField(verbose_name="按照该字段的大小排序")
	create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
	oper_user = models.ForeignKey('UserProfile', verbose_name='操作人', null=True, blank=True,
		related_name='quanxian_oper_user')

	component = models.CharField(verbose_name="vue 文件路径", max_length=64, null=True, blank=True)

	class Meta:
		verbose_name_plural = "角色表"
		app_label = "wendaku"


# 角色表
class Role(models.Model):
	name = models.CharField(verbose_name="角色名称", max_length=32)
	create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
	oper_user = models.ForeignKey('UserProfile', verbose_name='操作人', null=True, blank=True,
		related_name='role_oper_user')

	class Meta:
		verbose_name_plural = "角色表"
		app_label = "wendaku"

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
		app_label = "wendaku"


# 科室表
class Keshi(models.Model):
	name = models.CharField(verbose_name="名称", max_length=64)
	pid = models.ForeignKey('self', null=True, blank=True, verbose_name="父级id")
	priority = models.SmallIntegerField(verbose_name="优先级", default=0)
	oper_user = models.ForeignKey("UserProfile", verbose_name="操作人", null=True, blank=True)
	create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

	class Meta:
		app_label = "wendaku"


# 词类表
class CiLei(models.Model):
	name = models.CharField(verbose_name="名称", max_length=64)
	oper_user = models.ForeignKey("UserProfile", verbose_name="操作人", null=True, blank=True)
	create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

	class Meta:
		app_label = "wendaku"


# 答案类型表
class DaAnLeiXing(models.Model):
	name = models.CharField(verbose_name="名称", max_length=64)
	oper_user = models.ForeignKey("UserProfile", verbose_name="操作人", null=True, blank=True)
	create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

	class Meta:
		app_label = "wendaku"


# 答案库表
class DaAnKu(models.Model):
	content = models.TextField(verbose_name="答案")
	create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
	# shenhe_date = models.DateField(verbose_name="审核时间", null=True, blank=True)
	update_date = models.DateField(verbose_name="修改时间", null=True, blank=True)
	oper_user = models.ForeignKey("UserProfile", verbose_name="审核人", null=True, blank=True)
	daochu_num = models.SmallIntegerField(verbose_name="导出次数", default=0)

	cilei = models.ForeignKey('CiLei', verbose_name="词类", null=True, blank=True)
	keshi = models.ForeignKey('Keshi', verbose_name="科室", null=True, blank=True)
	daan_leixing = models.ForeignKey('DaAnLeiXing', verbose_name="答案类型", null=True, blank=True)

	class Meta:
		app_label = "wendaku"


# 问题表
class GuanJianCi(models.Model):
	status_choices = (
		(1, "已使用"),
		(2, "未使用"),
	)
	content = models.TextField(verbose_name="关键词")
	status = models.SmallIntegerField(choices=status_choices, verbose_name="使用状态", default=2)
	oper_user = models.ForeignKey("UserProfile", verbose_name="操作人", null=True, blank=True)
	class Meta:
		app_label = "wendaku"