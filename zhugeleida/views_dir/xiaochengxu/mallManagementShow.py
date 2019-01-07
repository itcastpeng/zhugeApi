from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.xiaochengxu.theOrder_verify import GoodsManagementSelectForm
import json, base64
from zhugeleida.forms.xiaochengxu.product_verify  import GoodGetForm

from django.db.models import Q
from zhugeleida.public.common import action_record
from django.db.models import F
import datetime
import uuid,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

@csrf_exempt
# @account.is_token(models.zgld_customer)
def mallManage(request):


    response = Response.ResponseObj()
    if request.method == "GET":

        customer_id = request.GET.get('user_id')
        uid = request.GET.get('uid')
        parentName_id = request.GET.get('parentName_id')
        detaileId = request.GET.get('detaileId')    # 查询详情
        u_idObjs = models.zgld_userprofile.objects.get(id=uid)
        company_id = u_idObjs.company_id

        xiaoChengXuObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxucompany_id=company_id)
        indexLunBoTu = ''
        if xiaoChengXuObjs:
            indexLunBoTu = xiaoChengXuObjs[0].lunbotu  # 查询首页 轮播图

        otherData = []
        forms_obj = GoodsManagementSelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            if detaileId:
                # print('=====================xiaoChengXuObjs[0].id.....> ',xiaoChengXuId)

                objs = models.zgld_goods_management.objects.filter(company_id=company_id,id=detaileId,goodsStatus__in=[1,3])
                count = objs.count()
                if objs:

                    obj = objs[0]
                    groupObjs = models.zgld_goods_classification_management.objects.filter(id=obj.parentName_id)
                    xianshangjiaoyi = '否'

                    if obj.xianshangjiaoyi:
                        xianshangjiaoyi = '是'

                    topLunBoTu = ''
                    if obj.topLunBoTu:
                        topLunBoTu = json.loads(obj.topLunBoTu)
                    detailePicture = ''
                    if obj.detailePicture:
                        detailePicture = json.loads(obj.detailePicture)
                    parentGroup_id = obj.parentName_id
                    parentGroup_name = obj.parentName.classificationName
                    if groupObjs[0].parentClassification_id:
                        parent_group_name = groupObjs[0].parentClassification.classificationName
                        parentGroup_name = parent_group_name + ' > ' + parentGroup_name

                    content = obj.content
                    if content:
                        content = json.loads(content)
                    goodsName = obj.goodsName
                    otherData.append({
                        'id':obj.id,
                        'goodsName': goodsName,
                        'parentName_id':parentGroup_id,
                        'parentName':parentGroup_name,
                        'goodsPrice':obj.goodsPrice,
                        'goodsStatus_code':obj.goodsStatus,
                        'goodsStatus':obj.get_goodsStatus_display(),
                        'xianshangjiaoyi':xianshangjiaoyi,
                        'shichangjiage':obj.shichangjiage,
                        'topLunBoTu': topLunBoTu,                       # 顶部轮播图
                        'content': content,
                        'detailePicture' : detailePicture,              # 详情图片
                        'createDate': obj.createDate.strftime('%Y-%m-%d %H:%M:%S'),
                        'shelvesCreateDate':obj.shelvesCreateDate.strftime('%Y-%m-%d %H:%M:%S'),
                        'DetailsDescription': obj.DetailsDescription    # 描述详情
                    })

                    if customer_id:
                        customer_obj = models.zgld_customer.objects.filter(id=customer_id)
                        if customer_obj and customer_obj[0].username:  # 说明客户访问时候经过认证的
                            remark = '正在查看【%s】,尽快把握商机' % (goodsName)
                            data = request.GET.copy()
                            data['action'] = 2
                            action_record(data, remark)

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                         'otherData':otherData,
                         'count' : count
                    }

                else:
                    response.code = 302
                    response.msg = '无数据'

            else:

                q1 = Q()
                q1.add(Q(**{'company_id': company_id}), Q.AND)

                if parentName_id:
                    q1.add(Q(**{'parentName_id': parentName_id}), Q.AND)

                objs = models.zgld_goods_management.objects.filter(q1).exclude(goodsStatus__in=[2,4]).order_by('-recommend_index')
                count = objs.count()

                if objs:
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]


                    for obj in objs:
                        topLunBoTu = ''
                        if obj.topLunBoTu:
                            topLunBoTu = json.loads(obj.topLunBoTu)

                        otherData.append({
                            'id':obj.id,
                            'goodsName': obj.goodsName,
                            'goodsPrice': obj.goodsPrice,
                            'topLunBoTu': topLunBoTu,
                            'shichangjiage': obj.shichangjiage,
                        })

                    if indexLunBoTu:
                        indexLunBoTu = json.loads(indexLunBoTu)

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'indexLunBoTu':indexLunBoTu,
                        'otherData':otherData,
                        'count': count
                    }
                    if customer_id:
                        customer_obj = models.zgld_customer.objects.filter(id=customer_id)
                        if customer_obj and customer_obj[0].username:  # 说明客户访问时候经过认证的
                            remark = '正在查看您发布的商品,尽快把握商机'
                            data = request.GET.copy()
                            data['action'] = 2
                            action_record(data, remark)

                else:
                    response.code = 302
                    response.msg = '无数据'



    return JsonResponse(response.__dict__)


@csrf_exempt
# @account.is_token(models.zgld_customer)
def mallManage_oper(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "GET":

        if oper_type == 'consult_product':

            forms_obj = GoodGetForm(request.GET)
            if forms_obj.is_valid():

                customer_id = request.GET.get('user_id')
                user_id = request.GET.get('uid')
                goods_id = request.GET.get('product_id')

                goods_obj = models.zgld_goods_management.objects.get(id=goods_id)


                topLunBoTu = goods_obj.topLunBoTu

                topLunBoTu = json.loads(topLunBoTu)
                url = topLunBoTu[0].get('data')

                goods_cover_url =  url[0]

                goods_price = goods_obj.goodsPrice   # 产品价格
                goods_name =  goods_obj.goodsName    #产品民称


                new_goods_cover_filename = str(uuid.uuid1())
                exit_goods_cover_path = BASE_DIR + '/' +  goods_cover_url

                file_type = exit_goods_cover_path.split('.')[-1]

                new_filename = new_goods_cover_filename + '.' + file_type

                new_goods_cover_path =  "/".join((BASE_DIR, 'statics', 'zhugeleida', 'imgs','chat' ,new_filename))
                print('------new_goods_cover_path------->>',new_goods_cover_path)

                with open(exit_goods_cover_path,'rb') as read_file:
                    with open(new_goods_cover_path, 'wb') as new_file:
                      new_file.write(read_file.read())

                static_goods_cover_url =  "/".join(( 'statics', 'zhugeleida', 'imgs', 'chat', new_filename))
                print('------static_goods_cover_url---->>',static_goods_cover_url)

                models.zgld_chatinfo.objects.filter(userprofile_id=user_id,customer_id=customer_id).update(is_last_msg=False)

                _content =  {
                    'info_type' : 2,  # (2,'product_info')   #客户和用户之间的产品咨询
                    'product_name' :  goods_name,
                    'product_price' : goods_price,
                    'product_cover_url' : static_goods_cover_url,
                    'product_id' : goods_id
                }
                content = json.dumps(_content)

                models.zgld_chatinfo.objects.create(
                    userprofile_id=user_id,
                    customer_id=customer_id,
                    send_type=2,  # 代表客户发送给用户
                    content=content
                    # info_type=2,  # (2,'product_info')   #客户和用户之间的产品咨询
                    # product_name=product_name,
                    # product_price=product_price,
                    # product_cover_url=static_product_cover_url,
                    )

                ## 记录客户咨询产品
                flow_up_objs = models.zgld_user_customer_belonger.objects.filter(user_id=user_id, customer_id=customer_id)
                # update(read_count=F('read_count') + 1)

                if flow_up_objs:  # 用戶發消息給客戶，修改最後跟進-時間
                    flow_up_objs.update(
                        is_customer_msg_num=F('is_customer_msg_num') + 1,
                        last_activity_time=datetime.datetime.now()
                    )

                remark = '向您咨询商品'
                data = request.GET.copy()
                data['action'] = 7 # 咨询产品
                action_record(data, remark)
                response.code = 200
                response.msg = "咨询商品返回成功"



        elif oper_type == 'forward_product':

            product_id = request.GET.get('product_id')
            objs = models.zgld_goods_management.objects.filter(id=product_id)

            if objs:
                remark = '转发了【%s】' % (objs[0].goodsName)
                data = request.GET.copy()
                data['action'] = 2
                action_record(data, remark)
                response.code = 200
                response.msg = "记录转发产品成功"

            else:

                response.code = 302
                response.msg = "商品不存在"


    return JsonResponse(response.__dict__)