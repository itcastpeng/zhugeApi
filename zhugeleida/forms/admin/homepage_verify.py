from django import forms

# 验证数据指标的传参
class LineInfoForm(forms.Form):


    days = forms.CharField(
        required=True,
        error_messages={
            # 'required': "天数不能为空",
            'invalid': "天数不能为空",
        }
    )
    index_type =  forms.CharField(
        required=True,
        error_messages={
            # 'required': "类型不能为空",
            'invalid':  "必须是整数类型"
        }
    )
