from django.db import models


# 公司管理
class zgld_company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    area = models.CharField(max_length=128, verbose_name='所在地区', null=True)
    address = models.TextField(verbose_name='公司详细地址')
    corp_id = models.CharField(verbose_name="企业ID(授权方企业微信id)", max_length=128)
    tongxunlu_secret = models.CharField(verbose_name="通讯录同步应用的secret", max_length=256)
    # permanent_code =  models.CharField(verbose_name="企业微信永久授权码", max_length=128,null=True)

    website_content = models.TextField(verbose_name='官网内容',default='[]')
    mingpian_available_num = models.SmallIntegerField(verbose_name='可开通名片数量',default=0) # 0说名一个也没有开通。
    charging_start_time = models.DateTimeField(verbose_name="开始付费时间", null=True)
    is_validate = models.BooleanField(verbose_name="验证通讯录secret是否通过",default=False)
    weChatQrCode = models.CharField(verbose_name='企业微信二维码', max_length=256, default='')
    remarks = models.TextField(verbose_name="备注",null=True)

    product_function_type_choice = (
        (1, '小程序(名片)版|公众号(文章)版'),
        (2, '小程序版(名片)版'),
        (3, '公众号(文章) 版'),
        (4, '小程序(案例)版|公众号(文章)版'),
    )
    product_function_type = models.SmallIntegerField(verbose_name='产品功能类型', default=1, choices=product_function_type_choice)
    xcx_qr_code = models.CharField(verbose_name='企业小程序二维码', max_length=128, null=True)

    shopping_type_choice = (
        (1,'产品'),
        (2,'商城')
    )
    shopping_type = models.SmallIntegerField(verbose_name='购物类型',default=2, choices=shopping_type_choice)

    is_show_jszc_choices = (
        (1, "展示"),
        (2, "不展示"),
    )
    is_show_jszc = models.SmallIntegerField(choices=is_show_jszc_choices, verbose_name="是否展示技术支持", default=1)

    open_length_time = models.SmallIntegerField(verbose_name="开通时长(按月份)",null=True)
    account_expired_time = models.DateTimeField(verbose_name="账户过期时间", null=True)
    is_customer_unique = models.BooleanField(verbose_name="客户(通讯录)唯一性", default=False)

    account_balance = models.FloatField(verbose_name='账户余额', null=True, default=0)
    leiji_chongzhi = models.FloatField(verbose_name='累计充值', null=True, default=0)
    leiji_zhichu = models.FloatField(verbose_name='累计支出', null=True, default=0)

    seconds = models.IntegerField(verbose_name='每几秒【多少钱】', null=True, default=0)
    article_account = models.FloatField(verbose_name='付给的钱数', null=True, default=0)

    bossleida_data_tongji =  models.TextField(verbose_name='BOSS雷达数据统计[公司]',default='{}')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    # ------------------用于雷达AI首页统计数据 -- 判断条件 --  后台--企业管理-用户管理 修改该字段
    articles_read_customers = models.IntegerField(verbose_name='客户累计阅读文章数', default=3)
    article_reading_time = models.IntegerField(verbose_name='每篇文章阅读时长', default=60)
    is_same_label = models.IntegerField(verbose_name='是否匹配相同标签的文章', default=0) # 默认不匹配
    # -------------------------------------------------------------------------------------------------


    class Meta:
        verbose_name_plural = "公司表"
        app_label = "zhugeleida"


# 公司管理
class zgld_three_service_setting(models.Model):
    # company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    type_choice = (
        (1, '企业微信第三方服务商'),
        (2, '公众号(文章版)第三方平台'),
        (3, '小程序(名片版)第三方平台'),
        (4, '小程序(案例库)第三方平台')
    )
    three_services_type = models.SmallIntegerField(verbose_name='三方类型区分', choices=type_choice,null=True)
    config = models.CharField(max_length=2048,verbose_name="企业微信第三方配置", null=True)
    status_choices = (
        (0, "未通过"),
        (1, "通过"),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态", default=0)

##公司官网模板
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
    agent_id = models.CharField(verbose_name="应用ID", max_length=128,null=True)
    app_secret = models.CharField(verbose_name="应用secret", max_length=256,null=True)
    permanent_code = models.CharField(verbose_name="企业微信永久授权码", max_length=128, null=True)
    app_type_choice = (
        (1,'AI雷达'),
        (2,'Boss雷达'),
        (3,'三方通讯录')
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

    is_focus_get_redpacket = models.BooleanField(verbose_name="关注领取红包是否开启", default=False)
    focus_get_money = models.FloatField(verbose_name='关注领取红包金额',null=True)
    focus_total_money = models.SmallIntegerField(verbose_name='红包总金额',null=True)


    mode_choices =  ( (1, '随机红包'),
                      (2, '固定红包')
                      )
    mode = models.SmallIntegerField(default=1, verbose_name='红包发送方式', choices=mode_choices)


    is_used_daifa_choices = (  (1, '代发红包'),
                               (2, '自己商户发红包')
                             )
    is_used_daifa_redPacket = models.SmallIntegerField(default=1, verbose_name='是否开启代发红包', choices=is_used_daifa_choices)

    max_single_money = models.FloatField(verbose_name='随机最大单个金额(元)',default=0,null=True)
    min_single_money = models.FloatField(verbose_name='随机最小单个金额(元)',default=0,null=True)

    is_open_comment_choices = ( (0,'不开启评论'),
                                (1,'开启评论'),
                           )
    is_open_comment = models.SmallIntegerField(default=1, verbose_name='是否开启自动打标签', choices=is_open_comment_choices)

    reason = models.CharField(verbose_name='发送红包失败原因',max_length=512,null=True)

    authorization_appid = models.CharField(verbose_name="授权方appid", max_length=128, null=True)
    authorization_secret = models.CharField(verbose_name="授权方appsecret", max_length=128, null=True)
    template_id = models.CharField(verbose_name="消息模板ID", max_length=128, null=True)
    authorizer_refresh_token = models.CharField(verbose_name='第三方平台接口调用凭据-刷新令牌', max_length=64, null=True)
    verify_type_info = models.BooleanField(verbose_name="微信认证是否通过", default=False)  # -1代表未认证，0代表微信认证
    introduce = models.CharField(verbose_name="公众号绑定的小程序", max_length=2048, default='[]')
    service_category = models.CharField(verbose_name="服务类目", max_length=64,null=True ,default="IT科技>硬件与设备")
    gzh_notice_qrcode = models.CharField(verbose_name="公众号二维码(绑定管理员)", max_length=128, null=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        verbose_name_plural = "公众号App应用"
        app_label = "zhugeleida"


#小程序App应用
class zgld_xiaochengxu_app(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name="小程序授权的后台用户", null=True)
    company = models.ForeignKey('zgld_company', verbose_name='所属公司',null=True)
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
        (12, '版本回退失败')
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

    is_open_comment_choices = ((0, '不开启评论'),
                               (1, '开启评论'),
                               )
    is_open_comment = models.SmallIntegerField(default=1, verbose_name='是否开启自动打标签', choices=is_open_comment_choices)

    type_choice = (
        (1, '小程序(名片版)第三方平台'),
        (2, '小程序(案例库)第三方平台')
    )
    three_services_type = models.SmallIntegerField(verbose_name='三方类型区分', choices=type_choice, null=True)
    poster_company_logo =  models.CharField(verbose_name="公司海报logo", max_length=1024,null=True)

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


# 企业用户(咨询表)管理
class zgld_userprofile(models.Model):
    userid = models.CharField(max_length=64, verbose_name='成员UserID')
    login_user = models.CharField(verbose_name="(登录)用户名", max_length=32,null=True)
    password = models.CharField(verbose_name="密码", max_length=64, null=True, blank=True)

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
        (1, "AI雷达启用"),
        (2, "AI雷达不启用"),
        # (3, "文章管理员")

    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name="AI雷达状态", default=2)

    boss_status_choices = (
        (1, "Boss雷达启用"),
        (2, "Boss雷达不启用"),
    )
    boss_status = models.SmallIntegerField(choices=boss_status_choices, verbose_name="Boss雷达状态", default=2)

    article_admin_status_choices = (
        (1, "文章管理员启用"),
        (2, "文章管理员不启用")
    )
    article_admin_status = models.SmallIntegerField(choices=article_admin_status_choices, verbose_name="文章管理员状态", default=2)


    popularity = models.IntegerField(verbose_name='人气数(被查看)', default=0)
    praise = models.IntegerField(verbose_name='被赞数', default=0)
    forward = models.IntegerField(verbose_name='转发数', default=0)
    sign = models.TextField(verbose_name='个性签名', null=True)
    sign_num = models.IntegerField(verbose_name='签名被赞个数', default=0)
    voice = models.CharField(verbose_name='语音介绍', null=True, max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    bossleida_data_tongji = models.TextField(verbose_name='BOSS雷达数据统计[个人]',default='{}')

    last_login_date = models.DateTimeField(verbose_name="最后登录时间", null=True)

    def __str__(self):
        return self.username

    class Meta:
        # unique_together = (("userid", "company"),)
        verbose_name_plural = "用户表"
        app_label = "zhugeleida"


# 用户(咨询)操作雷达日志 / 客户操作日志(咨询复制咨询名字/客户点击咨询对话框 等.....)
class ZgldUserOperLog(models.Model):
    user = models.ForeignKey('zgld_userprofile', verbose_name="咨询用户")

    oper_type_choices = (
        (1, "复制名字"),
        (2, "客户点击咨询对话框"),
        (3, "查看文章视频时长"),
        (4, "文章阅读时长"),
    )
    oper_type = models.SmallIntegerField(verbose_name="操作类型", choices=oper_type_choices)

    article = models.ForeignKey(to='zgld_article', verbose_name='归属哪篇文章', null=True, blank=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='客户ID', null=True, blank=True)

    # --------------------------客户点击对话框参数------------------
    # click_dialog_num = models.IntegerField(verbose_name='点击对话框次数', default=0)

    # -------------------------查看文章视频时长参数-------------------
    video_time = models.IntegerField(verbose_name='查看视频时长', default=0)

    # -------------------------文章阅读时长记录----------------------
    reading_time = models.IntegerField(verbose_name='阅读文章时长', default=0)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    timestamp = models.CharField(verbose_name='时间戳', max_length=128, null=True, blank=True) # 视频查看时长 同一篇文章 同一个查看人 同一个转发人 第二次查看时间戳不同

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
    tag_type_choices = (
        (1, '微信公众号'),
        (2, '微信小程序'),
    )
    tag_type = models.SmallIntegerField(verbose_name='标签类型', choices=tag_type_choices,null=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return 'tag: %s ' % (self.name)

    class Meta:
        verbose_name_plural = "标签管理"
        app_label = "zhugeleida"


# 小程序-客户管理
class zgld_customer(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属公司',null=True)
    username = models.CharField(verbose_name='客户姓名', max_length=128, null=True)
    memo_name = models.CharField(max_length=128, verbose_name='备注名', blank=True, null=True)
    openid = models.CharField(verbose_name='OpenID(用户唯一标识)', max_length=128)
    session_key =  models.CharField(verbose_name='会话密钥', max_length=128,null=True)
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
        (3, '雷达管家-消息推送'),
    )
    user_type = models.SmallIntegerField(u'客户访问类型', choices=user_type_choices)
    nickname = models.CharField(max_length=64, verbose_name='昵称', blank=True, null=True)
    phone = models.CharField(verbose_name='手机号', max_length=20, blank=True, null=True)
    country = models.CharField(max_length=64, verbose_name='国家', blank=True, null=True)
    city = models.CharField(max_length=32, verbose_name='客户所在城市', blank=True, null=True)
    province = models.CharField(max_length=32, verbose_name='所在省份', blank=True, null=True)
    language = models.CharField(max_length=32, verbose_name='语言', blank=True, null=True)
    formatted_address = models.CharField(verbose_name='具体位置', max_length=2048, null=True)

    subscribe_choices = (
        (0, '取消订阅该公众号'),
        (1, '已经订阅该公众号')
    )
    is_subscribe =  models.SmallIntegerField(verbose_name='用户是否订阅该公众号', choices=subscribe_choices,null=True)                                                                   #值为0时，代表此用户没有关注该公众号

    receive_redPacket_choices = (
        (0, '没有发送过关注红包'),
        (1, '发送了关注红包')
    )
    is_receive_redPacket =  models.SmallIntegerField(verbose_name='是否发送过关注红包', choices=receive_redPacket_choices,default=0)
    redPacket_money = models.FloatField(verbose_name='发红包金额', default=0)
    history_tags_record = models.TextField('历史标签记录',null=True,default='[]')
    history_browse_record = models.TextField('历史浏览记录',default='[]')

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
        (4, '公众号文章')
    )
    source = models.SmallIntegerField(u'客户来源', choices=source_type_choices)
    qr_code = models.CharField(verbose_name='用户-客户-对应二维码', max_length=128, null=True)
    poster_url = models.CharField(verbose_name='海报名片链接', max_length=128, null=True)
    customer_parent = models.ForeignKey('zgld_customer', verbose_name='客户所属父级',related_name="customer_parent" ,null=True, blank=True)
    expected_time = models.DateField(verbose_name='预计成交时间', blank=True, null=True)
    expedted_pr = models.IntegerField(verbose_name='预计成交概率', default=0, null=True)

    last_follow_time = models.DateTimeField(verbose_name='最后跟进时间', null=True)  # 指的是 用户最后发留言时间和用户跟进用语的写入。
    last_activity_time = models.DateTimeField(verbose_name='最后活动时间', null=True)

    is_customer_msg_num = models.IntegerField(default=0, verbose_name='是否是客户发的新消息个数')
    # is_customer_product_num = models.IntegerField(default=0, verbose_name='是否是客户咨询产品的消息个数')
    is_user_msg_num = models.IntegerField(default=0, verbose_name='是否是用户发的新消息个数')

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "客户所属用户关系|跟进信息绑定表"
        app_label = "zhugeleida"


# 跟进-消息详情表
class zgld_follow_info(models.Model):
    user_customer_flowup = models.ForeignKey('zgld_user_customer_belonger', verbose_name='跟进客户|用户绑定',null=True)
    follow_info = models.CharField(verbose_name='跟进发送信息', max_length=256, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "跟进-消息详情表"
        app_label = "zhugeleida"


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
        (16,'转发文章到朋友圈'),
        (17,'报名活动'),
        (18,'下单成功'),
        (19, '点赞文章'),  # 取消了对您的靠谱
        (20, '取消订单'),  # 取消了对您的靠谱

        (21, '查看日记首页'),  # 记录查看日记首页
        (22, '查看日记详情'),  # 记录查看日记列表页
        (23, '发送小程序'),  # 点击发送小程序

    )

    action = models.SmallIntegerField(verbose_name="访问的功能动作", choices=action_choices)
    user = models.ForeignKey('zgld_userprofile', verbose_name=' 被访问的用户',null=True)
    article = models.ForeignKey('zgld_article', verbose_name='文章',null=True)

    customer = models.ForeignKey('zgld_customer', verbose_name='访问的客户',null=True)
    remark = models.TextField(verbose_name='备注', help_text='访问信息备注')
    # activity_time = models.ForeignKey('zgld_user_customer_flowup', related_name='accesslog', verbose_name='活动时间(客户活动)',null=True)  # 代表客户活动日志最后一条记录的时间
    is_new_msg = models.BooleanField(default=True, verbose_name='是否为新日志')
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "访问动能日志记录表"
        app_label = "zhugeleida"


# 聊天室记录表
class zgld_chatinfo(models.Model):
    send_type_choice = ((1, 'user_to_customer'), # 雷达用户发送给小程序客户|公众号客户
                        (2, 'customer_to_user'),  #小程序客户|公众号客户发送给雷达用户
                        (3, 'chat_help_tips_info'), # 聊天的温馨提示信息
                        (4, 'store_temp_media')     # 存储临时素素材
                        )
    send_type = models.SmallIntegerField(choices=send_type_choice, verbose_name='发送类型', blank=True, null=True)
    is_customer_new_msg = models.BooleanField(default=True, verbose_name='是否为客户的新消息')
    is_user_new_msg = models.BooleanField(default=True, verbose_name='是否为用户的新消息')
    is_last_msg = models.BooleanField(default=True, verbose_name='是否为最后一次的消息')
    userprofile = models.ForeignKey('zgld_userprofile', verbose_name='用户', null=True, blank=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='客户', null=True, blank=True)
    msg = models.TextField(verbose_name='微信消息唯一ID', null=True, blank=True)
    content = models.TextField(verbose_name='消息', null=True, blank=True)
    article = models.ForeignKey(to='zgld_article', verbose_name='归属哪篇文章', null=True, blank=True)  # 如果该字段有值 为文章咨询
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "聊天室记录表"
        app_label = "zhugeleida"


#公众号-模板文章详细表
class  zgld_template_article(models.Model):

    user = models.ForeignKey('zgld_admin_userprofile', verbose_name='模板文章作者', null=True)
    company = models.ForeignKey('zgld_company', verbose_name='文章所属公司', null=True)

    source_choices = ((1, '同步[公众号文章]到模板库'),
                      (2, '同步[本地文章库]到模板库'),
                      )
    source = models.SmallIntegerField(default=1, verbose_name='文章来源', choices=source_choices)

    status_choices = (
                        (0, '未同步到[正式文章库]'),
                        (1, '已同步到[正式文章库]'),
                      )
    status = models.SmallIntegerField(default=0, verbose_name='文章状态', choices=status_choices)

    media_id = models.CharField(verbose_name="素材ID", max_length=128, null=True)
    source_url = models.CharField(verbose_name="公众号文章原生URL", max_length=256, null=True)

    title = models.CharField(verbose_name='文章标题', max_length=128)
    cover_picture = models.CharField(verbose_name="封面图片URL", max_length=128)
    summary = models.CharField(verbose_name='文章摘要', max_length=255)
    content = models.TextField(verbose_name='文章内容', null=True)
    update_time =  models.DateTimeField(verbose_name="最后更新时间",null=True)

    author = models.CharField(verbose_name='文章作者', max_length=256,null=True)
    tags = models.ManyToManyField('zgld_template_article_tag',verbose_name="模板文章关联的标签")
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
                       (3,'删除'), # 逻辑删除
                     )
    status = models.SmallIntegerField(default=1, verbose_name='文章状态', choices=status_choices)
    source_choices = ( (1,'原创'),
                       (2,'转载'),
                     )
    source = models.SmallIntegerField(default=1, verbose_name='文章来源', choices=source_choices)
    content = models.TextField(verbose_name='文章内容', null=True)

    tags = models.ManyToManyField('zgld_article_tag', verbose_name="文章关联的标签")
    up_count = models.IntegerField(default=0,verbose_name="赞次数")
    # down_count = models.IntegerField(default=0,verbose_name="踩次数")
    cover_picture  = models.CharField(verbose_name="封面图片URL",max_length=128)
    read_count = models.IntegerField(verbose_name="文章阅读数量",default=0)
    forward_count = models.IntegerField(verbose_name="文章转发个数",default=0)
    comment_count = models.IntegerField(default=0,verbose_name="被评论数量")

    insert_ads = models.TextField(verbose_name='插入广告语',null=True)
    plugin_report = models.ForeignKey('zgld_plugin_report', verbose_name="报名的插件", null=True)
    qrcode_url = models.CharField(verbose_name="二维码URL", max_length=128, null=True)
    media_id = models.CharField(verbose_name="素材ID", max_length=128, null=True)
    source_url = models.CharField(verbose_name="公众号文章原生URL", max_length=256, null=True)

    auto_tagging_choices = ( (0,'不开启'),
                             (1,'开启'),
                           )
    is_auto_tagging = models.SmallIntegerField(default=1, verbose_name='是否开启自动打标签', choices=auto_tagging_choices)

    tags_time_count = models.IntegerField(default=0, verbose_name="达到几秒实现打标签")

    create_date = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)


    class Meta:
        verbose_name_plural = "文章表"
        app_label = "zhugeleida"


# 文章被赞
class zgld_article_action(models.Model):
    article = models.ForeignKey('zgld_article', verbose_name='被赞的文章',null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='赞或踩的客户')
    user = models.ForeignKey('zgld_userprofile', verbose_name='企业用户', null=True)
    status_choices = ((0, '未点赞'),
                      (1, '已点赞')
                      )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices,null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:

        verbose_name_plural = "客户-文章-行为记录表"
        app_label = "zhugeleida"

##文章评论表
class zgld_article_comment(models.Model):
    # company = models.ForeignKey('zgld_company', verbose_name='所属公司', null=True)
    article = models.ForeignKey('zgld_article', verbose_name="关联的日记", null=True)
    from_customer = models.ForeignKey('zgld_customer', verbose_name="评论的客户", related_name='FromCustomer',null=True) ## 关联的客户
    to_customer = models.ForeignKey('zgld_customer', verbose_name="回复的客户", related_name='ToCustomer', null=True) ## 关联的客户
    content = models.TextField(verbose_name="评论内容", null=True)
    is_audit_pass_choices = (
        (0, '未进行审核'),
        (1, '审核通过'),
    )
    is_audit_pass = models.SmallIntegerField(default=0, verbose_name='是否通过审核', choices=is_audit_pass_choices)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "日记评论表"
        app_label = "zhugeleida"


# 公众号-文章-活动(任务)管理表
class zgld_article_activity(models.Model):
    article = models.ForeignKey('zgld_article',verbose_name='文章')
    company = models.ForeignKey('zgld_company', verbose_name='所属企业',null=True)
    # shanghu_name = models.CharField(verbose_name='商户名称', max_length=128,null=True)
    activity_name = models.CharField(verbose_name='活动名称', max_length=256,null=True)
    # wish_language = models.CharField(verbose_name='祝福语', max_length=256,null=True)
    status_choices = ((1, '未启用'),
                      (2, '进行中'),
                      (3, '已暂停'),
                      (4, '已结束')
                      )
    status = models.SmallIntegerField(default=2, verbose_name='活动状态', choices=status_choices)
    activity_rules = models.CharField(verbose_name='活动规则', max_length=2048,null=True)

    mode_choices =  ( (1, '随机红包'),
                      (2, '固定红包')
                      )
    mode = models.SmallIntegerField(default=1, verbose_name='红包发送方式', choices=mode_choices)


    activity_total_money= models.SmallIntegerField(verbose_name='活动总金额', default=0,null=True)
    redPacket_num = models.SmallIntegerField(verbose_name='红包个数(个)',null=True,default=0)
    activity_single_money= models.FloatField(verbose_name='单个金额(元)',default=0,null=True)
    max_single_money = models.FloatField(verbose_name='随机最大单个金额(元)',default=0,null=True)
    min_single_money = models.FloatField(verbose_name='随机最小单个金额(元)',default=0,null=True)

    is_limit_area = models.BooleanField(verbose_name='是否地区限制', default=False)  # 默认不限制
    limit_area = models.TextField(verbose_name='限制的区域', null=True,default="[]")

    reach_stay_time = models.SmallIntegerField(verbose_name='达到多少秒发红包', default=0) # 0 代表 没有限制
    reach_forward_num = models.SmallIntegerField(verbose_name='达到多少次发红包(转发阅读后次数))',null=True)
    already_send_redPacket_num = models.SmallIntegerField(verbose_name='已发放红包数量[总共]', default=0)
    already_send_redPacket_money = models.FloatField(verbose_name='已发红包金额', default=0)


    start_time = models.DateTimeField(verbose_name='活动开始时间', null=True)
    end_time   =   models.DateTimeField(verbose_name='活动结束时间', null=True)
    reason = models.CharField(verbose_name='返回的发红包错误信息', max_length=512, null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True,null=True)

    class Meta:

        verbose_name_plural = "文章活动表"
        app_label = "zhugeleida"


# 公众号-活动发红包记录表
class zgld_activity_redPacket(models.Model):
    article = models.ForeignKey('zgld_article', verbose_name='文章',null=True)
    activity =  models.ForeignKey('zgld_article_activity', verbose_name='文章活动',null=True)
    company = models.ForeignKey('zgld_company',verbose_name='文章所属公司',null=True)


    status_choices = ( (1,'已发(发送成功)'),
                       (2,'未发'),
                       (3,'已发(发送失败)'),
                       (4,'补发)'),
                     )
    status = models.SmallIntegerField(verbose_name='[红包]发放状态',default=2,choices=status_choices,null=True)

    # user = models.ForeignKey('zgld_userprofile', verbose_name="文章所属企业用户ID", null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name="查看文章的客户", null=True)
    customer_parent = models.ForeignKey('zgld_customer', verbose_name='客户所属的父级',related_name="activity_customer_parent", null=True)

    forward_read_count = models.IntegerField(verbose_name="转发后阅读人数", default=0)
    forward_stay_time = models.IntegerField(verbose_name='转发后阅读的时长', default=0)

    send_log = models.TextField(verbose_name='红包发放日志记录', null=True,default="[]")
    access_log = models.TextField(verbose_name='客户红包访问日志', null=True,default="[]")
    already_send_redPacket_money = models.FloatField(verbose_name='已发红包金额',default=0, null=True)
    already_send_redPacket_num = models.SmallIntegerField(verbose_name='已经发放次数(实发)[个人]',default=0 ,null=True)
    should_send_redPacket_num = models.SmallIntegerField(verbose_name='应该发放的次数(应发)',default=0 ,null=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        unique_together = [
            ('article','customer','activity')
        ]
        verbose_name_plural = "活动发红包记录表"
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
    customer = models.ForeignKey('zgld_customer', verbose_name="查看文章的客户", null=True)
    customer_parent = models.ForeignKey('zgld_customer', verbose_name='查看文章的客户所属的父级',related_name="article_customer_parent", null=True)

    level = models.IntegerField(verbose_name='客户所在层级',null=True)
    stay_time = models.IntegerField(verbose_name='停留时长',default=0)
    read_count = models.IntegerField(verbose_name="被阅读数量",default=0)
    forward_count = models.IntegerField(verbose_name="被转发个数",default=0)
    forward_friend_count = models.IntegerField(verbose_name="转发给朋友的个数", default=0)
    forward_friend_circle_count = models.IntegerField(verbose_name="转发给朋友圈的个数", default=0)
    is_have_child =  models.BooleanField(verbose_name='这个客户是否有子级',default=False)
    last_access_date = models.DateTimeField(verbose_name="最后访问时间", null=True)

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
    # customer = models.ForeignKey('zgld_customer', verbose_name="报名的客户", null=True)
    user = models.ForeignKey('zgld_userprofile', verbose_name='文章所属用户', null=True)
    activity = models.ForeignKey('zgld_plugin_report', verbose_name="报名的活动", null=True)
    customer_name = models.CharField(verbose_name="报名的客户", null=True,max_length=64)
    phone = models.CharField(verbose_name='手机号', max_length=20, blank=True, null=True)
    leave_message = models.TextField(verbose_name="客户留言", null=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


    class Meta:

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
    userProfile = models.ForeignKey(to='zgld_admin_userprofile', verbose_name='用户名称', null=True, blank=True)


# 小程序 - 商城基础设置
class zgld_shangcheng_jichushezhi(models.Model):
    shangChengName = models.CharField(verbose_name='商城名称', max_length=32, default='商城')
    # userProfile = models.ForeignKey(to='zgld_customer', verbose_name='用户名称', null=True, blank=True)
    shangHuHao = models.CharField(verbose_name='商户号', max_length=128, null=True, blank=True)
    shangHuMiYao = models.CharField(verbose_name='商户秘钥', max_length=128, null=True, blank=True)

    position_choices = (
        (1, '横向展示分类'),
        (2, '纵向展示分类')
    )
    classify_position = models.SmallIntegerField(verbose_name='商品分类展示位置', choices=position_choices, default=1)

    lunbotu = models.TextField(verbose_name='轮播图', null=True, blank=True)
    yongjin = models.CharField(verbose_name='佣金', max_length=64, null=True, blank=True)
    xiaochengxuApp = models.ForeignKey(to='zgld_xiaochengxu_app', verbose_name='小程序APP', null=True, blank=True)
    xiaochengxucompany = models.ForeignKey(to='zgld_company', verbose_name='公司名称', null=True, blank=True)
    zhengshu = models.TextField(verbose_name='证书', null=True, blank=True)
    createDate = models.DateTimeField(verbose_name="创建时间", null=True, blank=True)


# 小程序 - 商品分类管理
class zgld_goods_classification_management(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    classificationName = models.CharField(verbose_name='分类名称', max_length=128)
    # goodsNum = models.IntegerField(verbose_name='商品数量', default=0)
    parentClassification = models.ForeignKey(to='self', verbose_name='父级分类', null=True, blank=True)
    createDate = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # mallSetting = models.ForeignKey(to='zgld_shangcheng_jichushezhi', verbose_name='商城', null=True, blank=True)
    level = models.IntegerField(verbose_name='分类等级', default=1)


# 小程序 - 商品管理
class zgld_goods_management(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属企业')
    goodsName = models.CharField(verbose_name='商品名称', max_length=128)
    parentName = models.ForeignKey(to='zgld_goods_classification_management', verbose_name='归属分类', null=True, blank=True)

    goodsPrice = models.FloatField(verbose_name='商品单价',max_length=64, default=0)
    salesNum = models.IntegerField(verbose_name='销量', default=0)
    # inventoryNum = models.IntegerField(verbose_name='库存', default=0)
    commissionFee = models.IntegerField(verbose_name='佣金提成', default=0)
    recommend_index = models.SmallIntegerField(verbose_name='产品排序优先级', default=0)  # 从0 - 10 ,0 代表不推荐。
    status_choices = (
        (1, '已上架'),
        (2, '未上架'),
        (3, '已售罄'),
        (4, '下架')
    )
    goodsStatus = models.SmallIntegerField(verbose_name='商品状态', choices=status_choices, default=1)
    shelvesCreateDate = models.DateTimeField(verbose_name="上架时间", null=True, blank=True)
    xianshangjiaoyi = models.BooleanField(verbose_name='是否线上交易', default=False)
    shichangjiage = models.IntegerField(verbose_name='市场价格', default=0)
    # kucunbianhao = models.CharField(verbose_name='库存编号', max_length=128, default='')
    zhengshu = models.CharField(verbose_name='证书', max_length=256, null=True, blank=True)
    topLunBoTu = models.TextField(verbose_name='顶部轮播图', null=True, blank=True)
    detailePicture = models.TextField(verbose_name='详情图片', null=True, blank=True)
    content = models.TextField(verbose_name='内容', null=True)
    DetailsDescription = models.TextField(verbose_name='详情描述', null=True, blank=True)

    createDate = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小程序 - 订单管理
class zgld_shangcheng_dingdan_guanli(models.Model):
    shangpinguanli = models.ForeignKey(to='zgld_goods_management', verbose_name='商品管理', null=True, blank=True)
    goods_id = models.IntegerField(verbose_name='商品ID', null=True, blank=True)

    phone = models.CharField(verbose_name='手机号码', max_length=32, null=True, blank=True)
    orderNumber = models.CharField(verbose_name='订单号', max_length=128, null=True, blank=True)
    goodsPrice = models.FloatField(verbose_name='商品单价', max_length=64, default=0)
    topLunBoTu = models.TextField(verbose_name='顶部轮播图', null=True, blank=True)
    detailePicture = models.TextField(verbose_name='详情图片', null=True, blank=True)
    goodsName = models.CharField(verbose_name='商品名字', max_length=64, null=True, blank=True)
    unitRiceNum = models.IntegerField(verbose_name='数量', default=0)
    yingFuKuan = models.FloatField(verbose_name='应付款', default=0)
    youHui = models.IntegerField(verbose_name='优惠', default=0)
    yewuUser = models.ForeignKey(to='zgld_userprofile', verbose_name='业务员', null=True, blank=True)
    gongsimingcheng = models.ForeignKey(to='zgld_company', verbose_name='公司名称', null=True, blank=True)
    yongJin = models.IntegerField(verbose_name='佣金', default=0)
    # peiSong = models.CharField(verbose_name='配送', max_length=64, null=True, blank=True)
    shouHuoRen = models.ForeignKey(to='zgld_customer', verbose_name='收货人', max_length=128, null=True, blank=True)
    logicDelete = models.IntegerField(verbose_name='逻辑删除', default=0)
    order_status = (
        (1, '待付款'),
        (8, '交易成功'),
        (9, '交易失败'),
        (10, '取消订单'),   #手动或者自动十分钟内的取消订单

        (2, '退款完成'),
        (3, '退款失败'),
        (4, '退款中'),
        (5, '拒绝退款'),
    )
    theOrderStatus = models.SmallIntegerField(verbose_name='订单状态', choices=order_status, default=1)
    createDate = models.DateTimeField(verbose_name="创建时间", null=True, blank=True)
    stopDateTime = models.DateTimeField(verbose_name="完成时间", null=True, blank=True)


# 退款单管理
class zgld_shangcheng_tuikuan_dingdan_management(models.Model):
    orderNumber = models.ForeignKey(to='zgld_shangcheng_dingdan_guanli', verbose_name='订单号', null=True, blank=True)
    tuikuanyuanyin_status = (
        (1, '不想买了'),
        (2, '信息填错,重新下单'),
        (3, '见面交易'),
        (4, '其他原因'),
    )
    tuiKuanYuanYin = models.SmallIntegerField(verbose_name='退款原因', choices=tuikuanyuanyin_status, default=4)
    # tuiKuanJin_e = models.CharField(verbose_name='退款金额', max_length=64, null=True, blank=True)
    shengChengDateTime = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)
    tuiKuanDateTime = models.DateTimeField(verbose_name='退款时间', null=True, blank=True)
    tuikuandanhao = models.CharField(verbose_name='退款单号', max_length=128, null=True, blank=True)
    logicDelete = models.IntegerField(verbose_name='逻辑删除', default=0)
    remark = models.TextField(verbose_name='备注', null=True)


# 发放红包消费记录表
class zgld_red_envelope_to_issue(models.Model):
    wxappid = models.CharField(verbose_name='公众号appid', max_length=32, null=True, blank=True)
    mch_id = models.CharField(verbose_name='商户号', max_length=32, null=True, blank=True)
    re_openid = models.CharField(verbose_name='用户标识openid', max_length=32, null=True, blank=True)
    total_amount = models.CharField(verbose_name='付款金额', max_length=32, null=True, blank=True)     # 1:100
    mch_billno = models.CharField(verbose_name='商户订单号', max_length=28, null=True, blank=True)
    client_ip = models.CharField(verbose_name='用户IP', max_length=16, null=True, blank=True)
    send_name = models.CharField(verbose_name='(商户/红包发送者)名称', max_length=32, null=True, blank=True)
    act_name = models.CharField(verbose_name='活动名称', max_length=32, null=True, blank=True)
    remark = models.TextField(verbose_name='备注', null=True, blank=True)
    wishing = models.TextField(verbose_name='红包祝福语', max_length=128, null=True, blank=True)
    createDate = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    issuing_status = (
        (1, '发放完成'),
        (2, '发放失败'),
        (3, '发放中')
    )
    issuingState = models.SmallIntegerField(verbose_name='发放状态', choices=issuing_status, default=3)

    # endTheActivity = models.DateTimeField(verbose_name='活动结束时间', null=True, blank=True)
    articleId = models.IntegerField(verbose_name='文章ID', null=True, blank=True)


#帮助文档
class zgld_help_doc(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name='文章作者', null=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    content = models.TextField(verbose_name='文章内容', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)

    class Meta:
        verbose_name_plural = "帮助文档表"
        app_label = "zhugeleida"


# 资金流水记录表
class zgld_money_record(models.Model):
    company = models.ForeignKey('zgld_company',verbose_name='所属公司',null=True)

    source_choices = ( (1,'平台账号'),
                       (2,'公众号'),
                       (3,'小程序'),
                     )
    source = models.SmallIntegerField(verbose_name='来源',choices=source_choices,null=True)

    admin_user = models.ForeignKey('zgld_admin_userprofile', verbose_name='后台管理员', null=True)

    user = models.ForeignKey('zgld_userprofile', verbose_name='雷达企业用户', null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name="交易客户", null=True) ## 关联的客户(小程序\公众号)
    transaction_amount = models.FloatField(verbose_name='交易金额(元)', null=True)
    account_balance =   models.FloatField(verbose_name='余额(元)', null=True)

    type_choices = (   (1,'充值成功'),
                       (2,'提现成功'),
                       (3,'红包发放(关注公众号)'),
                       (4,'红包发放(文章裂变)'),
                       (5,'商城入账'),
                       (6,'商城退款')
                     )
    type = models.SmallIntegerField(verbose_name='交易类型',choices=type_choices, null=True)
    record_log = models.TextField(verbose_name='日志记录备注', null=True)
    create_date = models.DateTimeField(verbose_name="记账时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "资金记录表"
        app_label = "zhugeleida"


# ============================================日记================================================

#公众号-案例标签表
class zgld_case_tag(models.Model):
    company = models.ForeignKey('zgld_company', verbose_name='所属企业', null=True)
    name = models.CharField(verbose_name='标签名称', max_length=32)
    search_amount  = models.IntegerField(verbose_name="搜索数量", default=0)
    # parent_id = models.ForeignKey('self',verbose_name="父级ID",null=True)

    class Meta:
        verbose_name_plural = "案例标签表"
        app_label = "zhugeleida"


# 日记 列表页 (原 案例)
class zgld_case(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name='文章作者', null=True)
    company = models.ForeignKey('zgld_company', verbose_name='文章所属公司', null=True)
    customer_name  = models.CharField(max_length=64,verbose_name='客户昵称', null=True)
    headimgurl = models.CharField(verbose_name="客户头像url", max_length=256, default='statics/imgs/Avator.jpg')

    case_name = models.CharField(verbose_name='案例名称', max_length=128)
    cover_picture = models.TextField(verbose_name="封面图片",null=True)
    poster_cover = models.TextField(verbose_name="海报图片",null=True)
    become_beautiful_cover = models.TextField(verbose_name="变美过程图片",null=True)

    tags = models.ManyToManyField('zgld_case_tag', verbose_name="文章关联的标签")
    status_choices = (
        (1, '已发'),
        (2, '未发'),
        (3, '删除'),  # 逻辑删除
    )
    status = models.SmallIntegerField(default=2, verbose_name='案例状态', choices=status_choices)

    read_count = models.IntegerField(verbose_name="阅读数量", default=0)
    up_count = models.IntegerField(default=0, verbose_name="点赞次数")
    comment_count = models.IntegerField(default=0, verbose_name="被评论数量")

    case_type_choices = ((1, '普通案例'),
                         (2, '时间轴案例')
                        )
    case_type = models.SmallIntegerField(default=2, verbose_name='案例类型', choices=case_type_choices)

    update_date = models.DateTimeField(verbose_name="日记最后修改时间",null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "案例表"
        app_label = "zhugeleida"


# 日记 详情页  (原 案例)
class zgld_diary(models.Model):
    user = models.ForeignKey('zgld_admin_userprofile', verbose_name='文章作者', null=True)
    case = models.ForeignKey('zgld_case', verbose_name="关联的案例", null=True)
    company = models.ForeignKey('zgld_company',verbose_name='文章所属公司',null=True)

    title = models.CharField(verbose_name='日记标题', max_length=128)
    summary = models.CharField(verbose_name='日记摘要', max_length=255,null=True)

    diary_date = models.DateTimeField(verbose_name="日记时间")
    cover_picture = models.TextField(verbose_name="封面图URL和视频URL",null=True) # 普通案例 上传轮播图/时间轴案例取变美图片
    content = models.TextField(verbose_name='日记内容', null=True)

    read_count = models.IntegerField(verbose_name="阅读数量", default=0)
    up_count = models.IntegerField(default=0,verbose_name="点赞次数")
    comment_count = models.IntegerField(default=0,verbose_name="被评论数量")

    status_choices = ( (1,'已发'),
                       (2,'未发'),
                       (3,'删除'), # 逻辑删除
                     )
    status = models.SmallIntegerField(default=2, verbose_name='日记状态', choices=status_choices)

    cover_show_type_choices = ( (1,'只展示图片'),
                                (2,'只展示视频')
                               )
    poster_cover = models.TextField(verbose_name="海报图片", null=True)
    cover_show_type = models.SmallIntegerField(default=2, verbose_name='封面展示类型', choices=cover_show_type_choices)
    create_date = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)

    class Meta:
        verbose_name_plural = "案例日记表"
        app_label = "zhugeleida"


##日记评论表
class zgld_diary_comment(models.Model):
    # company = models.ForeignKey('zgld_company', verbose_name='所属公司', null=True)
    diary = models.ForeignKey('zgld_diary', verbose_name="关联的日记", null=True)
    from_customer = models.ForeignKey('zgld_customer', verbose_name="评论的客户", related_name='from_customer',null=True) ## 关联的客户
    to_customer = models.ForeignKey('zgld_customer', verbose_name="回复的客户", related_name='to_customer', null=True) ## 关联的客户
    is_audit_pass_choices = ( (0, '未进行审核'),
                              (1, '审核通过'),
                            )
    is_audit_pass = models.SmallIntegerField(default=0, verbose_name='是否通过审核', choices=is_audit_pass_choices)

    content = models.TextField(verbose_name="评论内容", null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "日记评论表"
        app_label = "zhugeleida"


# 日记被赞 或者收藏日记
class zgld_diary_action(models.Model):
    diary = models.ForeignKey('zgld_diary', verbose_name='被赞的日记',null=True)
    case = models.ForeignKey('zgld_case', verbose_name="关联的案例", null=True)
    customer = models.ForeignKey('zgld_customer', verbose_name='赞或踩的客户')
    action_choices = ((1, '点赞日记'),
                      (2, '收藏案例'),
                      (3, '浏览案例'),
                      (4, '点赞案例')
                      )
    action = models.SmallIntegerField(verbose_name='客户动作', choices=action_choices,null=True)

    status_choices = ((0, '未点赞|未收藏'),
                      (1, '已点赞|已收藏')
                      )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices,null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:

        verbose_name_plural = "客户-日记行为记录表"
        app_label = "zhugeleida"

# 搜索历史标签
class zgld_search_history(models.Model):
    user_customer_belonger = models.ForeignKey('zgld_user_customer_belonger', verbose_name='用户|客户关系表')
    history_tag = models.CharField(verbose_name='搜索历史', max_length=64)
    company = models.ForeignKey('zgld_company', verbose_name='日记所属公司', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 客户所属用户-关系绑定表
class zgld_customer_case_poster_belonger(models.Model):

    case = models.ForeignKey('zgld_case', verbose_name="关联的案例", null=True)
    user_customer_belonger = models.ForeignKey('zgld_user_customer_belonger', verbose_name='用户|客户关系表', null=True)

    qr_code = models.CharField(verbose_name='用户-客户-对应二维码', max_length=128, null=True)
    poster_url = models.CharField(verbose_name='用户-客户-对应的二维码', max_length=128, null=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "雷达用户|客户-生成海报关系表"
        app_label = "zhugeleida"

# ================================================================================================================