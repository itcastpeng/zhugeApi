from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError


class UpdateForm(forms.Form):

    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "订单ID不能为空"
        }
    )
    yingFuKuan = forms.FloatField(
        required=True,
        error_messages={
            'required': "应付款不能为空"
        }
    )
    phoneNumber = forms.CharField(
        required=True,
        error_messages={
            'required': "电话不能为空"
        }
    )

    # 判断企业产品是否存在
    def clean_o_id(self):
        o_id = self.data['o_id']
        objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '无此订单！')
        else:
            if objs[0].theOrderStatus != 1:
                self.add_error('o_id', '该订单已付款, 不可修改！')
            else:
                return o_id
    def clean_phoneNumber(self):
        phoneNumber = self.data.get('phoneNumber')
        phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
        res = re.search(phone_pat, phoneNumber)
        if res:
            return phoneNumber
        else:
            self.add_error('phoneNumber', '请输入正确手机号')

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
            length = 20
        else:
            length = int(self.data['length'])
        return length


class GoodsManagementSelectForm(forms.Form):


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

