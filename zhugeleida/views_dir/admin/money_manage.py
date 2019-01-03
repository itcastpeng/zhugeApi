from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from zhugeleida.public.common import conversion_seconds_hms, conversion_base64_customer_username_base64
from zhugeleida.forms.admin.activity_manage_verify import SetFocusGetRedPacketForm, ActivityAddForm, ActivitySelectForm, \
    ActivityUpdateForm, ArticleRedPacketSelectForm,QueryFocusCustomerSelectForm
import qrcode,requests
from django.http import HttpResponse
from zhugeleida.public.common import create_qrcode
import qrcode, re, requests, hashlib, random, uuid, time, json, xml.dom.minidom as xmldom, base64

import json
from django.db.models import Q, Sum, Count


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def money_manage(request, oper_type):
    response = Response.ResponseObj()

    if request.method == "POST":

        # 获取支付二维码
        if oper_type == 'get_payment_qrcode':


            user_id = request.GET.get('user_id')
            phone = request.POST.get('phone', '')

            """
                 # 生成可扫码支付的二维码
                 :param request:
                 :param args:
                 :param kwargs:
                 :return:
            """

            APP_ID = "wx84390d5be4304d80"                 # 你公众账号上的appid
            MCH_ID = "1520981531"                         # 你的商户号
            API_KEY = "HEzhongkangqiaokejiyouxian201812"  # 微信商户平台(pay.weixin.qq.com) -->账户设置 -->API安全 -->密钥设置，设置完成后把密钥复制到这里

            # shangcheng_objs = models.zgld_shangcheng_jichushezhi.objects.filter(
            #     xiaochengxucompany_id=company_id)
            #
            # shangHuHao = ''
            # shangHuMiYao = ''
            # if shangcheng_objs:
            #     shangcheng_obj = shangcheng_objs[0]
            #     shangHuHao = shangcheng_obj.shangHuHao
            #     # send_name = shangcheng_obj.shangChengName
            #     shangHuMiYao = shangcheng_obj.shangHuMiYao

            paydict = {
                'appid': APP_ID,
                'mch_id': MCH_ID,
                'nonce_str': str(uuid.uuid4()).replace('-', ''),
                'product_id': 13020006631,  # 商品id，可自定义
                'time_stamp': int(time.time()),
            }
            paydict['sign'] = get_sign(paydict, API_KEY)
            url = "weixin://wxpay/bizpayurl?appid=%s&mch_id=%s&nonce_str=%s&product_id=%s&time_stamp=%s&sign=%s" \
                  % (paydict['appid'], paydict['mch_id'], paydict['nonce_str'], paydict['product_id'],
                     paydict['time_stamp'], paydict['sign'])

            # 可以直接在微信中点击该url，如果有错误，微信会弹出提示框，如果是扫码，如果失败，什么提示都没有，不利于调试
            print('支付该url-------------->>',url)

            # 创建二维码
            qrcode_data = {
                'url': url,
                'type': 'payment_qrcode_url'
            }
            response_ret = create_qrcode(qrcode_data)
            pre_qrcode_url = response_ret.get('pre_qrcode_url')

            if pre_qrcode_url:
                print('预支付二维码pre_qrcode_url---------->>',pre_qrcode_url)
                response.data = {
                    'pay_qrcode_url' : pre_qrcode_url
                }
                response.code = 200
                response.msg = '返回成功'



            # forms_obj = SetFocusGetRedPacketForm(form_data)
            # if forms_obj.is_valid():
            #     company_id = models.zgld_admin_userprofile.objects.get(id=user_id).company_id
            #     gongzhonghao_app_objs = models.zgld_gongzhonghao_app.objects.filter(company_id=company_id)
            #
            #     if gongzhonghao_app_objs:
            #         gongzhonghao_app_objs.update(
            #             is_focus_get_redpacket=is_focus_get_redpacket,
            #             focus_get_money=focus_get_money,
            #             focus_total_money=focus_total_money
            #         )
            #         #  查询成功 返回200 状态码
            #         response.code = 200
            #         response.msg = '设置成功'
            #
            #     else:
            #         response.code = 301
            #         response.msg = '公众号不存在'
            #
            #
            # else:
            #     response.code = 301
            #     response.msg = json.loads(forms_obj.errors.as_json())

    else:
       pass



    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def activity_manage_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    if request.method == "POST":
        # 删除-个人产品
        if oper_type == "delete":

            objs = models.zgld_article_activity.objects.filter(id=o_id)

            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 301
                response.msg = '活动不存在或者正在进行中'

        # 修改个人产品
        elif oper_type == 'update':

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            activity_id = o_id
            activity_name = request.POST.get('activity_name')
            article_id = request.POST.get('article_id')  # 文章ID
            activity_total_money = request.POST.get('activity_total_money')
            activity_single_money = request.POST.get('activity_single_money')
            reach_forward_num = request.POST.get('reach_forward_num')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            reach_stay_time = request.POST.get('reach_stay_time')  # 达到多少秒发红包
            limit_area = request.POST.get('limit_area')
            is_limit_area = request.POST.get('is_limit_area')


            form_data = {

                'company_id': company_id,
                'activity_id': activity_id,  # 活动名称
                'activity_name': activity_name,  # 活动名称

                'article_id': article_id,  # 文章ID
                'activity_total_money': activity_total_money,  # 活动总金额(元)
                'activity_single_money': activity_single_money,  # 单个金额(元)
                'reach_forward_num': reach_forward_num,  # 达到多少次发红包(转发次数)
                'start_time': start_time,  # 达到多少次发红包(转发次数)
                'end_time': end_time,  # 达到多少次发红包(转发次数)

                'reach_stay_time': reach_stay_time,  # 达到多少秒
                'is_limit_area': is_limit_area       # 是否限制区域
            }

            forms_obj = ActivityUpdateForm(form_data)
            if forms_obj.is_valid():

                reach_stay_time = forms_obj.cleaned_data.get('reach_stay_time')

                if not  is_limit_area: # 没有限制
                    limit_area = json.dumps('[]')


                objs = models.zgld_article_activity.objects.filter(id=activity_id, company_id=company_id)

                if objs:
                    objs.update(
                        article_id=article_id,
                        activity_name=activity_name.strip(),
                        activity_total_money=activity_total_money,
                        activity_single_money=activity_single_money,
                        reach_forward_num=reach_forward_num,
                        start_time=start_time,
                        end_time=end_time,

                        reach_stay_time=reach_stay_time,
                        is_limit_area=is_limit_area,
                        limit_area=limit_area,
                    )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 增加红包活动
        elif oper_type == "add":

            user_id = request.GET.get('user_id')
            company_id = request.GET.get('company_id')
            activity_name = request.POST.get('activity_name')
            article_id = request.POST.get('article_id')  # 文章ID
            activity_total_money = request.POST.get('activity_total_money')
            activity_single_money = request.POST.get('activity_single_money')
            reach_forward_num = request.POST.get('reach_forward_num')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            reach_stay_time = request.POST.get('reach_stay_time')  #达到多少秒发红包
            limit_area = request.POST.get('limit_area')
            is_limit_area = request.POST.get('is_limit_area')



            form_data = {

                'company_id': company_id,
                'activity_name': activity_name,  # 活动名称
                'article_id': article_id,  # 文章ID
                'activity_total_money': activity_total_money,  # 活动总金额(元)
                'activity_single_money': activity_single_money,  # 单个金额(元)
                'reach_forward_num': reach_forward_num,  # 达到多少次发红包(转发次数)
                'start_time': start_time,  #
                'end_time': end_time,  #

                'reach_stay_time' : reach_stay_time, #达到多少秒
                'is_limit_area' : is_limit_area,     # 是否限制区域

            }

            forms_obj = ActivityAddForm(form_data)
            if forms_obj.is_valid():
                reach_stay_time = forms_obj.cleaned_data.get('reach_stay_time')

                if not  is_limit_area: # 没有限制
                    limit_area = json.dumps('[]')


                models.zgld_article_activity.objects.create(
                    article_id=article_id,
                    company_id=company_id,
                    activity_name=activity_name.strip(),
                    activity_total_money=activity_total_money,
                    activity_single_money=activity_single_money,
                    reach_forward_num=reach_forward_num,
                    start_time=start_time,
                    end_time=end_time,
                    reach_stay_time=reach_stay_time,
                    is_limit_area=is_limit_area,
                    limit_area=limit_area,
                )

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)




def random_str(randomlength=8):
    """
    生成随机字符串
    :param randomlength: 字符串长度
    :return:
    """
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str


def order_num(phone):
    """
    生成扫码付款订单号
    :param phone: 手机号
    :return:
    """
    local_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    result = phone + 'T' + local_time + random_str(5)
    return result


def get_sign(data_dict, key):
    # 签名函数，参数为签名的数据和密钥
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode('utf-8'))  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    return sign


def trans_dict_to_xml(data_dict):  # 定义字典转XML的函数
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml)).encode('utf-8')  # 返回XML，并转成utf-8，解决中文的问题


def trans_xml_to_dict(data_xml):
    soup = BeautifulSoup(data_xml, features='xml')
    xml = soup.find('xml')  # 解析XML
    if not xml:
        return {}
    data_dict = dict([(item.name, item.text) for item in xml.find_all()])
    return data_dict


def wx_pay_unifiedorde(detail):
    """
    访问微信支付统一下单接口
    :param detail:
    :return:
    """
    detail['sign'] = get_sign(detail, API_KEY)
    # print(detail)
    xml = trans_dict_to_xml(detail)  # 转换字典为XML
    response = requests.request('post', UFDODER_URL, data=xml)  # 以POST方式向微信公众平台服务器发起请求
    # data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    return response.content


def pay_fail(err_msg):
    """
    微信支付失败
    :param err_msg: 失败原因
    :return:
    """
    data_dict = {'return_msg': err_msg, 'return_code': 'FAIL'}
    return trans_dict_to_xml(data_dict)


