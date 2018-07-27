from django import forms

from zhugeleida import models
from publicFunc import account
import time


# 添加
class AddForm(forms.Form):

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "权限名称不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']

        objs = models.zgld_admin_role.objects.filter(
            name=name
        )
        if objs:
            self.add_error('name', '角色名称已存在')
        else:
            return name


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色id不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "权限名称不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']
        o_id = self.data['o_id']

        objs = models.zgld_admin_role.objects.filter(
            name=name
        ).exclude(id=o_id)
        if objs:
            self.add_error('name', '权限名称已存在')
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

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length
