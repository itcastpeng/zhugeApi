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
        objs = models.zgld_article.objects.filter(
          id = mingpian_id,user_id=user_id
        )

        if not objs:
            self.add_error('mingpian_id', '文章不存在')
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
class ReportUpdateForm(forms.Form):

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
        objs = models.zgld_article.objects.filter(
          id = mingpian_id,user_id=user_id
        )

        if not objs:
            self.add_error('mingpian_id', '文章不存在')
        else:
            return mingpian_id


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


