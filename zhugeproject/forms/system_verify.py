from django import forms
from zhugeproject import models

# 添加项目信息
class AddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "产品名不能为空"
        }
    )
    # is_section = forms.DateField(
    #     required=True,
    #     error_messages={
    #         'required': '责任项目部不能为空'
    #     }
    # )
    def clean_item_name(self):
        item_name = self.data['item_name']
        # print(username)
        objs = models.ProjectSystem.objects.filter(
            item_name=item_name,
        )
        if objs:
            self.add_error('item_name', '该项目名已存在')
        else:
            return item_name


# 更新项目信息
class UpdateForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "产品名不能为空"
        }
    )
    finish_status = forms.IntegerField(
        required=True,
        error_messages={
            'required':'数据类型为INT,项目状态不能为空'
        }
    )
    create_time = forms.DateField(
        required=True,
        error_messages={
            'required':'创建时间类型错误,创建时间不能为空'
        }
    )
    predict_time = forms.DateField(
        required=False,
        error_messages={
            'required': '预计结束时间类型错误'
        }
    )
    over_time = forms.DateField(
        required=False,
        error_messages={
            'invalid': '结束时间类型错误'
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
