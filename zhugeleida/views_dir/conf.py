
Conf = {
    # 企业的id，在管理端->"我的企业" 可以看到
    # "corpid": "wx81159f52aff62388",
    # # "通讯录同步"应用的secret, 开启api接口同步后，可以在管理端->"通讯录同步"看到
    # "corpsecret": "48m2h1e2DRcA55yfKqHa083UpbJy-30u30ypy4zPr8E",

    "token_url": "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
    "code_url":  "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo",
    "userlist_url" : "https://qyapi.weixin.qq.com/cgi-bin/user/getuserdetail",

    "tongxunlu_token_url": "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
    "add_user_url" : "https://qyapi.weixin.qq.com/cgi-bin/user/create",
    "update_user_url" : "https://qyapi.weixin.qq.com/cgi-bin/user/update",
    "delete_user_url" : "https://qyapi.weixin.qq.com/cgi-bin/user/delete",

    "add_department_url":  "https://qyapi.weixin.qq.com/cgi-bin/department/create",
    "update_department_url":  "https://qyapi.weixin.qq.com/cgi-bin/department/update",
    "delete_department_url": "https://qyapi.weixin.qq.com/cgi-bin/department/delete",


    "appid" : "wx1add8692a23b5976",                   #小程序唯一标识
    "appsecret": "26a939c9d1c6fe911acfd9cc9deac8f4",  #小程序的 app secret

    "appurl": "https://api.weixin.qq.com/sns/jscode2session",  #小程序临时登录凭证校验接口
    "qr_token_url" :  "https://api.weixin.qq.com/cgi-bin/token",
    "qr_code_url":  "https://api.weixin.qq.com/wxa/getwxacode",

    #小程序发送模板消息
    "template_msg_url" : "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send",

    # 企业微信发送消息
    "send_msg_url" :  "https://qyapi.weixin.qq.com/cgi-bin/message/send",


    # "qr_code_url":  "https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode",


}