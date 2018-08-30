from django import forms

from zhugeleida import models
from publicFunc import account
import datetime



class GongzhonghaoAddForm(forms.Form):
    # print('添加标签')
    # source = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': "客户来源不能为空"
    #     }
    # )


    state = forms.CharField(
        required=True,
        error_messages={
            'required': "验证的方式不能为空"
        }
    )

    # user_type = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': "客户访问类型不能为空"
    #     }
    # )
    code = forms.CharField(
        required=True,
        error_messages={
            'required': "code不能为空"
        }
    )

    # uid = forms.IntegerField(
    #     # 客户上级对应的用户
    #     required=False,
    #
    # )

    appid = forms.CharField(
        required=True,
        error_messages={
            'required': "appid不能为空"
        }
    )
    pid = forms.CharField(
        required=False,
        error_messages={
            'required': "pid 不能为空"
        }
    )
    level = forms.CharField(
        required=False,
        error_messages={
            'required': "pid 不能为空"
        }
    )

    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': "article_id 不能为空"
        }
    )

    # def clean_company_id(self):
    #     company_id = self.data['company_id']
    #     company_obj = models.zgld_company.objects.filter(id=company_id)
    #     if not company_obj:
    #         self.add_error('company_id', '公司不存在')
    #     else:
    #         return company_id




class LoginBindingForm(forms.Form):
    # print('添加标签')
    # source = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': "客户来源不能为空"
    #     }
    # )



    pid = forms.IntegerField(
        # 客户上级对应的用户
        required=False,
        error_messages={
            'required': "用户ID不能为空"
        }

    )
    user_id = forms.IntegerField(
        # 客户上级对应的用户
        required=True,
        error_messages={
            'required': "文章ID不能为空"
        }
    )
    level = forms.IntegerField(
        # 客户上级对应的用户
        required=True,
        error_messages={
            'required': "层级不能为空"
        }
    )

    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': "article_id 不能为空"
        }
    )
