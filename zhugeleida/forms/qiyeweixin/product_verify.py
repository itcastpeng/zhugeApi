from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

# 添加企业的产品
class ProductAddForm(forms.Form):

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "产品名称不能为空"
        }
    )
    price = forms.CharField(
        required=True,
        error_messages={
            'required': "价格不能为空"
        }
    )
    reason = forms.CharField(
        required=False,
        error_messages={
            'required': '角色不能为空'
        })

    title = forms.CharField(
        required=False,

    )
    content = forms.CharField(
        required=False,

    )

    # 判断企业产品是否存在
    def clean_name(self):
        name = self.data['name']
        company_id = models.zgld_userprofile.objects.get(id = self.data.get('user_id')).company_id

        objs = models.zgld_product.objects.filter(
            name=name,company_id=company_id
        )
        if objs:
            self.add_error('username', '产品名称不能重复')
        else:
            return name





