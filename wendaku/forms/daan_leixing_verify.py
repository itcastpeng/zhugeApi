from django import forms

from wendaku import models
from publickFunc import account
import datetime

# 添加角色信息
class DaanAddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "类型不能为空"
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
        print('name  -->',name)
        objs = models.DaAnLeiXing.objects.filter(
            name=name
        )
        if objs:
            self.add_error('name', '词名已存在')
        else:
            return name


# 更新用户信息
class DaanUpdateForm(forms.Form):
    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '类型ID不能为空'
        }
    )
    name = forms.CharField(
        required=True,
        error_messages={
            'required': '类型不能为空'
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
        objs = models.CiLei.objects.filter(
            name=name,
        ).exclude(id=role_id)
        if objs:
            self.add_error('name', '答案类型已存在')
        else:
            return name


# 判断是否是数字
class DaanSelectForm(forms.Form):
    current_page =forms.IntegerField(
        required = False,
        error_messages = {
        'required': "页码数据类型错误"
    })
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
