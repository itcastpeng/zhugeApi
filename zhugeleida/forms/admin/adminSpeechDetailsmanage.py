from django import forms

from zhugeleida import models
from publicFunc import account
import time


# 添加
class AddForm(forms.Form):
    contentWords = forms.CharField(
        required=True,
        error_messages={
            'required': "话术内容不能为空"
        }
    )
    userProfile = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户名称不能为空"
        }
    )
    talkGroupName = forms.IntegerField(
        required=False,
        error_messages={
            'required': "分组名称类型错误"
        }
    )

# 更新
class UpdateForm(forms.Form):
    contentWords = forms.CharField(
        required=True,
        error_messages={
            'required': "话术内容不能为空"
        }
    )
    talkGroupName = forms.IntegerField(
        required=True,
        error_messages={
            'required': "分组名称不能为空"
        }
    )
    userProfile = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户名称不能为空"
        }
    )

    # 查询名称是否存在
    def clean_groupName(self):
        groupName = self.data.get('groupName')

        objs = models.zgld_talk_group_management.objects.filter(
            groupName=groupName
        ).exclude(id=self.data.get('o_id'))
        if objs:
            self.add_error('groupName', '分组名称已存在！')
        else:
            return groupName


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
