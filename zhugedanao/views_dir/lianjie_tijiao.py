from django.shortcuts import render
from zhugedanao import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugedanao.forms.lianjie_tijiao import AddForm, UpdateForm, SelectForm
import json


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zhugedanao_userprofile)
def lianjie_tijiao(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        print('查询任务列表', request.GET)
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'task_name': '',
                'task_status': '',
                'task_progress': '',
                'create_date': ''
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.zhugedanao_lianjie_task_list.objects.filter(q).order_by(order)
            count = objs.count()
            detail_count = 0
            if objs:
                detail = models.zhugedanao_lianjie_tijiao.objects.filter(tid=objs[0].id).filter(is_zhixing=0)
                detail_count = detail.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                zhuangtai = '未完成'
                if obj.task_status:
                    zhuangtai = '已完成'
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'task_name': obj.task_name,
                    'task_status':zhuangtai,
                    'task_progress': obj.task_progress,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'count_taskList':obj.count_taskList
                })
            #  查询成功 返回200 状态码
            yiwancheng_obj = 0
            if count != 0:
                yiwancheng_obj = count - detail_count
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,    # 任务总数
                'yiwancheng_obj':yiwancheng_obj # 已完成数量
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zhugedanao_userprofile)
def lianjie_tijiao_detail(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        print('任务详情------------',request.GET)
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            tid = forms_obj.cleaned_data['tid']
            order = request.GET.get('order', '-id')
            field_dict = {
                'id': '',
                # 'name': '__contains',
                'url': '__contains',
                # 'create_date': '',
                'user_id': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.zhugedanao_lianjie_tijiao.objects.select_related('user', ).filter(q).filter(tid='{}'.format(tid)).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'url': obj.url,
                    'count': obj.count,
                    'status_text': obj.get_status_display(),
                    'status': obj.status,
                    # 'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
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


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zhugedanao_userprofile)
def lianjie_tijiao_oper(request, oper_type, o_id):
    print('--------------oper')
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            print('添加----',request.POST)
            print('===============> ', request.POST.get('url'))
            form_data = {
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'url': request.POST.get('url')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                # models.zhugedanao_userprofile.objects.create(**forms_obj.cleaned_data)
                url_list = forms_obj.cleaned_data.get('url')
                name = forms_obj.cleaned_data.get('name')
                oper_user_id = forms_obj.cleaned_data.get('oper_user_id')
                now_datetime = datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S')
                querysetlist = []
                objs_id = models.zhugedanao_lianjie_task_list.objects.create(
                    task_name = name,
                    create_date = now_datetime,
                )
                task_detail_num = 0
                for url in url_list:
                    task_detail_num += 1
                    querysetlist.append(
                        models.zhugedanao_lianjie_tijiao(
                            user_id=oper_user_id,
                            tid_id=objs_id.id,
                            url=url
                        )
                    )
                models.zhugedanao_lianjie_task_list.objects.filter(id=objs_id.id).update(
                    count_taskList=task_detail_num
                )
                models.zhugedanao_lianjie_tijiao.objects.bulk_create(querysetlist)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == "delete":
            # 删除 ID
            objs = models.zhugedanao_lianjie_task_list.objects.filter(id=o_id)
            if objs:
                objs.delete()
                task_id = objs[0].id
                task_detail_objs = models.zhugedanao_lianjie_tijiao.objects.filter(tid=task_id)
                task_detail_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'url': request.POST.get('url')
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                url = forms_obj.cleaned_data['url']
                #  查询数据库  用户id
                objs = models.zhugedanao_lianjie_tijiao.objects.filter(
                    id=o_id,
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name,
                        url=url
                    )

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == "update_status":
            status = request.POST.get('status')
            company_id = request.GET.get('company_id')
            print('status -->', status)
            objs = models.zhugedanao_userprofile.objects.filter(id=o_id, company_id=company_id)
            if objs:
                objs.update(status=status)
                response.code = 200
                response.msg = "状态修改成功"
            else:
                response.code = 301
                response.msg = "用户ID不存在"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
