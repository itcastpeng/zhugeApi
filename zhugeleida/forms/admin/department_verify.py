from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加部门信息
class DepartmentAddForm(forms.Form):
    # print('添加部门')
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "部门名不能为空"
        }
    )
    parentid_id = forms.CharField(
        required=False,
        error_messages={
            'required': "父级部门ID"
        }
    )

    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.zgld_department.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '部门名已存在')
        else:
            return name


# 更新用户信息
class DepartmentUpdateForm(forms.Form):
    department_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '部门ID不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': '部门名不能为空'
        }
    )


    # 判断部门是否存在
    def clean_name(self):
        department_id = self.data['department_id']
        name = self.data['name']
        objs = models.zgld_department.objects.filter(
            name=name,
        ).exclude(id=department_id)

        if objs:
            self.add_error('name', '部门已存在')
        else:
            return name


# 判断是否是数字
class DepartmentSelectForm(forms.Form):
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