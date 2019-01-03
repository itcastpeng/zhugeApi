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

    focus_get_money = forms.IntegerField(
        required=True,
        error_messages={
            'required': "关注领取红包金额不能为空"
        }
    )

    focus_total_money = forms.IntegerField(
        required=True,
        error_messages={
            'required': "领取红包总金额不能为空"
        }
    )


#增加活动
class ActivityAddForm(forms.Form):
    article_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "文章ID不能为空"
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

    mode  = forms.IntegerField(
        required=True,
        error_messages={
            'required': "红包发送方式不能为空"
        }
    )


    activity_total_money = forms.IntegerField(
        required=True,
        error_messages={
            'required': "活动总金额不能为空"
        }
    )

    activity_single_money = forms.FloatField(
        required=True,
        error_messages={
            'required': "单个金额(元)不能为空"
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
            'required': "设置开始时间不能为空"
        }
    )

    end_time = forms.CharField(
        required=True,
        error_messages={
            'required': "设置结束时间不能为空"
        }
    )

    reach_stay_time = forms.IntegerField(
        required=True,
        error_messages={
            'required': " reach_stay_time 不能为空"
        }
    )

    is_limit_area = forms.CharField(
        required=True,
        error_messages={
            'required': "是否限制区域"
        }
    )


    def clean_activity_single_money(self):
        activity_single_money = self.data['activity_single_money']

        if  activity_single_money:
            activity_single_money = int(activity_single_money)

            _activity_single_money = str(activity_single_money)
            if '-' in _activity_single_money:

                max_single_money =  _activity_single_money.split('-')[0]
                min_single_money = _activity_single_money.split('-')[1]

                max_single_money = int(max_single_money)
                min_single_money = int(min_single_money)

                if max_single_money >= 0.3 and max_single_money  <= 200:
                    self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

                elif min_single_money >= 0.3 and min_single_money  <= 200:
                    self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

                else:
                    return activity_single_money

            else:

                if activity_single_money >= 0.3 and activity_single_money  <= 200:
                    self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

                else:
                    return activity_single_money


    def clean_start_time(self):
        start_time = self.data['start_time']
        end_time = self.data['end_time']

        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        if start_time >= end_time:
            return self.add_error('start_time', '开始时间不能大于结束时间')

        return start_time

    # 判断文章是否存在
    def clean_end_time(self):
        end_time = self.data['end_time']
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if end_time <= datetime.datetime.now():
            return self.add_error('end_time', '结束时间不能小于当前时间')

        return end_time


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
        required=True,
        error_messages={
            'required': "单个金额(元)不能为空"
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

    def clean_activity_single_money(self):
        activity_single_money = self.data['activity_single_money']

        if  activity_single_money:
            activity_single_money = int(activity_single_money)

            _activity_single_money = str(activity_single_money)
            if '-' in _activity_single_money:

                max_single_money =  _activity_single_money.split('-')[0]
                min_single_money = _activity_single_money.split('-')[1]

                max_single_money = int(max_single_money)
                min_single_money = int(min_single_money)

                if max_single_money >= 0.3 and max_single_money  <= 200:
                    self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

                elif min_single_money >= 0.3 and min_single_money  <= 200:
                    self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

                else:
                    return activity_single_money

            else:

                if activity_single_money >= 0.3 and activity_single_money  <= 200:
                    self.add_error('activity_single_money', '红包金额不能小于0.3元或大于200元')

                else:
                    return activity_single_money



class ActivitySelectForm(forms.Form):


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


