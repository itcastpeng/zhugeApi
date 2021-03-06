from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加用户信息
class UserAddForm(forms.Form):
    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )
    password = forms.CharField(
        required=True,
        error_messages={
            'required': "密码不能为空"
        }
    )
    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色不能为空'
        })
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司不能为空'
        }
    )

    # 查询用户名判断是否存在
    def clean_username(self):
        username = self.data['username']
        # print(username)
        objs = models.zgld_userprofile.objects.filter(
            username=username,
        )
        if objs:
            self.add_error('username', '用户名已存在')
        else:
            return username

    # 返回加密后的密码
    def clean_password(self):
        return account.str_encrypt(self.data['password'])


# 更新用户信息
class UserUpdateForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户id不能为空"
        }
    )

    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色不能为空'
        }
    )

    # 判断用户名是否存在
    def clean_username(self):
        username = self.data['username']
        user_id = self.data['user_id']
        print(username)
        objs = models.zgld_userprofile.objects.filter(
            username=username,
        ).exclude(id=user_id)
        if objs:
            self.add_error('username', '用户名已存在')
        else:
            return username


class UserAllForm(forms.Form):

    uid = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "用户id不能为空",
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "客户id不能为空",
        }
    )


class UserSelectForm(forms.Form):

    uid = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "用户id不能为空",
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "客户id不能为空",
        }
    )

    #暂时不用做名片分页
    # current_page = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'invalid': "页码数据类型错误",
    #     }
    # )
    # length = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'invalid': "页显示数量类型错误"
    #     }
    # )
    #
    # def clean_current_page(self):
    #     if 'current_page' not in self.data:
    #         current_page = 1
    #     else:
    #         current_page = int(self.data['current_page'])
    #     return current_page
    #
    # def clean_length(self):
    #     if 'length' not in self.data:
    #         length = 10
    #     else:
    #         length = int(self.data['length'])
    #     return length