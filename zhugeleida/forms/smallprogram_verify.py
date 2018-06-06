from django import forms

from zhugeleida import models
from publicFunc import account
import datetime



# 添加标签信息
class SmallProgramAddForm(forms.Form):
    # print('添加标签')
    source = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户来源不能为空"
        }
    )

    user_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户访问类型不能为空"
        }
    )
    code = forms.CharField(
        required=True,
        error_messages={
            'required': "js code 不能为空"
        }
    )




    # tag_user = forms.CharField(
    #     required=True,
    #     error_messages = {
    #         'required': "关联用户不能为空"
    #     }
    #
    # )

