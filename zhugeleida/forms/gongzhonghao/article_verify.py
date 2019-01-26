from django import forms

from zhugeleida import models
from publicFunc import account
import datetime


# 添加公司信息
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
        print('----user_id ---title---->',user_id,title)
        objs = models.zgld_article.objects.filter(
            title=title,user_id=user_id
        )
        if objs:
            self.add_error('title', '文章名已存在')
        else:
            return title


# 更新用户信息
class ArticleUpdateForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

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

    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_article.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id

    # 判断公司名称是否存在
    def clean_title(self):
        article_id = self.data['article_id']
        user_id = self.data['user_id']
        title = self.data['title']
        objs = models.zgld_article.objects.filter(
            title=title,user_id=user_id
        ).exclude(id=article_id)

        if objs:
            self.add_error('title', '文章标题不能相同')
        else:
            return title


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


# 判断是否是数字
class ReviewArticleForm(forms.Form):
    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )


    content = forms.CharField(
        required=True,
        error_messages={
            'required': '内容不能为空'
        }
    )

    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_article.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id


# 判断是否是数字
class Forward_ArticleForm(forms.Form):
    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    uid = forms.CharField(
        required=True,
        error_messages={
            'required': '文章所属用户ID不能为空'
        }
    )

    customer_id = forms.CharField(
        required=True,
        error_messages={
            'required': '客户ID不能为空'
        }
    )

    forward_type = forms.CharField(
        required=True,
        error_messages={
            'required': '转发类型不能为空'
        }
    )

    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_article.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id



class MyarticleForm(forms.Form):
        article_id = forms.IntegerField(
            required=True,
            error_messages={
                'required': '文章ID不能为空'
            }
        )

        uid = forms.CharField(
            required=False,
            error_messages={
                'required': '文章所属用户ID不存在'
            }
        )

        parent_id = forms.CharField(
            required=False,
            error_messages={
                'required': '父ID不存在'
            }
        )

        def clean_article_id(self):
            article_id = self.data['article_id']

            objs = models.zgld_article.objects.filter(
                id=article_id
            )

            if not objs:
                self.add_error('article_id', '文章不存在')
            else:
                return article_id




class RecommendArticleSelectForm(forms.Form):
    article_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司ID不能为空'
        }
    )
    uid = forms.IntegerField(
        required=True,
        error_messages={
            'required': 'uidID不能为空'
        }
    )




class ArticleReviewSelectForm(forms.Form):
    article_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
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
            length = 20
        else:
            length = int(self.data['length'])
        return length




class LocationForm(forms.Form):
    x_num = forms.CharField(
        required=True,
        error_messages={
            'required': '经度不能为空'
        }
    )

    y_num = forms.CharField(
        required=True,
        error_messages={
            'required': '纬度不能为空'
        }
    )




class StayTime_ArticleForm(forms.Form):
    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    uid = forms.CharField(
        required=False,
        error_messages={
            'required': '文章所属用户ID不存在'
        }
    )

    customer_id = forms.CharField(
        required=True,
        error_messages={
            'required': '客户ID不存在'
        }
    )

    parent_id = forms.CharField(
        required=False,
        error_messages={
            'required': '父ID不存在'
        }
    )
    article_access_log_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户查看文章日志记录ID'
        }
    )

    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_article.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id

