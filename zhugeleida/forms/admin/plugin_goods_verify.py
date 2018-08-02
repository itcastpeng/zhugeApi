from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

# 添加企业的产品
class PluginGoodsAddForm(forms.Form):

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )
    title = forms.CharField(
        required=True,
        error_messages={
            'required': "标题不能为空"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )

    # 判断企业产品是否存在
    def clean_title(self):
        title = self.data['title']
        user_id = self.data.get('user_id')

        objs = models.zgld_plugin_goods.objects.filter(
            title=title,user_id=user_id
        )
        if objs:
            self.add_error('title', '商品名称不能重复')
        else:
            return title

# 修改企业的产品
class PluginGoodsUpdateForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "用户ID不能为空"
        }
    )

    goods_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "商品ID不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "标题不能为空"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )

    # 判断企业产品是否存在
    def clean_title(self):

        goods_id = self.data['goods_id']
        title = self.data['title']
        user_id = self.data.get('user_id')

        objs = models.zgld_plugin_goods.objects.filter(
            title=title, user_id=user_id
        ).exclude(id=goods_id)
        if objs:
            self.add_error('title', '商品名称不能重复')
        else:
            return title

    # 判断企业产品名称是否存在
    def clean_goods_id(self):
        goods_id = self.data.get('goods_id')
        user_id = self.data.get('user_id')

        objs = models.zgld_plugin_goods.objects.filter(id = goods_id,user_id=user_id)

        if  not  objs:
            self.add_error('goods_id', '商品不存在')

        else:
            return goods_id


class PluginGoodsSelectForm(forms.Form):

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

