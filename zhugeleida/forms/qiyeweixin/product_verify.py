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
        required=False,
        # error_messages={
        #     'required': "价格不能为空"
        # }
    )
    reason = forms.CharField(
        required=False,

    )


    content = forms.CharField(
        required=False,
        error_messages={
            'required': "文章内容不能为空"
        }
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
class ProductUpdateForm(forms.Form):
    user_id = forms.IntegerField(
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


    name = forms.CharField(
        required=True,
        error_messages={
            'required': "产品名称不能为空"
        }
    )
    price = forms.CharField(
        required=False,
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
        error_messages={
            'required': "内容不能为空"
        }
    )

    # 判断企业产品名称是否存在
    def clean_name(self):
        name = self.data['name']
        product_id = self.data['product_id']
        company_id = models.zgld_userprofile.objects.get(id = self.data.get('user_id')).company_id

        objs = models.zgld_product.objects.filter(
            name=name,company_id=company_id
        ).exclude(id=product_id)

        if  objs:
            self.add_error('name', '产品名称不能重复')
        else:
            return name

    # 判断企业产品名称是否存在
    def clean_product_id(self):
        product_id = self.data['product_id']
        objs = models.zgld_product.objects.filter(id = product_id)

        if  not objs:
            self.add_error('product_id', '产品不存在')

        else:
            return product_id



# 修改企业的产品
class RecommendIndexForm(forms.Form):
    user_id = forms.IntegerField(
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

    recommend_index = forms.IntegerField(
        required=True,
        error_messages={
            'required': "推荐指数不能为空"
        }
    )




    # 判断企业产品名称是否存在
    def clean_product_id(self):
        product_id = self.data['product_id']
        objs = models.zgld_product.objects.filter(id = product_id)

        if  not objs:
            print('-----产品不存在----->>')
            self.add_error('product_id', '产品不存在')

        else:
            return product_id



class ProductSelectForm(forms.Form):


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


