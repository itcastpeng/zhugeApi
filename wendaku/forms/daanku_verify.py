from django import forms

from wendaku import models
from publickFunc import account
import datetime


# 添加答案信息
class DaankuAddForm(forms.Form):
    content = forms.CharField(
        required=True,
        error_messages={
            'required': "答案不能为空"
        }
    )
    # oper_user_id = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '审核人'
    #     })
    # cilei_id = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '词类'
    #     }
    # )
    # keshi_id = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '科室'
    #     }
    # )
    # daan_leixing_id = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '答案'
    #     }
    # )

    # 查询答案是否存在
    def clean_content(self):
        content = self.data['content']
        objs = models.DaAnKuTemp.objects.filter(
            content=content
        )
        if objs:
            self.add_error('content', '答案已存在')
        else:
            models.DaAnKuTemp.objects.create(content=content)
            return content


# 更新答案信息
class DaankuUpdateForm(forms.Form):
    tid = forms.IntegerField(
        required=True,
        error_messages={
            'required': '任务id不能为空'
        }
    )
    content = forms.CharField(
        required=True,
        error_messages={
            'required': '答案不能为空'
        }
    )

    cilei_id = forms.CharField(
        required=True,
        error_messages={
            'required': '词类名称不能为空'
        }
    )

    daan_leixing_id = forms.CharField(
        required=True,
        error_messages={
            'required': '答案类型不能为空'
        }
    )

    keshi_id = forms.CharField(
        required=True,
        error_messages={
            'required': '科室不能为空'
        }
    )

    oper_user_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    def clean_content(self):
        content = self.data['content']
        if "{" in content and '}' in content:
            return content
        else:
            self.add_error('content', '答案中未发现模板标记')

    # 判断角色是否存在
    # def clean_name(self):
    #     role_id = self.data['role_id']
    #     name = self.data['name']
    #     objs = models.CiLei.objects.filter(
    #         name=name,
    #     ).exclude(id=role_id)
    #     if objs:
    #         self.add_error('name', '答案类型已存在')
    #     else:
    #         return name


# 判断是否是数字
class DaankuSelectForm(forms.Form):
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
