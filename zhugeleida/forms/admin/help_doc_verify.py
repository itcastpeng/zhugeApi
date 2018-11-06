from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加公司信息
class ArticleAddForm(forms.Form):

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "文章标题不能为空"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )



# 更新用户信息
class ArticleUpdateForm(forms.Form):


    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "文章标题不能为空"
        }
    )


    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )

    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_help_doc.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id


# 判断是否是数字
class ArticleSelectForm(forms.Form):
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


