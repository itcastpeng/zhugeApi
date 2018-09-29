import json


def user_send_template_msg(request):
    # response = ResponseObj()

    print('request -->', request.GET)
    data = json.loads(request.GET.get('data'))

    user_id = data.get('user_id')
    customer_id = data.get('customer_id')
    userprofile_obj = models.zgld_userprofile.objects.get(id=user_id)
    company_id = userprofile_obj.company_id
    print('company_id -->', company_id)
    obj = models.zgld_xiaochengxu_app.objects.get(company_id=company_id)
    authorizer_refresh_token = obj.authorizer_refresh_token
    authorizer_appid = obj.authorization_appid
    template_id = obj.template_id


    rc = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)
    customer_obj = models.zgld_customer.objects.filter(id=customer_id)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    objs = models.zgld_user_customer_belonger.objects.select_related('user').filter(
        customer_id=customer_id,
        user_id=user_id
    )
    exist_formid_json = json.loads(objs[0].customer.formid)
    user_name = objs[0].user.username
    flag = True
    while flag:

        post_template_data =  {}
        # get_token_data['appid'] = authorization_appid
        # get_token_data['secret'] = authorization_secret
        # get_token_data['grant_type'] = 'client_credential'

        component_appid = 'wx67e2fde0f694111c'  # 第三平台的app id
        key_name = '%s_authorizer_access_token' % (authorizer_appid)
        authorizer_access_token = rc.get(key_name)  # 不同的 小程序使用不同的 authorizer_access_token，缓存名字要不一致。

        if not authorizer_access_token:
            data = {
                'key_name' : key_name,
                'authorizer_refresh_token': authorizer_refresh_token,
                'authorizer_appid': authorizer_appid,

            }
            authorizer_access_token = create_authorizer_access_token(data)

        get_template_data = {
            'access_token' : authorizer_access_token      #授权方接口调用凭据（在授权的公众号或小程序具备API权限时，才有此返回值），也简称为令牌
        }
        # global openid,form_id
        if customer_obj and objs:
            openid = customer_obj[0].openid
            post_template_data['touser'] = openid

            # post_template_data['template_id'] = 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE'
            post_template_data['template_id'] = template_id
            # path = 'pages/mingpian/index?source=2&uid=%s&pid=' % (user_id)
            path = 'pages/mingpian/msg?source=template_msg&uid=%s&pid=' % (user_id)
            post_template_data['page'] = path

            if len(exist_formid_json) == 0:
                response.msg = "没有formID"
                response.code = 301
                print('------- 没有消费的formID -------->>')
                break

            print('---------formId 消费前数据----------->>',exist_formid_json)
            form_id = exist_formid_json.pop(-1)
            obj = models.zgld_customer.objects.filter(id=customer_id)

            obj.update(formid=json.dumps(exist_formid_json))
            print('---------formId 消费了哪个 ----------->>', form_id)
            post_template_data['form_id'] = form_id


            # 留言回复通知
            data = {
                'keyword1': {
                    'value': user_name  # 回复者
                },
                'keyword2': {
                    'value': now_time   # 回复时间
                },
                'keyword3': {
                    'value': '您有未读消息,点击小程序查看哦'  #回复内容
                }
            }
            post_template_data['data'] = data
            # post_template_data['emphasis_keyword'] = 'keyword1.DATA'
            print('===========post_template_data=======>>',post_template_data)

            # https://developers.weixin.qq.com/miniprogram/dev/api/notice.html  #发送模板消息-参考

            template_ret = requests.post(Conf['template_msg_url'], params=get_template_data, data=json.dumps(post_template_data))
            template_ret = template_ret.json()

            print('--------企业用户 send to 小程序 Template 接口返回数据--------->',template_ret)

            if template_ret.get('errmsg') == "ok":
                print('-----企业用户 send to 小程序 Template 消息 Successful---->>', )
                response.code = 200
                response.msg = "企业用户发送模板消息成功"
                flag = False

            elif template_ret.get('errcode') == 40001:
                rc.delete(key_name)

            else:
                print('-----企业用户 send to 小程序 Template 消息 Failed---->>', )
                response.code = 301
                response.msg = "企业用户发送模板消息失败"

        else:
            response.msg = "客户不存在"
            response.code = 301
            print('---- Template Msg 客户不存在---->>')

    return JsonResponse(response.__dict__)


