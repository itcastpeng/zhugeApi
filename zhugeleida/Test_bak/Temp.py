
import json
#
# jsonData = [{'name': 'ITY张某某', 'age': 30, 'sex': '男'}, {'name': '李某', 'age': 20, 'sex': '女'}]
#
# # 序列化，然后输出
# jsonStr = json.dumps(jsonData, ensure_ascii=False)
# print("序列化结果：")
# print(jsonStr)

import requests
app_id = 'wx67e2fde0f694111c'





#
# get_wx_info_data = {}
# post_wx_info_data = {}
# access_token = "13_H0YQkLqGN8KYZDT4mVhmuI96gIF2sDBPaGLHxo_Iivc5jajloUpby3yqCNFWU9nANuyuZVsVCfB0kpFCdiUEf4SbyAL2Hkwe8q8UfIjbCBZEMutVK8lFWnlrJ-FOgFCDBZrO7zBF7OSeh5tPSWZeABAHLO"
#
# post_wx_info_data['component_appid'] = app_id
# post_wx_info_data['authorizer_appid'] = 'wxd306d71b02c5075e'
# get_wx_info_data['component_access_token'] = access_token


# url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
# authorizer_info_ret = requests.post(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
#
# print('----------- 获取小程序授权方的authorizer_info信息 返回 ------------->', json.dumps(authorizer_info_ret.json()))
#
# gettemplate_list_url = 'https://api.weixin.qq.com/wxa/gettemplatelist'
# gettemplate_list_data = {
#     'access_token' : access_token
# }
#
# gettemplate_list_ret = requests.post(gettemplate_list_url, params=gettemplate_list_data)
#
# print('----------- 版库中的所有小程序代码模版 返回 ------------->', json.dumps(gettemplate_list_ret.json()))


# authorizer_access_token = "13_iIWzM88IS2bsJVG9guziHYRHfB4AUA2k8F3-XxbYmraDMI045etJ6474EoLeWw7VKXljIRof95H6CDUtz8mNdicQD5ripTUemLqz1qoZlVPw2taDA7kXokIK-AsHALk0lrCb99yFIE2bHytmBOBbAKDXKX"
# bind_tester_url = 'https://api.weixin.qq.com/wxa/bind_tester'
# get_bind_tester_data = {
#     'access_token': authorizer_access_token
# }
#
# for wechatid in ['Ju_do_it', 'ai6026325', 'crazy_acong', 'lihanjie5201314', 'wxid_6bom1qvrrjhv22']:
#     post_bind_tester_data = {
#         "wechatid": wechatid
#     }
#     domain_data_ret = requests.post(bind_tester_url, params=get_bind_tester_data,
#                                     data=json.dumps(post_bind_tester_data))
#     domain_data_ret = domain_data_ret.json()
#     print('----------绑定微信用户为小程序体验者------------>>', domain_data_ret)



################ 版本回退 @@@@@@@

# access_token = '13_R56rXwAjyGxvdJQu5XEGaXL1vLqwn2OD94-xVKVOhubjS17HclTf7ikdhdpPUPYvEbuhrXzi8ybYNhntstm-Nas-_vkHsxO76SPA3WOUtbbm7inpv-uqpmCDEWG_jYXvb0OId_H3sli7cip3VQJbAKDFAT'
#
# get_wx_info_data = {
#     'access_token' : access_token
#
# }
#
#
# url = 'https://api.weixin.qq.com/wxa/revertcoderelease'
#
# authorizer_info_ret = requests.get(url, params=get_wx_info_data)
#
# print('----------- 版库中的所有小程序代码模版 返回 ------------->', json.dumps(authorizer_info_ret.json()))



#
# def  create_authorizer_access_token():
#
#     app_id = 'wx67e2fde0f694111c'
#     get_auth_token_data = {
#         'component_access_token': "13_-0xJnm3FKROqkZb2GvNvqsRUV3RmL1Q_iDZpyaIqh5V92ShjxkduabLIWuQdsc-LQ_p46XaocIW_XBWfcdjvC3EGR7-Ca9AmBeV9btjNIHKHynyW_zV0OG5ipK0CXpvJOq4vzIEodBpHOkrYIQHdAHAPXO"
#     }
#
#     post_auth_token_data = {
#         'component_appid': app_id,
#         'authorizer_appid': 'wx1add8692a23b5976',
#         'authorizer_refresh_token': 'refreshtoken@@@09yY9swB2BonuG6Yk_Q80AaCGCuc5ftYTZiwVNS9Byw'
#     }
#
#     authorizer_token_url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
#     authorizer_info_ret = requests.post(authorizer_token_url, params=get_auth_token_data,
#                                         data=json.dumps(post_auth_token_data))
#     authorizer_info_ret = authorizer_info_ret.json()
#
#     print('-------获取（刷新）授权小程序的接口调用凭据 authorizer_token 返回--------->>', authorizer_info_ret)
#
#     authorizer_access_token = authorizer_info_ret.get('authorizer_access_token')
#     authorizer_refresh_token = authorizer_info_ret.get('authorizer_refresh_token')
#
#         # response.data = {
#         #     'authorizer_access_token' : authorizer_access_token
#         # }
#     print('------ 获取令牌（authorizer_access_token）成功------>>',authorizer_access_token)
#
#     get_wx_info_data = {
#         'access_token': authorizer_access_token
#
#     }
#     post_wx_info_data = {
#
#     }
#
#     #url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
#     # url = 'https://api.weixin.qq.com/cgi-bin/account/getaccountbasicinfo'
#     # url = 'https://api.weixin.qq.com/cgi-bin/wxopen/getcategory'
#     url = 'https://api.weixin.qq.com/wxa/getwxasearchstatus'
#     authorizer_info_ret = requests.get(url, params=get_wx_info_data, data=json.dumps(post_wx_info_data))
#     authorizer_info_ret = authorizer_info_ret.json()
#
#     print('-->', json.dumps(authorizer_info_ret))
#
#
#
# create_authorizer_access_token()







# access_token = "13_pD2PP2-ElQpVkbt03YpmgLMw11-ProDxZBtX9bkxw98QGoir3jhEcc_ohI98T4VO0thagj53xgp8WRTOzBiFpwOxQBewfuBm_D4nv94EVvANa4gg6Vn4m4OtnVeLbEZJux4tH5tR4KZXOPoNMYQgAMDIUM"


# # url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
# # url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_create_user_to_customer_qrCode_poster'
#
# get_data = {
#     'data': json.dumps({"user_id": 60, "customer_id": 1})
# }
#
# # print(get_data)
#
# s = requests.session()
# s.keep_alive = False  # 关闭多余连接
# ret = s.get(url, params=get_data)
#
# # ret = requests.get(url, params=get_data)
#
#
# print(json.dumps(ret.json()))


# authorizer_access_token = '16_QYOo8rOBtXfh7Hn2S5DmPZFLwPw0TZTheC1TTUy2iqGvDooNQjMR0pWnJ2MQZSCThvOs9g4eT4vflf-M8bN9S-oXDSca7Mx0I3h_CO978wk39FvTTrdYjMS1kniX3GVyyJABCroTA02EDshOPPXhAHDEEM'
#
# get_domin_data = {
#     'access_token': authorizer_access_token
# }
# post_domain_data = {
#     'action': 'set',
#     'requestdomain': ['https://api.zhugeyingxiao.com'],
#     'wsrequestdomain': ['wss://api.zhugeyingxiao.com'],
#     'uploaddomain': ['https://statics.api.zhugeyingxiao.com'],    #https://statics.api.zhugeyingxiao.com
#     'downloaddomain': ['https://api.zhugeyingxiao.com','https://statics.api.zhugeyingxiao.com']
# }
# #
#
# post_domain_url = 'https://api.weixin.qq.com/wxa/modify_domain'
# domain_data_ret = requests.post(post_domain_url, params=get_domin_data, data=json.dumps(post_domain_data))
# domain_data_ret = domain_data_ret.json()
# print('--------- 修改小程序服务器 接口返回---------->>', json.dumps(domain_data_ret))
#
#
# post_domain_data = {
#     'action': 'get'
# }
# domain_data_ret = requests.post(post_domain_url, params=get_domin_data, data=json.dumps(post_domain_data))
# domain_data_ret = domain_data_ret.json()
# print('--------- 修改小程序服务器 接口返回---------->>', json.dumps(domain_data_ret))

import re

a = {"update_time": 1545553692, "create_time": 1545553602, "news_item": [{"content_source_url": "", "content": "<p>\u6ca1\u3010\u7559\u91cf\u3011\u6bd4\u6ca1\u6d41\u91cf\u66f4\u53ef\u6015\u2014\u5408\u4f17\u5eb7\u6865</p><p>2018-12-10</p><p>\u5173\u6ce8\u516c\u4f17\u53f7\u5e76\u5206\u4eab\u6587\u7ae0</p><p>\u9886\u73b0\u91d1\u7ea2\u5305</p><p style=\"line-height: 26px;text-align: center;\">\u5408\u4f17\u5eb7\u6865-\u4e13\u6ce8\u533b\u9662\u54c1\u724c\u8425\u9500\uff0c<br  /></p><p style=\"line-height: 26px;text-align: center;\">\u5e2e\u52a9\u533b\u9662\u63d0\u534750%\u8f6c\u5316\u7387</p><p style=\"line-height: 26px;text-align: center;\">5\u5e74\u6765\u575a\u5b88\u4e00\u4e2a\u5c0f\u627f\u8bfa</p><p style=\"line-height: 26px;text-align: center;\">\u4e0d\u8fbe\u6807\uff0c\u5c31\u9000\u6b3e</p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4981684981684982\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7j1eqrTNvHN8W26vsZVLuKomhVRZ50vFTAtO77lpwoxiaxElBibloYJoA/640?wx_fmt=png\" data-type=\"png\" data-w=\"546\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4375\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7V62unBfhw6tAHf7oVE3fIQA2YmHyGBWz15c8HU5SVBm3UpeBY6RIcA/640?wx_fmt=png\" data-type=\"png\" data-w=\"544\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4132841328413284\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7RiaE9NbicwFQlLfeRoM7btadv0nmvfiaM9DHiaFyOrq0ibp4o8a0FMt2IhQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"542\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.449355432780847\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7nY8IE1knoqwpUuzNT3pz5a0v9YeZJQY57Iz55hFjBVxohkwxs2icplQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"543\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.5347912524850895\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7HMibZvLpzEqb7RuhQD32xwkNY20I2AXyHdh0dKKbPiajLsqduOkeI3rA/640?wx_fmt=png\" data-type=\"png\" data-w=\"503\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4453441295546559\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7hUtohc0S8ia46uZGhJp0HgzRMndh2WKd7XzBG2x7pxpwwvNjBughwzw/640?wx_fmt=png\" data-type=\"png\" data-w=\"494\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4225865209471766\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7AqxPpkkcgXV8u6kDic2acct2wfbez4Zno2op2Ws14Guq5PvHC2VNuEQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"549\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.501930501930502\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7TIib08I3WdpejzDWTDu5drZfr8t6qMXh2n7Q4U8mRrW0iaBpcibqpysqA/640?wx_fmt=png\" data-type=\"png\" data-w=\"518\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"0.5485110470701249\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7zIe58HmQnxq7wc1GNOia4T2MFCUj3jBBWEe459bvsjhGO35WJUnkeiaA/640?wx_fmt=png\" data-type=\"png\" data-w=\"1041\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;\"><br  /></p><p><img class=\"\" data-ratio=\"1\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7jnibhbsZqXxCYWq8YEjJwpibqmDQ2Kfm7gsFFZgAerX4ZS9RdWPUmBSg/640?wx_fmt=png\" data-type=\"png\" data-w=\"474\" style=\"width: 46px;height: 46px;border-radius: 23px;\"></p><p>\u5f20\u70ac</p><p>\u8425\u9500\u4e13\u5458</p><p>13020006631</p><p><br  /></p>", "digest": "\u6ca1\u3010\u7559\u91cf\u3011\u6bd4\u6ca1\u6d41\u91cf\u66f4\u53ef\u6015\u2014\u5408\u4f17\u5eb7\u68652018-12-10\u5173\u6ce8\u516c\u4f17\u53f7\u5e76\u5206\u4eab\u6587\u7ae0\u9886\u73b0\u91d1\u7ea2\u5305\u5408\u4f17\u5eb7\u6865-\u4e13\u6ce8\u533b\u9662\u54c1\u724c\u8425", "thumb_media_id": "ivcZrCjmhDznUrwcjIReRF5RhHkNuJqdzycndksV39s", "need_open_comment": 0, "title": "\u6ca1\u3010\u7559\u91cf\u3011\u6bd4\u6ca1\u6d41\u91cf\u66f4\u53ef\u6015\u2014\u5408\u4f17\u5eb7\u6865", "thumb_url": "http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg", "author": "", "url": "http://mp.weixin.qq.com/s?__biz=Mzg4MzA1ODU0Mw==&mid=100000003&idx=1&sn=53707000490e5f038874127c557caf03&chksm=4f4c7303783bfa1568406085f6715521b9e672a3472205bce4e5e9828de52edc19995c9e308e#rd", "only_fans_can_comment": 0, "show_cover_pic": 0}]}
b  = {
	"update_time": 1545553692,
	"create_time": 1545553602,
	"news_item": [{
		"content_source_url": "",
		"content": "<p>没【留量】比没流量更可怕—合众康桥</p><p>2018-12-10</p><p>关注公众号并分享文章</p><p>领现金红包</p><p style=\"line-height: 26px;text-align: center;\">合众康桥-专注医院品牌营销，<br  /></p><p style=\"line-height: 26px;text-align: center;\">帮助医院提升50%转化率</p><p style=\"line-height: 26px;text-align: center;\">5年来坚守一个小承诺</p><p style=\"line-height: 26px;text-align: center;\">不达标，就退款</p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4981684981684982\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7j1eqrTNvHN8W26vsZVLuKomhVRZ50vFTAtO77lpwoxiaxElBibloYJoA/640?wx_fmt=png\" data-type=\"png\" data-w=\"546\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4375\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7V62unBfhw6tAHf7oVE3fIQA2YmHyGBWz15c8HU5SVBm3UpeBY6RIcA/640?wx_fmt=png\" data-type=\"png\" data-w=\"544\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4132841328413284\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7RiaE9NbicwFQlLfeRoM7btadv0nmvfiaM9DHiaFyOrq0ibp4o8a0FMt2IhQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"542\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.449355432780847\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7nY8IE1knoqwpUuzNT3pz5a0v9YeZJQY57Iz55hFjBVxohkwxs2icplQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"543\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.5347912524850895\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7HMibZvLpzEqb7RuhQD32xwkNY20I2AXyHdh0dKKbPiajLsqduOkeI3rA/640?wx_fmt=png\" data-type=\"png\" data-w=\"503\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4453441295546559\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7hUtohc0S8ia46uZGhJp0HgzRMndh2WKd7XzBG2x7pxpwwvNjBughwzw/640?wx_fmt=png\" data-type=\"png\" data-w=\"494\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.4225865209471766\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7AqxPpkkcgXV8u6kDic2acct2wfbez4Zno2op2Ws14Guq5PvHC2VNuEQ/640?wx_fmt=png\" data-type=\"png\" data-w=\"549\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"1.501930501930502\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7TIib08I3WdpejzDWTDu5drZfr8t6qMXh2n7Q4U8mRrW0iaBpcibqpysqA/640?wx_fmt=png\" data-type=\"png\" data-w=\"518\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;width: 781px;overflow: hidden;\"><img class=\"\" data-ratio=\"0.5485110470701249\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7zIe58HmQnxq7wc1GNOia4T2MFCUj3jBBWEe459bvsjhGO35WJUnkeiaA/640?wx_fmt=png\" data-type=\"png\" data-w=\"1041\" style=\"max-width: 340px;\" width=\"100%\"></p><p style=\"line-height: 26px;\"><br  /></p><p><img class=\"\" data-ratio=\"1\" data-src=\"https://mmbiz.qpic.cn/mmbiz_png/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7jnibhbsZqXxCYWq8YEjJwpibqmDQ2Kfm7gsFFZgAerX4ZS9RdWPUmBSg/640?wx_fmt=png\" data-type=\"png\" data-w=\"474\" style=\"width: 46px;height: 46px;border-radius: 23px;\"></p><p>张炬</p><p>营销专员</p><p>13020006631</p><p><br  /></p>",
		"digest": "没【留量】比没流量更可怕—合众康桥2018-12-10关注公众号并分享文章领现金红包合众康桥-专注医院品牌营",
		"thumb_media_id": "ivcZrCjmhDznUrwcjIReRF5RhHkNuJqdzycndksV39s",
		"need_open_comment": 0,
		"title": "没【留量】比没流量更可怕—合众康桥",
		"thumb_url": "http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg",
		"author": "",
		"url": "http://mp.weixin.qq.com/s?__biz=Mzg4MzA1ODU0Mw==&mid=100000003&idx=1&sn=53707000490e5f038874127c557caf03&chksm=4f4c7303783bfa1568406085f6715521b9e672a3472205bce4e5e9828de52edc19995c9e308e#rd",
		"only_fans_can_comment": 0,
		"show_cover_pic": 0
	}]
}



# print(json.loads(json.dumps(a)).get('news_item')[0].get('content'))
# print(json.dumps(a))

# content = 'data-src="111?wx_fmt=png data-src="222?wx_fmt=jpg'


# phone = "2004-959-559#这是一个电话号码"
# # 删除注释
# num = re.sub(r'#.*$', "", phone)
# print("电话号码 : ", num)

# 移除非数字的内容

# print(b)

# content = b.get('news_item')[0].get('content')
#
#
# dict = {'data-src' : 'src', '?wx_fmt=jpg' : '', '?wx_fmt=png' : ''}
#
# for key,value in dict.items():
#
#     content  = content.replace(key,value)
#     # print(url)
#
# print(content)


# import random
#
# class CDispatch:
#
# 	def __init__(self, sum, count):
# 		self.sum = sum
# 		self.count = count
#
# 	# print 'init here sum =',sum,',count =',count
# 	def __del__(self):
# 		pass
#
# 	# print 'run del the class'
# 	def getListInfo(self):
# 		listInfo = []
# 		sumMoney = self.sum * 100
#
# 		for num in range(0, self.count):
# 			if (num == self.count - 1):
# 				listInfo.append(float('%0.2f' % sumMoney) / 100)
# 				break
# 			bigRand = sumMoney + 1 + num - self.count
# 			# print 'sumMoney=',sumMoney,'num=',num,'self.count=',self.count,'big=',bigRand
# 			try:
# 				a = random.randint(1, int(bigRand))
# 			except:
# 				for i in range(0, num):
# 					print ('listInfo[%d]' % i, '=', listInfo[i])
# 				if num > 0:
# 					print ('sumMoney=', sumMoney, 'num=', num, 'listInfo[num-1]=', listInfo[
# 						num - 1], 'self.count=', self.count, 'big=', bigRand)
# 				break
#
# 			sumMoney -= a
# 			listInfo.append(float(a) / 100)
#
# 		return listInfo
#
#
# for i in range(0, 100000):
# 	dispatch = CDispatch(10,2)
# 	listGet = dispatch.getListInfo()
# 	print ('-----listGet----->>',listGet)
#
# 	del dispatch

import random
import sys


def calRandomValue(total, num):
	total = float(total)
	num = int(num)
	min = 0.01  # 基数
	if (num < 1):
		return

	if num == 1:
		print("第%d个人拿到红包数为：%.2f" % (num, total))
		return

	i = 1
	while (i < num):
		max = total - min * (num - i)
		k = int((num - i) / 2)
		if num - i <= 2:
			k = num - i
		max = max / k
		monney = random.randint(int(min * 100), int(max * 100))
		monney = float(monney) / 100
		total = total - monney
		print("第%d个人拿到红包数为：%.2f, 余额为: %.2f" % (i, monney, total))
		i += 1

	print ("第%d个人拿到红包数为：%.2f, 余额为: %.2f" % (i, total, 0.0))


calRandomValue(200, 100)





