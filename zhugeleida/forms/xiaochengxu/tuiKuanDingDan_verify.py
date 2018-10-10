from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

# 添加退款单
class AddForm(forms.Form):
    orderNumber = forms.IntegerField(
        required=True,
        error_messages={
            'required': "订单ID不能为空"
        }
    )
    tuiKuanYuanYin = forms.IntegerField(
        required=True,
        error_messages={
            'required': "退款原因不能为空"
        }
    )
    # 判断企业产品是否存在
    def clean_orderNumber(self):
        orderNumber = self.data['orderNumber']
        objs = models.zgld_shangcheng_dingdan_guanli.objects.filter(id=orderNumber)
        if not objs:
            self.add_error('orderNumber', '无此订单！')
        else:
            tuiKuanObjs = models.zgld_shangcheng_tuikuan_dingdan_management.objects.filter(orderNumber_id=orderNumber)
            if not tuiKuanObjs:
                return orderNumber
            else:
                self.add_error('orderNumber', '该订单已退款, 请勿重复操作！')

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


