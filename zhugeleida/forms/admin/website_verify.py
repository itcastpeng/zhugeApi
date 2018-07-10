from django import forms

from zhugeleida import models
from publicFunc import account
import datetime

# 添加部门信息
class DepartmentAddForm(forms.Form):
    # print('添加部门')
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名id不能为空"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "部门名不能为空"
        }
    )

    company_id = forms.CharField(
        required=False,
        # error_messages={
        #     'required': "公司id不能为空"
        # }
    )

    parentid_id = forms.CharField(
        required=False,
        error_messages={
            'required': "父级部门ID"
        }
    )

    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.zgld_department.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '部门名已存在')
        else:
            return name

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

        elif role_id == 2:  # 普通用户角色
            company_id = obj.company_id
            return company_id

    def clean_parentid_id(self):
        if not self.data.get('parentid_id'):
            return None

# 更新用户信息
class DepartmentUpdateForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名id不能为空"
        }
    )


    name = forms.CharField(
        required=True,
        error_messages={
            'required': "部门名不能为空"
        }
    )

    company_id = forms.CharField(
        required=False,
        # error_messages={
        #     'required': "公司id不能为空"
        # }
    )

    parentid_id = forms.CharField(
        required=False,
        error_messages={
            'required': "父级部门ID不能为空"
        }
    )
    department_id = forms.CharField(
        required=True,
        error_messages={
            'required': "部门ID不能为空"
        }
    )

    # 查询用户名判断是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.zgld_department.objects.filter(
            name=name,
        ).exclude(id=self.data.get('department_id'))

        if objs:
            self.add_error('name', '部门名已经存在')
        else:
            return name

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

        elif role_id == 2:  # 普通用户角色
            company_id = obj.company_id
            return company_id

# 判断是否是数字
class DepartmentSelectForm(forms.Form):
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