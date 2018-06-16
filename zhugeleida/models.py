from django.db import models


# 公司管理
class zgld_company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    corp_id = models.CharField(verbose_name="企业ID", max_length=128)
    tongxunlu_secret = models.CharField(verbose_name="通讯录同步应用的secret", max_length=256)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "公司表"
        app_label = "zhugeleida"

class zgld_department(models.Model):
    company = models.ForeignKey('zgld_company',verbose_name='所属公司')
    name = models.CharField(verbose_name="部门名称", max_length=128)
    parentid = models.ForeignKey('self',verbose_name='父级部门ID',null=True,blank=True)
    order = models.IntegerField(verbose_name='在父部门中的次序值',null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "部门表"
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
    department = models.ManyToManyField('zgld_department', verbose_name='所属部门')
    position = models.CharField(verbose_name='职位信息',max_length=128)
    role = models.ForeignKey("zgld_role", verbose_name="角色")
    phone = models.CharField(verbose_name='绑定微信手机号', max_length=20, blank=True, null=True)
    mingpian_phone = models.CharField(verbose_name='名片展示手机号', max_length=20, blank=True, null=True)

    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)
    avatar = models.CharField(verbose_name="头像url", max_length=128, default='statics/imgs/setAvator.jpg')
    qr_code = models.CharField(verbose_name='员工个人二维码', max_length=128,null=True)
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="成员状态", default=2)

    popularity = models.IntegerField(verbose_name='人气(被查看)',default=0)
    praise = models.IntegerField(verbose_name='被赞',default=0)
    forward = models.IntegerField(verbose_name='转发',default=0)


    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)


    def __str__(self):
        return self.username

    class Meta:
        # unique_together = (("userid", "company"),)
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
    user = models.ForeignKey('zgld_userprofile', verbose_name='所属用户', null=True)
    name = models.CharField(verbose_name='标签名称', max_length=64)
    tag_parent = models.ForeignKey('self',verbose_name='标签父级',null=True)
    tag_customer = models.ManyToManyField('zgld_customer',verbose_name='关联到客户',null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return 'tag: %s ' % (self.name)

    class Meta:
        app_label = "zhugeleida"


# 客户管理
class zgld_customer(models.Model):
    username = models.CharField(verbose_name='客户姓名', max_length=64,null=True)
    memo_name = models.CharField(max_length=64, verbose_name='备注名', blank=True, null=True)

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.IntegerField(choices=sex_choices, default=1,blank=True,null=True)

    openid = models.CharField(verbose_name='OpenID(用户唯一标识)', max_length=64)
    headimgurl = models.CharField(verbose_name="用户头像url", max_length=128,default='statics/imgs/Avator.jpg')
    expected_time = models.DateField(verbose_name='预计成交时间', blank=True, null=True, help_text="格式yyyy-mm-dd")
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)

    user_type_choices = (
        (1, '微信公众号'),
        (2, '微信小程序'),

    )
    user_type = models.SmallIntegerField(u'客户访问类型', choices=user_type_choices)
    source_type_choices = (
        (1, '扫码'),
        (2, '转发'),

    )
    source = models.SmallIntegerField(u'客户来源', choices=source_type_choices)

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


    def __str__(self):
        return 'Custer: %s ' % (self.username)

    class Meta:
        verbose_name_plural = "客户表"
        app_label = "zhugeleida"

#用户-客户跟进信息-关系绑定表
class zgld_user_customer_flowup(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='用户', null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='客户', null=True)
    last_follow_time = models.DateTimeField(verbose_name='最后跟进时间', null=True) # 指的是 用户最后留言时间和用户跟进用语的写入。
    last_activity_time = models.DateTimeField(verbose_name='最后活动时间', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "用户-客户跟进信息-关系绑定表"
        app_label = "zhugeleida"

#跟进-消息详情表
class zgld_follow_info(models.Model):
    user_customer_flowup = models.ForeignKey('zgld_user_customer_flowup',verbose_name='跟进客户|用户绑定')
    follow_info = models.CharField(verbose_name='跟进发送信息',max_length=256,null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    class Meta:
        verbose_name_plural = "跟进-消息详情表"
        app_label = "zhugeleida"

#跟进常用语
class zgld_follow_language(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='用户', null=True)
    custom_language = models.CharField(max_length=256,verbose_name='自定义常用语',null=True)
    # language_choices =  (
    #         (1,'客户查看了公司产品,有合作意向'),
    #         (2,'标记一下,客户有合作意向'),
    #         (3,'客户多次查看小程序,合作意向强烈'),
    #         (4,'计划近期安排拜访'),
    #         (5,'意向客户,需安排拜访'),
    #         (6,'见面聊过,客户有合作意向'),
    #         (7,'曾拜访过的客户'),
    #         (8,'标记一下,需要给客户发送报价'),
    #         (9,'已发报价,待客户反馈'),
    #         (10,'已成交客户,维护好后续关系')
    #     )
    # follow_language = models.SmallIntegerField( choices=language_choices, verbose_name='常用跟进用语', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)    # 今天新增或者几天前新增,判断当活动没有活动和跟进时间的时候，就会比较新增时间，返回。

    class Meta:
        verbose_name_plural = "跟进常用语"
        app_label = "zhugeleida"

#资料详情表
class zgld_information(models.Model):
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
        verbose_name_plural = "资料详情表"
        app_label = "zhugeleida"



class zgld_photo(models.Model):
    photo_url = models.CharField(verbose_name="客户信息照片地址", max_length=128)
    photo = models.FileField(upload_to='photo',verbose_name='客户上传照片地址')
    information = models.ForeignKey('zgld_information', verbose_name='客户详情')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        app_label = "zhugeleida"


#访问动能日志记录表
class zgld_accesslog(models.Model):
    """Store Schedule run logs """

    action_choices = (
        (1, '查看名片'),  # 查看了名片第XXX次。
        (2, '查看产品'),  # 查看您的产品; 查看竞价排名; 转发了竞价排名。
        (3, '查看动态'),  # 查看了公司的动态。 评论了您的企业动态。
        (4, '查看官网'),  # 查看了您的官网 , 转发了您官网。

        (5, '复制微信'),
        (6, '转发名片'),  #
        (7, '咨询产品'),
        (8, '保存电话'),
        (9, '觉得靠谱'),  # 取消了对您的靠谱
        (10, '拨打电话'),
        (11, '播放语音'),
        (12, '复制邮箱'),
    )

    action = models.SmallIntegerField(verbose_name="访问的功能动作", choices=action_choices)
    user = models.ForeignKey('zgld_userprofile',verbose_name=' 被访问的用户')
    customer = models.ForeignKey('zgld_customer',verbose_name='访问的客户')
    remark = models.TextField(verbose_name='备注', help_text='访问信息备注')
    activity_time = models.ForeignKey('zgld_user_customer_flowup',related_name='accesslog',verbose_name='活动时间(客户活动)', null=True)  # 代表客户活动日志最后一条记录的时间
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "访问动能日志记录表"
        app_label = "zhugeleida"

#聊天室记录表
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
    activity_time = models.ForeignKey('zgld_user_customer_flowup',related_name='chatinfo' ,verbose_name='最后活动时间(客户发起对话)', null=True)
    follow_time = models.ForeignKey('zgld_user_customer_flowup', verbose_name='最后跟进时间(用户发起对话)', null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "聊天室记录表"
        app_label = "zhugeleida"