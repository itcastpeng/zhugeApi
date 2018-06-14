from django import forms

from wendaku import models
from publicFunc import account
import datetime


# 添加科室信息
class KeshiAddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "科室名不能为空"
        }
    )
    pid_id = forms.IntegerField(
        required=False,
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        })

    # 查询科室名称是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.Keshi.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '科室名已存在')
        else:
            return name


# 更新用户信息
class KeshiUpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "用户id不能为空"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "科室名不能为空"
        }
    )

    pid_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '父级ID不能为空'
        })
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        })

    # 判断用户名是否存在
    def clean_username(self):
        name = self.data['name']
        user_id = self.data['user_id']
        print(name, user_id)
        objs = models.Keshi.objects.filter(
            name=name,
        ).exclude(id=user_id)
        if objs:
            print('科室存在')
            self.add_error('username', '科室名已存在')
        else:
            return name


# 判断是否是数字
class KeshiSelectForm(forms.Form):
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
