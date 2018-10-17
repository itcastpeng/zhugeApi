from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加
class AddForm(forms.Form):
    classificationName = forms.CharField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )
    parentClassification_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "父级分类类型错误"
        }
    )
    # goodsNum = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': '商品总数不能为空'
    #     })

    # xiaochengxu_app_id = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': '小程序ID不能为空'
    #     })
    # def clean_xiaochengxu_app_id(self):
    #     xiaochengxu_app_id = self.data.get('xiaochengxu_app_id')
    #     objs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxu_app_id)
    #     if not objs:
    #         self.add_error('xiaochengxu_app_id', '无此小程序！')
    #     else:
    #         return xiaochengxu_app_id

# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改ID不能为空"
        }
    )
    classificationName = forms.CharField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )
    parentClassification_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "父级分类类型错误"
        }
    )

    # xiaochengxu_app_id = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': '小程序不能为空'
    #     })
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.zgld_goods_classification_management.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '修改ID不存在！')
        else:
            return o_id

    # def clean_xiaochengxu_app_id(self):
    #     xiaochengxu_app_id = self.data.get('xiaochengxu_app_id')
    #     objs = models.zgld_shangcheng_jichushezhi.objects.filter(id=xiaochengxu_app_id)
    #     if not objs:
    #         self.add_error('xiaochengxu_app_id', '无此小程序！')
    #     else:
    #         return xiaochengxu_app_id



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