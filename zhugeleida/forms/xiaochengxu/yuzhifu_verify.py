from django import forms

from zhugeleida import models
from publicFunc import account
import datetime, random, time, re


class yuZhiFu(forms.Form):
    phoneNumber = forms.IntegerField(
        required=True,
        error_messages={
            'required': "手机号不能为空"
        }
    )

    def clean_phoneNumber(self):
        phoneNumber = self.data.get('phoneNumber')
        phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
        res = re.search(phone_pat, phoneNumber)
        if not res:
            self.add_error('phoneNumber', '请输入正确的手机号')
        else:
            return phoneNumber











