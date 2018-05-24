from django import forms

from zhugeproject import models
from publickFunc import account
import datetime


# 添加角色信息
class AddForm(forms.Form):
    # print('添加角色')
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "角色名不能为空"
        }
    )

    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.ProjectRole.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '角色名已存在')
        else:
            return name


# 更新角色信息
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': 'ID不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': '角色名不能为空'
        }
    )


    # 判断角色是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['name']
        objs = models.ProjectRole.objects.filter(
            name=name,
        ).exclude(id=o_id)
        if objs:
            self.add_error('name', '角色已存在')
        else:
            return name


# 判断是否是数字
class SelectForm(forms.Form):
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
