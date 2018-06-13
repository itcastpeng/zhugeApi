from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加标签信息
class TagCustomerAddForm(forms.Form):
    # print('添加标签')
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "标签不能为空"
        }
    )
    # tag_user = forms.CharField(
    #     required=True,
    #     error_messages = {
    #         'required': "关联用户不能为空"
    #     }
    #
    # )

    # 查询标签名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.zgld_tag.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '标签名已存在')
        else:
            return name


# 更新标签信息
class TagCustomerUpdateForm(forms.Form):
    tag_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '标签ID不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': '标签名不能为空'
        }
    )

    # 判断标签是否存在
    def clean_name(self):
        tag_id = self.data['tag_id']
        name = self.data['name']
        objs = models.zgld_tag.objects.filter(
            name=name,
        )
        if not objs:
            self.add_error('name', '标签不存在')
        else:
            return name


# 判断是否是数字
class TagCustomerSelectForm(forms.Form):
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