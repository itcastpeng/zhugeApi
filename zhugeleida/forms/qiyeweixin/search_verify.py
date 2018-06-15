from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加标签信息
class SearchTagSelectForm(forms.Form):
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
