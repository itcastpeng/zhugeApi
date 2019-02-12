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
    status = forms.CharField(
        required=True,
        error_messages={
            'required': 'status不能为空'
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
        ).exclude(status__in=[3])

        if objs:
            self.add_error('title', '文章名已存在')
        else:
            return title

# 添加公司信息
class LocalArticleAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )
    status = forms.CharField(
        required=True,
        error_messages={
            'required': 'status不能为空'
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
            title=title,company_id=1
        ).exclude(status__in=[3])

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

    status = forms.CharField(
        required=True,
        error_messages={
            'required': 'status不能为空'
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



class GzhArticleSelectForm(forms.Form):
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

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司ID不存在'
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




class MyarticleForm(forms.Form):
    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    uid = forms.CharField(
        required=False,
        error_messages={
            'required': '用户ID不存在'
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



class SyncMyarticleForm(forms.Form):
    media_id_list = forms.CharField(
        required=False,
        error_messages={
            'required': '素材列表不能为空'
        }
    )

    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': '公司ID不存在'
        }
    )

    source_url = forms.CharField(
        required=False,
        error_messages={
            'required': '图文页的URL不能为空'
        }
    )



# 判断是否是数字
class QueryarticleInfoForm(forms.Form):

    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )


# 判断是否是数字
class ThreadPictureForm(forms.Form):
    customer_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    company_id = forms.CharField(
        required=False,
        error_messages={
            'required': '公司ID不存在'
        }
    )

    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误",
        }
    )
    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if not self.data.get('current_page'):
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if not self.data.get('length'):
            length = 20
        else:
            length = int(self.data['length'])
        return length


class EffectRankingByLevelForm(forms.Form):
    level = forms.IntegerField(
        required=True,
        error_messages={
            'required': '层级不能为空'
        }
    )

    # uid = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': '文章所属用户ID不存在'
    #     }
    # )

    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章所属用户ID不存在'
        }
    )



    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误",
        }
    )
    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if not self.data.get('current_page'):
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if not self.data.get('length'):
            length = 20
        else:
            length = int(self.data['length'])
        return length


    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_article.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id


class EffectRankingByTableForm(forms.Form):
    level = forms.IntegerField(
        required=True,
        error_messages={
            'required': '层级不能为空'
        }
    )

    # uid = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': '文章所属用户ID不存在'
    #     }
    # )

    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章所属用户ID不存在'
        }
    )



    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误",
        }
    )
    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if not self.data.get('current_page'):
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if not self.data.get('length'):
            length = 20
        else:
            length = int(self.data['length'])
        return length


    def clean_article_id(self):
        article_id = self.data['article_id']

        objs = models.zgld_article.objects.filter(
            id=article_id
        )

        if not objs:
            self.add_error('article_id', '文章不存在')
        else:
            return article_id


class QueryCustomerTransmitForm(forms.Form):
    level = forms.CharField(
        required=True,
        error_messages={
            'required': '层级不能为空'
        }
    )


    article_id = forms.CharField(
        required=True,
        error_messages={
            'required': '文章所属用户ID不能为空'
        }
    )

    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误",
        }
    )
    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
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

    def clean_current_page(self):
        if not self.data.get('current_page'):
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if not self.data.get('length'):
            length = 20
        else:
            length = int(self.data['length'])
        return length


