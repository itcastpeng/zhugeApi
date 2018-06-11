from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加公司信息
class CompanyAddForm(forms.Form):
    # print('添加公司')
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "公司名不能为空"
        }
    )

    corp_id = forms.CharField(
        required=True,
        error_messages={
            'required': "企业ID不能为空"
        }
    )
    tongxunlu_secret = forms.CharField(
        required=True,
        error_messages={
            'required': "通讯录secret不能为空"
        }
    )
    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.zgld_company.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '公司名已存在')
        else:
            return name


# 更新用户信息
class CompanyUpdateForm(forms.Form):
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司ID不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': '公司名不能为空'
        }
    )

    corp_id = forms.CharField(
        required=True,
        error_messages={
            'required': "企业ID不能为空"
        }
    )
    tongxunlu_secret = forms.CharField(
        required=True,
        error_messages={
            'required': "通讯录secret不能为空"
        }
    )

    # 判断公司名称是否存在
    def clean_name(self):
        company_id = self.data['company_id']
        name = self.data['name']
        objs = models.zgld_company.objects.filter(
            name=name,
        ).exclude(id=company_id)

        if objs:
            self.add_error('name', '公司名称已经存在')
        else:
            return name


# 判断是否是数字
class CompanySelectForm(forms.Form):
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


    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length