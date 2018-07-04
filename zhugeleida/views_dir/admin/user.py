from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserAddForm, UserUpdateForm, UserSelectForm
import json
from ..conf import *
import requests
from  zhugeleida.views_dir.qiyeweixin.qr_code_auth import create_small_program_qr_code

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def user(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
                'role__name': '__contains',
                'company__name': '__contains',
                'create_date': '',
                'last_login_date': '',

            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            print('order -->', order)
            print(models.zgld_userprofile.objects.all())
            objs = models.zgld_userprofile.objects.select_related('role', 'company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            print('------------->>>', objs)
            ret_data = []
            for obj in objs:
                print('oper_user_username -->', obj)
                #  将查询出来的数据 加入列表

                department = ''
                department_id = []
                departmane_objs = obj.department.all()
                print('departmane_objs -->', departmane_objs)
                if departmane_objs:
                    print('departmane_objs.values_list("name") -->', departmane_objs.values_list('name'))

                    department = ', '.join([i[0] for i in departmane_objs.values_list('name')])
                    department_id = [i[0] for i in departmane_objs.values_list('id')]

                ret_data.append({
                    'id': obj.id,
                    'userid': obj.userid,
                    'username': obj.username,
                    'role_name': obj.role.name,
                    'role_id': obj.role.id,
                    'create_date': obj.create_date,
                    'last_login_date': obj.last_login_date,
                    'position': obj.position,
                    'mingpian_phone': obj.mingpian_phone,
                    'phone': obj.wechat_phone,         # 代表微信电话
                    'status': obj.get_status_display(),
                    'avatar': obj.avatar,
                    'qr_code': obj.qr_code,
                    'company': obj.company.name,
                    'company_id': obj.company_id,
                    'department' : department,
                    'department_id' : department_id,
                    'gender': obj.gender,

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


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        global userid
        if oper_type == "add":
            form_data = {
                'user_id': request.GET.get('user_id'),
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                'role_id': request.POST.get('role_id'),
                'company_id': request.POST.get('company_id'),
                'position': request.POST.get('position'),
                'wechat_phone': request.POST.get('phone'), ##
                'mingpian_phone': request.POST.get('mingpian_phone')

            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = UserAddForm(form_data)

            if forms_obj.is_valid():
                print("验证通过")
                userid = str(int(time.time()*1000))   # 成员UserID。对应管理端的帐号，企业内必须唯一
                username = forms_obj.cleaned_data.get('username')
                password = forms_obj.cleaned_data.get('password')
                role_id = forms_obj.cleaned_data.get('role_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                position = forms_obj.cleaned_data.get('position')
                wechat_phone = forms_obj.cleaned_data.get('wechat_phone')
                mingpian_phone = forms_obj.cleaned_data.get('mingpian_phone')

                depart_id_list = []
                department_id = request.POST.get('department_id')

                if  department_id:
                    depart_id_list = json.loads(department_id)
                    # depart_id_list = [int(departmentId) for departmentId in department_id]
                    # for id in department_id:
                    #     depart_id_list.append(int(id))

                    objs = models.zgld_department.objects.filter(id__in=depart_id_list)
                    if objs:
                        for c_id in objs:
                            department_company_id = c_id.company_id

                            if str(department_company_id) != str(forms_obj.cleaned_data['company_id']):
                                response.code = 404
                                response.msg = '非法请求'
                                return JsonResponse(response.__dict__)
                print('depart_id_list',depart_id_list)

                company_obj = models.zgld_company.objects.get(id=company_id)
                get_token_data = {}
                post_user_data = {}
                get_user_data = {}
                get_token_data['corpid'] = company_obj.corp_id
                get_token_data['corpsecret'] = company_obj.tongxunlu_secret

                import redis
                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                token_ret = rc.get('tongxunlu_token')
                print('---token_ret---->>',token_ret)

                if not  token_ret:
                    ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                    ret_json = ret.json()
                    access_token = ret_json['access_token']
                    get_user_data['access_token'] = access_token
                    rc.set('tongxunlu_token',access_token,7000)
                else:
                    get_user_data['access_token'] = token_ret

                post_user_data['userid'] = userid
                post_user_data['name'] = username
                post_user_data['position'] = position
                post_user_data['mobile'] = wechat_phone
                post_user_data['department'] = depart_id_list
                add_user_url = Conf['add_user_url']

                ret = requests.post(add_user_url, params=get_user_data, data=json.dumps(post_user_data))
                print('-----requests----->>', ret.text)

                weixin_ret = json.loads(ret.text)
                if  weixin_ret.get('errmsg') == 'created':

                    obj = models.zgld_userprofile.objects.create(
                        userid= userid,
                        username=username,
                        password=account.str_encrypt(password),
                        role_id=role_id,
                        company_id=company_id,
                        position=position,
                        wechat_phone=wechat_phone,
                        mingpian_phone=mingpian_phone
                    )

                    obj.department = depart_id_list

                    # 生成企业用户二维码

                    data_dict ={'user_id': obj.id}
                    response = create_small_program_qr_code(data_dict) #
                    if response.code != 200:
                        return JsonResponse(response.__dict__)

                    response.code = 200
                    response.msg = "添加用户成功"

                else:
                    response.code = weixin_ret['errcode']
                    response.msg = "企业微信验证未通过"

            else:
                    print("验证不通过")
                    print(forms_obj.errors)
                    response.code = 301
                    print(forms_obj.errors.as_json())
                    response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            print(request.GET.get('user_id'), o_id)

            if str(request.GET.get('user_id')) == str(o_id):
                response.msg = '不允许删除自己'
                response.code = 305

            else:
                user_objs = models.zgld_userprofile.objects.filter(id=o_id)
                if user_objs:

                    get_token_data = {}
                    get_user_data = {}
                    get_token_data['corpid'] = user_objs[0].company.corp_id
                    get_token_data['corpsecret'] = user_objs[0].company.tongxunlu_secret

                    import redis
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    token_ret = rc.get('tongxunlu_token')
                    print('---token_ret---->>', token_ret)

                    if not token_ret:
                        ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                        ret_json = ret.json()
                        access_token = ret_json['access_token']
                        get_user_data['access_token'] = access_token
                        rc.set('tongxunlu_token', access_token, 7000)
                    else:
                        get_user_data['access_token'] = token_ret

                    userid = user_objs[0].userid
                    if userid:
                        get_user_data['userid'] = userid
                        ret = requests.get(Conf['delete_user_url'], params=get_user_data)

                        weixin_ret = json.loads(ret.text)

                        if weixin_ret['errcode'] == 0:
                            user_objs.delete()
                            response.code = 200
                            response.msg = "删除成功"
                        else:
                            response.code = weixin_ret['errcode']
                            response.msg = "企业微信验证未能通过"
                    else:
                        response.code = '302'
                        response.msg = "userid不存在"
                else:
                    response.code = 302
                    response.msg = '用户ID不存在'

        elif oper_type == "update":
            print("dir(requests.POST) ===>", dir(request.POST))
            print('=====request.POST=====>>>', o_id, request.POST)

            # 获取ID 用户名 及 角色
            form_data = {
                'o_id': o_id,
                'user_id': request.GET.get('user_id'),
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                'role_id': request.POST.get('role_id'),
                'company_id': request.POST.get('company_id'),
                'position': request.POST.get('position'),
                'department_id': request.POST.get('department_id'),
                'wechat_phone': request.POST.get('phone'),
                'mingpian_phone': request.POST.get('mingpian_phone')
            }

            print("request.POST.getlist('department_id') -->", request.POST.get('department_id'))

            forms_obj = UserUpdateForm(form_data)

            if forms_obj.is_valid():
                print("验证通过")

                print(forms_obj.cleaned_data)
                username = forms_obj.cleaned_data.get('username')
                role_id = forms_obj.cleaned_data.get('role_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                position = forms_obj.cleaned_data.get('position')
                department_id = forms_obj.cleaned_data.get('department_id')
                wechat_phone = forms_obj.cleaned_data.get('wechat_phone')
                mingpian_phone = forms_obj.cleaned_data.get('mingpian_phone')

                print('-------department_ids------->>', type(department_id))
                #  查询数据库  用户id
                user_objs = models.zgld_userprofile.objects.filter(id=o_id)
                #  更新用户 数据
                if user_objs:

                    print(user_objs[0].company.corp_id, user_objs[0].company.tongxunlu_secret)
                    get_token_data = {}
                    post_user_data = {}
                    get_user_data = {}
                    get_token_data['corpid'] = user_objs[0].company.corp_id
                    get_token_data['corpsecret'] = user_objs[0].company.tongxunlu_secret

                    import redis
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    token_ret = rc.get('tongxunlu_token')
                    print('---token_ret---->>', token_ret)

                    if not token_ret:
                        ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                        ret_json = ret.json()
                        access_token = ret_json['access_token']
                        get_user_data['access_token'] = access_token
                        rc.set('tongxunlu_token', access_token, 7000)
                    else:
                        get_user_data['access_token'] = token_ret


                    post_user_data['userid'] = user_objs[0].userid
                    post_user_data['name'] = username
                    post_user_data['position'] = position
                    post_user_data['department'] = department_id
                    post_user_data['mobile'] = wechat_phone
                    ret = requests.post(Conf['update_user_url'], params=get_user_data, data=json.dumps(post_user_data))
                    print(ret.text)

                    weixin_ret = json.loads(ret.text)
                    if weixin_ret['errmsg'] == 'updated':

                        user_objs.update(
                            username=username,
                            role_id=role_id,
                            company_id=company_id,
                            position=position,
                            wechat_phone=wechat_phone,
                            mingpian_phone=mingpian_phone,
                        )

                        user_obj = user_objs[0]
                        user_obj.department = department_id
                        user_obj.save()
                        response.code = 200
                        response.msg = "修改成功"
                    else:
                        response.code = weixin_ret['errcode']
                        response.msg = "修改成功"

                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
