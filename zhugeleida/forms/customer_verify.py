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

class Customer_UpdateExpectedTime_Form(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "用户ID不能为空",
        }
    )

    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )
    expected_time = forms.DateField(
        required=True,
        error_messages={
            'required': "预计成交日期"
        }
    )

    # 判断客户是否存在
    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        info_obj = models.zgld_customer.objects.filter(id=customer_id)

        if not info_obj:
            self.add_error('customer_id', '客户不存在')
        else:
            return customer_id

    def clean_user_id(self):

        user_id = self.data['user_id']
        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        print('-------->>',objs)

        if not objs:
            print('--用户名不xxxxxx存在------>>', objs[0])
            self.add_error('username', '用户名不xxxxxx存在')
        else:
            return user_id

class Customer_UpdateExpedtedPr_Form(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "用户ID不能为空",
        }
    )

    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )
    expedted_pr = forms.CharField(
        required=True,
        error_messages={
            'required': "预计成交概率"
        }
    )

    # 判断客户是否存在
    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        info_obj = models.zgld_customer.objects.filter(id=customer_id)

        if not info_obj:
            self.add_error('customer_id', '客户不存在')
        else:
            return customer_id

    def clean_user_id(self):

        user_id = self.data['user_id']
        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('username', '用户名不存在')
        else:
            return user_id

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
    sex = forms.IntegerField(
        required=True,
        error_messages= {
            'required': "性别不能为空"
        }
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

    # source = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': '客户来源不能为空'
    #     })

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
        required=False,
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
    customer_id = forms.CharField(
        required = True,
        error_messages={
            'required': "备注名不能为空"
        }
    )


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

