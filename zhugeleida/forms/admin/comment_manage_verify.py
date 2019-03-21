from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

# 添加企业的产品
class SetFocusGetRedPacketForm(forms.Form):

    is_focus_get_redpacket = forms.CharField(
        required=True,
        error_messages={
            'required': "关注领取红包是否开启不能为空"
        }
    )

    focus_get_money = forms.FloatField(
        required=False,
        error_messages={
            'required': "关注领取红包金额不能为空"
        }
    )

    max_single_money = forms.FloatField(
        required=False,
        error_messages={
            'required': "随机单个金额(元)不能为空"
        }
    )

    min_single_money = forms.FloatField(
        required=False,
        error_messages={
            'required': "随机单个金额(元)不能为空"
        }
    )

    focus_total_money = forms.IntegerField(
        required=True,
        error_messages={
            'required': "领取红包总金额不能为空"
        }
    )

    def clean_max_single_money(self):
        max_single_money = self.data['max_single_money']
        mode = self.data['mode']

        if  max_single_money:
            max_single_money = float(max_single_money)

            if max_single_money < 0.3 or max_single_money  > 200:
                self.add_error('max_single_money', '红包金额不能小于0.3元或大于200元')

            else:
                return max_single_money

        else:
            mode = int(mode)
            if mode == 1: #随机金额
                self.add_error('max_single_money', '最大随机金额不能为空')

    def clean_min_single_money(self):
        min_single_money = self.data['min_single_money']
        mode = self.data['mode']

        if  min_single_money:
            min_single_money = float(min_single_money)

            if min_single_money < 0.3 or min_single_money  > 200:
                self.add_error('max_single_money', '红包金额不能小于0.3元或大于200元')

            else:
                return min_single_money

        else:
            mode = int(mode)
            if mode == 1: #随机金额
                self.add_error('min_single_money', '最大随机金额不能为空')

    def clean_focus_get_money(self):
        focus_get_money = self.data['focus_get_money']
        mode = self.data['mode']

        if focus_get_money:
            focus_get_money = float(focus_get_money)

            if focus_get_money < 0.3 or focus_get_money  > 200:
                self.add_error('focus_get_money', '红包金额不能小于0.3元或大于200元')

            else:

                return focus_get_money
        else:
            mode = int(mode)
            if mode == 2:  # 固定金额
                self.add_error('focus_get_money', '固定金额不能为空')

# 查询
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误",
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


#增加活动
# class commentAddForm(forms.Form):
#
#     case_id = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': "案例ID不能为空"
#         }
#     )
#
#     company_id = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "公司ID不能为空"
#         }
#     )
#
#     title = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "标题不能为空"
#         }
#     )
#     summary = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "摘要不能为空"
#         }
#     )
#
#     comment_date = forms.DateTimeField(
#         required=True,
#         error_messages={
#             'required': "日记日期不能为空"
#         }
#     )
#
#     cover_picture  = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "封面不能为空"
#         }
#     )
#     content  = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "内容不能为空"
#         }
#     )
#
#     status = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': "状态不能为空"
#         }
#     )
#
#     cover_show_type = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': "展示类型不能为空"
#         }
#     )
#
#     def clean_comment_name(self):
#
#         company_id = self.data['company_id']
#         comment_name =  self.data['comment_name']
#
#         objs = models.zgld_comment.objects.filter(
#             comment_name=comment_name, company_id=company_id
#         )
#
#         if objs:
#             self.add_error('comment_name', '不能存在相同的文章名')
#         else:
#             return comment_name


# 修改案例
# class commentUpdateForm(forms.Form):
#     case_id = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': "案例ID不能为空"
#         }
#     )
#
#     company_id = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "公司ID不能为空"
#         }
#     )
#
#     title = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "标题不能为空"
#         }
#     )
#
#     summary = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "摘要不能为空"
#         }
#     )
#
#     comment_date = forms.DateTimeField(
#         required=True,
#         error_messages={
#             'required': "日记日期不能为空"
#         }
#     )
#
#     cover_picture = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "封面不能为空"
#         }
#     )
#     content = forms.CharField(
#         required=True,
#         error_messages={
#             'required': "内容不能为空"
#         }
#     )
#
#     status = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': "状态不能为空"
#         }
#     )
#
#     cover_show_type = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': "展示类型不能为空"
#         }
#     )
#
#     def clean_comment_name(self):
#         comment_id = self.data['comment_id']
#         company_id = self.data['company_id']
#         comment_name = self.data['comment_name']
#
#         objs = models.zgld_comment.objects.filter(
#             comment_name=comment_name, company_id=company_id
#         ).exclude(id=comment_id)
#
#         if objs:
#             self.add_error('comment_name', '不能存在相同的文章名')
#         else:
#             return comment_name



#修改活动
class ActivityUpdateForm(forms.Form):
    article_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "文章ID不能为空"
        }
    )
    mode  = forms.IntegerField(
        required=True,
        error_messages={
            'required': "红包发送方式不能为空"
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    activity_name = forms.CharField(
        required=True,
        error_messages={
            'required': "活动名称不能为空"
        }
    )

    activity_id = forms.CharField(
        required=True,
        error_messages={
            'required': "活动ID不能为空"
        }
    )


    activity_total_money = forms.IntegerField(
        required=True,
        error_messages={
            'required': "活动总金额不能为空"
        }
    )

    activity_single_money = forms.FloatField(
        required=False,
        error_messages={
            'required': "单个金额(元)不能为空"
        }
    )

    max_single_money = forms.FloatField(
        required=False,
        error_messages={
            'required': "随机单个金额(元)不能为空"
        }
    )

    min_single_money = forms.FloatField(
        required=False,
        error_messages={
            'required': "随机单个金额(元)不能为空"
        }
    )

    reach_forward_num = forms.IntegerField(
        required=True,
        error_messages={
            'required': "设置转发次数不能为空"
        }
    )

    start_time = forms.CharField(
        required=True,
        error_messages={
            'required': "设置转发次数不能为空"
        }
    )

    end_time = forms.CharField(
        required=True,
        error_messages={
            'required': "设置转发次数不能为空"
        }
    )

    reach_stay_time = forms.IntegerField(
        required=True,
        error_messages={
            'required': " 限制时间秒数 不能为空"
        }
    )

    is_limit_area = forms.CharField(
        required=True,
        error_messages={
            'required': "是否限制区域 不能为空"
        }
    )


    # 判断文章是否存在
    def clean_article_id(self):
        article_id = self.data['article_id']
        objs = models.zgld_article.objects.filter(id = article_id)

        if  not objs:
            self.add_error('article_id', '此文章不存在')

        else:
            return article_id

    def clean_activity_id(self):
        activity_id = self.data['activity_id']
        objs = models.zgld_article_activity.objects.filter(id = activity_id)

        if  not objs:
            self.add_error('activity_id', '此活动不存在')

        else:
            return activity_id

    def clean_max_single_money(self):
        max_single_money = self.data['max_single_money']
        mode = self.data['mode']

        if max_single_money:
            max_single_money = float(max_single_money)

            if max_single_money < 0.3 or max_single_money > 200:
                self.add_error('max_single_money', '红包金额不能小于0.3元或大于200元')

            else:
                return max_single_money

        else:
            mode = int(mode)
            if mode == 1:  # 随机金额
                self.add_error('max_single_money', '最大随机金额不能为空')

    def clean_min_single_money(self):
        min_single_money = self.data['min_single_money']
        mode = self.data['mode']

        if min_single_money:
            min_single_money = float(min_single_money)

            if min_single_money < 0.3 or min_single_money > 200:
                self.add_error('max_single_money', '红包金额不能小于0.3元或大于200元')

            else:
                return min_single_money

        else:
            mode = int(mode)
            if mode == 1:  # 随机金额
                self.add_error('min_single_money', '最大随机金额不能为空')

    def clean_activity_single_money(self):
        activity_single_money = self.data['activity_single_money']
        mode = self.data['mode']

        if activity_single_money:
            activity_single_money = float(activity_single_money)

            if activity_single_money < 0.3 or activity_single_money > 200:
                self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

            else:

                return activity_single_money
        else:
            mode = int(mode)
            if mode == 2:  # 固定金额
                self.add_error('activity_single_money', '固定金额不能为空')



class commentSelectForm(forms.Form):


    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误",
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
            'required': "公司ID不能为空"
        }
    )
    is_audit_pass = forms.IntegerField(
        required=True,
        error_messages={
            'required': "is_audit_pass不能为空"
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


class QueryFocusCustomerSelectForm(forms.Form):


    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误",
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
            'required': "公司ID不能为空"
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



class ArticleRedPacketSelectForm(forms.Form):


    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误",
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
            'required': "公司ID不能为空"
        }
    )

    article_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "文章ID不能为空"
        }
    )

    activity_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "活动ID不能为空"
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


# class ReviewcommentForm(forms.Form):
#     comment_id = forms.CharField(
#         required=True,
#         error_messages={
#             'required': '日记ID不能为空'
#         }
#     )
#
#     content = forms.CharField(
#         required=True,
#         error_messages={
#             'required': '内容不能为空'
#         }
#     )
#
#     def clean_article_id(self):
#         comment_id = self.data['comment_id']
#
#         objs = models.zgld_comment.objects.filter(
#             id=comment_id
#         )
#
#         if not objs:
#             self.add_error('comment_id', '文章不存在')
#         else:
#             return comment_id


class commentReviewSelectForm(forms.Form):

    comment_id = forms.IntegerField(
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


class PraisecommentForm(forms.Form):

    comment_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章ID不能为空'
        }
    )

    status = forms.IntegerField(
        required=False,
        error_messages={
            'required': "状态不能为空"
        }
    )


# 审核评论
class AuditDiaryForm(forms.Form):
    comments_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '评论ID不能为空'
        }
    )
    # user_id = forms.IntegerField(
    #     required=True,
    #     error_messages={
    #         'required': '评论ID不能为空'
    #     }
    # )
    is_audit = forms.IntegerField(
        required=True,
        error_messages={
            'required': '审核状态不能为空'
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司不能为空'
        }
    )
    def clean_comments_id(self):
        company_id = self.data.get('company_id')
        comments_id = self.data.get('comments_id')
        objs = models.zgld_diary_comment.objects.filter(
            diary__case__company_id=company_id,
            id=comments_id
        )
        if objs:
            if int(objs[0].is_audit_pass) == 0:
                return comments_id, objs
            else:
                self.add_error('comments_id', '该评论已审核')
        else:
            self.add_error('comments_id', '评论不存在')

    def clean_is_audit(self):
        is_audit = int(self.data.get('is_audit'))
        if is_audit in [0, 1]:
            return is_audit
        else:
            self.add_error('is_audit', '审核状态码错误')

# 删除评论
class DeleteDiaryForm(forms.Form):
    comments_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '评论ID不能为空'
        }
    )
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司不能为空'
        }
    )
    def clean_comments_id(self):
        company_id = self.data.get('company_id')
        comments_id = self.data.get('comments_id')
        objs = models.zgld_diary_comment.objects.filter(
            diary__case__company_id=company_id,
            id=comments_id
        )
        if objs:
            objs.delete()
        else:
            self.add_error('comments_id', '评论不存在')