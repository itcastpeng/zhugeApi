from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加
class AddForm(forms.Form):
    goodsName = forms.CharField(
        required=True,
        error_messages={
            'required': "商品名称不能为空"
        }
    )

    parentName = forms.IntegerField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )

    goodsPrice = forms.FloatField(
        required=True,
        error_messages={
            'required': '商品标价不能为空'
        }
    )
    DetailsDescription = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    # inventoryNum = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': "商品库存不能为空"
    #     }
    # )

    xianshangjiaoyi = forms.BooleanField(
        required=False,
        error_messages={
            'required': "是否线上交易类型错误"
        }
    )

    shichangjiage = forms.IntegerField(
        required=False,
        error_messages={
            'required': "市场价格类型错误"
        }
    )

    # kucunbianhao = forms.CharField(
    #     required=False,
    #     error_messages={
    #         'required': "库存编号不能为空"
    #     }
    # )

    goodsStatus = forms.IntegerField(
        required=True,
        error_messages={
            'required': "商品状态不能为空"
        }
    )
    def clean_DetailsDescription(self):
        DetailsDescription = self.data.get('DetailsDescription')
        if DetailsDescription:
            if len(DetailsDescription) > 1024:
                self.add_error('DetailsDescription', '描述详情长度不可超过1024')
            else:
                return DetailsDescription
# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改ID不能为空"
        }
    )
    DetailsDescription = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    goodsName = forms.CharField(
        required=True,
        error_messages={
            'required': "商品名称不能为空"
        }
    )

    parentName = forms.IntegerField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )

    goodsPrice = forms.FloatField(
        required=True,
        error_messages={
            'required': '商品标价不能为空'
        }
    )

    goodsStatus = forms.IntegerField(
        required=True,
        error_messages={
            'required': "商品状态不能为空"
        }
    )
    xianshangjiaoyi = forms.BooleanField(
        required=False,
        error_messages={
            'required': "是否线上交易类型错误"
        }
    )
    shichangjiage = forms.IntegerField(
        required=False,
        error_messages={
            'required': "市场价格类型错误"
        }
    )
    # kucunbianhao = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': "库存编号不能为空"
    #     }
    # )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.zgld_goods_management.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '修改ID不存在！')
        else:
            return o_id
    def clean_DetailsDescription(self):
        DetailsDescription = self.data.get('DetailsDescription')
        if DetailsDescription:
            if len(DetailsDescription) > 1024:
                self.add_error('DetailsDescription', '描述详情长度不可超过1024')
            else:
                return DetailsDescription


class SelectForm(forms.Form):
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