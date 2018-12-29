#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com


from django import forms
from zhugeleida.public.check_complex_passwd import checkPassword
from publicFunc import account


class LoginForm(forms.Form):   # 重置密码
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)

    def clean_password1(self):
        password1 = self.data.get('password1')
        password2 = self.data.get('password2')

        if password1 == password2:
            if checkPassword(password1):
                return account.str_encrypt(password1.stip())

            self.add_error('password1', '密码复杂度检查未通过,请检查最小长度为八位,包含大小写字母和数字')
        else:
            self.add_error('password1', '两次密码输入不一致')

class ModifyPwdForm(forms.Form):   # 重置密码
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)

    def clean_password2(self):
        password1 = self.data.get('password1')
        password2 = self.data.get('password2')
        if password1 and password2:
            password1 = password1.strip()
            password2 = password2.strip()

        if password1 == password2:
            if checkPassword(password1):
                return account.str_encrypt(password2)

            self.add_error('password2', '密码复杂度检查未通过,请检查最小长度为八位,包含大小写字母和数字')
        else:
            self.add_error('password2', '两次密码输入不一致')