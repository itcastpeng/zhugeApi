from django.db import models


#公司管理
class zgld_company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    class Meta:
        verbose_name_plural = "公司表"
        app_label = "zhugeleida"


#用户管理
class zgld_userprofile(models.Model):

    userid = models.CharField(max_length=64, verbose_name='成员UserID')
    name = models.CharField(verbose_name="成员姓名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.IntegerField(choices=gender_choices, default=1)
    company = models.ForeignKey('zgld_company',verbose_name='所属企业')
    role = models.ForeignKey("zgld_role", verbose_name="角色")
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    avatar = models.CharField(verbose_name="头像url", max_length=128, default='statics/imgs/Avator.jpg')
    qr_code = models.CharField(verbose_name='员工个人二维码',max_length=128)
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="成员状态", default=2)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("userid", "company"),)
        verbose_name_plural = "用户表"
        app_label = "zhugeleida"


#角色管理
class zgld_role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


    class Meta:
        verbose_name_plural = "角色表"
        app_label = "zhugeleida"

    def __str__(self):
        return "%s - %s" % (self.id,self.name)

#权限管理
class zgld_quanxian(models.Model):
    path = models.CharField(verbose_name="访问路径", max_length=64)
    icon = models.CharField(verbose_name="图标", max_length=64)
    title = models.CharField(verbose_name="功能名称", max_length=64)
    pid = models.ForeignKey('self', verbose_name="父级id", null=True, blank=True)
    order_num = models.SmallIntegerField(verbose_name="按照该字段的大小排序")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('zgld_userprofile', verbose_name='操作人', null=True, blank=True,
    related_name='quanxian_oper_user')

    component = models.CharField(verbose_name="vue 文件路径", max_length=64, null=True, blank=True)

    class Meta:
        verbose_name_plural = "权限表"
        app_label = "zhugeleida"


#标签管理
class zgld_tag(models.Model):
    name = models.CharField(verbose_name='标签名称',max_length=64)
    tag_user = models.ManyToManyField('zgld_userprofile',verbose_name='关联的用户')

    def __str__(self):
        return 'tag: %s '  % (self.name)
    class Meta:
        app_label = "zhugeleida"


#客户管理
class zgld_customer(models.Model):
    username = models.CharField(verbose_name='客户姓名',max_length=64)
    openid = models.CharField(verbose_name='微信openid',max_length=64)
    set_avator = models.CharField(verbose_name="头像图片地址", max_length=128, default='statics/imgs/setAvator.jpg')
    expected_time = models.DateField(verbose_name='预计成交时间', max_length=64, blank=True, null=True, help_text="格式yyyy-mm-dd")
    pr_choice = ( (1,u'100%'),
                  (2,u'80%'),
                  (3,u'60%'),
                  (4,u'40%'),
                  (5,u'20%'),
                  (6,u'0%'),
                 )
    expedted_pr =  models.IntegerField(verbose_name='概率',choices=pr_choice,help_text="预计成交概率")
    superior = models.ForeignKey('self',null=True,blank=True,verbose_name='上级人')
    belonger = models.ForeignKey('zgld_userprofile',verbose_name='归属人',null=True,blank=True)
    information = models.ForeignKey('zgld_information',verbose_name='资料详情表')

    def __str__(self):
        return 'Custer: %s '  % (self.username)
    class Meta:
        verbose_name_plural = "客户表"
        app_label = "zhugeleida"


class zgld_photo(models.Model):
    photo_url = models.CharField(verbose_name="客户信息照片地址",max_length=128)
    information = models.ForeignKey('zgld_information', verbose_name='客户详情')
    class Meta:
        app_label = "zhugeleida"

class zgld_information(models.Model):
    source_type = (('small program','小程序'),
                   ('public number','公众号'),
                  )

    source = models.CharField(u'客户来源',max_length=64,choices=source_type)
    # photo = models.ManyToManyField('zgld_photo',verbose_name='照片详情',blank=True)
    memo_name = models.CharField(max_length=64,verbose_name='备注名')
    phone= models.CharField(verbose_name='手机号',max_length=20,blank=True,null=True)
    email= models.EmailField(u'常用邮箱',blank=True,null=True)
    company = models.CharField(u'在职公司',max_length=256,blank=True,null=True)
    position = models.CharField(u'职位',max_length=256,blank=True,null=True)
    address = models.TextField(verbose_name='住址')
    birthday = models.DateField(u'出生日期',max_length=64,blank=True,null=True,help_text='格式yyyy-mm-dd')
    mem = models.TextField(u'备注',help_text='客户个人信息备注等')

    class Meta:
        app_label = "zhugeleida"

class zgld_accesslog(models.Model):
    """Store Schedule run logs """
    customer = models.ForeignKey('zgld_customer')
    # status_choices = ((0,'查看'),(1,'购买'),(2,'预定'),(3,'考虑中'))
    # status = models.SmallIntegerField(choices=status_choices,max_length=8,verbose_name='客户状态')
    create_date = models.DateTimeField(auto_now_add=True)
    mem = models.TextField(u'备注',help_text='客户个人信息备注等')
    class Meta:
        app_label = "zhugeleida"

