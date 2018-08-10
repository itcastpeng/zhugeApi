from django import forms
from zhugeleida import models


class CommitCodeInfoForm(forms.Form):
    customer_id = forms.CharField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )

    template_id = forms.CharField(
        required=True,
        error_messages={
            'required': "代码模版ID不能为空"
        }
    )

    ext_json = forms.CharField(
        required=True,
        error_messages={
            'required': "自定义的配置不能为空"
        }
    )
    user_version = forms.CharField(
        required=True,
        error_messages={
            'required': "代码版本号不能为空"
        }
    )

    user_desc = forms.CharField(
        required=True,
        error_messages={
            'required': "代码描述不能为空"
        }
    )

    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        obj = models.zgld_xiaochengxu_app.objects.filter(user_id=customer_id)
        if not obj:
            self.add_error('customer_id', '小程序关联的用户不存在')
        else:
            authorizer_refresh_token = obj[0].authorizer_refresh_token
            if not authorizer_refresh_token:
                self.add_error('customer_id', '小程序刷新令牌authorizer_refresh_token不存在')
            else:
                return customer_id


class GetqrCodeForm(forms.Form):
    customer_id = forms.CharField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )

    path = forms.CharField(
        #指定体验版二维码跳转到某个具体页面（如果不需要的话，则不需要填path参数)
        required=False,
        error_messages={
            'required': "跳转Path不能为空"
        }
    )


    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        obj = models.zgld_xiaochengxu_app.objects.filter(user_id=customer_id)
        if not obj:
            self.add_error('customer_id', '小程序关联的用户不存在')
        else:
            authorizer_refresh_token = obj[0].authorizer_refresh_token
            if not authorizer_refresh_token:
                self.add_error('customer_id', '小程序刷新令牌authorizer_refresh_token不存在')
            else:
                return customer_id

class SubmitAuditForm(forms.Form):
    customer_id = forms.CharField(
        required=True,
        error_messages={
            'required': "客户ID不能为空"
        }
    )



    def clean_customer_id(self):
        customer_id = self.data['customer_id']
        obj = models.zgld_xiaochengxu_app.objects.filter(user_id=customer_id)
        if not obj:
            self.add_error('customer_id', '小程序关联的用户不存在')
        else:
            authorizer_refresh_token = obj[0].authorizer_refresh_token
            if not authorizer_refresh_token:
                self.add_error('customer_id', '小程序刷新令牌authorizer_refresh_token不存在')
            else:
                return customer_id

