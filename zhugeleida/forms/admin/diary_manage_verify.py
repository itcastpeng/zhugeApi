from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError

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
            length = 10
        else:
            length = int(self.data['length'])
        return length


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


# 增加日记
class diaryAddForm(forms.Form):

    case_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "日记ID不能为空"
        }
    )

    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "标题不能为空"
        }
    )

    diary_date = forms.DateTimeField(
        required=True,
        error_messages={
            'required': "日记日期不能为空"
        }
    )

    content  = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )

    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "状态不能为空"
        }
    )

    cover_show_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "展示类型不能为空"
        }
    )

    cover_picture = forms.CharField(
        required=False,
        error_messages={
            'required': "普通日记-轮播图/日记类型错误"
        }
    )
    def clean_diary_name(self):

        company_id = self.data['company_id']
        diary_name =  self.data['diary_name']

        objs = models.zgld_diary.objects.filter(
            diary_name=diary_name, company_id=company_id
        )

        if objs:
            self.add_error('diary_name', '不能存在相同的文章名')
        else:
            return diary_name

    def clean_case_id(self):
        case_id = self.data.get('case_id')
        cover_picture = self.data.get('cover_picture')
        company_id = self.data.get('company_id')
        objs = models.zgld_case.objects.filter(id=case_id, company_id=company_id)
        if objs:
            obj = objs[0]
            case_type = obj.case_type
            if int(obj.case_type) == 1:
                if not cover_picture:
                    self.add_error('cover_picture', '轮播图不能为空')
                else:
                    return case_id, case_type
            return case_id, case_type
        else:
            self.add_error('case_id', '权限不足')


# 修改案例
class diaryUpdateForm(forms.Form):
    diary_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改日记不能为空"
        }
    )
    case_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "日记列表ID不能为空"
        }
    )

    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "标题不能为空"
        }
    )

    summary = forms.CharField(
        required=False,
        error_messages={
            'required': "摘要不能为空"
        }
    )

    diary_date = forms.DateTimeField(
        required=True,
        error_messages={
            'required': "日记日期不能为空"
        }
    )

    cover_picture = forms.CharField(
        required=False,
        error_messages={
            'required': "封面不能为空"
        }
    )
    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )

    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "状态不能为空"
        }
    )

    cover_show_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "展示类型不能为空"
        }
    )

    def clean_diary_name(self):
        diary_id = self.data['diary_id']
        company_id = self.data['company_id']
        diary_name = self.data['diary_name']

        objs = models.zgld_diary.objects.filter(
            diary_name=diary_name, company_id=company_id
        ).exclude(id=diary_id)

        if objs:
            self.add_error('diary_name', '不能存在相同的文章名')
        else:
            return diary_name
    def clean_diary_id(self):
        diary_id = self.data.get('diary_id')
        objs = models.zgld_diary.objects.filter(id=diary_id)
        if objs:
            return diary_id
        else:
            self.add_error('diary_id', '修改日记不存在')
    def clean_case_id(self):
        case_id = self.data.get('case_id')
        cover_picture = self.data.get('cover_picture')
        company_id = self.data.get('company_id')
        objs = models.zgld_case.objects.filter(id=case_id, company_id=company_id)
        if objs:
            obj = objs[0]
            case_type = obj.case_type
            if int(case_type) == 1:
                if not cover_picture:
                    self.add_error('cover_picture', '轮播图不能为空')
                else:
                    return case_id, case_type
            return case_id, case_type
        else:
            self.add_error('case_id', '权限不足')


# 修改活动
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



class diarySelectForm(forms.Form):


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

# 客户评论
class ReviewDiaryForm(forms.Form):
    diary_id = forms.CharField(
        required=True,
        error_messages={
            'required': '日记ID不能为空'
        }
    )

    comments = forms.CharField(
        required=True,
        error_messages={
            'required': '内容不能为空'
        }
    )
    # reply_comment = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '回复评论类型错误'
    #     }
    # )
    def clean_diary_id(self):
        diary_id = self.data['diary_id']

        objs = models.zgld_diary.objects.filter(
            id=diary_id
        )

        if not objs:
            self.add_error('diary_id', '日记不存在')
        else:
            return diary_id, objs

    # def clean_reply_comment(self):
    #     reply_comment = self.data.get('reply_comment')  # 回复评论ID
    #     diary_id = self.data.get('diary_id')
    #     if reply_comment:
    #         objs = models.zgld_diary_comment.objects.filter(diary_id=diary_id, id=reply_comment)
    #         if objs:
    #             return reply_comment
    #         else:
    #             self.add_error('reply_comment', '评论失败')


# 查询评论
class DiaryReviewSelectForm(forms.Form):

    diary_id = forms.IntegerField(
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

    def clean_diary_id(self):
        diary_id = self.data.get('diary_id')
        objs = models.zgld_diary.objects.filter(id=diary_id)
        if objs:
            return diary_id
        else:
            self.add_error('diary_id', '日记不存在')


class PraiseDiaryForm(forms.Form):

    diary_id = forms.IntegerField(
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



# 点赞
class CollectionDiaryForm(forms.Form):
    case_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '日记ID不能为空'
        }
    )

    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )
    case_type = forms.IntegerField(
        required=False,
        error_messages={
            'required': "日记类型不能为空"
        }
    )
    diary_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "时间轴ID类型错误"
        }
    )

    def clean_diary_id(self):
        diary_id = self.data.get('diary_id')
        if diary_id:
            objs = models.zgld_diary.objects.filter(id=diary_id)
            if objs:
                obj = objs[0]
                if int(obj.case.case_type) == 2:
                    return diary_id
                else:
                    self.add_error('diary_id', '此日记不是时间轴日记')
            else:
                self.add_error('diary_id', '时间轴ID错误')