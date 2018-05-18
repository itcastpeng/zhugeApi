from django import forms
from zhugeproject import models

# 添加项目信息
class AddForm(forms.Form):
    item_name_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "产品名不能为空"
        }
    )
    # oper_user_id = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': "创建人不能为空"
    #     }
    # )


# 更新项目信息
class UpdateForm(forms.Form):
    item_name_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "产品名不能为空"
        }
    )



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
