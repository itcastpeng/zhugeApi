from django import forms

from zhugeproject import models
from publicFunc import account


# 添加需求信息
class AddForm(forms.Form):
    demand_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "需求人不能为空"
        }
    )
    is_system_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "属于哪个功能不能为空"
        }
    )
    is_remark = forms.CharField(
        required=True,
        error_messages={
            'required': "需求不能为空"
        }
    )

# 更新需求信息
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作id不能为空"
        }
    )

    demand_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "需求人不能为空"
        }
    )

    is_system_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '归属需求不能为空'
        }
    )
    is_remark = forms.CharField(
        required=True,
        error_messages={
            'required': '需求不能为空'
        }
    )



# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误",
        }
    )
    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

