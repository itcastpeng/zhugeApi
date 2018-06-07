from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加用户信息
class UserAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )
    password = forms.CharField(
        required=True,
        error_messages={
            'required': "密码不能为空"
        }
    )
    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色不能为空'
        })
    company_id = forms.IntegerField(
        required=False,
        # error_messages={
        #     'required': '公司不能为空'
        # }
    )
    department_id = forms.IntegerField(
        required=,

    )

    # 查询用户名判断是否存在
    def clean_username(self):
        username = self.data['username']
        # print(username)
        objs = models.zgld_userprofile.objects.filter(
            username=username,
        )
        if objs:
            self.add_error('username', '用户名已存在')
        else:
            return username

    # 返回加密后的密码
    def clean_password(self):
        return account.str_encrypt(self.data['password'])

    # 获取公司id
    def clean_company_id(self):
        obj = models.zgld_userprofile.objects.get(id=self.data['user_id'])
        role_id = obj.role_id


        if role_id == 1:  # 管理员角色
            company_id = self.data['company_id']
            company_obj = models.zgld_company.objects.filter(id=company_id)
            if not company_obj:
                self.add_error('company_id', '公司id不能为空')
            else:
                return company_id
            # company_obj = models.zgld_company.objects.filter(id=self.data['company_id'])
            # if company_obj:
            #     print('-- company_obj[0]-->>', list(company_obj)[0] , list(company_obj))
            #
            #     return company_obj[0]

        elif role_id == 2:  # 普通用户角色
            company_id = obj.company_id
            return company_id




# 更新用户信息
class UserUpdateForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户id不能为空"
        }
    )

    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色不能为空'
        }
    )

    # 判断用户名是否存在
    def clean_username(self):
        username = self.data['username']
        user_id = self.data['user_id']
        print(username)
        objs = models.zgld_userprofile.objects.filter(
            username=username,
        ).exclude(id=user_id)
        if objs:
            self.add_error('username', '用户名已存在')
        else:
            return username


# 判断是否是数字
class UserSelectForm(forms.Form):
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
