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

    )

    title = forms.CharField(
        required=False,

    )
    content = forms.CharField(
        required=False,

    )

    # 判断企业产品是否存在
    def clean_name(self):
        name = self.data['name']
        user_id = self.data.get('user_id')
        company_id = models.zgld_userprofile.objects.get(id=user_id).company_id

        objs = models.zgld_product.objects.filter(
            name=name,company_id=company_id
        )
        if objs:
            self.add_error('name', '产品名称不能重复')
        else:
            return name


# 修改企业的产品
class ProductGetForm(forms.Form):
    u_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )
    product_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "产品ID不能为空"
        }
    )


    def clean_u_id(self):

        user_id = self.data['u_id']
        objs = models.zgld_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('u_id', '用户名不存在')
        else:
            return user_id

    # # 判断企业产品名称是否存在
    # def clean_product_id(self):
    #     product_id = self.data['product_id']
    #     objs = models.zgld_product.objects.filter(id = product_id)
    #
    #     if  not objs:
    #         self.add_error('product_id', '产品不存在')
    #
    #     else:
    #         return product_id


class ProductSelectForm(forms.Form):

    u_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
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


