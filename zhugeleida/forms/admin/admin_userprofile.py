from django import forms

from zhugeleida import models
from publicFunc import account
import time


# 添加
class AddForm(forms.Form):

    login_user = forms.CharField(
        required=True,
        error_messages={
            'required': "名字不能为空"
        }
    )

    username = forms.CharField(
        required=False,
        error_messages={
            'required': "名字不能为空"
        }
    )

    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    position = forms.CharField(
        required=True,
        error_messages={
            'required': "职位不能为空"
        }
    )

    password = forms.CharField(
        required=True,
        error_messages={
            'required': "权限路径不能为空"
        }
    )

    role_id = forms.IntegerField(
        required=True,
        error_messages = {
        'required': "用户角色不能为空"
    }

    )

    # 查询名称是否存在
    def clean_login_user(self):
        login_user = self.data['login_user']

        objs = models.zgld_admin_userprofile.objects.filter(
            login_user=login_user
        )
        if objs:
            self.add_error('login_user', '登录用户名不能重复')
        else:
            return login_user

    # 查询名称是否存在
    def clean_username(self):
        username = self.data['username']

        objs = models.zgld_admin_userprofile.objects.filter(
            username=username
        )
        if objs:
            self.add_error('username', '名字不能重复')
        else:
            return username


    # 返回加密后的密码
    def clean_password(self):
        return account.str_encrypt(self.data['password'])


    def clean_company_id(self):
        company_id = self.data.get('company_id')
        company_obj = models.zgld_company.objects.filter(id=company_id)
        if not company_obj:
            self.add_error('company_id', '公司id不存在')
        else:
            return company_id


# 更新
class UpdateForm(forms.Form):

    id = forms.CharField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }


    )

    login_user = forms.CharField(
        required=True,
        error_messages={
            'required': "名字不能为空"
        }
    )

    username = forms.CharField(
        required=False,
        error_messages={
            'required': "名字不能为空"
        }
    )

    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    position = forms.CharField(
        required=True,
        error_messages={
            'required': "职位不能为空"
        }
    )

    password = forms.CharField(
        required=True,
        error_messages={
            'required': "权限路径不能为空"
        }
    )

    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户角色不能为空"
        }

    )

    # 查询名称是否存在
    def clean_login_user(self):
        login_user = self.data['login_user']

        objs = models.zgld_admin_userprofile.objects.filter(
            login_user=login_user
        )
        if objs:
            self.add_error('login_user', '登录用户名不能重复')
        else:
            return login_user

    # 查询名称是否存在
    def clean_username(self):
        username = self.data['username']

        objs = models.zgld_admin_userprofile.objects.filter(
            username=username
        )
        if objs:
            self.add_error('username', '名字不能重复')
        else:
            return username

    # 返回加密后的密码
    def clean_password(self):
        return account.str_encrypt(self.data['password'])

    def clean_company_id(self):
        company_id = self.data.get('company_id')
        company_obj = models.zgld_company.objects.filter(id=company_id)
        if not company_obj:
            self.add_error('company_id', '公司id不存在')
        else:
            return company_id



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

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length
