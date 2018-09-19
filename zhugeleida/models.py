from django.db import models


# 公司管理
class zgld_company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    area = models.CharField(max_length=128, verbose_name='所在地区', null=True)
    address = models.TextField(verbose_name='公司详细地址')
    corp_id = models.CharField(verbose_name="企业ID", max_length=128)
    tongxunlu_secret = models.CharField(verbose_name="通讯录同步应用的secret", max_length=256)
    website_content = models.TextField(verbose_name='官网内容',default='[]')
    mingpian_available_num = models.SmallIntegerField(verbose_name='可开通名片数量',default=0) # 0说名一个也没有开通。
    charging_start_time = models.DateTimeField(verbose_name="开始付费时间", null=True)
    is_validate = models.BooleanField(verbose_name="验证通讯录secret是否通过",default=False)
    weChatQrCode = models.CharField(verbose_name='企业微信二维码', max_length=256, default='')
    remarks = models.TextField(verbose_name="备注",null=True)

    open_length_time_choices = (
        (1, "一个月"),
        (2, "二个月"),
        (3, "三个月"),
        (4, "一年"),
        (5, "二年")
    )
    open_length_time = models.SmallIntegerField(choices=open_length_time_choices, verbose_name="开通时长",null=True)
    account_expired_time = models.DateTimeField(verbose_name="账户过期时间", null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "公司表"
        app_label = "zhugeleida"



# 官网模板
class zgld_website_template(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    template_content = models.TextField(verbose_name='官网内容',default='[]')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "公司官网模板"
        app_label = "zhugeleida"



#企业App应用
class zgld_app(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    name = models.CharField(verbose_name="企业应用_名称", max_length=128)
    agent_id = models.CharField(verbose_name="应用ID", max_length=128)
    app_secret = models.CharField(verbose_name="应用secret", max_length=256)
    app_type_choice = (
        (1,'AI雷达'),
        (2,'Boss雷达')
    )
    app_type = models.SmallIntegerField(verbose_name='app类型区分', choices=app_type_choice,default=1)

    is_validate = models.BooleanField(verbose_name="验证应用secret是否通过", default=False)

    class Meta:
        verbose_name_plural = "企业微信App应用"
        app_label = "zhugeleida"


#企业公众号-App应用
class zgld_gongzhonghao_app(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name="公众号授权的后台用户", null=True)
    company = models.ForeignKey('zgld_company', verbose_name='所属公司')
    original_id = models.CharField(verbose_name='公众号原始唯一ID', max_length=64, null=True)

    head_img = models.CharField(verbose_name="授权方头像", max_length=256, null=True)
    qrcode_url = models.CharField(verbose_name="二维码图片的URL", max_length=128, null=True)
    name = models.CharField(verbose_name="公众号名称", max_length=128, null=True)
    principal_name = models.CharField(verbose_name="公众号主体名称", max_length=128, null=True)

    authorization_appid = models.CharField(verbose_name="授权方appid", max_length=128, null=True)
    authorization_secret = models.CharField(verbose_name="授权方appsecret", max_length=128, null=True)
    template_id = models.CharField(verbose_name="消息模板ID", max_length=128, null=True)
    authorizer_refresh_token = models.CharField(verbose_name='第三方平台接口调用凭据-刷新令牌', max_length=64, null=True)
    verify_type_info = models.BooleanField(verbose_name="微信认证是否通过", default=False)  # -1代表未认证，0代表微信认证
    introduce = models.CharField(verbose_name="公众号介绍", max_length=1024, null=True)
    service_category = models.CharField(verbose_name="服务类目", max_length=64,null=True ,default="IT科技>硬件与设备")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        verbose_name_plural = "公众号App应用"
        app_label = "zhugeleida"





#小程序App应用
class zgld_xiaochengxu_app(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name="小程序授权的后台用户", null=True)
    company = models.ForeignKey('zgld_company', verbose_name='所属公司')
    original_id = models.CharField(verbose_name='小程序原始唯一ID',max_length=64,null=True)

    head_img = models.CharField(verbose_name="授权方头像", max_length=256,null=True)
    qrcode_url = models.CharField(verbose_name="二维码图片的URL", max_length=128,null=True)
    name = models.CharField(verbose_name="小程序名称", max_length=128, null=True)
    principal_name = models.CharField(verbose_name="小程序主体名称", max_length=128,null=True)

    code_release_status_choice = (
        (1, '代码上传成功'),
        (2, '代码上传失败'),

        (3, '提交审核报错'),
        (4, '审核中'),
        (5, '审核通过'),
        (6, '审核未通过'),

        (7, '上线成功'),
        (8, '上线失败'),
        (9, '审核撤回成功'),
        (10, '审核撤回失败'),
        (11, '版本回退成功'),
        (12, '版本回退失败'),

    )
    code_release_status = models.SmallIntegerField(verbose_name='代码发布流程状态', null=True, choices=code_release_status_choice)
    code_release_result = models.CharField(verbose_name='结果',max_length=1024,null=True)

    authorization_appid = models.CharField(verbose_name="授权方appid", max_length=128,null=True)
    authorization_secret = models.CharField(verbose_name="授权方appsecret", max_length=128,null=True)
    template_id = models.CharField(verbose_name="消息模板ID", max_length=128,null=True)
    version_num = models.CharField(verbose_name="[已经上线]版本号", null=True, max_length=32)
    authorizer_refresh_token = models.CharField(verbose_name='第三方平台接口调用凭据-刷新令牌', max_length=64, null=True)
    verify_type_info = models.BooleanField(verbose_name="微信认证是否通过", default=False)    #-1代表未认证，0代表微信认证
    introduce = models.CharField(verbose_name="小程序介绍", max_length=1024,null=True)
    service_category = models.CharField(verbose_name="服务类目", max_length=64,null=True, default="IT科技>硬件与设备")
    ext_json = models.TextField(verbose_name="第三方自定义的配置", null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        verbose_name_plural = "小程序App应用"
        app_label = "zhugeleida"


# 代小程序上传代码表 和 代小程序提交审核
class zgld_xiapchengxu_upload_audit(models.Model):
    app = models.ForeignKey('zgld_xiaochengxu_app', verbose_name='所属小程序App')
    publisher = models.ForeignKey('zgld_admin_userprofile', verbose_name="代小程序-发布者", null=True)
    desc = models.TextField(verbose_name='描述', null=True)
    version_num = models.CharField(verbose_name="版本号",null=True,max_length=32)
    template_id = models.IntegerField(verbose_name="小程序模板ID", null=True)
    upload_code_date = models.DateTimeField(verbose_name="代码长传时间", null=True)
    experience_qrcode =  models.CharField(verbose_name="体验二维码",null=True,max_length=128)

    upload_result_type = (
        (0,'代码上传成功'),
        (1,'代码上传失败')
    )
    upload_result = models.SmallIntegerField(verbose_name='上传结果',null=True,choices=upload_result_type)

    # app = models.ForeignKey('zgld_xiaochengxu_app', verbose_name='审核的-小程序App')
    # upload_code = models.OneToOneField('zgld_xiapchengxu_upload', verbose_name='上传的代码') # 审核的哪个版本的长传后的代码。
    auditid = models.IntegerField(verbose_name="接口返回审核编号", null=True)
    audit_commit_date = models.DateTimeField(verbose_name='提交审核时间',null=True)
    audit_reply_date = models.DateTimeField(verbose_name="审核回复时间", null=True)
    audit_result_type = (
        (0,'审核成功'),
        (1,'审核失败'),
        (2,'审核中'),
        (3,'提交审核代码失败'),
        (4,'审核撤回成功'),
        (5,'审核撤回失败')
    )
    audit_result = models.SmallIntegerField(verbose_name='审核结果',null=True,choices=audit_result_type)
    reason = models.CharField(verbose_name='审核失败原因',max_length=1024,null=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.auditid)

    class Meta:
        verbose_name_plural = "代小程序提交审核代码表"
        app_label = "zhugeleida"




## 代小程序发布审核通过代码表 ##
class zgld_xiapchengxu_release(models.Model):
    app = models.ForeignKey('zgld_xiaochengxu_app', verbose_name='审核的-小程序App')
    audit_code = models.ForeignKey('zgld_xiapchengxu_upload_audit', verbose_name='审核通过的代码') # 审核的哪个版本的长传后的代码。
    release_commit_date = models.DateTimeField(verbose_name='发布时间',null=True)
    # release_reply_date = models.DateTimeField(verbose_name="发布回复时间", null=True)
    release_result_type = (
        (1,'上线通过'),
        (2,'上线失败'),
        (3, '版本回退成功'),
        (4, '版本回退失败'),
    )
    release_result = models.SmallIntegerField(verbose_name='发布结果',null=True,choices=release_result_type)
    reason = models.CharField(verbose_name='上线失败原因',max_length=1024,null=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.audit_code)

    class Meta:
        verbose_name_plural = "代小程序提交发布代码表"
        app_label = "zhugeleida"



# 公司部门
class zgld_department(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属公司')
    name = models.CharField(verbose_name="部门名称", max_length=128)
    parentid = models.ForeignKey('self', verbose_name='父级部门ID', null=True, blank=True)
    order = models.IntegerField(verbose_name='在父部门中的次序值', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        verbose_name_plural = "部门表"
        app_label = "zhugeleida"


# 角色管理
class zgld_admin_role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    rules= models.ManyToManyField('zgld_access_rules',verbose_name="关联权限条目")

    class Meta:
        verbose_name_plural = "角色表"
        app_label = "zhugeleida"

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

# 后台用户管理
class zgld_admin_userprofile(models.Model):
    login_user =  models.CharField(verbose_name="登录用户名", max_length=32)
    username = models.CharField(verbose_name="成员姓名", max_length=32)
    memo_name = models.CharField(verbose_name="成员备注名", max_length=32,null=True)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    position = models.CharField(verbose_name='职位', max_length=128)
    avatar = models.CharField(verbose_name="头像url", max_length=256, default='statics/imgs/setAvator.jpg')
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="成员状态", default=1)

    is_reset_password = models.BooleanField(verbose_name="是否重置密码", default=False)
    token = models.CharField(verbose_name="token值", max_length=64, null=True, blank=True)
    role = models.ForeignKey("zgld_admin_role", verbose_name="角色")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        # unique_together = (("userid", "company"),)
        verbose_name_plural = "后台用户管理"
        app_label = "zhugeleida"

# 权限表
class zgld_access_rules(models.Model):
    name = models.CharField(verbose_name="权限名称", max_length=64)
    title = models.CharField(verbose_name="标题", max_length=64, null=True, blank=True)
    super_id = models.ForeignKey('self', verbose_name="上级ID", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "权限规则表"

    def __str__(self):
        return "%s" % self.name



# 企业用户管理
class zgld_userprofile(models.Model):
    userid = models.CharField(max_length=64, verbose_name='成员UserID')
    login_user = models.CharField(verbose_name="(登录)用户名", max_length=32,null=True)
    password = models.CharField(verbose_name="密码", max_length=32, null=True, blank=True)

    username = models.CharField(verbose_name="成员姓名", max_length=32)
    memo_name = models.CharField(max_length=64, verbose_name='名片-昵称', blank=True, null=True)
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(choices=gender_choices, default=1,null=True)
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    department = models.ManyToManyField('zgld_department', verbose_name='所属部门')
    position = models.CharField(verbose_name='职位信息', max_length=128,null=True)
    # role = models.ForeignKey("zgld_role", verbose_name="角色")

    telephone = models.CharField(verbose_name='座机号', max_length=20, blank=True, null=True)
    wechat_phone = models.CharField(verbose_name='微信绑定的手机号', max_length=20, blank=True, null=True)
    wechat = models.CharField(verbose_name='微信号', max_length=64, null=True)
    email = models.EmailField(u'常用邮箱', blank=True, null=True)

    mingpian_phone = models.CharField(verbose_name='名片展示手机号', max_length=20, blank=True, null=True)
    is_show_phone = models.BooleanField(verbose_name='手机号是否显示在名片上', default=True)

    country_choices = ((1, '国内'),
                       (2, '国外'),
                       )
    country = models.SmallIntegerField(choices=country_choices, verbose_name='国家', null=True)
    area = models.CharField(max_length=128, verbose_name='所在地区', null=True)
    address = models.TextField(verbose_name='详细地址', null=True)

    token = models.CharField(verbose_name="token值", max_length=64, null=True, blank=True)
    avatar = models.CharField(verbose_name="头像url", max_length=256, default='statics/imgs/setAvator.jpg')
    qr_code = models.CharField(verbose_name='企业用户个人二维码', max_length=128, null=True)
    status_choices = (
        (1, "启用"),
        (2, "未启用"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="成员状态", default=2)

    popularity = models.IntegerField(verbose_name='人气数(被查看)', default=0)
    praise = models.IntegerField(verbose_name='被赞数', default=0)
    forward = models.IntegerField(verbose_name='转发数', default=0)
    sign = models.TextField(verbose_name='个性签名', null=True)
    sign_num = models.IntegerField(verbose_name='签名被赞个数', default=0)
    voice = models.CharField(verbose_name='语音介绍', null=True, max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # user_expired = models.DateTimeField(verbose_name="用户过期时间",null=True)
    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True, auto_now_add=True,)

    def __str__(self):
        return self.username

    class Meta:
        # unique_together = (("userid", "company"),)
        verbose_name_plural = "用户表"
        app_label = "zhugeleida"


# 企业用户临时表
class zgld_temp_userprofile(models.Model):

    username = models.CharField(verbose_name="成员姓名", max_length=32)
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    department = models.CharField(max_length=64,verbose_name='所属部门')
    position = models.CharField(verbose_name='职位信息', max_length=128,null=True)

    #telephone = models.CharField(verbose_name='座机号', max_length=20, blank=True, null=True)
    wechat = models.CharField(verbose_name='微信号', max_length=64, null=True)
    wechat_phone = models.CharField(verbose_name='微信绑定的手机号', max_length=20, blank=True, null=True)
    mingpian_phone = models.CharField(verbose_name='名片展示手机号', max_length=20, blank=True, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        # unique_together = (("userid", "company"),)
        verbose_name_plural = "用户临时表"
        app_label = "zhugeleida"



# 用户标签
class zgld_user_tag(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='标签所属用户')
    name = models.CharField(verbose_name='标签名称', max_length=64)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "用户标签表"
        app_label = "zhugeleida"


# 用户照片和头像
class zgld_user_photo(models.Model):
    photo_type_choices =(
        (1,'photo'),   # 用户上传照片
        (2,'avator')   # 用户名片头像
    )
    photo_type = models.SmallIntegerField(verbose_name='用户图片的类型',choices=photo_type_choices)
    user = models.ForeignKey('zgld_userprofile', verbose_name='照片所属用户')
    photo_url = models.CharField(verbose_name='照片URL链接', max_length=256, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    order = models.SmallIntegerField(verbose_name='序号', null=True)

    class Meta:
        verbose_name_plural = "用户照片表"
        app_label = "zhugeleida"


#意见反馈表
class zgld_user_feedback(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='意见所属用户')
    problem_type_choices = (
        (1,'客户服务'),
        (2,'功能异常'),
        (3,'产品建议')
    )
    problem_type = models.SmallIntegerField(verbose_name='问题类型',choices=problem_type_choices)
    status_choices = (
        (1,'未处理'),
        (2,'已处理')
    )
    status = models.SmallIntegerField(verbose_name='问题处理进度',choices=status_choices,default=1)
    content = models.TextField(verbose_name='内容', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "用户意见反馈表"
        app_label = "zhugeleida"



# #公司产品
class zgld_product(models.Model):
    product_status_choices = (
        (1,'已发布'),
        (2,'已下架'),
        (3,'推荐')
    )
    status = models.SmallIntegerField(verbose_name='产品状态',choices=product_status_choices,default=1)
    user = models.ForeignKey('zgld_userprofile', verbose_name='所属用户', null=True)
    company = models.ForeignKey('zgld_company', verbose_name='所属企业', null=True)
    name = models.CharField(verbose_name='产品名称', null=True, max_length=128)
    price = models.CharField(verbose_name='价格', max_length=64, null=True)
    reason = models.CharField(verbose_name='推荐理由', max_length=1024, null=True)
    content = models.TextField(verbose_name='内容', null=True)
    recommend_index =  models.SmallIntegerField(verbose_name='产品推荐指数',default=0) # 从0 - 10 ,0 代表不推荐。
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "公司产品表"
        app_label = "zhugeleida"


class zgld_product_article(models.Model):
    product = models.ForeignKey('zgld_product', verbose_name='文章所属的产品', null=True)
    article_type_choices = (
                            (1,'标题'),
                            (2,'内容'),
    )
    type = models.SmallIntegerField(verbose_name='类型', choices=article_type_choices,null=True)
    order = models.SmallIntegerField(verbose_name='序号', null=True)
    title = models.CharField(verbose_name='标题', max_length=64, null=True)
    content = models.TextField(verbose_name='内容', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "产品文章表"
        app_label = "zhugeleida"


class zgld_product_picture(models.Model):
    order = models.SmallIntegerField(verbose_name='序号', null=True)
    product = models.ForeignKey('zgld_product', verbose_name='图片所属的产品', null=True)
    picture_type_choices = (
        (1, '产品封面'),
        (2, '产品介绍')
    )
    picture_type = models.SmallIntegerField(verbose_name='图片类型', null=True, choices=picture_type_choices)
    picture_url = models.CharField(verbose_name='图片URL链接', max_length=256, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "用户照片表"
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
    tag_parent = models.ForeignKey('self', verbose_name='标签父级', null=True)
    tag_customer = models.ManyToManyField('zgld_customer', verbose_name='关联到客户')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return 'tag: %s ' % (self.name)

    class Meta:
        app_label = "zhugeleida"


# 小程序-客户管理
class zgld_customer(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属公司')
    username = models.CharField(verbose_name='客户姓名', max_length=128, null=True)
    memo_name = models.CharField(max_length=128, verbose_name='备注名', blank=True, null=True)
    openid = models.CharField(verbose_name='OpenID(用户唯一标识)', max_length=128)
    formid = models.TextField(verbose_name='formId(用于发送模板消息)',null=True,default="[]")

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.IntegerField(choices=sex_choices, blank=True, null=True)

    headimgurl = models.CharField(verbose_name="用户头像url", max_length=256, default='statics/imgs/Avator.jpg')
    # expected_time = models.DateField(verbose_name='预计成交时间', blank=True, null=True, help_text="格式yyyy-mm-dd")
    token = models.CharField(verbose_name="token值", max_length=32, null=True, blank=True)

    user_type_choices = (
        (1, '微信公众号'),
        (2, '微信小程序'),

    )
    user_type = models.SmallIntegerField(u'客户访问类型', choices=user_type_choices)
    nickname = models.CharField(max_length=64, verbose_name='昵称', blank=True, null=True)
    phone = models.CharField(verbose_name='手机号', max_length=20, blank=True, null=True)
    country = models.CharField(max_length=64, verbose_name='国家', blank=True, null=True)
    city = models.CharField(max_length=32, verbose_name='客户所在城市', blank=True, null=True)
    province = models.CharField(max_length=32, verbose_name='所在省份', blank=True, null=True)
    language = models.CharField(max_length=32, verbose_name='语言', blank=True, null=True)
    # expedted_pr = models.IntegerField(verbose_name='预计成交概率',default=0, null=True)
    subscribe_time = models.DateTimeField(verbose_name='用户关注时间', blank=True, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return 'Custer: %s ' % (self.username)

    class Meta:
        verbose_name_plural = "客户表"
        app_label = "zhugeleida"


# 客户所属用户-关系绑定表
class zgld_user_customer_belonger(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='客户所属的用户', null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='客户ID', null=True)
    source_type_choices = (
        (1, '扫码'),
        (2, '转发'),
        (3, '搜索'),
    )
    source = models.SmallIntegerField(u'客户来源', choices=source_type_choices)
    qr_code = models.CharField(verbose_name='用户-客户-对应二维码', max_length=128, null=True)
    customer_parent = models.ForeignKey('zgld_customer', verbose_name='客户所属父级',related_name="customer_parent" ,null=True, blank=True)
    expected_time = models.DateField(verbose_name='预计成交时间', blank=True, null=True)
    expedted_pr = models.IntegerField(verbose_name='预计成交概率', default=0, null=True)

    last_follow_time = models.DateTimeField(verbose_name='最后跟进时间', null=True)  # 指的是 用户最后发留言时间和用户跟进用语的写入。
    last_activity_time = models.DateTimeField(verbose_name='最后活动时间', null=True)

    is_customer_msg_num = models.IntegerField(default=0, verbose_name='是否是客户发的新消息个数')
    is_customer_product_num = models.IntegerField(default=0, verbose_name='是否是客户咨询产品的消息个数')
    is_user_msg_num = models.IntegerField(default=0, verbose_name='是否是用户发的新消息个数')

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "客户所属用户关系|跟进信息绑定表"
        app_label = "zhugeleida"

# 跟进-消息详情表
class zgld_follow_info(models.Model):
    user_customer_flowup = models.ForeignKey('zgld_user_customer_belonger', verbose_name='跟进客户|用户绑定')
    follow_info = models.CharField(verbose_name='跟进发送信息', max_length=256, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "跟进-消息详情表"
        app_label = "zhugeleida"



# 用户-客户跟进信息-关系绑定表
# class zgld_user_customer_flowup(models.Model):
#     user = models.ForeignKey('zgld_userprofile', verbose_name='用户', null=True)
#     customer = models.ForeignKey('zgld_customer', verbose_name='客户', null=True)
#
#     last_follow_time = models.DateTimeField(verbose_name='最后跟进时间', null=True)  # 指的是 用户最后发留言时间和用户跟进用语的写入。
#     last_activity_time = models.DateTimeField(verbose_name='最后活动时间', null=True)
#
#     is_customer_msg_num = models.IntegerField(default=0, verbose_name='是否是客户发的新消息个数')
#     is_customer_product_num = models.IntegerField(default=0, verbose_name='是否是客户咨询产品的消息个数')
#     is_user_msg_num = models.IntegerField(default=0, verbose_name='是否是用户发的新消息个数')
#
#     create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
#
#     class Meta:
#         verbose_name_plural = "用户-客户跟进信息-关系绑定表"
#         # unique_together = [
#         #     ('customer', 'user'),
#         # ]
#         app_label = "zhugeleida"


# 用户被赞【是否靠谱】
class zgld_up_down(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='被赞的用户')
    customer = models.ForeignKey('zgld_customer', verbose_name='赞或踩的客户')
    up = models.BooleanField(verbose_name='是否赞', default=False)

    class Meta:
        unique_together = [
            ('customer', 'user'),
        ]
        verbose_name_plural = "用户顶或踩表"
        app_label = "zhugeleida"


# 用户签名是否被赞
class zgld_up_down_sign(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='被赞的用户签名')
    customer = models.ForeignKey('zgld_customer', verbose_name='赞或踩的用户')
    up = models.BooleanField(verbose_name='是否赞', default=False)

    class Meta:
        unique_together = [
            ('customer', 'user'),
        ]
        verbose_name_plural = "用户签名顶或踩表"
        app_label = "zhugeleida"


# 跟进常用语
class zgld_follow_language(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name='用户', null=True)
    custom_language = models.CharField(max_length=256, verbose_name='自定义常用语', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间",
                                       auto_now_add=True)  # 今天新增或者几天前新增,判断当活动没有活动和跟进时间的时候，就会比较新增时间，返回。

    class Meta:
        verbose_name_plural = "跟进常用语"
        app_label = "zhugeleida"


# 资料详情表
class zgld_information(models.Model):
    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.IntegerField(choices=sex_choices, blank=True, null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='客户表', null=True)
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
    photo = models.FileField(upload_to='photo', verbose_name='客户上传照片地址')
    information = models.ForeignKey('zgld_information', verbose_name='客户详情')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        app_label = "zhugeleida"


# 访问动能日志记录表
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
        (13, '授权访问'),

        (14,'查看文章'),
        (15,'转发文章到朋友'),
        (16,'转发文章到朋友圈')

    )

    action = models.SmallIntegerField(verbose_name="访问的功能动作", choices=action_choices)
    user = models.ForeignKey('zgld_userprofile', verbose_name=' 被访问的用户',null=True)
    article = models.ForeignKey('zgld_article', verbose_name='文章',null=True)

    customer = models.ForeignKey('zgld_customer', verbose_name='访问的客户')
    remark = models.TextField(verbose_name='备注', help_text='访问信息备注')
    # activity_time = models.ForeignKey('zgld_user_customer_flowup', related_name='accesslog', verbose_name='活动时间(客户活动)',null=True)  # 代表客户活动日志最后一条记录的时间
    is_new_msg = models.BooleanField(default=True, verbose_name='是否为新日志')
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "访问动能日志记录表"
        app_label = "zhugeleida"


# 聊天室记录表
class zgld_chatinfo(models.Model):
    send_type_choice = ((1, 'user_to_customer'),
                        (2, 'customer_to_user')
                        )
    send_type = models.SmallIntegerField(choices=send_type_choice, verbose_name='发送类型', blank=True, null=True)
    is_customer_new_msg = models.BooleanField(default=True, verbose_name='是否为客户的新消息')
    is_user_new_msg = models.BooleanField(default=True, verbose_name='是否为用户的新消息')
    is_last_msg = models.BooleanField(default=True, verbose_name='是否为最后一次的消息')
    userprofile = models.ForeignKey('zgld_userprofile', verbose_name='用户', null=True, blank=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='客户', null=True, blank=True)
    msg = models.TextField(u'消息', null=True, blank=True)
    content = models.TextField(verbose_name='消息', null=True, blank=True)

    info_type_choices = (
                        (1,'chat_people_info'),     #客户和用户之间的聊天信息
                        (2,'chat_product_info')   #客户和用户之间的产品咨询
    )
    info_type = models.SmallIntegerField(default=1, verbose_name='聊天信息的类型',choices=info_type_choices)
    product_cover_url = models.CharField(verbose_name='产品封面URl', max_length=256, null=True)
    product_name = models.CharField(verbose_name='产品名称', null=True, max_length=128)
    product_price = models.CharField(verbose_name='价格', max_length=64, null=True)

    # activity_time = models.ForeignKey('zgld_user_customer_flowup', related_name='chatinfo',
    #                                   verbose_name='最后活动时间(客户发起对话)', null=True)
    # follow_time = models.ForeignKey('zgld_user_customer_flowup', verbose_name='最后跟进时间(用户发起对话)', null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "聊天室记录表"
        app_label = "zhugeleida"




#公众号-模板文章详细表
class zgld_template_article(models.Model):

    user = models.ForeignKey('zgld_admin_userprofile', verbose_name='模板文章作者', null=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    cover_picture = models.CharField(verbose_name="封面图片URL", max_length=128)
    summary = models.CharField(verbose_name='文章摘要', max_length=255)
    content = models.TextField(verbose_name='文章内容', null=True)
    # tags = models.ManyToManyField('zgld_article_tag', through='zgld_article_to_tag', through_fields=('article', 'tag'))
    tags = models.ManyToManyField('zgld_template_article_tag',verbose_name="模板文章关联的标签")
    qrcode_url = models.CharField(verbose_name="二维码URL", max_length=128, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "模板文章表"
        app_label = "zhugeleida"


#公众号-文章标签表
class zgld_template_article_tag(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile',verbose_name="模板文章标签所属用户",null=True)
    name = models.CharField(verbose_name='标签名称', max_length=32)
    # parent_id = models.ForeignKey('self',verbose_name="父级ID",null=True)

    class Meta:
        verbose_name_plural = "模板文章标签表"
        app_label = "zhugeleida"


#公众号-文章表
class zgld_article(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name='文章作者', null=True)
    company = models.ForeignKey('zgld_company',verbose_name='文章所属公司',null=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章摘要', max_length=255)
    status_choices = ( (1,'已发'),
                       (2,'未发'),
                     )
    status = models.SmallIntegerField(default=2, verbose_name='文章状态', choices=status_choices)
    source_choices = ( (1,'原创'),
                       (2,'转载'),
                     )
    source = models.SmallIntegerField(default=1, verbose_name='文章来源', choices=source_choices)
    content = models.TextField(verbose_name='文章内容', null=True)

    tags = models.ManyToManyField('zgld_article_tag', verbose_name="文章关联的标签")
    # up_count = models.IntegerField(default=0,verbose_name="赞次数")
    # down_count = models.IntegerField(default=0,verbose_name="踩次数")
    cover_picture  = models.CharField(verbose_name="封面图片URL",max_length=128)
    read_count = models.IntegerField(verbose_name="被阅读数量",default=0)
    forward_count = models.IntegerField(verbose_name="被转发个数",default=0)
    comment_count = models.IntegerField(default=0,verbose_name="被评论数量")
    insert_ads = models.TextField(verbose_name='插入广告语',null=True)
    qrcode_url = models.CharField(verbose_name="二维码URL", max_length=128, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)

    class Meta:
        verbose_name_plural = "文章表"
        app_label = "zhugeleida"

#公众号-文章标签表
class zgld_article_tag(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile',verbose_name="标签所属用户",null=True)
    name = models.CharField(verbose_name='标签名称', max_length=32)
    # parent_id = models.ForeignKey('self',verbose_name="父级ID",null=True)

    class Meta:
        verbose_name_plural = "文章标签表"
        app_label = "zhugeleida"

#公众号-文章和查看客户之间的绑定关系表
class zgld_article_to_customer_belonger(models.Model):
    article = models.ForeignKey('zgld_article',verbose_name='文章')
    user = models.ForeignKey('zgld_userprofile', verbose_name="文章所属用户ID", null=True)

    level = models.IntegerField(verbose_name='客户所在层级',null=True)
    stay_time = models.IntegerField(verbose_name='停留时长',default=0)
    read_count = models.IntegerField(verbose_name="被阅读数量",default=0)
    forward_count = models.IntegerField(verbose_name="被转发个数",default=0)
    forward_friend_count = models.IntegerField(verbose_name="转发给朋友的个数", default=0)
    forward_friend_circle_count = models.IntegerField(verbose_name="转发给朋友圈的个数", default=0)
    customer = models.ForeignKey('zgld_customer', verbose_name="查看文章的客户", null=True)
    customer_parent = models.ForeignKey('zgld_customer', verbose_name='查看文章的客户所属的父级', related_name="article_customer_parent", null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        unique_together = [
            ('article', 'customer','user','customer_parent'),
        ]
        verbose_name_plural = "文章和查看客户之间绑定关系表"
        app_label = "zhugeleida"


#公众号-文章查看用户停留时间表
class zgld_article_access_log(models.Model):
    article = models.ForeignKey('zgld_article',verbose_name='文章')
    user = models.ForeignKey('zgld_userprofile', verbose_name="文章所属用户ID")

    customer = models.ForeignKey('zgld_customer', verbose_name="查看的客户")
    customer_parent = models.ForeignKey('zgld_customer', verbose_name='查看文章的客户所属的父级',
                                        related_name="article_customer_parent_log", null=True)
    stay_time = models.IntegerField(verbose_name='停留时长(秒)',default=0)
    last_access_date = models.DateTimeField(verbose_name="最后访问时间", null=True)

    class Meta:

        verbose_name_plural = "用户查看文章停留时间日志表"
        app_label = "zhugeleida"





#公众号-明片插件
class zgld_plugin_mingpian(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name="标签所属用户", null=True)
    name = models.CharField(verbose_name="名片名称", max_length=64)
    avatar = models.CharField(verbose_name="头像url", max_length=256, default='statics/imgs/setAvator.jpg')
    username = models.CharField(verbose_name='客户姓名', max_length=128, null=True)
    phone = models.CharField(verbose_name='手机号', max_length=20, blank=True, null=True)
    webchat_code = models.CharField(verbose_name='微信二维码', max_length=128, null=True)
    position = models.CharField(verbose_name='职位', max_length=256, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        verbose_name_plural = "插件-名片"
        app_label = "zhugeleida"


# 公众号-报名插件
class zgld_plugin_report(models.Model):
    #广告位
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name="归属的员工", null=True)
    ad_slogan = models.CharField(verbose_name="广告语", max_length=128)
    sign_up_button = models.CharField(verbose_name="报名按钮", max_length=64, default='statics/imgs/setAvator.jpg')
    is_get_phone_code = models.BooleanField(verbose_name='是否获取手机验证码', default=False)
    leave_message = models.TextField(verbose_name="客户留言提示", null=True)
    #报名页
    title = models.CharField(verbose_name='活动标题', max_length=128, null=True)
    introduce = models.TextField(verbose_name='活动说明', blank=True, null=True)
    skip_link = models.CharField(verbose_name="跳转链接",max_length=128,null=True)
    read_count = models.IntegerField(verbose_name="总阅读数量", default=0)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.ad_slogan)

    class Meta:
        verbose_name_plural = "插件-报名插件"
        app_label = "zhugeleida"

# 公众号-报名的客户
class zgld_report_to_customer(models.Model):
    customer = models.ForeignKey('zgld_customer', verbose_name="报名的客户", null=True)
    activity = models.ForeignKey('zgld_plugin_report', verbose_name="报名的活动", null=True)

    leave_message = models.TextField(verbose_name="客户留言", null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return 'Custer: %s | activity: %s ' % (self.customer_id,self.activity_id)

    class Meta:
        unique_together = (("customer", "activity"))
        verbose_name_plural = "报名的客户和活动绑定的关系"
        app_label = "zhugeleida"

# 公众号 - 名片商品
class zgld_plugin_goods(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name="归属的员工", null=True)
    title = models.CharField(verbose_name='商品标题', max_length=128, null=True)
    content = models.TextField(verbose_name='商品内容', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.title)

    class Meta:
        verbose_name_plural = "插件-商品插件"
        app_label = "zhugeleida"

# 公众号 - 名片商品
class zgld_plugin_goods_order(models.Model):
    customer = models.ForeignKey('zgld_customer', verbose_name="收货人", null=True)
    address = models.CharField(max_length=256,verbose_name='收货详细地址')
    leave_message = models.CharField(max_length=1024, verbose_name="客户留言", null=True)
    activity = models.ForeignKey('zgld_plugin_goods', verbose_name="购买的商品", null=True)
    order_amount = models.IntegerField(verbose_name='订单总金额',default=0)  #
    pay_status_choices = (
        (1, "未支付"),
        (2, "已支付"),
    )
    pay_status = models.SmallIntegerField(choices=pay_status_choices, verbose_name="支付状态", default=1)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.customer_id)

    class Meta:
        verbose_name_plural = "插件-商品-订单表"
        app_label = "zhugeleida"



# 后台管理 - 话术分组管理
class zgld_talk_group_management(models.Model):
    groupName = models.CharField(verbose_name='话术分组名称', max_length=64)
    userProfile = models.ForeignKey(to='zgld_admin_userprofile', verbose_name='用户名称', null=True, blank=True)
    companyName = models.ForeignKey(to='zgld_company', verbose_name='公司名称', null=True, blank=True)
    createDate = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
# 后台管理 - 话术详情管理
class zgld_speech_details_management(models.Model):
    contentWords = models.CharField(verbose_name='话术内容', max_length=128)
    sendNum = models.IntegerField(verbose_name='发送次数', default=0)
    talkGroupName = models.ForeignKey(to='zgld_talk_group_management', verbose_name='分组名称', null=True, blank=True)
    createDate = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

