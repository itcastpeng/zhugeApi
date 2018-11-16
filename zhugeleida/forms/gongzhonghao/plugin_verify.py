from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加名片信息
class MingpianAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "名片名称不能为空"
        }
    )

    avatar = forms.CharField(
        required=True,
        error_messages={
            'required': "头像不能为空"
        }
    )
    username = forms.CharField(
        required=True,
        error_messages={
            'required': "客户姓名不能为空"
        }
    )

    phone = forms.CharField(
        required=True,
        error_messages={
            'required': "手机号不能为空"
        }
    )

    webchat_code = forms.CharField(
        required=True,
        error_messages={
            'required': "微信二维码不能为空"
        }
    )
    position = forms.CharField(
        required=True,
        error_messages={
            'required': "职位不能为空"
        }
    )


    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        user_id = self.data['user_id']

        objs = models.zgld_plugin_mingpian.objects.filter(
            name=name,user_id=user_id
        )
        if objs:
            self.add_error('name', '名片名称已存在')
        else:
            return name


# 更新名片信息
class MingpianUpdateForm(forms.Form):

    mingpain_id = forms.CharField(
        required=True,
        error_messages={
            'required': ' 名片ID不能为空'
        }
    )
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "名片名称不能为空"
        }
    )

    avatar = forms.CharField(
        required=True,
        error_messages={
            'required': "头像不能为空"
        }
    )
    username = forms.CharField(
        required=True,
        error_messages={
            'required': "客户姓名不能为空"
        }
    )

    phone = forms.CharField(
        required=True,
        error_messages={
            'required': "手机号不能为空"
        }
    )

    webchat_code = forms.CharField(
        required=True,
        error_messages={
            'required': "微信二维码不能为空"
        }
    )
    position = forms.CharField(
        required=True,
        error_messages={
            'required': "职位不能为空"
        }
    )

    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        user_id = self.data['user_id']
        mingpain_id = self.data['mingpain_id']
        objs = models.zgld_plugin_mingpian.objects.filter(
            name=name, user_id=user_id
        ).exclude(id=mingpain_id)

        if objs:
            self.add_error('name', '名片名称已存在')
        else:
            return name

    #判断公司名称是否存在
    def clean_mingpian_id(self):
        mingpian_id = self.data['mingpian_id']
        user_id = self.data['user_id']
        objs = models.zgld_plugin_mingpian.objects.filter(
          id = mingpian_id,user_id=user_id
        )

        if not objs:
            self.add_error('mingpian_id', '名片不存在')
        else:
            return mingpian_id


# 判断是否是数字
class MingpianSelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )



    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page


    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length




# 添加名片信息
class ReportAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    ad_slogan = forms.CharField(
        required=True,
        error_messages={
            'required': " 广告语不能为空"
        }
    )
    sign_up_button = forms.CharField(
        required=True,
        error_messages={
            'required': "报名按钮不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "活动标题不能为空"
        }
    )
    introduce = forms.CharField(
        required=True,
        error_messages={
            'required': "活动说明不能为空"
        }
    )

    skip_link = forms.CharField(
        required= False,

    )


    # 查询用户名判断是否存在
    def clean_title(self):
        title = self.data['title']
        user_id = self.data['user_id']

        objs = models.zgld_plugin_report.objects.filter(
            title=title,user_id=user_id
        )
        if objs:
            self.add_error('title', '名片名称已存在')
        else:
            return title


# 更新名片信息
class ReportUpdateForm(forms.Form):

    id = forms.CharField(
        required=True,
        error_messages={
            'required': 'ID不能为空'
        }
    )
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )


    ad_slogan = forms.CharField(
        required=True,
        error_messages={
            'required': " 广告语不能为空"
        }
    )
    sign_up_button = forms.CharField(
        required=True,
        error_messages={
            'required': "报名按钮不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "活动标题不能为空"
        }
    )
    introduce = forms.CharField(
        required=True,
        error_messages={
            'required': "活动说明不能为空"
        }
    )

    skip_link = forms.CharField(
        required=False,

    )

    # 查询用户名判断是否存在
    def clean_title(self):
        title = self.data['title']
        user_id = self.data['user_id']
        id = self.data['id']
        objs = models.zgld_plugin_report.objects.filter(
            title=title, user_id=user_id
        ).exclude(id=id)

        if objs:
            self.add_error('title', '报名活动名称已存在')
        else:
            return title

    #判断公司名称是否存在
    def clean_id(self):
        id = self.data['id']
        user_id = self.data['user_id']
        objs = models.zgld_plugin_report.objects.filter(
          id = id,user_id=user_id
        )

        if not objs:
            self.add_error('id', '报名活动不存在')
        else:
            return id


# 判断是否是数字
class ReportSelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length


# 添加名片信息
class ReportSignUpAddForm(forms.Form):
    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '客户ID不存在'
        }
    )

    activity_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': " 活动不能为空"
        }
    )
    customer_name = forms.CharField(
        required=True,
        error_messages={
            'required': "客户姓名不能为空"
        }
    )

    phone = forms.CharField(
        required=True,
        error_messages={
            'required': "客户报名手机号不能为空"
        }
    )
    phone_verify_code = forms.CharField(
        required=False,
        error_messages={
            'required': "手机号发送的验证码"
        }
    )

    leave_message = forms.CharField(
        required=False,
        error_messages={
            'required': "留言"
        }
    )


    # 查询用户名判断是否存在
    def clean_activity_id(self):
        activity_id = self.data['activity_id']
        # user_id = self.data['user_id']

        objs = models.zgld_plugin_report.objects.filter(
            id=activity_id
        )
        if  not objs:
            self.add_error('activity_id', '报名活动不存在')
        else:
            return activity_id

    # 查询用户名判断是否存在
    def clean_phone(self):
        phone = self.data['phone']
        activity_id = self.data['activity_id']

        objs = models.zgld_report_to_customer.objects.filter(
            activity_id=activity_id,
            phone =  phone
        )
        if  objs.count() >= 1:
            self.add_error('phone', '手机号已存在')
        else:
            return phone