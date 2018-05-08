from django import forms

from wendaku import models
from publickFunc import account
import datetime


# 添加任务日志信息
class AddForm(forms.Form):
    belog_log_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "归属任务不能为空"
        }
    )
    log_status = forms.CharField(
        required=True,
        error_messages={
            'required': '当前状态不能为空'
        })
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        })
    # 查询用户名判断是否存在
    # def clean_name(self):
    #     name = self.data['project_name']
    #     objs = models.Role.objects.filter(
    #         project_name=name,
    #     )
    #     if objs:
    #         self.add_error('name', '项目名已存在')
    #     else:
    #         return name


# 更新用户信息
class UpdateForm(forms.Form):
    log_status = forms.CharField(
        required=True,
        error_messages={
            'required': "操作人不能为空"
        }
    )
    # 判断角项目是否存在
    # def clean_name(self):
    #     o_id = self.data['o_id']
    #     name = self.data['project_name']
    #     objs = models.Role.objects.filter(
    #         name=name,
    #     ).exclude(id=o_id)
    #     if objs:
    #         self.add_error('name', '该项目已存在')
    #     else:
    #         return name


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
