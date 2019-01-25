from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加标签信息
class CaseTagAddForm(forms.Form):
    parent_tag_name = forms.CharField(
        required=True,
        error_messages={
            'required': "一级标签不能为空"
        }
    )
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )

    second_tag_name = forms.CharField(
        required=False,

    )

    # 查询标签名判断是否存在
    def clean_parent_tag_name(self):
        name = self.data['parent_tag_name']
        objs = models.zgld_case_tag.objects.filter(
            name=name, user_id=self.data.get('user_id')
        )
        if objs:
            self.add_error('name', '不能存在相同的标签名')
        else:
            return name

# 添加标签信息
class CaseTagSingleAddForm(forms.Form):

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    tag_name = forms.CharField(
        required=True,
        error_messages={
            'required': "标签不能为空"
        }

    )


    def clean_tag_name(self):
        company_id = self.data['company_id']
        tag_name = self.data['tag_name']

        objs = models.zgld_case_tag.objects.filter(
            name=tag_name, company_id=company_id
        )
        if objs:
            self.add_error('tag_name', '不能存在相同的标签名')
        else:
            return tag_name





# 修改标签信息
class CaseTagUpdateAddForm(forms.Form):
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )
    tag_id = forms.CharField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )

    tag_name = forms.CharField(
        required=True,
        error_messages={
            'required': "标签不能为空"
        }

    )



    def clean_tag_name(self):
        tag_id = self.data['tag_id']
        company_id = self.data['company_id']
        tag_name =  self.data['tag_name']
        objs = models.zgld_case_tag.objects.filter(
            name=tag_name, company_id=company_id
        ).exclude(id=tag_id)

        if objs:
            self.add_error('tag_name', '不能存在相同的标签名')
        else:
            return tag_name


# 分页
class TagUserSelectForm(forms.Form):
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