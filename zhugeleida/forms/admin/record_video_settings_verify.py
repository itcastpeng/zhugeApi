from django import forms
from zhugeleida import models
from publicFunc import account
import datetime


# 添加视频分类
class ClassificationAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作ID不能为空"
        }
    )
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司不存在"
        }
    )
    classification_name = forms.CharField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )
    def clean_classification_name(self):
        classification_name = self.data.get('classification_name')
        company_id = self.data.get('company_id')
        objs = models.zgld_recorded_video_classification.objects.filter(
            company_id=company_id,
            classification_name=classification_name
        )
        if objs:
            self.add_error('classification_name', '分类名称已存在')
        else:
            return classification_name


# 修改视频分类
class ClassificationUpdateForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作ID不能为空"
        }
    )
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司不存在"
        }
    )
    classification_name = forms.CharField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        company_id = self.data.get('company_id')
        objs = models.zgld_recorded_video_classification.objects.filter(id=o_id)
        if objs and objs[0].company_id == company_id:
            return o_id
        else:
            if objs:
                self.add_error('o_id', '无权限操作')
            else:
                self.add_error('o_id', '操作分类不存在')

    def clean_classification_name(self):
        classification_name = self.data.get('classification_name')
        o_id = self.data.get('o_id')
        company_id = self.data.get('company_id')
        objs = models.zgld_recorded_video_classification.objects.filter(
            company_id=company_id,
            classification_name=classification_name
        ).exclude(id=o_id)
        if objs:
            self.add_error('classification_name', '分类名称已存在')
        else:
            return classification_name

# 删除视频分类
class ClassificationDeleteForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '用户ID不存在'
        }
    )

    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作ID不能为空"
        }
    )
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司不存在"
        }
    )


    def clean_o_id(self):
        o_id = self.data.get('o_id')
        company_id = self.data.get('company_id')
        objs = models.zgld_recorded_video_classification.objects.filter(id=o_id)
        if objs and objs[0].company_id == company_id:
            if models.zgld_recorded_video.objects.filter(classification_id=o_id):
                self.add_error('o_id', '含有视频信息, 请先删除后操作')
            else:
                return o_id
        else:
            if objs:
                self.add_error('o_id', '无权限操作')
            else:
                self.add_error('o_id', '操作分类不存在')



# 添加视频
class VideoAddForm(forms.Form):
    classification = forms.CharField(
        required=True,
        error_messages={
            'required': '视频分类不能为空'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': '视频标题不能为空'
        }
    )

    abstract = forms.CharField(
        required=True,
        error_messages={
            'required': '视频摘要不能为空'
        }
    )

    cover_photo = forms.CharField(
        required=True,
        error_messages={
            'required': '视频封面不能为空'
        }
    )

    expert_introduction = forms.CharField(
        required=True,
        error_messages={
            'required': '专家介绍不能为空'
        }
    )

    textual_interpretation = forms.CharField(
        required=True,
        error_messages={
            'required': '文字介绍不能为空'
        }
    )
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '登录异常'
        }
    )
    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': '登录异常'
        }
    )
    video_url = forms.CharField(
        required=True,
        error_messages={
            'required': '视频不能为空'
        }
    )

    whether_writer_number = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_verify_phone = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_consult_online = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_authority_expert = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_text_interpretation = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_previous_video = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    def clean_classification(self):
        classification = self.data.get('classification')
        company_id = self.data.get('company_id')
        objs = models.zgld_recorded_video_classification.objects.filter(
            id=classification,
            company_id=company_id
        )
        if objs:
            return classification
        else:
            self.add_error('classification', '不可选择该分类')

    def clean_title(self):
        title = self.data.get('title')
        company_id= self.data.get('company_id')

        objs = models.zgld_recorded_video.objects.filter(
            company_id=company_id,
            title=title
        )
        if objs:
            self.add_error('title', '标题重复')
        else:
            return title

# 修改视频
class VideoUpdateForm(forms.Form):
    classification = forms.CharField(
        required=True,
        error_messages={
            'required': '视频分类不能为空'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': '视频标题不能为空'
        }
    )

    abstract = forms.CharField(
        required=True,
        error_messages={
            'required': '视频摘要不能为空'
        }
    )

    cover_photo = forms.CharField(
        required=True,
        error_messages={
            'required': '视频封面不能为空'
        }
    )

    expert_introduction = forms.CharField(
        required=True,
        error_messages={
            'required': '专家介绍不能为空'
        }
    )

    textual_interpretation = forms.CharField(
        required=True,
        error_messages={
            'required': '文字介绍不能为空'
        }
    )
    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': '登录异常'
        }
    )
    o_id = forms.CharField(
        required=True,
        error_messages={
            'required': '登录异常'
        }
    )
    company_id = forms.CharField(
        required=True,
        error_messages={
            'required': '登录异常'
        }
    )
    video_url = forms.CharField(
        required=True,
        error_messages={
            'required': '视频不能为空'
        }
    )
    whether_writer_number = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_verify_phone = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_consult_online = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_authority_expert = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_text_interpretation = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )
    whether_previous_video = forms.CharField(
        required=False,
        error_messages={
            'required': ''
        }
    )

    def clean_classification(self):
        classification = self.data.get('classification')
        company_id = self.data.get('company_id')
        objs = models.zgld_recorded_video_classification.objects.filter(
            id=classification,
            company_id=company_id
        )
        if objs:
            return classification
        else:
            self.add_error('classification', '不可选择该分类')

    def clean_title(self):
        title = self.data.get('title')
        o_id = self.data.get('o_id')
        company_id= self.data.get('company_id')

        objs = models.zgld_recorded_video.objects.filter(
            company_id=company_id,
            title=title
        ).exclude(id=o_id)
        if objs:
            self.add_error('title', '标题重复')
        else:
            return title

    def clean_o_id(self):
        company_id = self.data.get('company_id')
        o_id = self.data.get('o_id')
        obj = models.zgld_recorded_video.objects.get(id=o_id)
        if obj.user.company_id == company_id:
            return o_id
        else:
            self.add_error('o_id', '无权操作')


# 删除视频
class VideoDeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作视频有误'
        }
    )




# 公共查询
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





