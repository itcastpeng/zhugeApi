from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.department_verify import DepartmentAddForm, DepartmentUpdateForm, DepartmentSelectForm
from publicFunc.condition_com import conditionCom
from ..conf import *
from django.db.models import Q
from zhugeleida.public.common import jianrong_create_qiyeweixin_access_token
import requests, json

# 展示部门（雷达）用户
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def department(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        field_dict = {
            'id': '',
            'name': '__contains',
            'create_date': '',

        }
        user_id = request.GET.get('user_id')
        admin_userobj = models.zgld_admin_userprofile.objects.get(id=user_id)
        role_id = admin_userobj.role_id
        company_id = admin_userobj.company_id

        q = conditionCom(request, field_dict)
        q.add(Q(**{"company_id": company_id}), Q.AND)

        objs = models.zgld_department.objects.filter(q).order_by('-create_date')
        count = objs.count()

        # 获取所有数据
        ret_data = []
        # 获取第几页的数据
        for obj in objs:
            ret_data.append({
                'id': obj.id,
                'name': obj.name,
                'parentid': obj.parentid_id,
                'department_id': obj.id,
                'create_date': obj.create_date,
                'company_id': obj.company_id,
                'order': obj.order,
            })

        response.code = 200
        response.data = {
            'ret_data': ret_data,
            'data_count': count,
        }
        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


# 部门操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def department_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":

        # 添加部门
        if oper_type == "add":

            print('----department add ---->>',request.POST)
            department_data = {
                'user_id': request.GET.get('user_id'),
                'company_id': request.POST.get('company_id'),
                'name': request.POST.get('name'),
                'parentid_id': request.POST.get('parentid')

            }

            forms_obj = DepartmentAddForm(department_data)

            if forms_obj.is_valid():
                del forms_obj.cleaned_data['user_id']
                print('-----forms_obj.cleaned_data--------->>',forms_obj.cleaned_data)

                parentid_id = forms_obj.cleaned_data.get('parentid_id')
                if not  parentid_id:
                    parentid_id = ''
                company_id = forms_obj.cleaned_data.get('company_id')

                name = forms_obj.cleaned_data.get('name')
                data_dict = {
                    'company_id' : company_id,
                    'name' : name,
                    'parentid_id' : parentid_id
                }
                obj = models.zgld_department.objects.create(**data_dict)

                # print('obj.id -->', obj.id)
                # get_token_data = {}
                # get_user_data = {}
                #
                # get_token_data['corpid'] = obj.company.corp_id
                # get_token_data['corpsecret'] = obj.company.tongxunlu_secret
                #
                #
                # import redis
                # rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                # key_name = "company_%s_tongxunlu_token" % (obj.company_id)
                # token_ret = rc.get(key_name)
                #
                # print('---token_ret---->>', token_ret)
                #
                # if not token_ret:
                #     ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                #     ret_json = ret.json()
                #     access_token = ret_json['access_token']
                #     get_user_data['access_token'] = access_token
                #
                #     rc.set(key_name, access_token, 7000)
                #
                # else:
                #     get_user_data['access_token'] = token_ret

                token_ret = jianrong_create_qiyeweixin_access_token(company_id)
                get_user_data = {
                    'access_token': token_ret
                }

                if not obj.parentid_id: #为空的话，说明是顶级
                    parentid_id = 1
                else:
                    parentid_id = obj.parentid_id

                print('parentid_id -->', parentid_id)

                post_user_data = {
                    'id': obj.id,
                    'name': name,
                    'parentid': parentid_id
                }
                print('-----json.dumps(post_user_data)----->>',json.dumps(post_user_data))

                ret = requests.post(Conf['add_department_url'], params=get_user_data,data=json.dumps(post_user_data))
                weixin_ret = ret.json()

                if weixin_ret.get('errmsg') == 'created':
                    response.code = 200
                    response.msg = "添加成功"
                else:
                    models.zgld_department.objects.filter(id=obj.id).delete()
                    response.code = weixin_ret['errcode']
                    response.msg = "企业微信返回错误,%s" %  weixin_ret['errmsg']

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除部门
        elif oper_type == "delete":
            print('------delete o_id --------->>', o_id)

            # department_relate_user = models.zgld_department.objects.get(id=o_id).zgld_userprofile_set.all()

            department_objs = models.zgld_department.objects.filter(id=o_id)

            if  department_objs:
                user_objs = models.zgld_userprofile.objects.filter(department=o_id)

                if user_objs.count() == 0:

                    company_id =  department_objs[0].company_id
                    # get_token_data = {}
                    # get_user_data = {}
                    #
                    # get_token_data['corpid'] = department_objs[0].company.corp_id
                    # get_token_data['corpsecret'] = department_objs[0].company.tongxunlu_secret
                    #
                    # import redis
                    # rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    # key_name = "company_%s_tongxunlu_token" % (department_objs[0].company_id)
                    # token_ret = rc.get(key_name)
                    # print('---token_ret---->>', token_ret)
                    #
                    # if not token_ret:
                    #     ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                    #     ret_json = ret.json()
                    #     access_token = ret_json['access_token']
                    #     get_user_data['access_token'] = access_token
                    #
                    #     rc.set(key_name, access_token, 7000)
                    # else:
                    #     get_user_data['access_token'] = token_ret

                    token_ret = jianrong_create_qiyeweixin_access_token(company_id)
                    get_user_data = {
                        'access_token': token_ret,
                        'id' : o_id
                    }
                    ret = requests.get(Conf['delete_department_url'], params=get_user_data)
                    print(ret.json())

                    weixin_ret = json.loads(ret.text)
                    if weixin_ret.get('errmsg') == 'deleted':
                        department_objs.delete()
                        response.code = 200
                        response.msg = "删除成功"
                    else:

                        response.code = weixin_ret['errcode']
                        if weixin_ret['errcode'] == 60005:
                           error_msg = '部门下存在成员,请先删除或转移子级数据'
                        else:
                           error_msg =  "企业微信返回错误,%s" % weixin_ret['errmsg']

                        response.msg =  error_msg


                else:
                    response.code = 304
                    response.msg = "含有子级数据,请先删除或转移子级数据"

            else:
                response.code = 302
                response.msg = '部门ID不存在'

        # 修改部门
        elif oper_type == "update":
            form_data = {

                'user_id': request.GET.get('user_id'),
                'company_id': request.POST.get('company_id'),
                'name': request.POST.get('name'),
                'parentid_id': request.POST.get('parentid'),
                'department_id': o_id
            }

            print(form_data)
            forms_obj = DepartmentUpdateForm(form_data)
            if forms_obj.is_valid():
                name = forms_obj.cleaned_data['name']
                department_id = forms_obj.cleaned_data['department_id']
                print(department_id)
                department_objs = models.zgld_department.objects.filter(
                    id=forms_obj.cleaned_data['department_id'],

                )


                if department_objs:
                    company_id =  department_objs[0].company_id
                    # get_token_data = {}
                    # get_user_data = {}
                    #
                    # get_token_data['corpid'] = department_objs[0].company.corp_id
                    # get_token_data['corpsecret'] = department_objs[0].company.tongxunlu_secret
                    #
                    # import redis
                    # rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
                    # key_name = "company_%s_tongxunlu_token" % (department_objs[0].company_id)
                    # token_ret = rc.get(key_name)
                    # print('---token_ret---->>', token_ret)
                    #
                    # if not token_ret:
                    #     ret = requests.get(Conf['tongxunlu_token_url'], params=get_token_data)
                    #     ret_json = ret.json()
                    #     access_token = ret_json['access_token']
                    #     get_user_data['access_token'] = access_token
                    #     rc.set(key_name, access_token, 7000)
                    #
                    # else:
                    #     get_user_data['access_token'] = token_ret

                    token_ret = jianrong_create_qiyeweixin_access_token(company_id)
                    get_user_data = {
                        'access_token': token_ret
                    }

                    post_user_data = {
                        'id': o_id,
                        'name': forms_obj.cleaned_data.get('name'),

                    }

                    parentid = forms_obj.cleaned_data.get('parentid_id')
                    if not parentid:
                        parentid = 1  # 微信端 父部门id默认从1 开始。当我们数据库里存进去为1时候，父部门一级别从空开始

                    post_user_data['parentid'] = parentid

                    print('-----json.dumps(post_user_data)----->>', json.dumps(post_user_data),forms_obj.cleaned_data.get('name'))
                    ret = requests.post(Conf['update_department_url'], params=get_user_data, data=json.dumps(post_user_data))
                    print(ret.text)

                    weixin_ret = json.loads(ret.text)
                    if weixin_ret.get('errmsg') == 'updated':
                        if not forms_obj.cleaned_data.get('parentid_id'):
                            parentid = ''

                        department_objs.update(
                            name=name,
                            company_id=forms_obj.cleaned_data['company_id'],
                            parentid_id=parentid
                        )
                        response.code = 200
                        response.msg = "修改成功"

                    else:
                        response.code = weixin_ret['errcode']
                        response.msg = "企业微信返回错误,%s" % weixin_ret['errmsg']


                else:
                    response.code = 302
                    response.msg = '部门ID不存在'
            else:
                response.code = 303
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
