from django import forms

from ribao import models
from publickFunc import account
import datetime


# 添加任务名称
class AddForm(forms.Form):
    task_name = forms.CharField(
        required=True,
        error_messages={
            'required': "任务名称不能为空"
        }
    )
    belog_task = forms.CharField(
        required=True,
        error_messages={
            'required': '归属项目不能为空'
        })
    director = forms.CharField(
        required=True,
        error_messages={
            'required': '开发负责人不能为空'
        })
    boor_urgent = forms.BooleanField(
        required=True,
        error_messages={
            'required': '是否加急类型错误'
        })

    # # 查询用户名判断是否存在
    # def clean_name(self):
    #     name = self.data['name']
    #     objs = models.RibaoRole.objects.filter(
    #         name=name,
    #     )
    #     if objs:
    #         self.add_error('name', '角色名已存在')
    #     else:
    #         return name


# 更新用户信息
class UpdateForm(forms.Form):
    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色ID不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': '角色名不能为空'
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    # 判断角色是否存在
    def clean_name(self):
        role_id = self.data['role_id']
        name = self.data['name']
        objs = models.RibaoRole.objects.filter(
            name=name,
        ).exclude(id=role_id)
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
