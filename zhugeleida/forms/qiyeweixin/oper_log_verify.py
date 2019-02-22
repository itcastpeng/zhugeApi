from django import forms

# from zhugeleida import models


# 记录用户操作日志
class OperLogAddForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户名不能为空",
            "invalid": "参数类型错误"
        }
    )

    oper_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "oper_type不能为空",
            "invalid": "参数类型错误"
        }
    )
