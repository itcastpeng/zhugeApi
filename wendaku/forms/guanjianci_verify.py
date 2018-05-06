from django import forms
from wendaku import models

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

    content = forms.CharField(
        required=True,
        error_messages={
         'required' : '关键词不能为空'
        }
    )
    # 判断问题是否存在
    def clean_content(self):
        content = self.data['content']
        objs = models.GuanJianCi.objects.filter(
            content=content,
        )
        if objs:
            self.add_error('content', '该关键词已存在')
        else:
            return content


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

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "关键词不能为空"
        }
    )
    # 判断关键词是否存在
    def clean_path(self):
        content = self.data['content']
        o_id = self.data['o_id']
        objs = models.GuanJianCi.objects.filter(
            content=content,
        ).exclude(id=o_id)
        if objs:
            self.add_error('content', '关键词已存在')
        else:
            return content

# 判断是否是数字
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