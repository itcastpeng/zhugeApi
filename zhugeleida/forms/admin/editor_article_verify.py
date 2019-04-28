from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加文章
class ArticleAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "文章标题不能为空"
        }
    )

    summary = forms.CharField(
        required=True,
        error_messages={
            'required': "文章摘要不能为空"
        }
    )
    cover_picture = forms.CharField(
        required=True,
        error_messages={
            'required': "文章封面不能为空"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )


    # 查询用户名判断是否存在
    def clean_title(self):
        title = self.data['title']
        user_id = self.data['user_id']
        company_id = models.zgld_editor.objects.get(id=user_id).company_id

        objs = models.zgld_editor_article.objects.filter(
            title=title,
            user__company_id=company_id
        )
        if objs:
            self.add_error('title', '本公司已存在该文章名')
        else:
            return title, company_id


# 修改文章
class ArticleUpdateForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "文章标题不能为空"
        }
    )

    summary = forms.CharField(
        required=True,
        error_messages={
            'required': "文章摘要不能为空"
        }
    )
    cover_picture = forms.CharField(
        required=True,
        error_messages={
            'required': "文章封面不能为空"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改文章不能为空"
        }
    )

    # 查询用户名判断是否存在
    def clean_title(self):
        title = self.data['title']
        user_id = self.data['user_id']
        o_id = self.data['o_id']
        company_id = models.zgld_editor.objects.get(id=user_id).company_id

        objs = models.zgld_editor_article.objects.filter(
            title=title,
            user__company_id=company_id
        ).exclude(id=o_id)
        if objs:
            self.add_error('title', '本公司已存在该文章名')
        else:
            return title, company_id

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.zgld_editor_article.objects.filter(id=o_id)
        if objs:
            obj = objs[0]
            status = int(obj.status)
            if status in [1, 3]:
                return o_id
            else:
                if status == 2:
                    text = '审核'
                else:
                    text = '完成'
                self.add_error('o_id', '{}状态下, 不可修改'.format(text))
        else:
            self.add_error('o_id', '修改的文章不存在')


# 删除文章
class ArticleDeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '删除文章不能为空'
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.zgld_editor_article.objects.filter(id=o_id)
        if objs:
            obj = objs[0]
            status = int(obj.status)
            if status in [1, 3]:
                objs.delete()
                return o_id

            else:
                if status in [2]:
                    text = '待审核'
                else:
                    text = '已完成'
                self.add_error('o_id', '{}状态, 不可删除'.format(text))
        else:
            self.add_error('o_id', '删除文章不存在')

# 查询文章
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误"
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
            length = 10
        else:
            length = int(self.data['length'])
        return length

# 查询报名插件
class ReportSelectForm(forms.Form):
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
    activity_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': " 活动不能为空"
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

# 提交文章
class SubmitArticleForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '提交文章不能为空'
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.zgld_editor_article.objects.filter(id=o_id)
        if objs:
            obj = objs[0]
            status = int(obj.status)
            if status in [1, 3]:
                objs.update(status=2)
                return o_id
            else:
                if status != 4:
                    self.add_error('o_id', '请勿重复提交')
                else:
                    self.add_error('o_id', '已完成, 不可提交')
        else:
            self.add_error('o_id', '提交错误')






