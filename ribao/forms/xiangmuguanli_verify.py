from django import forms

from wendaku import models
from publicFunc import account
import datetime


# 添加项目信息
class AddForm(forms.Form):
    # print('添加角色')
    project_name = forms.CharField(
        required=True,
        error_messages={
            'required': "项目名不能为空"
        }
    )
    person_people_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '责任开发人不能为空'
        })
    # 查询项目名判断是否存在
    def clean_name(self):
        name = self.data['project_name']
        objs = models.Role.objects.filter(
            project_name=name,
        )
        if objs:
            self.add_error('name', '项目名已存在')
        else:
            return name


# 更新项目信息
class UpdateForm(forms.Form):
    project_name = forms.CharField(
        required=True,
        error_messages={
            'required': "项目名不能为空"
        }
    )
    person_people_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '责任开发人类型错误'
        })

    # 判断角项目是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['project_name']
        objs = models.Role.objects.filter(
            name=name,
        ).exclude(id=o_id)
        if objs:
            self.add_error('name', '该项目已存在')
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
