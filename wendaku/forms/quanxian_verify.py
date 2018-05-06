from django import forms

from wendaku import models
from publickFunc import account
import datetime


# 添加
class AddForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作ID异常"
        }
    )

    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    path = forms.CharField(
        required=True,
        error_messages={
            'required': "访问路径不能为空"
        }
    )

    icon = forms.CharField(
        required=True,
        error_messages={
            'required': "图标不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "功能名称不能为空"
        }
    )

    pid_id = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "父级id类型异常"
        }
    )

    order_num = forms.IntegerField(
        required=True,
        error_messages={
            'required': "排序值不能为空",
            'invalid': "排序值只能为数组类型"
        }
    )

    component = forms.CharField(
        required=False
    )

    # 判断路径是否存在
    def clean_path(self):
        path = self.data['path']
        objs = models.QuanXian.objects.filter(
            path=path,
        )
        if objs:
            self.add_error('path', '路径已存在')
        else:
            return path

    # 判断功能名称是否存在
    def clean_title(self):
        title = self.data['title']
        objs = models.QuanXian.objects.filter(
            title=title,
        )
        if objs:
            self.add_error('title', '功能名称已存在')
        else:
            return title


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作ID异常"
        }
    )

    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    path = forms.CharField(
        required=True,
        error_messages={
            'required': "访问路径不能为空"
        }
    )

    icon = forms.CharField(
        required=True,
        error_messages={
            'required': "图标不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "功能名称不能为空"
        }
    )

    pid_id = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "父级id类型异常"
        }
    )

    order_num = forms.IntegerField(
        required=True,
        error_messages={
            'required': "排序值不能为空",
            'invalid': "排序值只能为数组类型"
        }
    )

    component = forms.CharField(
        required=False
    )

    # 判断路径是否存在
    def clean_path(self):
        path = self.data['path']
        o_id = self.data['o_id']
        objs = models.QuanXian.objects.filter(
            path=path,
        ).exclude(id=o_id)
        if objs:
            self.add_error('path', '路径已存在')
        else:
            return path

    # 判断功能名称是否存在
    def clean_title(self):
        title = self.data['title']
        o_id = self.data['o_id']
        objs = models.QuanXian.objects.filter(
            title=title,
        ).exclude(id=o_id)
        if objs:
            self.add_error('title', '功能名称已存在')
        else:
            return title

