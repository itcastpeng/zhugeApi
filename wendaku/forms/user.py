from django import forms

from wendaku import models
from publickFunc import account
import datetime

# 添加用户信息
class UserForm(forms.Form):
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
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        })

    # 查询用户名判断是否存在
    def clean_username(self):
        username = self.data['username']
        # print(username)
        objs = models.UserProfile.objects.filter(
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
        objs = models.UserProfile.objects.filter(
            username=username,
        ).exclude(id=user_id)
        if objs:
            self.add_error('username', '用户名已存在')
        else:
            return username
