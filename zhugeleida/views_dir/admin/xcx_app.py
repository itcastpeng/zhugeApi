from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.admin.xcx_app_verify import UserAddForm, UserUpdateForm, AppSelectForm
import json
from ..conf import *
import requests
from  zhugeleida.views_dir.qiyeweixin.qr_code_auth import create_small_program_qr_code
from zhugeapi_celery_project import tasks
from django.db.models import Q

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def xcx_app(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        forms_obj = AppSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = request.GET.get('user_id')

            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',      # 按着用户名字搜索
                'company__name': '__contains',  # 按着公司名字搜索
                'create_date': ''
            }

            q = conditionCom(request, field_dict)
            q.add(Q(**{'verify_type_info': True}), Q.AND)

            objs = models.zgld_xiaochengxu_app.objects.select_related('user','company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            print('------------->>>', objs)
            ret_data = []
            reason = ''

            for obj in objs:
                print('oper_user_username -->', obj)
                upload_audit_obj = models.zgld_xiapchengxu_upload_audit.objects.filter(app_id=obj.id).order_by('-upload_code_date')

                if upload_audit_obj:
                    status_time = ''
                    status_text = ''
                    app_status = ''
                    version_num = upload_audit_obj[0].version_num
                    template_id = upload_audit_obj[0].template_id
                    experience_qrcode = upload_audit_obj[0].experience_qrcode
                    status = upload_audit_obj[0].upload_result
                    if status == 0:
                        app_status = 1
                        status_text = '代码上传成功'
                        status_time = upload_audit_obj[0].upload_code_date
                        reason = ''

                    elif status == 1:
                        app_status = 2
                        status_text = '代码上传失败'
                        status_time = upload_audit_obj[0].upload_code_date
                        reason = upload_audit_obj[0].reason


                    status =  upload_audit_obj[0].audit_result

                    if status == 0:
                        app_status = 5
                        status_text = '审核通过'
                        status_time = upload_audit_obj[0].audit_reply_date


                    elif status == 1:
                        app_status = 6
                        status_text =  '审核未通过'
                        status_time = upload_audit_obj[0].audit_reply_date
                        reason = upload_audit_obj[0].reason

                    elif status == 2:
                        app_status = 4
                        status_text =  '审核中'
                        status_time = upload_audit_obj[0].audit_commit_date

                    elif status == 3:
                        app_status = 3
                        status_text =  '提交审核报错'
                        status_time = upload_audit_obj[0].audit_commit_date
                        reason = upload_audit_obj[0].reason

                    elif status == 4:
                        app_status = 9
                        status_text = '审核撤回成功'
                        status_time = upload_audit_obj[0].audit_reply_date
                        reason = upload_audit_obj[0].reason

                    elif status == 5:
                        app_status = 10
                        status_text = '审核撤回失败'
                        status_time = upload_audit_obj[0].audit_reply_date
                        reason = upload_audit_obj[0].reason

                    release_obj = models.zgld_xiapchengxu_release.objects.filter(audit_code_id=upload_audit_obj[0].id).order_by('-release_commit_date')
                    if release_obj:
                        status = release_obj[0].release_result
                        status_time = release_obj[0].release_commit_date

                        if status == 1:
                            app_status = 7
                            status_text =  '上线成功'
                            reason = ''

                        elif status == 2:
                            app_status = 8
                            status_text = '上线失败'
                            reason =  release_obj[0].reason

                        elif status == 3:
                            app_status = 11
                            status_text = '版本回退成功'
                            reason =  release_obj[0].reason

                        elif status == 4:
                            app_status = 12
                            status_text = '版本回退失败'
                            reason = release_obj[0].reason

                else:
                    version_num = ''
                    template_id = ''
                    experience_qrcode = ''
                    app_status = 0
                    status_text = ''
                    status_time = ''


                ret_data.append({
                    'id': obj.id,
                    'belong_user': obj.user.login_user, # 小程序授权的用户
                    'company_id': obj.company_id,
                    'company_name': obj.company.name,
                    'version_num' : version_num,
                    'template_id' : template_id,
                    'status' :  app_status,           # 审核的结果。
                    'status_text' :  status_text,     # 审核的结果。
                    'status_time' : status_time.strftime('%Y-%m-%d %H:%M') if status_time else '',
                    'experience_qrcode': experience_qrcode ,
                    'reason': reason,


                })
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


