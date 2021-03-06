from django.shortcuts import render
from zhugeleida import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from zhugeleida.forms.admin.shangchengshezhi_verify import jichushezhi, zhifupeizhi, yongjinshezhi
import json, zipfile, os, random, datetime, time, requests
from zhugeleida.views_dir.xiaochengxu import prepaidManagement as yuzhifu


# 商城基础查询
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def jiChuSheZhi(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_idObjs = models.zgld_admin_userprofile.objects.get(id=user_id)
    # xiaochengxu = models.zgld_xiaochengxu_app.objects.filter(id=u_idObjs[0].company_id)
    shezhi_obj = models.zgld_shangcheng_jichushezhi.objects.select_related('xiaochengxuApp__company').filter(xiaochengxuApp__company_id=user_idObjs.company_id)
    user_id_mallStatus = models.zgld_company.objects.filter(id=user_idObjs.company_id)
    mallStatus = user_id_mallStatus[0].get_shopping_type_display()
    mallStatusID = user_id_mallStatus[0].shopping_type
    otherData = []
    for obj in shezhi_obj:
        lunbotu = ''
        if obj.lunbotu:
            lunbotu = json.loads(obj.lunbotu)
        xiaoChengXuCompanyName = ''
        if obj.xiaochengxucompany:
            xiaoChengXuCompanyName = obj.xiaochengxucompany.name
        otherData.append({
            'shangChengName': obj.shangChengName,
            'shangHuHao': obj.shangHuHao,
            'shangHuMiYao': obj.shangHuMiYao,
            'lunbotu': lunbotu,
            'yongjin': obj.yongjin,
            'xiaochengxuApp': obj.xiaochengxuApp.name,
            'xiaochengxuApp_id': obj.xiaochengxuApp_id,
            'xiaochengxucompany_id': obj.xiaochengxucompany_id,
            'xiaochengxucompany': xiaoChengXuCompanyName,
            'zhengshu': obj.zhengshu,
            'mallStatus':mallStatus,
            'mallStatusID':mallStatusID,
            'classify_position':obj.classify_position,
            'classify_position_text':obj.get_classify_position_display(),
        })

    response.msg = '查询成功'
    response.data = {'otherData':otherData}
    response.code = 200
    return JsonResponse(response.__dict__)


#  商城基础操作
@csrf_exempt
@account.is_token(models.zgld_admin_userprofile)
def jiChuSheZhiOper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    u_idObjs = models.zgld_admin_userprofile.objects.get(id=user_id)
    company_id = u_idObjs.company_id
    userObjs = models.zgld_shangcheng_jichushezhi.objects.select_related(
        'xiaochengxuApp__company'
    ).filter(xiaochengxucompany_id=company_id)

    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    if request.method == "POST":

        # 商城基础设置 第一页基础设置
        if oper_type == 'jichushezhi':
            classify_position = request.POST.get('classify_position')

            resultData = {
                'classify_position': classify_position,
                'mallStatus' : request.POST.get('mallStatus'),          # 是否打开 商城 1为产品 2为商城
                'shangChengName' : request.POST.get('shangChengName'),
                'lunbotu' : request.POST.get('lunbotu'),
            }
            forms_obj = jichushezhi(resultData)
            if forms_obj.is_valid():
                formObjs = forms_obj.cleaned_data
                print('验证通过')
                if userObjs:
                    # 判断
                    if int(resultData.get('mallStatus')) == 2:
                        models.zgld_company.objects.filter(id=company_id).update(shopping_type=2)
                    else:
                        models.zgld_company.objects.filter(id=company_id).update(shopping_type=1)

                    # 更新基础设置 轮播图和商城名称
                    userObjs.update(
                        classify_position=classify_position,
                        shangChengName=formObjs.get('shangChengName'),
                        lunbotu=formObjs.get('lunbotu')
                    )
                    response.msg = '修改成功'
                    response.code = 200
                    response.data = {}
                else:
                    response.code = 301
                    response.msg = '未注册小程序'
                    return JsonResponse(response.__dict__)
            else:
                response.code = 301
                response.msg = '未通过'
                response.data = json.loads(forms_obj.errors.as_json())

        # 商城基础设置 第二页支付设置
        elif oper_type == 'zhifupeizhi':
            resultData = {
                'shangHuHao': request.POST.get('shangHuHao'),
                'shangHuMiYao': request.POST.get('shangHuMiYao'),
                'zhengshu': request.POST.get('zhengshu'),
            }
            forms_obj = zhifupeizhi(resultData)
            if forms_obj.is_valid():
                formObjs = forms_obj.cleaned_data
                zhengShuPath = formObjs.get('zhengshu')
                shangHuMiYao = formObjs.get('shangHuMiYao')
                shangHuHao = formObjs.get('shangHuHao') # 1516421881
                if userObjs:
                    try:
                        print('---- shangHuHao ---->>',shangHuHao) # 1516421881


                        shanghuzhengshupath =  base_path + '/' + zhengShuPath
                        file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin','secretKeyFile') + '/' + shangHuHao
                                              # statics/zhugeleida/imgs/admin/secretKeyFile/1543922970035.zip

                        print('---- os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) ---->>', '\n' ,os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                        #/data/www/zhugeApi
                        print('---- shanghuzhengshupath ---->>', shanghuzhengshupath)
                        # /data/www/zhugeApi/statics/zhugeleida/imgs/admin/secretKeyFile/1543924902964.zip

                        file_zip = zipfile.ZipFile(shanghuzhengshupath, 'r')
                        for file in file_zip.namelist():
                            file_zip.extract(file, r'{}'.format(file_dir))

                        file_zip.close()
                        os.remove(zhengShuPath)
                        print('---- os.remove(zhengShuPath) ---->>', zhengShuPath)  # statics/zhugeleida/imgs/admin/secretKeyFile/1543924902964.zip
                        print('------ file_dir ------> ',file_dir)                  # statics/zhugeleida/imgs/admin/secretKeyFile/1516421881

                        response.code = 200

                    except Exception:
                        response.code = 301
                        response.msg = '请添加正确 微信证书压缩包'
                        return JsonResponse(response.__dict__)

                    # 生成预支付订单 判断商户KEY 和 商户号 是否正确
                    xiaochengxu_app = models.zgld_gongzhonghao_app.objects.filter(
                        company_id=company_id)  # 真实数据appid
                    appid = xiaochengxu_app[0].authorization_appid
                    ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    shijianchuoafter5 = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
                    dingdanhao = str(ymdhms) + shijianchuoafter5 + str(random.randint(10, 99))

                    url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'  # 微信支付接口
                    customer_objs = models.zgld_customer.objects.filter(user_type=1,company_id=company_id,openid__isnull=False)
                    re_openid = ''
                    if customer_objs:
                        customer_obj = customer_objs[0]
                        re_openid = customer_obj.openid

                    result_data = {
                        'scene_id' : 'PRODUCT_5', #   发放红包使用场景，红包金额大于200或者小于1元时必传
                        'nonce_str': yuzhifu.generateRandomStamping(),  # 32位随机值a
                        'mch_billno': dingdanhao,  # 订单号
                        'mch_id': shangHuHao,      # 商户号
                        'wxappid': appid,  # 真实数据appid
                        're_openid': re_openid,  # 用户唯一标识
                        'total_amount': 30,  # 付款金额 1:100 | 发送一分钱
                        'client_ip': '192.168.1.1',  # 终端IP
                        'total_num': 1,  # 红包发放总人数
                        'send_name': '诸葛雷达_测试发红包',  # 商户名称 中文
                        'act_name': '测试商户',  # 活动名称 32长度
                        'remark': '测试备注信息',  # 备注信息 256长度
                        'wishing': '测试红包祝福语',  # 红包祝福语 128长度
                    }
                    print('--------- result_data --------> ',result_data)
                    SHANGHUKEY = formObjs.get('shangHuMiYao')    # 商户KEY
                    stringSignTemp = yuzhifu.shengchengsign(result_data, SHANGHUKEY)
                    result_data['sign'] = yuzhifu.md5(stringSignTemp).upper()
                    xml_data = yuzhifu.toXml(result_data).encode('utf8')

                    cret = base_path + "/" +  os.path.join(file_dir, 'apiclient_cert.pem')
                    key =  base_path + "/" +  os.path.join(file_dir, 'apiclient_key.pem')
                    print('--- cret -->>',cret) # statics/zhugeleida/imgs/admin/secretKeyFile/1516421881/apiclient_cert.pem
                    print('--- key -->>',key)   # statics/zhugeleida/imgs/admin/secretKeyFile/1516421881/apiclient_key.pem

                    ret = requests.post(url, data=xml_data, cert=(cret, key))
                    print(ret.text)
                    DOMTree = yuzhifu.xmldom.parseString(ret.text)
                    collection = DOMTree.documentElement
                    return_msg = collection.getElementsByTagName("return_msg")[0].childNodes[0].data
                    return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
                    print('----- return_code --> ',return_code)

                    if return_code == 'SUCCESS':  # 判断预支付返回参数 是否正确
                        userObjs.update(
                            shangHuHao=shangHuHao,
                            shangHuMiYao=shangHuMiYao,
                            zhengshu=file_dir
                        )
                        response.code = 200
                        response.msg = '修改成功'
                    else:
                        return_code = collection.getElementsByTagName("return_msg")[0].childNodes[0].data
                        response.code = '%s' % (return_code)
                        response.msg = '微信接口返回错误: {return_msg}'.format(return_msg=return_msg)

                        return JsonResponse(response.__dict__)
                else:
                    response.code = 301
                    response.msg = '未注册小程序'
                    return JsonResponse(response.__dict__)
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())

        # 商城基础设置 佣金配置
        elif oper_type == 'yongjinshezhi':
            resultData = {
                'yongjin': request.POST.get('yongjin'),
            }
            forms_obj = yongjinshezhi(resultData)
            if forms_obj.is_valid():
                formObjs = forms_obj.cleaned_data
                if userObjs:
                    userObjs.update(
                        yongjin=formObjs.get('yongjin')
                    )
                    response.msg = '修改成功'
                    response.code = 200
                    response.data = ''
                else:
                    response.code = 301
                    response.msg = '未注册小程序'
                # else:
                #     models.zgld_shangcheng_jichushezhi.objects.create(
                #         yongjin=formObjs.get('yongjin'),
                #     )

            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())


    elif request.method == 'GET':

        # 添加小程序ID
        if oper_type == 'addSmallProgram':
            xiaochengxuid = request.GET.get('xiaochengxuid')
            response = Response.ResponseObj()
            xiaochengxuObjs = models.zgld_xiaochengxu_app.objects.filter(id=xiaochengxuid)
            if xiaochengxuObjs:
                userObjs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxuApp_id=xiaochengxuid)
                nowdate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if not userObjs:
                    models.zgld_shangcheng_jichushezhi.objects.create(
                        xiaochengxuApp_id=xiaochengxuid,
                        xiaochengxucompany_id=company_id,
                        createDate=nowdate
                    )
                    response.code = 200
                    response.msg = '添加成功'
                else:
                    response.code = 301
                    response.msg = '该小程序已创建设置'

        # 用于商户对已发放的红包进行查询红包的具体信息，可支持普通红包和裂变包。
        elif oper_type == 'myself_query_fafang_info':
            dingdanhao = request.GET.get('mch_billno')
            company_id = request.GET.get('company_id')

            # 生成预支付订单 判断商户KEY 和 商户号 是否正确
            xiaochengxu_app = models.zgld_gongzhonghao_app.objects.filter(
                company_id=company_id)  # 真实数据appid

            jichushezhi_objs = models.zgld_shangcheng_jichushezhi.objects.filter(xiaochengxucompany_id=company_id)
            shangHuMiYao = ''
            shangHuHao = ''
            file_dir = ''
            if jichushezhi_objs:
                jichushezhi_obj = jichushezhi_objs[0]
                shangHuMiYao = jichushezhi_obj.shangHuMiYao
                shangHuHao = jichushezhi_obj.shangHuHao
                file_dir = jichushezhi_obj.zhengshu

            appid = xiaochengxu_app[0].authorization_appid

            url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/gethbinfo'  # 微信支付接口
            # customer_objs = models.zgld_customer.objects.filter(user_type=1, company_id=company_id,
            #                                                     openid__isnull=False)
            # re_openid = ''
            # if customer_objs:
            #     customer_obj = customer_objs[0]
            #     re_openid = customer_obj.openid

            result_data = {
                # 'scene_id' : 'PRODUCT_1', #   发放红包使用场景，红包金额大于200或者小于1元时必传
                'nonce_str': yuzhifu.generateRandomStamping(),  # 32位随机值a
                'mch_billno': dingdanhao,  # 订单号
                'mch_id': shangHuHao,  # 商户号

                'appid': appid,  # 真实数据appid
                'bill_type': 'MCHT',
            }
            print('--------- result_data --------> ', result_data)
              # 商户KEY
            stringSignTemp = yuzhifu.shengchengsign(result_data, shangHuMiYao)
            result_data['sign'] = yuzhifu.md5(stringSignTemp).upper()
            xml_data = yuzhifu.toXml(result_data).encode('utf8')

            cret = base_path + "/" + os.path.join(file_dir, 'apiclient_cert.pem')
            key = base_path + "/" + os.path.join(file_dir, 'apiclient_key.pem')
            print('--- cret -->>', cret)  # statics/zhugeleida/imgs/admin/secretKeyFile/1516421881/apiclient_cert.pem
            print('--- key -->>', key)  # statics/zhugeleida/imgs/admin/secretKeyFile/1516421881/apiclient_key.pem

            ret = requests.post(url, data=xml_data, cert=(cret, key))
            print(ret.text)
            DOMTree = yuzhifu.xmldom.parseString(ret.text)
            collection = DOMTree.documentElement
            return_msg = collection.getElementsByTagName("return_msg")[0].childNodes[0].data
            return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
            print('----- return_code --> ', return_code)

            if return_code == 'SUCCESS':  # 判断预支付返回参数 是否正确
                # userObjs.update(
                #     shangHuHao=shangHuHao,
                #     shangHuMiYao=shangHuMiYao,
                #     zhengshu=file_dir
                # )
                response.code = 200
                response.msg = 'chaxun 成功'
            else:
                return_code = collection.getElementsByTagName("return_msg")[0].childNodes[0].data
                response.code = '%s' % (return_code)
                response.msg = '微信接口返回错误: {return_msg}'.format(return_msg=return_msg)
                return JsonResponse(response.__dict__)


    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
