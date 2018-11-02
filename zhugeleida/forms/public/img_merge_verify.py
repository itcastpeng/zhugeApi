from django import forms
# 合并图片 Form 验证
class imgMergeForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "文件名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    chunk_num = forms.IntegerField(
        error_messages={
            'required': "总份数不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )
    img_source =  forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid':  "必须是字符串"
        }
    )