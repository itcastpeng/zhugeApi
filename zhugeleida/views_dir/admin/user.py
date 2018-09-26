from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from zhugeleida.forms.user_verify import UserAddForm, UserUpdateForm, UserSelectForm,ScanCodeToAddUserForm
import json
from ..conf import *
import requests
from  zhugeleida.views_dir.qiyeweixin.qr_code_auth import create_small_program_qr_code
from zhugeapi_celery_project import tasks
from django.db.models import Q



# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def user(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = UserSelectForm(request.GET)
        type = request.GET.get('type')

        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = request.GET.get('user_id')
            print('--------------->>',request.GET)
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            status = request.GET.get('status')

            field_dict = {
                'id': '',
                'username': '__contains',         #名称模糊搜索
                # 'company__name': '__contains',    #公司名称
                'position':  '__contains',        # 职位搜索
                'department':  '',                # 部门搜索，按ID
                'status':  '',                    # (1, "启用"),   (2, "未启用"),
                # 'last_login_date': ''
            }

            q = conditionCom(request, field_dict)
            # if status:
            #     q.add(Q(**{'status': int(status)}), Q.AND)

            print('------q------>>',q)
            admin_userobj = models.zgld_admin_userprofile.objects.get(id=user_id)
            role_id = admin_userobj.role_id
            company_id = admin_userobj.company_id

            # if role_id == 1:  # 超级管理员,展示出所有的企业用户
            #    pass
            #
            # else:  #管理员，展示出自己公司的用户
            q.add(Q(**{"company_id": company_id}), Q.AND)

            if type == 'temp_user':
                objs = models.zgld_temp_userprofile.objects.select_related('company').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                    ret_data = []
                    department_objs = models.zgld_department.objects.filter(company_id=company_id).values('id', 'name')
                    department_list_all = list(department_objs) if department_objs else []
                    if objs:

                        for obj in objs:

                            departmane_list = obj.department
                            if departmane_list:
                                departmane_list = json.loads(departmane_list)
                                department_name_list = []
                                for department_dict in department_list_all:

                                    id =  int(department_dict.get('id'))  if  department_dict.get('id') else ''
                                    name = department_dict.get('name')
                                    if id in  departmane_list:
                                        department_name_list.append(name)
                                print('--- department --->',departmane_list,department_name_list)

                                department = ', '.join(department_name_list)



                                # print('departmane_objs.values_list("name") -->', departmane_objs.values_list('name'))

                                # department = ', '.join([i[0] for i in departmane_objs.values_list('name')])
                                # department_id = [i[0] for i in departmane_objs.values_list('id')]

                                ret_data.append({
                                    'temp_user_id': obj.id,

                                    'username': obj.username,
                                    'create_date': obj.create_date,

                                    'position': obj.position,
                                    'wechat': obj.wechat,  # 代表注册企业微信注册时的电话
                                    'mingpian_phone': obj.mingpian_phone,   # 名片显示的手机号
                                    'wechat_phone': obj.wechat_phone,               # 代表注册企业微信注册时的电话

                                    'company': obj.company.name,
                                    'company_id': obj.company_id,
                                    'department': department,
                                    'department_id': departmane_list,


                                })
                                #  查询成功 返回200 状态码

                            response.code = 200
                            response.msg = '查询成功'
                            response.data = {
                                'ret_data': ret_data,
                                'data_count': count,
                                'department_list': department_list_all
                            }

            else:
                objs = models.zgld_userprofile.objects.select_related('company').filter(q).order_by(order)

                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]


                ret_data = []

                department_objs = models.zgld_department.objects.filter(company_id=company_id).values('id','name')
                department_list =  list(department_objs)  if department_objs else []

                if objs:
                    mingpian_available_num = objs[0].company.mingpian_available_num
                    for obj in objs:
                        print('oper_user_username -->', obj)

                        department = ''
                        department_id = []
                        departmane_objs = obj.department.all()
                        print('departmane_objs -->', departmane_objs)
                        if departmane_objs:
                            #print('departmane_objs.values_list("name") -->', departmane_objs.values_list('name'))
                            department = ', '.join([i[0] for i in departmane_objs.values_list('name')])
                            department_id = [i[0] for i in departmane_objs.values_list('id')]


                        mingpian_avatar_obj = models.zgld_user_photo.objects.filter(user_id=obj.id, photo_type=2).order_by('-create_date')

                        mingpian_avatar = ''
                        if mingpian_avatar_obj:
                            mingpian_avatar =  mingpian_avatar_obj[0].photo_url
                        else:

                            if obj.avatar.startswith("http"):
                                mingpian_avatar = obj.avatar
                            else:
                                mingpian_avatar =  obj.avatar

                        ret_data.append({
                            'id': obj.id,
                            'userid': obj.userid,
                            'username': obj.username,
                            'create_date': obj.create_date,
                            'last_login_date': obj.last_login_date,
                            'position': obj.position,
                            'mingpian_phone': obj.mingpian_phone,  # 名片显示的手机号
                            'phone': obj.wechat_phone,          # 代表注册企业微信注册时的电话
                            'status': obj.get_status_display(),
                            'avatar': mingpian_avatar,          # 头像
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
                        'mingpian_available_num': mingpian_available_num,
                        'data_count': count,
                        'department_list' : department_list
                    }


                else:
                    response.code = 301
                    response.msg = "产品为空"

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改 用户表
#  csrf  token验证
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        global userid
        if oper_type == "add":

            form_data = {
                'user_id': request.GET.get('user_id'),
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                # 'role_id': request.POST.get('role_id'),
                'company_id': request.POST.get('company_id'),
                'position': request.POST.get('position'),
                'wechat_phone': request.POST.get('phone'), ##
                'mingpian_phone': request.POST.get('mingpian_phone')

            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = UserAddForm(form_data)

            if forms_obj.is_valid():
                print("验证通过")

                # user_id = request.GET.get('user_id')
                userid = str(int(time.time()*1000))   # 成员UserID。对应管理端的帐号，企业内必须唯一
                username = forms_obj.cleaned_data.get('username')
                password = forms_obj.cleaned_data.get('password')
                # role_id = forms_obj.cleaned_data.get('role_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                position = forms_obj.cleaned_data.get('position')
                wechat_phone = forms_obj.cleaned_data.get('wechat_phone')
                mingpian_phone = forms_obj.cleaned_data.get('mingpian_phone')


                available_user_num = models.zgld_company.objects.filter(id=company_id)[0].mingpian_available_num
                used_user_num  = models.zgld_userprofile.objects.filter(company_id=company_id).count() #


                print('-----超过明片最大开通数------>>',available_user_num,used_user_num)
                if  int(used_user_num) >= int(available_user_num): # 开通的用户数量 等于 == 该公司最大可用名片数
                    response.code = 302
                    response.msg = "超过明片最大开通数,请您联系管理员"
                    return JsonResponse(response.__dict__)

                elif int(used_user_num) < int(available_user_num):  # 开通的用户数量 小于 < 该公司最大可用名片数,才能继续开通
                    depart_id_list = []
                    department_id = request.POST.get('department_id')
                    print('-----department_id---->',department_id)
                    if  department_id:
                        depart_id_list = json.loads(department_id)

                        objs = models.zgld_department.objects.filter(id__in=depart_id_list)
                        if objs:
                            for c_id in objs:
                                department_company_id = c_id.company_id

                                if str(department_company_id) != str(forms_obj.cleaned_data['company_id']):
                                    response.code = 404
                                    response.msg = '非法请求'
                                    return JsonResponse(response.__dict__)


                    company_obj = models.zgld_company.objects.get(id=company_id)
                    get_token_data = {}
                    post_user_data = {}
                    get_user_data = {}
                    get_token_data['corpid'] = company_obj.corp_id
                    get_token_data['corpsecret'] = company_obj.tongxunlu_secret

                    import redis
                    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    key_name = "company_%s_tongxunlu_token" % (company_id)
                    token_ret = rc.get(key_name)

                    print('---token_ret---->>',token_ret)

                    if not  token_ret:
                        ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                        ret_json = ret.json()
                        print('--------ret_json-->>',ret_json)

                        access_token = ret_json['access_token']
                        get_user_data['access_token'] = access_token

                        rc.set(key_name,access_token,7000)

                    else:
                        get_user_data['access_token'] = token_ret
                    if len(depart_id_list) == 0:
                        depart_id_list = [1]

                    post_user_data['userid'] = userid
                    post_user_data['name'] = username
                    post_user_data['position'] = position
                    post_user_data['mobile'] = wechat_phone
                    post_user_data['department'] = depart_id_list
                    add_user_url = Conf['add_user_url']

                    print('-------->>',json.dumps(post_user_data))

                    ret = requests.post(add_user_url, params=get_user_data, data=json.dumps(post_user_data))
                    print('-----requests----->>', ret.text)

                    weixin_ret = json.loads(ret.text)
                    if  weixin_ret.get('errmsg') == 'created': # 在企业微信中创建用户成功
                        token = account.get_token(account.str_encrypt(password))

                        obj = models.zgld_userprofile.objects.create(
                            userid= userid,
                            username=username,
                            password=account.str_encrypt(password),
                            # role_id=role_id,
                            company_id=company_id,
                            position=position,
                            wechat_phone=wechat_phone,
                            mingpian_phone=mingpian_phone,
                            token=token
                        )
                        if depart_id_list[0] == 1:
                            depart_id_list = []
                        obj.department = depart_id_list

                        # 生成企业用户二维码
                        data_dict ={ 'user_id': obj.id, 'customer_id':'' }
                        tasks.create_user_or_customer_small_program_qr_code.delay(json.dumps(data_dict))

                        response.code = 200
                        response.msg = "添加用户成功"

                    else:
                        rc.delete(key_name)
                        response.code = weixin_ret['errcode']
                        response.msg = "企业微信返回错误,%s" % weixin_ret['errmsg']


            else:
                    print("验证不通过")
                    print(forms_obj.errors)
                    response.code = 301
                    print(forms_obj.errors.as_json())
                    response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            type = request.GET.get('type')


            if type == 'temp_user':
                user_objs = models.zgld_temp_userprofile.objects.filter(id=o_id)
                if user_objs:
                    user_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 302
                    response.msg = '用户ID不存在'


            else:
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
                        key_name = "company_%s_tongxunlu_token" % (user_objs[0].company_id)
                        token_ret = rc.get(key_name)

                        print('---token_ret---->>', token_ret)

                        if not token_ret:
                            ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                            ret_json = ret.json()
                            access_token = ret_json['access_token']
                            get_user_data['access_token'] = access_token

                            rc.set(key_name, access_token, 7000)
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
                                rc.delete(key_name)
                                response.code = weixin_ret['errcode']
                                response.msg = "企业微信返回错误,%s" % weixin_ret['errmsg']


                        else:
                            response.code = '302'
                            response.msg = "userid不存在"
                    else:
                        response.code = 302
                        response.msg = '用户ID不存在'

        elif oper_type == "update":

            print('-------->>',request.POST)
            type = request.POST.get('type')

            user_id =  request.GET.get('user_id')
            wechat =  request.GET.get('wechat')
            wechat_phone = request.POST.get('phone')
            if request.POST.get('wechat_phone'):
                wechat_phone = request.POST.get('wechat_phone')
            department_id = request.POST.get('department_id')

            # 获取ID 用户名 及 角色
            form_data = {
                'o_id': o_id,
                'user_id': request.GET.get('user_id'),
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                # 'role_id': request.POST.get('role_id'),
                'company_id': request.POST.get('company_id'),
                'position': request.POST.get('position'),
                'department_id': department_id,
                'wechat_phone': wechat_phone,
                'mingpian_phone': request.POST.get('mingpian_phone')
            }

            forms_obj = UserUpdateForm(form_data)

            if forms_obj.is_valid():
                print("验证通过")

                print(forms_obj.cleaned_data)
                username = forms_obj.cleaned_data.get('username')
                # role_id = forms_obj.cleaned_data.get('role_id')
                company_id = forms_obj.cleaned_data.get('company_id')
                position = forms_obj.cleaned_data.get('position')

                wechat_phone = forms_obj.cleaned_data.get('wechat_phone')
                mingpian_phone = forms_obj.cleaned_data.get('mingpian_phone')

                if type == 'temp_user':

                    temp_userprofile_objs = models.zgld_temp_userprofile.objects.filter(id=o_id)
                    if temp_userprofile_objs:
                        temp_userprofile_objs.update(
                            username=username,

                            company_id=company_id,
                            position=position,

                            wechat=wechat,
                            wechat_phone=wechat_phone,
                            mingpian_phone=mingpian_phone,
                        )

                    print('-- department_id --->',department_id)
                    user_obj = temp_userprofile_objs[0]
                    user_obj.department = department_id
                    user_obj.save()
                    response.code = 200
                    response.msg = "修改成功"


                else:

                    user_objs = models.zgld_userprofile.objects.select_related('company').filter(id=o_id)

                    if user_objs:

                        # print(user_objs[0].company.corp_id, user_objs[0].company.tongxunlu_secret)
                        get_token_data = {}
                        post_user_data = {}
                        get_user_data = {}
                        get_token_data['corpid'] = user_objs[0].company.corp_id
                        get_token_data['corpsecret'] = user_objs[0].company.tongxunlu_secret

                        import redis
                        rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                        key_name = "company_%s_tongxunlu_token" % (user_objs[0].company_id)
                        token_ret = rc.get(key_name)

                        print('---token_ret---->>', token_ret)

                        if not token_ret:
                            ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                            ret_json = ret.json()
                            access_token = ret_json['access_token']
                            get_user_data['access_token'] = access_token

                            rc.set(key_name, access_token, 7000)

                        else:
                            get_user_data['access_token'] = token_ret

                        if len(forms_obj.cleaned_data.get('department_id')) == 0:
                            department_id = [1]
                        post_user_data['userid'] = user_objs[0].userid
                        post_user_data['name'] = username
                        post_user_data['position'] = position
                        post_user_data['department'] = department_id
                        post_user_data['mobile'] = wechat_phone
                        print(Conf['update_user_url'], get_user_data, post_user_data)
                        ret = requests.post(Conf['update_user_url'], params=get_user_data, data=json.dumps(post_user_data))
                        print(ret.text)

                        if department_id[0] == 1 and len(department_id) == 1:
                            department_id = []

                        print('------ManToMany department_id ----->')
                        weixin_ret = json.loads(ret.text)
                        if weixin_ret['errmsg'] == 'updated':

                            user_objs.update(
                                username=username,
                                # role_id=role_id,
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

        elif oper_type == "update_status":

            status = request.POST.get('status')    #(1, "启用"),  (2, "未启用"),
            user_id = request.GET.get('user_id')

            objs = models.zgld_userprofile.objects.filter(id=o_id)

            if objs:

                if int(user_id) == int(o_id):
                    response.code = 305
                    response.msg = "不能修改自己"

                else:
                    objs.update(status=status)
                    response.code = 200
                    response.msg = "修改成功"

        elif oper_type == 'create_small_program_qr_code':
            user_id = request.POST.get('user_id')
            user_obj = models.zgld_userprofile.objects.filter(id=user_id)
            if user_obj:
                # 生成企业用户二维码

                # tasks.create_user_or_customer_small_program_qr_code.delay(json.dumps(data_dict))

                data_dict = {
                    'user_id': user_id,
                    'customer_id': ''
                }

                url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'

                print('--------mycelery 使用 request post_的数据 ------->>',data_dict)

                response_ret = requests.post(url , data=data_dict)
                response_ret = response_ret.json()

                print('-------- mycelery/触发 celery  返回的结果 -------->>',response_ret)

                qr_code =  response_ret['data'].get('qr_code')
                response.data = {
                    'qr_code': qr_code
                }
                response.code = 200
                response.msg = "生成用户二维码成功"

            else:
                response.code = 301
                response.msg = "用户不存在"

        elif oper_type == 'sync_user_tongxunlu':
            company_id = o_id

            company_obj = models.zgld_company.objects.filter(id=company_id)
            if company_obj:
                get_token_data = {}
                post_user_data = {}
                get_user_data = {}
                get_token_data['corpid'] = company_obj[0].corp_id
                get_token_data['corpsecret'] = company_obj[0].tongxunlu_secret

                import redis
                rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                key_name = "company_%s_tongxunlu_token" % (company_id)
                token_ret = rc.get(key_name)

                print('---token_ret---->>', token_ret)

                if not token_ret:
                    ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                    ret_json = ret.json()
                    print('--------ret_json-->>', ret_json)

                    access_token = ret_json['access_token']
                    get_user_data['access_token'] = access_token

                    rc.set(key_name, access_token, 7000)

                else:
                    get_user_data['access_token'] = token_ret

                department_list_url =  'https://qyapi.weixin.qq.com/cgi-bin/department/list'
                department_list_ret = requests.get(department_list_url, params=get_user_data)

                department_list_ret = department_list_ret.json()
                department_list = department_list_ret.get('department')
                print('-------- 获取部门列表 接口返回----------->>',json.dumps(department_list_ret))

                if department_list:
                    for dep_dict in department_list:
                        department_id = dep_dict.get('id')

                        department_liebiao = dep_dict.get('department') # 已经存在的部门列表

                        user_simplelist_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist'
                        get_user_data['department_id'] = department_id

                        user_simplelist_ret = requests.get(user_simplelist_url, params=get_user_data)
                        print('----- 获取部门成员 返回接口信息----->>', json.dumps(user_simplelist_ret.json()))
                        user_simplelist_ret = user_simplelist_ret.json()
                        errcode = user_simplelist_ret.get('errcode')
                        errmsg = user_simplelist_ret.get('errmsg')
                        userlist = user_simplelist_ret.get('userlist')

                        if userlist:
                            print('------- 获取-客户信息【成功】 ------->>',user_simplelist_ret)

                            for user_dict in userlist:
                                username = user_dict.get('name')
                                userid = user_dict.get('userid')
                                department_list = user_dict.get('department')
                                password = '123456'
                                token = account.get_token(account.str_encrypt(password))
                                objs =  models.zgld_userprofile.objects.filter(userid=userid,company_id=company_id)

                                if objs:
                                    print('-------- 用户数据成功已存在 username | userid | user_id -------->>',username,userid,objs[0].id)
                                else:
                                    obj = models.zgld_userprofile.objects.create(
                                        userid=userid,
                                        username= username,
                                        password= account.str_encrypt(password),
                                        # role_id=role_id,
                                        company_id=company_id,
                                        # position='',
                                        # wechat_phone='',
                                        # mingpian_phone= '',
                                        token=token
                                    )

                                    print('-------- 同步用户数据成功 user_id：-------->>',obj.id)

                                    # if department_list:
                                    #     obj.department = department_list

                                    # 生成企业用户二维码
                                    data_dict = {'user_id': obj.id, 'customer_id': ''}
                                    tasks.create_user_or_customer_small_program_qr_code.delay(json.dumps(data_dict))
                            response.code = 200
                            response.msg = "同步成功并生成用户二维码成功"
                            
                        else:
                            print('---- 获取部门成员 [报错]：------>',errcode,"|",errmsg)


            else:
                response.code = 301
                response.msg = "公司不存在"

        # 用户添加自己的信息入临时库
        elif oper_type == 'scan_code_to_add_user':
            user_id = request.GET.get('user_id')

            userprofile_obj = models.zgld_admin_userprofile.objects.get(id=user_id)
            company_id = userprofile_obj.company_id

            form_data = {
                'user_id': user_id,
                'company_id': company_id,
                'username': request.POST.get('username'),
                'position': request.POST.get('position'),
                'wechat': request.POST.get('wechat'),
                'wechat_phone': request.POST.get('wechat_phone'),       ## 微信绑定的手机号
                'mingpian_phone': request.POST.get('mingpian_phone')    # 名片显示的手机号

            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = ScanCodeToAddUserForm(form_data)

            if forms_obj.is_valid():
                print("验证通过")

                depart_id_list = []
                department_id = request.POST.get('department_id')
                print('-----department_id---->', department_id)

                if department_id:
                    depart_id_list = json.loads(department_id)

                username = forms_obj.cleaned_data.get('username')

                position = forms_obj.cleaned_data.get('position')
                wechat_phone = forms_obj.cleaned_data.get('wechat_phone')
                mingpian_phone = forms_obj.cleaned_data.get('mingpian_phone')
                wechat = request.POST.get('wechat')


                # if len(depart_id_list) == 0:
                #     depart_id_list = [1]

                obj = models.zgld_temp_userprofile.objects.create(

                    username=username,
                    company_id=company_id,
                    position=position,
                    wechat_phone=wechat_phone,
                    mingpian_phone=mingpian_phone,
                    wechat=wechat,

                )

                obj.department = json.dumps(depart_id_list)
                obj.save()

                response.code = 200
                response.msg = "添加用户成功"


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 管理员审核用户【批量】入库
        elif oper_type == 'approval_storage_user_info':

            user_id_list = request.POST.get('user_id_list')
            if user_id_list:
                user_id_list = json.loads(user_id_list)

                temp_userprofile_objs =models.zgld_temp_userprofile.objects.filter(id__in=user_id_list)
                if temp_userprofile_objs:

                    for temp_obj in temp_userprofile_objs:
                        company_id = temp_obj.company_id

                        department_id_list = json.loads(temp_obj.department)

                        if len(department_id_list) == 0:
                            department_id_list = [1]


                        print("验证通过")
                        userid = str(int(time.time() * 1000))   # 成员UserID。对应管理端的帐号，企业内必须唯一
                        password = '123456'

                        available_user_num = models.zgld_company.objects.filter(id=company_id)[0].mingpian_available_num
                        used_user_num = models.zgld_userprofile.objects.filter(company_id=company_id).count()  #

                        print('-----超过明片最大开通数------>>', available_user_num, used_user_num)
                        if int(used_user_num) >= int(available_user_num):  # 开通的用户数量 等于 == 该公司最大可用名片数
                            response.code = 302
                            response.msg = "超过明片最大开通数,请您联系管理员"
                            return JsonResponse(response.__dict__)

                        elif int(used_user_num) < int(available_user_num):  # 开通的用户数量 小于 < 该公司最大可用名片数,才能继续开通

                            token = account.get_token(account.str_encrypt(password))

                            username = temp_obj.username
                            position = temp_obj.position
                            wechat= temp_obj.wechat
                            wechat_phone= temp_obj.wechat_phone
                            mingpian_phone= temp_obj.mingpian_phone

                            temp_user_info_dict = {
                                'userid': userid,
                                'password': account.str_encrypt(password),
                                'token': token,
                                'username': username,
                                'company_id':company_id,
                                'position': position,
                                'wechat':  wechat,
                                'wechat_phone': wechat_phone,
                                'mingpian_phone': mingpian_phone,

                            }

                            company_obj = models.zgld_company.objects.get(id=company_id)
                            get_token_data = {}
                            post_user_data = {}
                            get_user_data = {}
                            get_token_data['corpid'] = company_obj.corp_id
                            get_token_data['corpsecret'] = company_obj.tongxunlu_secret

                            import redis
                            rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                            key_name = "company_%s_tongxunlu_token" % (company_id)
                            token_ret = rc.get(key_name)

                            print('---token_ret---->>', token_ret)

                            if not token_ret:
                                ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                                ret_json = ret.json()
                                print('--------ret_json-->>', ret_json)

                                access_token = ret_json['access_token']
                                get_user_data['access_token'] = access_token

                                rc.set(key_name, access_token, 7000)

                            else:
                                get_user_data['access_token'] = token_ret

                            post_user_data['userid'] = userid
                            post_user_data['name'] = username
                            post_user_data['position'] = position
                            post_user_data['mobile'] = wechat_phone
                            post_user_data['department'] = department_id_list
                            add_user_url = Conf['add_user_url']

                            print('-------->>', json.dumps(post_user_data))

                            ret = requests.post(add_user_url, params=get_user_data, data=json.dumps(post_user_data))
                            print('-----requests----->>', ret.text)

                            weixin_ret = json.loads(ret.text)
                            if weixin_ret.get('errmsg') == 'created':  # 在企业微信中创建用户成功

                                obj = models.zgld_userprofile.objects.create(**temp_user_info_dict)
                                if len(department_id_list) == 1  and department_id_list[0] == 1:
                                    department_id_list = []

                                obj.department = department_id_list
                                obj.save()

                                # 生成企业用户二维码
                                data_dict = {'user_id': obj.id, 'customer_id': ''}
                                tasks.create_user_or_customer_small_program_qr_code.delay(json.dumps(data_dict))

                                response.code = 200
                                response.msg = "添加用户成功"

                            else:
                                rc.delete(key_name)
                                response.code = weixin_ret['errcode']
                                response.msg = "企业微信返回错误,%s" % weixin_ret['errmsg']


                else:
                    response.code = 301
                    response.msg =  '用户临时表无数据'




    elif request.method == 'GET':

        # 生成 扫描的用户二维码
        if  oper_type == "create_scan_code":
            user_id = request.GET.get('user_id')
            from zhugeleida.public.common import create_scan_code_userinfo_qrcode
            obj = models.zgld_admin_userprofile.objects.get(id=user_id)

            token = obj.token
            timestamp = str(int(time.time() * 1000))

            rand_str = account.str_encrypt(timestamp + token)
            timestamp = timestamp

            url = 'http://zhugeleida.zhugeyingxiao.com/#/gongzhonghao/zhuceyonghu?rand_str=%s&timestamp=%s&user_id=%d' % (
            rand_str, timestamp, int(user_id))
            data = {
                'url': url,
                'admin_uid': user_id

            }
            response_ret  = create_scan_code_userinfo_qrcode(data)

            qrcode_url = response_ret.data.get('qrcode_url')
            if qrcode_url:
                response = response_ret
                response.code = 200
                response.msg = "添加成功"
                print('---- create_code_to_add_user url -->', url)



            else:
                response.code = 302
                response.msg = "用户不存在"


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


