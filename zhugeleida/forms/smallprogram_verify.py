from django import forms

from zhugeleida import models
from publicFunc import account
import datetime



class SmallProgramAddForm(forms.Form):
    # print('添加标签')
    source = forms.IntegerField(
        required=False,
        error_messages={
            'required': "客户来源不能为空"
        }
    )


    user_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户访问类型不能为空"
        }
    )
    code = forms.CharField(
        required=True,
        error_messages={
            'required': "js code 不能为空"
        }
    )

    uid = forms.IntegerField(
        # 客户上级对应的用户
        required=False,

    )

    company_id = forms.CharField(
        required=False,
        error_messages={
            'required': "公司id不能为空"
        }
    )
    # def clean_uid(self):
    #     uid = self.data.get('uid')
    #     objs = models.zgld_userprofile.objects.filter(id=uid)
    #     if objs:
    #         now = datetime.datetime.today()
    #         compay_objs = models.zgld_company.objects.filter(id=objs[0].company_id)
    #         if compay_objs[0].account_expired_time >= now:
    #             return uid
    #         else:
    #             self.add_error('uid', '已过期')
    #     else:
    #         self.add_error('uid', '该用户不存在')
    # def clean_company_id(self):
    #     company_id = self.data['company_id']
    #     company_obj = models.zgld_company.objects.filter(id=company_id)
    #     if not company_obj:
    #         self.add_error('company_id', '公司不存在')
    #     else:
    #         return company_id




class LoginBindingForm(forms.Form):
    # print('添加标签')
    source = forms.CharField(
        required=False,
        error_messages={
            'required': "客户来源不能为空"
        }
    )

    # user_type = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': "客户访问类型不能为空"
    #     }
    # )


    uid = forms.IntegerField(
        # 客户上级对应的用户
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }

    )
    user_id = forms.IntegerField(
        # 客户上级对应的用户
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )





    # tag_user = forms.CharField(
    #     required=True,
    #     error_messages = {
    #         'required': "关联用户不能为空"
    #     }
    #
    # )

