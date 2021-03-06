from django.shortcuts import render
from wendaku import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from wendaku.forms.daanku_verify import DaankuAddForm, DaankuUpdateForm, DaankuSelectForm
from publicFunc.condition_com import conditionCom
import json
import datetime


# 数据的展示
@csrf_exempt
@account.is_token(models.UserProfile)
def daanku(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认
        forms_obj = DaankuSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            order = request.GET.get('order', '-create_date')

            field_dict = {
                'id': '',
                'content': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
                'shenhe_date': '',
                'cilei_id': '',
                'keshi_id': '',
                'oper_user_id': '',
                'daan_leixing_id': '',
                'is_update': '',
                'cilei__name': '__contains',
                'keshi_name': '__contains',
                'daan_leiixng': ''
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            # 获取所有数据
            objs = models.DaAnKu.objects.select_related('oper_user', 'cilei', 'keshi', 'daan_leixing').filter(
                q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []

            # 获取第几页的数据
            for obj in objs:

                cilei_name = ''
                cilei_id = ''
                keshi_name = ''
                keshi_id = ''
                daan_leixing_name = ''
                daan_leixing_id = ''
                oper_user__username = ''
                if obj.cilei:
                    cilei_name = obj.cilei.name
                    cilei_id = obj.cilei.id

                if obj.keshi:
                    keshi_name = obj.keshi.name
                    keshi_id = obj.keshi.id

                if obj.daan_leixing:
                    daan_leixing_name = obj.daan_leixing.name
                    daan_leixing_id = obj.daan_leixing.id

                if obj.oper_user:
                    oper_user__username = obj.oper_user.username

                ret_data.append({
                    'id': obj.id,
                    'content': obj.content,
                    'create_date': obj.create_date,
                    'oper_user__username': oper_user__username,
                    'update_date': obj.update_date,
                    'cilei_id': cilei_id,
                    'cilei__name': cilei_name,
                    'keshi_id': keshi_id,
                    'keshi_name': keshi_name,
                    'daan_leixing_id': daan_leixing_id,
                    'daan_leixing_name': daan_leixing_name

                })

            response.code = 200
            response.data = {
                'ret_data': ret_data,
                'data_count': count
            }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


#  增删改
@csrf_exempt
# @account.is_token(models.UserProfile)
def daanku_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            print('开始入库')
            data = request.POST.get('data')
            print('data -------- >',data)
            role_data = {
                # # 审核人
                'oper_user_id':request.GET.get('user_id'),
                # 答案
                'content': data,
                # # 词类
                # 'cilei_id':request.POST.get('cilei_id'),
                # # 科室
                # 'keshi_id':request.POST.get('keshi_id'),
                # # 答案类型
                # 'daan_leixing_id':request.POST.get('daan_leixing_id'),
            }
            forms_obj = DaankuAddForm(role_data)
            if forms_obj.is_valid():
            # if role_data['content']:
                # data_list = request.POST.get('data_list')
                # for data in data_list:
                # print(role_data['content'])
                # print('forms_obj.forms_obj -->',forms_obj.cleaned_data)
                # models.DaAnKu.objects.create(**forms_obj.cleaned_data)
                print('添加成功')
                response.code = 200
                response.msg = "添加成功"
            else:
                print('添加失败')
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            print('o_id -->', o_id)
            objs = models.DaAnKu.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '答案不存在'

        elif oper_type == "update":
            form_data = {
                'tid': o_id,
                'content': request.POST.get('content'),
                'cilei_id': request.POST.get('cilei_id'),
                'daan_leixing_id': request.POST.get('daan_leixing_id'),
                'keshi_id': request.POST.get('keshi_id'),
                'oper_user_id': request.GET.get('user_id'),
            }
            forms_obj = DaankuUpdateForm(form_data)
            if forms_obj.is_valid():
                oper_user_id = forms_obj.cleaned_data['oper_user_id']
                content = forms_obj.cleaned_data['content']
                tid = forms_obj.cleaned_data['tid']
                cilei_id = forms_obj.cleaned_data['cilei_id']
                daan_leixing_id = forms_obj.cleaned_data['daan_leixing_id']
                keshi_id = forms_obj.cleaned_data['keshi_id']
                daanku_objs = models.DaAnKu.objects.filter(
                    id=tid
                )
                if daanku_objs:
                    daanku_objs.update(
                        content=content,
                        cilei_id=cilei_id,
                        daan_leixing_id=daan_leixing_id,
                        keshi_id=keshi_id,
                        update_date=datetime.datetime.now(),
                        oper_user_id=oper_user_id,
                        is_update=True
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 302
                    response.msg = "操作id不存在"
            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'batch_delete':
            # 获取多个id值(字符串类型)
            list_ids = request.POST.get('list_ids')
            # 切割出每个字符
            list_id = list_ids.split(',')
            id_list = []
            # 遍历添加到列表
            for p_id in list_id:
                id_list.append(p_id)
            # 查询id是否在这个列表
            models.DaAnKu.objects.filter(id__in=id_list).delete()
            response.code=200
            response.msg='删除成功'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
