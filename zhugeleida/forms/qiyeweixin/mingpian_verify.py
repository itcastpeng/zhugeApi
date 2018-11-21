from django import forms

from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

def mobile_validate(value):
    # mobile_re = re.compile(r'^(13[0-9]|15[0-9]|17[0-9]|18[0-9]|14[0-9])[0-9]{8}$') #正则匹配
    mobile_num = len(str(value))

    if int(mobile_num) != 11:
        raise ValidationError('手机号码格式错误') #如果没有匹配到主动触发一个错误
    else:
        return value


# 添加用户信息
class MingPianPhoneUpdateForm(forms.Form):


    mingpian_phone = forms.CharField(
        required=True,
        validators=[mobile_validate, ],  # 应用咱们自己定义的规则
    )




# 更新用户信息
class  MingPianInfoUpdateForm(forms.Form):
    # o_id = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': "操作ID不能为空"
    #     }
    # )
    #
    memo_name = forms.CharField(
        required=False,

    )
    wechat = forms.CharField(
        required=False,

    )

    telephone = forms.CharField(
        required=False,

    )

    email = forms.EmailField(
        required=False,

    )

    country = forms.IntegerField(
        required=True,

    )

    area = forms.CharField(
        required=False,
    )

    address = forms.CharField(
        required=False,
    )

    mingpian_phone = forms.CharField(
        required=True,
        validators=[mobile_validate, ],  # 应用咱们自己定义的规则
    )


    # 查询用户名判断是否存在
    # def clean_username(self):
    #     username = self.data['username']
    #     o_id = self.data['o_id']
    #     # print(username)
    #     objs = models.zgld_userprofile.objects.filter(
    #         username=username,
    #     ).exclude(id=o_id)
    #
    #     if objs:
    #         self.add_error('username', '用户名已存在')
    #     else:
    #         return username

    # # 返回加密后的密码
    # def clean_password(self):
    #     return account.str_encrypt(self.data['password'])

    # 获取公司id
    def clean_company_id(self):
        print('form----->>',self.data.get('user_id'))

        obj = models.zgld_userprofile.objects.get(id=self.data.get('user_id'))
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

    def clean_role_id(self):
        obj = models.zgld_userprofile.objects.get(id=self.data['user_id'])
        role_id = obj.role_id

        if int(role_id) == 1 and int(self.data['role_id']) == 1:  # 管理员角色
             role_id = 1

        else:
             role_id = 2

        return role_id

    def  clean_department_id(self):
        # depart_id_list = []
        print('---------->>',self.data.get('department_id'))
        # for id in self.data.get('department_id').split(','):
        #     depart_id_list.append(int(id))

        depart_id_list = self.data.get('department_id')
        if depart_id_list:
            depart_id_list = json.loads(depart_id_list)

        objs = models.zgld_department.objects.filter(id__in=depart_id_list)
        if objs:
            return depart_id_list

            # for c_id in objs:
                # print('=========department_company_id=====>>', objs, c_id.company_id ,self.data.get('company_id'))
                # department_company_id = c_id.company_id
                #
                # if  str(department_company_id) !=  str(self.data.get('company_id')):
                #     self.add_error('department_id', '公司id不能为空')
        else:
             return []





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
