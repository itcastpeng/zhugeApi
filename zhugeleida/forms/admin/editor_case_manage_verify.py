from django import forms
from zhugeleida import models
from publicFunc import account
import datetime
import re
import json
from django.core.exceptions import ValidationError



# 增加案例
class CaseAddForm(forms.Form):


    case_name = forms.CharField(
        required=True,
        error_messages={
            'required': "案例名称不能为空"
        }
    )

    customer_name = forms.CharField(
        required=True,
        error_messages={
            'required': "客户名字不能为空"
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    headimgurl  = forms.CharField(
        required=True,
        error_messages={
            'required': "头像不能为空"
        }
    )

    case_type  = forms.IntegerField(
        required=True,
        error_messages={
            'required': "案例类型不能为空"
        }
    )

    tags_id_list = forms.CharField(
        required=True,
        error_messages={
            'required': "案例标签不能为空"
        }
    )
    become_beautiful_cover = forms.CharField(
        required=False,
        error_messages={
            'required': "变美图片类型错误"
        }
    )
    cover_picture = forms.CharField(
        required=False,
        error_messages={
            'required': "封面图片类型错误"
        }
    )
    def clean_case_name(self):
        company_id =  self.data['company_id']
        case_name =  self.data['case_name']
        objs = models.zgld_case.objects.filter(
            case_name=case_name,
            company_id=company_id
        )

        if objs:
            self.add_error('case_name', '不能存在相同的案例名')
        else:
            return case_name

    def clean_tags_id_list(self):
        tags_id_list = self.data.get('tags_id_list')
        tags_id_list = json.loads(tags_id_list)
        if len(tags_id_list) <= 0:
            self.add_error('tags_id_list', '标签不能为空')
        else:
            return tags_id_list

    def clean_case_type(self):
        case_type = int(self.data.get('case_type'))          # 日记列表类型
        become_beautiful_cover = self.data.get('become_beautiful_cover')  # 变美图片
        cover_picture = self.data.get('cover_picture')  # 封面
        if case_type == 2: # 时间轴日记
            if not become_beautiful_cover:
                self.add_error('become_beautiful_cover', '变美图片不能为空')
            if not cover_picture:
                self.add_error('cover_picture', '封面图片不能为空')
        return case_type

# 修改案例
class CaseUpdateForm(forms.Form):

    case_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "案例ID不能为空"
        }
    )

    case_name = forms.CharField(
        required=True,
        error_messages={
            'required': "案例名称不能为空"
        }
    )

    customer_name = forms.CharField(
        required=True,
        error_messages={
            'required': "客户名字不能为空"
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    headimgurl = forms.CharField(
        required=True,
        error_messages={
            'required': "头像不能为空"
        }
    )
    case_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "案例类型不能为空"
        }
    )

    tags_id_list = forms.CharField(
        required=True,
        error_messages={
            'required': "案例标签不能为空"
        }
    )
    become_beautiful_cover = forms.CharField(
        required=False,
        error_messages={
            'required': "变美图片类型错误"
        }
    )
    cover_picture = forms.CharField(
        required=False,
        error_messages={
            'required': "封面图片类型错误"
        }
    )

    def clean_case_name(self):

        case_id = self.data['case_id']
        company_id = self.data['company_id']
        case_name = self.data['case_name']

        objs = models.zgld_case.objects.filter(
            case_name=case_name,
            company_id=company_id,
        )

        if objs:
            self.add_error('case_name', '不能存在相同的案例名')
        else:
            return case_name

    def clean_case_type(self):
        case_type = int(self.data.get('case_type'))  # 日记列表类型
        become_beautiful_cover = self.data.get('become_beautiful_cover')  # 变美图片
        cover_picture = self.data.get('cover_picture')  # 封面
        if case_type == 2:  # 时间轴日记
            if not become_beautiful_cover:
                self.add_error('become_beautiful_cover', '变美图片不能为空')
            if not cover_picture:
                self.add_error('cover_picture', '封面图片不能为空')
        return case_type

    def clean_tags_id_list(self):
        tags_id_list = self.data.get('tags_id_list')
        tags_id_list = json.loads(tags_id_list)
        if len(tags_id_list) <= 0:
            self.add_error('tags_id_list', '标签不能为空')
        else:
            return tags_id_list

    def clean_case_id(self):
        case_id = self.data.get('case_id')
        objs = models.zgld_editor_case.objects.filter(id=case_id)
        if objs:
            obj = objs[0]
            status = int(obj.status)

            if status in [1, 3]:
                return case_id
            else:
                if status in [2]:
                    text = '待审核'
                else:
                    text = '已完成'
                self.add_error('case_id', '{}状态, 不可修改'.format(text))
        else:
            self.add_error('case_id', '修改的案例不存在')

# 删除案例
class CaseDeleteForm(forms.Form):
    case_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "案例ID不能为空"
        }
    )
    def clean_case_id(self):
        case_id = self.data.get('case_id')
        objs = models.zgld_editor_case.objects.filter(id=case_id)
        if objs and int(objs[0].status) in [1, 3]:
            diary_objs = models.zgld_editor_diary.objects.filter(case_id=objs[0].id)
            for diary_obj in diary_objs:
                status = int(diary_obj.status)
                if status not in [1, 3]:
                    if status in [2]:
                        text = '待审核'
                    else:
                        text = '已完成'
                    self.add_error('case_id', '案例含有子级{}状态不能删除'.format(text))

            diary_objs.delete()  # 删除该日记库下所有日记
            objs.delete()        # 删除日记库

        else:
            if not objs:
                self.add_error('case_id', '删除ID不存在')
            else:
                if int(objs[0].status == 2):
                    text = '待审核'
                else:
                    text = '已完成'
                self.add_error('case_id', '案例{}状态不能删除'.format(text))

# 查询案例
class CaseSelectForm(forms.Form):
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

# 提交案例
class SubmitCaseForm(forms.Form):
    case_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "提交案例ID不能为空"
        }
    )

    def clean_case_id(self):
        case_id = self.data.get('case_id')
        objs = models.zgld_editor_case.objects.filter(id=case_id)
        if objs:
            obj = objs[0]
            status = int(obj.status)
            if status in [1, 3]:
                objs.update(status=2)
                return case_id

            else:
                if status in [2]:
                    text = '待审核状态, 请勿提交'
                else:
                    text = '已完成状态, 请勿重复提交'
                self.add_error('case_id', '{}'.format(text))
        else:
            self.add_error('case_id', '提交的案例不存在')










