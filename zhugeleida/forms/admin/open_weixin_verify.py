from django import forms

# 添加企业的产品
class UpdateIDForm(forms.Form):
    authorization_appid = forms.CharField(
        required=True,
        error_messages={
            'required': "authorization_appid 不能为空"
        }
    )

    three_services_type = forms.IntegerField(
        required=False,
        error_messages={
            'required': "三方类型区分 不能为空"
        }
    )

class UpdateInfoForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "小程序名称不能为空"
        }
    )

    head_img = forms.CharField(
        required=True,
        error_messages={
            'required': "小程序头像不能为空"
        }
    )
    introduce = forms.CharField(
        required=False,
        error_messages={
            'required': "小程序头像不能为空"
        }
    )

    service_category = forms.CharField(
        required=True,
        error_messages={
            'required': "服务类目不能为空"
        }
    )
