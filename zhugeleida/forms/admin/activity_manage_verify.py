from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

# 添加企业的产品
class SetFocusGetRedPacketForm(forms.Form):

    is_focus_get_redpacket = forms.CharField(
        required=True,
        error_messages={
            'required': "关注领取红包是否开启不能为空"
        }
    )

    focus_get_money = forms.IntegerField(
        required=True,
        error_messages={
            'required': "关注领取红包金额不能为空"
        }
    )


# 修改企业的产品
class ProductGetForm(forms.Form):
    uid = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )
    product_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "产品ID不能为空"
        }
    )


    def clean_uid(self):

        user_id = self.data['uid']
        objs = models.zgld_admin_userprofile.objects.filter(
            id=user_id,
        )
        if not objs:
            self.add_error('uid', '用户名不存在')
        else:
            return user_id

    # 判断企业产品名称是否存在
    def clean_product_id(self):
        product_id = self.data['product_id']
        objs = models.zgld_product.objects.filter(id = product_id)

        if  not objs:
            self.add_error('product_id', '产品不存在')

        else:
            return product_id


class ProductSelectForm(forms.Form):

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )

    product_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "产品类型不为空"
        }
    )



    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误",
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
            length = 20
        else:
            length = int(self.data['length'])
        return length


# 添加企业的产品
class imgUploadForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "图片名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    img_data = forms.CharField(
        error_messages={
            'required': "图片内容不能为空"
        }
    )

    chunk = forms.IntegerField(
        error_messages={
            'required': "当前是第几份文件不能为空",
            'invalid': '份数必须是整数类型'
        }
    )


# 添加企业的产品
class imgMergeForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "文件名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    chunk_num = forms.IntegerField(
        error_messages={
            'required': "总份数不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )


    picture_type = forms.IntegerField(
        error_messages={
            'required': "图片不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )


class FeedbackSelectForm(forms.Form):


    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误",
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
            length = 20
        else:
            length = int(self.data['length'])
        return length



