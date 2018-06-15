from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.qiyeweixin.search_verify import SearchTagSelectForm
import time
import datetime
import json

from publicFunc.condition_com import conditionCom
from django.db.models import Q


# 查询标签和所属的用户
@csrf_exempt
@account.is_token(models.zgld_userprofile)
def search(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        # 切片获取 top9 标签[客户标签]
        if oper_type == 'get_tag':
            print('------->>', request.GET)

            # current_page = forms_obj.cleaned_data['current_page']
            # length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', 'create_date')

            field_dict = {
                'id': '',
                'name': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.zgld_tag.objects.filter(q).order_by(order)

            # if length != 0:
            #     print('current_page -->', current_page)
            #     start_line = (current_page - 1) * length
            #     stop_line = start_line + length
            #     objs = objs[start_line: stop_line]

            # 获取所有数据
            ret_data = []
            for obj in objs:
                customer_list = []
                for c_obj in obj.tag_customer.all():
                    customer_list.append({'id': c_obj.id, 'headimgurl': c_obj.headimgurl, 'name': c_obj.username})

                if customer_list:
                    customer_num = len(customer_list)
                    ret_data.append({
                        'id': obj.id,
                        'name': obj.name,
                        'tag_id': obj.id,
                        'customer_num': customer_num,
                        'customer_list': customer_list,

                    })

            response.code = 200
            response.data = {
                'ret_data': insert_sort(ret_data)[0:9],
                'ret_count': len(ret_data),
            }

        elif oper_type == 'get_user':

            # q = Q(Q(username='xxx') | Q(username='ddd'))
            # q = Q()
            # q.add(Q(**{'username': 'xxx', 'sex': '1'}), Q.OR)
            # q.add(Q(**{'username': 'xxsssx'}), Q.OR)
            # print('q --===->', q)

            order = request.GET.get('order', 'create_date')
            field_dict = {
                'id': '',
                'username': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            search_fiedld = request.GET.get('username')
            if search_fiedld: # 判断有输入username 才会从数据库查数据
                objs = models.zgld_customer.objects.filter(q).order_by(order)
                count = objs.count()
                print('------objs---->>',objs)
                ret_data = []
                if objs:
                    for obj in objs:
                        ret_data.append({
                            'customer_id': obj.id,
                            'username': obj.username,
                            'headimgurl': obj.headimgurl,
                            'create_date': obj.create_date,  #
                        })

                    #  查询成功 返回200 状态码
                    print('----ret_data----->', ret_data)

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'data_count': count,
                    }

        else:
            response.code = 402
            response.msg = "请求异常"


        return JsonResponse(response.__dict__)

    else:
        response.code = 402
        response.msg = "请求异常"


def insert_sort(objs):
    for i in range(1, len(objs)):
        if objs[i]['customer_num'] > objs[i - 1]['customer_num']:
            temp = objs[i]['customer_num']
            temp_tag_id = objs[i]['tag_id']
            name = objs[i]['name']
            id = objs[i]['id']
            customer_list = objs[i]['customer_list']

            for j in range(i - 1, -1, -1):
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
