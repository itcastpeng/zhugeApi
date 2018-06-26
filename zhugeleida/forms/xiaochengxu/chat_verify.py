from django import forms

from zhugeleida import models
from publicFunc import account
import datetime
import re
from django.core.exceptions import ValidationError


# 判断是否是数字
class ChatSelectForm(forms.Form):


    u_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "用户ID不能为空",
        }
    )


    # 判断用户id是否存在
    def clean_user_id(self):

        user_id = self.data['u_id']

        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('username', '用户名不存在')
        else:
            return user_id





# 判断是否是数字
class ChatGetForm(forms.Form):
    u_id = forms.IntegerField(
        required=True,
        error_messages= {
            'invalid': "用户ID不能为空",
        }
    )


    # 判断用户id是否存在
    def clean_user_id(self):

        user_id = self.data['u_id']

        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('username', '用户名不存在')
        else:
            return user_id

    # 判断用户名是否存在
    def clean_customer_id(self):

        customer_id = self.data['user_id']

        objs = models.zgld_customer.objects.filter(
            id=customer_id,
        )
        if not objs:
            self.add_error('customer_id', '客户不存在')
        else:
            return customer_id