from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

# 添加企业的产品
class jichushezhi(forms.Form):

    shangChengName = forms.CharField(
        required=True,
        error_messages={
            'required': "商城名称不能为空"
        }
    )

    lunbotu = forms.CharField(
        required=False,

    )

class zhifupeizhi(forms.Form):
    shangHuHao = forms.CharField(
        required=True,
        error_messages={
            'required': "商户号不能为空"
        }
    )

    shangHuMiYao = forms.CharField(
        required=True,
        error_messages={
            'required': "商户秘钥不能为空"
        }
    )

    def clean_shangHuHao(self):
        shangHuHao = self.data.get('shangHuHao')
        if len(shangHuHao) > 30:
            self.add_error('shangHuHao', '当前商户号长度{}, 不能超过30位！'.format(len(shangHuHao)))
        else:
            return shangHuHao
    def clean_shangHuMiYao(self):
        shangHuMiYao = self.data.get('shangHuMiYao')
        if len(shangHuMiYao) != 32:
            self.add_error('shangHuMiYao', '当前商户秘钥长度{}, 请输入32位正确秘钥！'.format(len(shangHuMiYao)))
        else:
            return shangHuMiYao

class yongjinshezhi(forms.Form):
    yongjin = forms.CharField(
        required=True,
        error_messages={
            'required': "佣金不能为空"
        }

    )

