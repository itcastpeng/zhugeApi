from django import forms

from zhugeproject import models
from publickFunc import account


# 添加权限信息
class AddForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )
    path = forms.CharField(
        required=True,
        error_messages={
            'required': "路径不能为空"
        }
    )
    quanxian_name = forms.CharField(
        required=True,
        error_messages={
            'required': '权限名不能为空'
        })

    # 查询用户名判断是否存在
    def clean_quanxian_name(self):
        quanxian_name = self.data['quanxian_name']
        objs = models.ProjectQuanXian.objects.filter(
            quanxian_name=quanxian_name,
        )
        if objs:
            self.add_error('quanxian_name', '权限名已存在')
        else:
            return quanxian_name



# 更新权限信息
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户id不能为空"
        }
    )

    path = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    quanxian_name = forms.CharField(
        required=True,
        error_messages={
            'required': '权限名字不能为空'
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

