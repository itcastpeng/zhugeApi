from django import forms

from zhugeleida import models
from publicFunc import account
import datetime, time, re


# 添加编辑信息
class AddForm(forms.Form):
    login_user = forms.CharField(
        required=True,
        error_messages={
            'required': '用户名不能为空'
        }
    )
    user_name = forms.CharField(
        required=True,
        error_messages={
            'required': '备注不能为空'
        }
    )
    password = forms.CharField(
        required=True,
        error_messages={
            'required': '密码不能为空'
        }
    )
    phone = forms.CharField(
        required=True,
        error_messages={
            'required': '电话不能为空'
        }
    )
    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': '公司不能为空'
        }
    )
    position = forms.CharField(
        required=True,
        error_messages={
            'required': '职位不能为空'
        }
    )
    token = forms.CharField(
        required=False
    )

    # 返回加密后的密码
    def clean_password(self):
        return account.str_encrypt(self.data['password'])

    def clean_token(self):
        password = self.data['password']
        return account.get_token(str(password) + str(int(time.time()) * 1000))

    def clean_login_user(self):
        company_id = self.data.get('company_id')
        login_user = self.data.get('login_user')
        objs = models.zgld_editor.objects.filter(
            login_user=login_user,
            company_id=company_id
        )
        if objs:
            self.add_error('login_user', '用户名存在')
        else:
            return login_user

    def clean_phone(self):
        phone = self.data.get('phone')
        phone_pat = re.compile('^(13\\d|14[5|7]|15\\d|166|17[3|6|7]|18\\d)\\d{8}$')
        res = re.search(phone_pat, phone)
        if res:
            return phone
        else:
            self.add_error('phone', '请填写正确电话号码')

# 更新编辑信息
class UpdateForm(forms.Form):
    login_user = forms.CharField(
        required=True,
        error_messages={
            'required': '用户名不能为空'
        }
    )
    user_name = forms.CharField(
        required=True,
        error_messages={
            'required': '备注不能为空'
        }
    )
    position = forms.CharField(
        required=True,
        error_messages={
            'required': '职位不能为空'
        }
    )
    phone = forms.CharField(
        required=True,
        error_messages={
            'required': '电话不能为空'
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '修改ID不能为空'
        }
    )
    def clean_login_user(self):
        company_id = self.data.get('company_id')
        o_id = self.data.get('o_id')
        login_user = self.data.get('login_user')
        objs = models.zgld_editor.objects.filter(
            login_user=login_user,
            company_id=company_id,
            is_delete=False
        ).exclude(id=o_id)
        if objs:
            self.add_error('login_user', '用户名存在')
        else:
            return login_user

    def clean_phone(self):
        phone = self.data.get('phone')
        phone_pat = re.compile('^(13\\d|14[5|7]|15\\d|166|17[3|6|7]|18\\d)\\d{8}$')
        res = re.search(phone_pat, phone)
        if res:
            return phone
        else:
            self.add_error('phone', '请填写正确电话号码')

# 查询
class SelectForm(forms.Form):

    user_id = forms.IntegerField(
        required=False,
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



# 编辑登录
class LoginForm(forms.Form):
    login_user = forms.CharField(
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

    def clean_login_user(self):
        login_user = self.data.get('login_user')
        password = self.data.get('password')
        print('-account.str_encrypt(password)-------> ', account.str_encrypt(password))
        objs = models.zgld_editor.objects.filter(
            login_user=login_user,
            password=account.str_encrypt(password),
            status=1
        ).exclude(
            is_delete=1
        )
        if not objs:
            objs = models.zgld_editor.objects.filter(
                phone=login_user,
                password=account.str_encrypt(password),
                status=1
            ).exclude(
                is_delete=1
            )
        if not objs:
            self.add_error('login_user', '用户名或密码输入错误')
        else:
            obj = objs[0]
            if datetime.datetime.today() <= obj.company.account_expired_time:
                return obj

            else:
                self.add_error('login_user', '该公司已过期')

        # else:
        #     self.add_error('login_user', '用户名或密码输入错误')



# 审核文章
class AuditArticleForm(forms.Form):
    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择审核状态"
        }
    )
    reason_rejection = forms.CharField(
        required=False,
        error_messages={
            'required': ""
        }
    )

    def clean_status(self):
        status = int(self.data.get('status'))
        reason_rejection = self.data.get('reason_rejection')
        if status == 0:
            if not reason_rejection:
                self.add_error('status', '请填写驳回理由')
            else:
                return 3
        else:
            return 4

# 审核案例
class AuditCaseForm(forms.Form):
    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择审核状态"
        }
    )
    reason_rejection = forms.CharField(
        required=False,
        error_messages={
            'required': ""
        }
    )
    def clean_status(self):
        status = int(self.data.get('status'))
        reason_rejection = self.data.get('reason_rejection')
        if status == 0:
            if not reason_rejection:
                self.add_error('status', '请填写驳回理由')
            else:
                return 3
        else:
            return 4


# 审核案例
class AuditDiaryForm(forms.Form):
    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择审核状态"
        }
    )
    reason_rejection = forms.CharField(
        required=False,
        error_messages={
            'required': ""
        }
    )
    def clean_status(self):
        status = int(self.data.get('status'))
        reason_rejection = self.data.get('reason_rejection')
        if status == 0:
            if not reason_rejection:
                self.add_error('status', '请填写驳回理由')
            else:
                return 3
        else:
            return 4









