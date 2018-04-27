from django import forms

from wendaku import models
from publickFunc import account
import datetime

# 添加角色信息
class RoleForm(forms.Form):
    # print('添加角色')
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "角色名不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        })

    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.Role.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '角色名已存在')
        else:
            return name




# 更新用户信息
class RoleUpdateForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户id不能为空"
        }
    )
    name = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色名不能为空'
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        })

    # 判断用户名是否存在
    def clean_name(self):
        name = self.data['name']
        user_id = self.data['user_id']
        print(name)
        objs = models.Role.objects.filter(
            name=name,
        ).exclude(id=user_id)
        if objs:
            self.add_error('name', '用户名已存在')
        else:
            return name
