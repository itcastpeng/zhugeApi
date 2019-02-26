from django import forms

import json
from zhugeleida import models
from publicFunc import account
import datetime
import re
from django.core.exceptions import ValidationError


# 判断查询通讯录验证
class TongxunluSelectForm(forms.Form):

    uid = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "UID不能为空",
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
        return  length


# 判断查询通讯录验证
class TongxunluUserList(forms.Form):
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "UID不能为空",
        }
    )
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
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


# 判断查询通讯录验证
class TongxunluUserListSelectForm(forms.Form):
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "UID不能为空",
        }
    )

    old_uid = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "old_uid 不能为空",
        }
    )

    type = forms.CharField(
        required=False,
        error_messages={
            'invalid': "type 不能为空",
        }
    )

    new_uid = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "new_uid 不能为空",
        }
    )

    customer_id_list = forms.CharField(
        required=False,
        error_messages={
            'invalid': "customer_id_list 不能为空",
        }
    )

    def clean_customer_id_list(self):
        customer_id_list = self.data.get('customer_id_list')
        type = self.data.get('type')
        if customer_id_list:
            customer_id_list = json.loads(customer_id_list)

            if type != 'all_customer' and len(customer_id_list) == 0:
                self.add_error('customer_id_list', 'customer_id_list不能为空')

        return customer_id_list

    def clean_new_uid(self):
        old_uid = self.data.get('old_uid')
        new_uid = self.data.get('new_uid')

        if old_uid == new_uid:
            self.add_error('new_uid', ' new_uid 和 new_uid不能一样')

        return new_uid


