from django import forms


# 验证指标的传参
class QueryHaveCustomerDetailForm(forms.Form):
    # type = forms.CharField(
    #     required=True,
    #     error_messages={
    #         # 'required': "天数不能为空",
    #         'invalid': "类型不能为空",
    #     }
    # )

    days = forms.CharField(
        required=False,
        error_messages={
            # 'required': "天数不能为空",
            'invalid': "天数不能为空",
        }
    )
    query_user_id = forms.CharField(
        required=True,
        error_messages={
            # 'required': "类型不能为空",
            'invalid': "查询用户ID不能为空"
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

    # def clean_article_id(self):
    #     article_id = self.data['article_id']
    #
    #     objs = models.zgld_article.objects.filter(
    #         id=article_id
    #     )
    #
    #     if not objs:
    #         self.add_error('article_id', '文章不存在')
    #     else:
    #         return article_id

    def clean_current_page(self):
        if not self.data.get('current_page'):
            current_page = 1
        else:
            current_page = int(self.data['current_page'])

        return current_page

    def clean_length(self):
        if not self.data.get('length'):
            length = 10
        else:
            length = int(self.data['length'])

        return length


class QueryHudongHaveCustomerDetailPeopleForm(forms.Form):
    type = forms.CharField(
        required=True,
        error_messages={
            # 'required': "类型不能为空",
            'invalid': "类型不能为空"
        }
    )

    days = forms.CharField(
        required=True,
        error_messages={
            # 'required': "天数不能为空",
            'invalid': "天数不能为空",
        }
    )
    query_user_id = forms.CharField(
        required=True,
        error_messages={
            # 'required': "类型不能为空",
            'invalid': "查询用户ID不能为空"
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

    # def clean_article_id(self):
    #     article_id = self.data['article_id']
    #
    #     objs = models.zgld_article.objects.filter(
    #         id=article_id
    #     )
    #
    #     if not objs:
    #         self.add_error('article_id', '文章不存在')
    #     else:
    #         return article_id

    def clean_current_page(self):
        if not self.data.get('current_page'):
            current_page = 1
        else:
            current_page = int(self.data['current_page'])

        return current_page

    def clean_length(self):
        if not self.data.get('length'):
            length = 5
        else:
            length = int(self.data['length'])

        return length

# 验证数据指标的传参
class LineInfoForm(forms.Form):
    # days = forms.CharField(
    #     required=True,
    #     error_messages={
    #         # 'required': "天数不能为空",
    #         'invalid': "天数不能为空",
    #     }
    # )
    index_type = forms.CharField(
        required=False,
        error_messages={
            # 'required': "类型不能为空",
            'invalid': "必须是整数类型"
        }
    )

