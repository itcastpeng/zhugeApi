from django import forms

from zhugeleida import models
from publicFunc import account
import datetime
import re
from django.core.exceptions import ValidationError


def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$') #正则匹配
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误') #如果没有匹配到主动触发一个错误

class Customer_UpdateForm(forms.Form):
    id = forms.IntegerField(
        required=True,
        error_messages= {
            'required': "客户ID不能为空"
        }
    )
    expected_time = forms.DateField(
        required=False,
        error_messages={
            'required': "预计成交日期"
        }
    )
    expedted_pr = forms.DateField(
        required=False,
        error_messages={
            'required': "预计成交概率"
        }
    )


# 更新客户信息
class Customer_information_UpdateForm(forms.Form):
    id = forms.IntegerField(
        required=True,
        error_messages= {
            'required': "客户ID不能为空"
        }
    )
    email = forms.EmailField(
        required=False,
        error_messages=
            {'required': u'邮箱不能为空'}
    )

    phone = forms.CharField(
        required=False,
        validators=[mobile_validate, ],        # 应用咱们自己定义的规则
    )

    memo_name = forms.CharField(
        required=False,
        error_messages={
            'required': "备注名不能为空"
        }
    )

    source = forms.IntegerField(
        required=True,
        error_messages={
            'required': '客户来源不能为空'
        })

    company = forms.CharField(
        required=False,

    )
    position = forms.CharField(
        required=False,
    )
    address = forms.CharField(
        required=False,
    )
    birthday = forms.DateField(
        required=False,
    )
    mem = forms.CharField(
        widget=forms.Textarea
    )


    # 判断客户是否存在
    def clean_id(self):
        id = self.data['id']
        info_obj = models.zgld_customer.objects.filter(id=id)

        if not info_obj:
            self.add_error('id', '客户不存在')
        else:
            return id


#
class CustomerSelectForm(forms.Form):
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

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length