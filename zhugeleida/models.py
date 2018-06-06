from django.db import models


# 公司管理
class zgld_company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "公司表"
        app_label = "zhugeleida"


# 用户管理
class zgld_userprofile(models.Model):
    userid = models.CharField(max_length=64, verbose_name='成员UserID')
    username = models.CharField(verbose_name="成员姓名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(choices=gender_choices, default=1)
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    role = models.ForeignKey("zgld_role", verbose_name="角色")
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    avatar = models.CharField(verbose_name="头像url", max_length=128, default='statics/imgs/Avator.jpg')
    qr_code = models.CharField(verbose_name='员工个人二维码', max_length=128)
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    popularity = models.IntegerField(verbose_name='人气(被查看)',default=0)
    praise = models.IntegerField(verbose_name='被赞',default=0)
    forward = models.IntegerField(verbose_name='转发',default=0)

    status = models.SmallIntegerField(choices=status_choices, verbose_name="成员状态", default=2)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)


    def __str__(self):
        return self.username

    class Meta:
        unique_together = (("userid", "company"),)
        verbose_name_plural = "用户表"
        app_label = "zhugeleida"


# 角色管理
class zgld_role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "角色表"
        app_label = "zhugeleida"

    def __str__(self):
        return "%s - %s" % (self.id, self.name)


# 权限管理
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


# 标签管理
class zgld_tag(models.Model):
    name = models.CharField(verbose_name='标签名称', max_length=64)
    tag_customer = models.ManyToManyField('zgld_customer',verbose_name='关联到客户',blank=True,null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return 'tag: %s ' % (self.name)

    class Meta:
        app_label = "zhugeleida"


# 客户管理
class zgld_customer(models.Model):
    username = models.CharField(verbose_name='客户姓名', max_length=64,null=True)
    user_type_choices = (
        (1, '微信公众号'),
        (2, '微信小程序'),

    )
    user_type = models.SmallIntegerField(u'客户访问类型', choices=user_type_choices)
    openid = models.CharField(verbose_name='OpenID(用户唯一标识)', max_length=64)
    headimgurl = models.CharField(verbose_name="用户头像url", max_length=128,null=True)
    expected_time = models.DateField(verbose_name='预计成交时间', max_length=64, blank=True, null=True,
                                     help_text="格式yyyy-mm-dd")
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    source_type_choices = (
        (1, '扫码'),
        (2, '转发'),

    )
    source = models.SmallIntegerField(u'客户来源', choices=source_type_choices) #1

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.IntegerField(choices=sex_choices, default=1,blank=True,null=True)
    memo_name = models.CharField(max_length=64,verbose_name='备注名',blank=True,null=True)
    status_choice =  (
        (1, '未跟进过'),
        (2, '跟进中'),
        (3, '今日新增'),
    )
    status = models.SmallIntegerField(verbose_name='客户状态',choices=status_choice,null=True,blank=True)

    nickname = models.CharField(max_length=64, verbose_name='昵称',blank=True,null=True)

    country = models.CharField(max_length=64,verbose_name='国家',blank=True,null=True)
    city =  models.CharField(max_length=32,verbose_name='客户所在城市',blank=True,null=True)
    province = models.CharField(max_length=32,verbose_name='所在省份',blank=True,null=True)
    language = models.CharField(max_length=32,verbose_name='语言',blank=True,null=True)
    expedted_pr = models.CharField(verbose_name='预计成交概率',max_length=64,blank=True,null=True)
    superior = models.ForeignKey('self', verbose_name='上级人',null=True,blank=True)
    belonger = models.ForeignKey('zgld_userprofile', verbose_name='归属人',null=True)
    subscribe_time = models.DateTimeField(verbose_name='用户关注时间',blank=True,null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # 微信聊天室
    # userprofile = models.ManyToManyField('zgld_userprofile', verbose_name='用户可对话的客户')

    def __str__(self):
        return 'Custer: %s ' % (self.username)

    class Meta:
        verbose_name_plural = "客户表"
        app_label = "zhugeleida"

class zgld_information(models.Model):
    '''资料详情表'''
    customer = models.ForeignKey('zgld_customer', verbose_name='客户表',null=True)
    phone = models.CharField(verbose_name='手机号', max_length=20, blank=True, null=True)
    email = models.EmailField(u'常用邮箱', blank=True, null=True)
    company = models.CharField(u'在职公司', max_length=256, blank=True, null=True)
    position = models.CharField(u'职位', max_length=256, blank=True, null=True)
    address = models.TextField(verbose_name='详细地址')
    birthday = models.DateField(u'出生日期', max_length=64, blank=True, null=True, help_text='格式yyyy-mm-dd')
    mem = models.TextField(u'备注', help_text='客户个人信息备注等')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        app_label = "zhugeleida"



class zgld_photo(models.Model):
    photo_url = models.CharField(verbose_name="客户信息照片地址", max_length=128)
    photo = models.FileField(upload_to='photo',verbose_name='客户上传照片地址')
    information = models.ForeignKey('zgld_information', verbose_name='客户详情')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        app_label = "zhugeleida"


class zgld_accesslog(models.Model):
    """Store Schedule run logs """
    sharing_user = models.ForeignKey('zgld_userprofile',verbose_name='分享的用户')
    customer = models.ForeignKey('zgld_customer',verbose_name='访问的客户')
    accsess_url = models.CharField(max_length=128,verbose_name="访问的url")

    create_date = models.DateTimeField(auto_now_add=True)
    mem = models.TextField(u'备注', help_text='客户个人信息备注等')

    class Meta:
        app_label = "zhugeleida"


class zgld_chatinfo(models.Model):
    send_type_choice = ((1,'user_to_customer'),
                        (2,'customer_to_user')
                        )
    send_type = models.SmallIntegerField(choices=send_type_choice,verbose_name='发送类型',blank=True,null=True)
    is_new_msg = models.BooleanField(default=True, verbose_name='是否为新消息', )
    is_last_msg = models.BooleanField(default=True,verbose_name='是否为最后一次的消息')
    userprofile = models.ForeignKey('zgld_userprofile',verbose_name='用户',null=True,blank=True)
    customer  = models.ForeignKey('zgld_customer',verbose_name='客户',null=True,blank=True)

    msg = models.TextField(u'消息',null=True,blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

