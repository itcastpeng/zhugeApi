from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加跟进常用语信息
class FollowLanguageAddForm(forms.Form):
    # print('添加标签')
    custom_language = forms.CharField(
        required=True,
        error_messages={
            'required': "自定义用语不能为空"
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages= {
            'invalid': "用户ID不能为空",
        }
    )

    def clean_user_id(self):

        user_id = self.data['user_id']

        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('username', '用户名不存在')
        else:
            return user_id



    # 查询自定义常用语是否存在。
    def clean_custom_language(self):
        custom_language = self.data['custom_language']
        objs = models.zgld_follow_language.objects.filter(
            custom_language=custom_language,
        )
        if objs:
            self.add_error('name', '自定义常用语已存在')
        else:
            return custom_language

# 分页 - 获取跟进用语
class FollowLanguageSelectForm(forms.Form):

    user_id = forms.IntegerField(
        required=True,
        error_messages= {
            'invalid': "用户ID不能为空",
        }
    )

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
            length = 20
        else:
            length = int(self.data['length'])
        return length

    def clean_user_id(self):

        user_id = self.data['user_id']

        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('username', '用户名不存在')
        else:
            return user_id



# 分页 - 获取跟进信息展示
class FollowInfoSelectForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "用户ID不能为空",
        }
    )
    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )

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
            length = 20
        else:
            length = int(self.data['length'])
        return length

    # def clean_user_id(self):
    #
    #     user_id = self.data['user_id']
    #
    #     objs = models.zgld_userprofile.objects.filter(
    #         id=user_id,
    #     )
    #     if not objs:
    #         self.add_error('username', '用户名不存在')
    #     else:
    #         return user_id

    # 判断客户是否存在
    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        info_obj = models.zgld_customer.objects.filter(id=customer_id)

        if not info_obj:
            self.add_error('customer_id', '客户ID不存在')
        else:
            return customer_id

class FollowInfoAddForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "用户ID不能为空",
        }
    )

    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )

    follow_info = forms.CharField(
        required=True,
        error_messages={
            'required': "跟进信息不能为空"
        }
    )

    def clean_user_id(self):

        user_id = self.data['user_id']

        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('username', '用户名不存在')
        else:
            return user_id

    # 判断客户是否存在
    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        info_obj = models.zgld_customer.objects.filter(id=customer_id)

        if not info_obj:
            self.add_error('customer_id', '客户不存在')
        else:
            return customer_id



