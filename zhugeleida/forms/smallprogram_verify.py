from django import forms

from zhugeleida import models
from publicFunc import account
import datetime



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

    uid = forms.IntegerField(
        # 客户上级对应的用户
        required=False,

    )



    # tag_user = forms.CharField(
    #     required=True,
    #     error_messages = {
    #         'required': "关联用户不能为空"
    #     }
    #
    # )




class LoginBindingForm(forms.Form):
    # print('添加标签')
    source = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户来源不能为空"
        }
    )

    # user_type = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': "客户访问类型不能为空"
    #     }
    # )

    uid = forms.IntegerField(
        # 客户上级对应的用户
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }

    )
    user_id = forms.IntegerField(
        # 客户上级对应的用户
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )





    # tag_user = forms.CharField(
    #     required=True,
    #     error_messages = {
    #         'required': "关联用户不能为空"
    #     }
    #
    # )

