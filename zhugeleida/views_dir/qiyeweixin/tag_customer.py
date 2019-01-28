
from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.tag_customer_verify import TagCustomerAddForm, TagCustomerUpdateForm, TagCustomerSelectForm
import time
import datetime
import json,base64


from publicFunc.condition_com import conditionCom

def insert_sort(objs):
    for i in  range(1,len(objs)):
        if  objs[i]['customer_num']  >  objs[i-1]['customer_num']:
            temp = objs[i]['customer_num']
            temp_tag_id = objs[i]['tag_id']
            name = objs[i]['name']
            id = objs[i]['id']
            customer_list =  objs[i]['customer_list']

            for j in range(i-1,-1,-1):
                if objs[j]['customer_num'] < temp:
                    objs[j + 1]['customer_num'] = objs[j]['customer_num']

                    objs[j + 1]['tag_id'] = objs[j]['tag_id']
                    objs[j + 1]['name'] = objs[j]['name']
                    objs[j + 1]['id'] = objs[j]['id']
                    objs[j + 1]['customer_list'] = objs[j]['customer_list']

                    index = j  # 记下应该插入的位置
                else:
                    break
                objs[index]['customer_num'] = temp
                objs[index]['tag_id'] = temp_tag_id
                objs[index]['name'] = name
                objs[index]['id'] = id
                objs[index]['customer_list'] = customer_list

    return objs

#查询标签和所属的用户
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_customer(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 获取参数 页数 默认1
        tag_type = request.GET.get('tag_type')



        forms_obj = TagCustomerSelectForm(request.GET)
        if forms_obj.is_valid():

            order = request.GET.get('order', '-create_date')

            field_dict = {
                 'id': '',
                 'name': '__contains',
            }

            q = conditionCom(request, field_dict)
            if tag_type:
                q.add('tag_type',tag_type)

            objs = models.zgld_tag.objects.filter(q).order_by(order)


            # 获取所有数据
            ret_data = []
            for obj in objs:
                customer_list = []
                for c_obj in obj.tag_customer.all():

                    try:
                        username = base64.b64decode(c_obj.username)
                        customer_name = str(username, 'utf-8')
                        print('----- 解密b64decode username----->', username)

                    except Exception as e:
                        print('----- b64decode解密失败的 customer_id 是 | e ----->', c_obj.id, "|", e)
                        customer_name = '客户ID%s' % (c_obj.id)

                    customer_list.append({'id': c_obj.id,'headimgurl': c_obj.headimgurl ,'name': customer_name})

                if customer_list:
                    customer_num = len(customer_list)
                    ret_data.append({
                        'id': obj.id,
                        'name': obj.name,
                        'tag_id': obj.id,
                        'customer_num': customer_num,
                        'customer_list': customer_list
                    })

            response.code = 200
            response.data = {
                'ret_data': insert_sort(ret_data),
                'ret_count': len(ret_data),
            }

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)

# 标签 和 标签客户的操作
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def tag_customer_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 添加标签
        if oper_type == "add":

            tag_type = request.POST.get('tag_type')

            tag_data = {
                'name' : request.POST.get('name'),
                'tag_type' : tag_type
            }


            forms_obj = TagCustomerAddForm(tag_data)
            if forms_obj.is_valid():
                parent_id = models.zgld_tag.objects.filter(name='自定义')[0].id
                customer_list = json.loads(request.POST.get('customer_list'))

                if customer_list:
                    obj = models.zgld_tag.objects.create(**forms_obj.cleaned_data)
                    obj.tag_parent_id = parent_id
                    obj.tag_customer = customer_list

                    response.code = 200
                    response.msg = "添加成功"
                else:
                    response.code = 302
                    response.msg = "标签关联客户不能为空"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        # 添加标签
        elif  oper_type == "update":

            tag_data = {
                'tag_id': o_id,
                # 'name' : request.POST.get('name'),
            }

            forms_obj = TagCustomerUpdateForm(tag_data)
            if forms_obj.is_valid():
                customer_list = json.loads(request.POST.get('customer_list'))
                if customer_list:
                    print('customer_list ------->>',customer_list)

                    objs = models.zgld_tag.objects.filter(id=o_id)
                    if objs:
                        objs[0].tag_customer = customer_list
                        response.code = 200
                        response.msg = "添加成功"
                    else:
                        response.code = 302
                        response.msg = "标签不存在"

                else:
                    response.code = 302
                    response.msg = "标签关联客户不能为空"

            else:
                # print("验证不通过")
                print(forms_obj.errors)
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        # 删除用户标签

        elif oper_type == "delete":
            tag_id = request.POST.get('id')
            company_id = request.GET.get('company_id')

            tag_objs = models.zgld_tag.objects.filter(id=tag_id,user__company_id=company_id)
            if tag_objs:
                tag_objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '标签不存在'


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)






