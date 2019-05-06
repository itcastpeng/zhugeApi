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


# 增加日记
class diaryAddForm(forms.Form):

    case_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "日记ID不能为空"
        }
    )
    company_id = forms.IntegerField(
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
        diary_name =  self.data.get('diary_name')
        company_id =  self.data.get('company_id')
        objs = models.zgld_diary.objects.filter(
            title=diary_name,
            company_id=company_id,
        )
        if objs:
            self.add_error('diary_name', '不能存在相同的文章名')
        else:
            return diary_name

    def clean_case_id(self):
        case_id = self.data.get('case_id')
        cover_picture = self.data.get('cover_picture')
        objs = models.zgld_editor_case.objects.filter(id=case_id)
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


# 修改日记
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
    company_id = forms.IntegerField(
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

    cover_show_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "展示类型不能为空"
        }
    )

    def clean_diary_name(self):
        diary_id = self.data.get('diary_id')
        company_id = self.data.get('company_id')
        diary_name = self.data.get('diary_name')

        objs = models.zgld_editor_diary.objects.filter(
            title=diary_name,
            company_id=company_id

        )

        if objs:
            self.add_error('diary_name', '不能存在相同的文章名')
        else:
            return diary_name
    def clean_diary_id(self):
        diary_id = self.data.get('diary_id')
        objs = models.zgld_editor_diary.objects.filter(id=diary_id)
        if objs:
            return diary_id
        else:
            self.add_error('diary_id', '修改日记不存在')
    def clean_case_id(self):
        case_id = self.data.get('case_id')
        cover_picture = self.data.get('cover_picture')
        objs = models.zgld_editor_case.objects.filter(id=case_id)
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


# 删除日记
class DeleteDiaryForm(forms.Form):
    diary_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "删除日记不能为空"
        }
    )

    def clean_diary_id(self):
        diary_id = self.data.get('diary_id')
        objs = models.zgld_editor_diary.objects.filter(id=diary_id)
        if objs:
            obj = objs[0]
            status = int(obj.status)
            if status in [1, 3]:
                objs.delete()
                return diary_id
            else:
                if status in [2]:
                    text = '待审核'
                else:
                    text = '已完成'
                self.add_error('diary_id', '日记{}状态不能删除'.format(text))
        else:
            self.add_error('diary_id', '删除日记不存在')


# 提交日记
class SubmitDiaryForm(forms.Form):
    diary_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "提交日记不能为空"
        }
    )

    def clean_diary_id(self):
        diary_id = self.data.get('diary_id')
        objs = models.zgld_editor_diary.objects.filter(id=diary_id)
        if objs:
            obj = objs[0]
            case_status = int(obj.case.status)
            if case_status in [4]: # 如果案例审核 通过
                status = int(obj.status)
                if status in [1, 3]:
                    objs.update(status=2)
                    return diary_id
                else:
                    if status in [2]:
                        text = '审核状态, 不可提交'
                    else:
                        text = '完成状态, 请勿重复提交'
                    self.add_error('diary_id', '{}'.format(text))
            else:
                self.add_error('diary_id', '请先提交审核 该日记的案例')
        else:
            self.add_error('diary_id', '提交日记不存在')








