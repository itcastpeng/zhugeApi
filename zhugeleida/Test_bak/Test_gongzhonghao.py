
from publicFunc import account

import time
import requests
import json

token = '93b5f91eb56b8a4f8d96b7182920d68d'
# token = 'f20a5549cefd04ca6daa06eeb251ca36'
timestamp = str(int(time.time() * 1000))

get_data = {
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    # 'user_id': 1,
    'user_id': 9,



}

post_data = {

}

# ip = 'http://127.0.0.1:8001'
# ip = 'http://192.168.100.20:8000'

ip = 'http://api.zhugeyingxiao.com'




# url =  ip + '/zhugeleida/gongzhonghao/work_gongzhonghao_auth'  # 获取产品的列表
# get_data['code'] = '021Fp1es1T9eMn0rDLes1LSGds1Fp1eh'
# # get_data['state'] = 'snsapi_base'
# get_data['state'] = 'snsapi_userinfo'
# get_data['user_type'] = 1
# get_data['appid'] = 'wxa77213c591897a13'
# get_data['pid'] = ''
# get_data['article_id'] = 9
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/gongzhonghao/work_gongzhonghao_auth/gongzhonghao_share_sign'  # 获取产品的列表
# get_data['company_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/gongzhonghao/work_gongzhonghao_auth/create_gongzhonghao_share_auth_url'  # 获取产品的列表
# get_data['uid'] = 1
# get_data['level'] = 1
# get_data['article_id'] = 1
# get_data['company_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/gongzhonghao/article/forward_article/2'  # 获取产品的列表
# get_data['uid'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/gongzhonghao/article/staytime/2'  # 获取产品的列表
# get_data['uid'] = 6
# get_data['parent_id'] = 6
# get_data['article_access_log_id'] = 6
# ret = requests.get(url, data = post_data ,params=get_data)



####################################################################################

# url =  ip + '/zhugeleida/admin/login'  # 获取产品的列表
# post_data['username'] = 'zhangcong'
# post_data['password'] = '123456'
#
# ret = requests.post(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/modify_password'  # 获取产品的列表
# post_data['password1'] = '1234qwerQWER'
# post_data['password2'] = '1234qwerQWER'
#
# ret = requests.post(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/login_rules'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)

######################### 小程序第三方授权 ############################

# url = ip + '/zhugeleida/admin/open_weixin/tongzhi'
# get_data['signature'] = '6b6913bd899e3a4ab761d7d385caa598f15b4d3b'
# get_data['timestamp'] = '1533708502'
# get_data['nonce'] = '1568674329'
# get_data['msg_signature'] = 'b9287c7d48aff83269b7e3ea528ab826e99a93d9'
#
# post_data['postdata'] = """
# 	<xml>
# 		<AppId><![CDATA[wx67e2fde0f694111c]]></AppId>
# 		<Encrypt><![CDATA[tf9Ck4zUGvL1s1QBIG3McN7BJhKpMzkCdFJYVR1QJdqcRO4v5Z2DmyFkuTQctoCYiFKNYjxMiK75BAepovmv5j+Ta188nsXXOsAqT17NRFZPif8/bcbqSMDOWBhkNVAS6DCoOrKkN+RMx3HLhkLp2A6lh+3jDpXvoeqbrhP4sWjwMzBzntGOdKnf/rIyODl5azXY29dwXrWDoqrrKAcOAxz38gjMFssDc8AYDcXFzxmLsSf14fYzzJj6WyKBLR23Jp/1spuCLDWcMnUE35T7gXCFaW/p1cQwtcwGGbqZlbI6cpQbFZNTKD83KVew+qGFFrdsJuErXORHU5B+H3Jx7R9o/+F+gvYssAGHEEVG8ZZKvP2VCti/4tN1j5BVuCgyAPki2UedFpDCRxSmXmK8WIIURx2DTnyu5+mqttgxg2ubKpsHFbTnpIAIBCIVYVbHisyx0k17vZma/BGlJfmgJg==]]></Encrypt>
# 	</xml>
# """

# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/open_weixin/create_grant_url'  # 获取 关联第三方的二维码
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/xcx_auth_process'
# ret = requests.get(url, params=get_data,data=post_data)


# url = ip + "/zhugeleida/admin/xcx_auth_process/update/1" #
# post_data['authorization_appid'] = 'wxd306d71b02c5075e'
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/xcx_auth_process/update/xcx_get_authorizer_info"
# ret = requests.get(url, params=get_data)




# url = ip + "/zhugeleida/admin/xcx_auth_process/update/3" #
# post_data['name'] = '测试小程序'
# post_data['head_img'] = 'xxx/yy.jpg'
# post_data['introduce'] = '不错的小程序哦'
# post_data['service_category'] = 'IT互联网'
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/dai_xcx/get_qrcode" #  获取体验小程序的体验二维码
# post_data['customer_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/dai_xcx/submit_audit" #  获取体验小程序的体验二维码
# post_data['customer_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)

############################## 公众号授权 #######################################

# url = ip + '/zhugeleida/admin/open_weixin_gongzhonghao/create_grant_url'  # 获取 关联第三方的二维码
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/gzh_auth_process'
# ret = requests.get(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/gzh_auth_process/update/app_id" #
# post_data['authorization_appid'] = 'wx6ba07e6ddcdc69b3'
# ret = requests.post(url, params=get_data, data=post_data)

######################## 公众号 #####################################

# url = ip + '/zhugeleida/gongzhonghao/create_gongzhonghao_auth_url/1'  # 获取 关联第三方的二维码
# ret = requests.get(url, params=get_data,data=post_data)







################################ 公众号 聊天 ####################################


# url = ip + '/zhugeleida/gongzhonghao/chat/send_msg/0' # 增加聊天消息
# post_data['u_id'] = 1
# # post_data['msg'] = 'YYYYTTTTT'
# post_data['content'] = json.dumps({
#     'info_type': 1,             # 1代表发送的文字\表情\ 或 话术库里的自定义(文字表情)。
#     'msg': '这个信息是文字\表情'
#
# })
# post_data['send_type'] = 2
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/gongzhonghao/chat/getmsg/0' # 实时聊天记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/gongzhonghao/chat/query_num/0' # 实时聊天记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/qiyeweixin/tongxunlu'  # 查询-通讯录信息
# get_data['type'] = 'gongzhonghao'
# get_data['order'] = '-last_activity_time' # '-last_follow_time' # last_follow_time | last_activity_time
# # get_data['customer__source'] =1
# ret = requests.get(url, params=get_data)






# url = ip + '/zhugeleida/gongzhonghao/chat/history_chatinfo_store_content/0' # 实时聊天记录
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/gongzhonghao/chat/encrypted_phone_number/0' # 实时聊天记录
# post_data['u_id'] = 18
# post_data['encryptedData'] = "Q10d07JnNold5IsikOa55mMGqAYapDe/6i43RbayjnvBgN99jpQxRu5OIE5ovfmJwJ+n7eU0K6BH+bTERl/63LpkdSNGulwyVQwHbUQQ+wMmhZLqE1b0pZdmymJATZxWAQHP6p/D/CSIIqNgfLA8e2qxhA/tGOravGQwKANjYVys+RkGJQfBfck+xB5Ze6fu7pqFzmyavGFnufNsU57Gpg=="
# post_data['iv'] = "IQBdM5LzHNBKCFD9R8ikeg=="
# ret = requests.post(url, params=get_data,data=post_data)



# url = ip +   '/zhugeleida/gongzhonghao/chat' # 分页 聊天信息记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/gongzhonghao/chat' # 分页 聊天信息记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/contact' #
# ret = requests.get(url, params=get_data)




###############################################################################################


# url = ip + '/zhugeleida/admin/home_page/acount_data' # 统计-名片状态+账号状态
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/admin/home_page' # 统计-数据概览
# ret = requests.get(url, params=get_data)

# url = ip + '/zhugeleida/admin/home_page/line_info' # 统计-曲折图数据
# post_data['days'] = 7
# post_data['index_type'] = 1
# ret = requests.post(url, params=get_data,data=post_data)


#修改用户状态
# url = ip + '/zhugeleida/admin/user/update_status/1' # 更新用户的开启状态
# post_data['status'] = 1
# ret = requests.post(url, data=post_data,params=get_data)




#查询企业用户

# url = ip + '/zhugeleida/admin/user' # 更新用户的开启状态
# get_data['status'] = ''
# get_data['department'] = 1
# get_data['position'] = '拉'
# get_data['username'] = '张'
# ret = requests.get(url, data=post_data,params=get_data)




# url =  ip + '/zhugeleida/admin/product/product_list'  # 获取产品的列表
# get_data['product_type'] = 2
# # get_data['company_id'] = 4
# # get_data['product_name'] = '膜法'
# # get_data['status'] = 1  # # (1,'已上架') # (2,'已下架')
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/product/feedback_list'  # 获取产品的列表
# # get_data['status'] = 1
# # get_data['company_id'] = 1
#
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/product/product_single'  # 获取产品的列表
# get_data['product_id'] = 7
# get_data['product_type'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


##################################### 文章 + 文章标签 + 文章增删改查 ###############################


# url =  ip + '/zhugeleida/admin/article/myarticle_list'  # 获取产品的列表
# get_data['id'] = 1
# get_data['status'] = 2
# # get_data['title'] = 'xx'
# # get_data['order'] = '-read_count'  # -forward_count  -create_date
# # get_data['tags_list'] = '[1]'
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/gongzhonghao/article/staytime/1'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/article/add/0'  # 获取产品的列表
# post_data['title'] = 'YYYYY'
# post_data['summary'] = 'BBBB'
# post_data['content'] = 'xx'
# post_data['cover_picture'] = 'xxxx.jpg'
#
# ret = requests.post(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/article/update/9'  # 获取 二维码 产品的列表
# post_data['title'] = 'HHHHH'
# post_data['summary'] = 'CCCCC'
# post_data['content'] = 'NNNNN'
# post_data['cover_picture'] = 'xxxx.jpg'
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article/delete/10'  # 获取产品的列表
# ret = requests.post(url, data = post_data ,params=get_data)





# url =  ip + '/zhugeleida/admin/article_tag'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/article_tag/add/0'  # 获取产品的列表
# post_data['tag_name'] = 'xxxx'
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article_tag/update/5'  # 获取产品的列表
# post_data['tag_name'] = 'TTTT'
# ret = requests.post(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/article_tag/delete/5'  # 获取产品的列表
# ret = requests.post(url, data = post_data ,params=get_data)




# url =  ip + '/zhugeleida/gongzhonghao/article/myarticle/1'  # 获取产品的列表
# get_data['uid'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/gongzhonghao/article/forward_article/2'  # 获取产品的列表
# get_data['uid'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)

#
# url =  ip + '/zhugeleida/mycelery/user_forward_send_activity_redPacket'  # 获取产品的列表
# get_data['parent_id'] = 850
# get_data['article_id'] = 23
# get_data['activity_id'] = 2
# get_data['company_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


url =  ip + '/zhugeleida/mycelery/query_total_xiaofei'  # 获取产品的列表
get_data['company_id'] = 1
ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/mycelery/user_focus_send_activity_redPacket'  # 获取产品的列表
#
# get_data['company_id'] = 1
# get_data['customer_id'] = 850
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/gongzhonghao/article/test_send_redPacket/0'  # 获取产品的列表
# # get_data['parent_id'] = 850
# # get_data['article_id'] = 23
# # get_data['activity_id'] = 2
# # get_data['company_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/gongzhonghao/article/staytime/2'  # 获取产品的列表
# get_data['uid'] = 1
# get_data['pid'] = ''
# get_data['article_access_log_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)





#############################################################################################





# url = ip + '/zhugeleida/admin/product/change_status/3' # 更新产品的状态
# post_data['status'] = 3
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/product/delete/11' # 更新产品的状态
#
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/product/add/0' # 添加产品
# post_data['name'] = 'jajjaj'
# post_data['price'] = 111
# post_data['price'] = 'naifad'
# post_data['product_type'] = 1
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)




# url = ip + '/zhugeleida/admin/product/update/13' # 修改产品
# post_data['name'] = '发的发生的'
# post_data['price'] = 111
# post_data['price'] = 'naifad'
# post_data['product_type'] = 1
#
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/product/change_feedback_status/1' # 更新产品的状态
# post_data['status'] = 2
# ret = requests.post(url, data=post_data,params=get_data)

#
# url = ip + '/zhugeleida/admin/product/recommend_index/7' # 更新推荐指数的状态
# post_data['index'] = 2
# ret = requests.post(url, data=post_data,params=get_data)





########################### 公司管理 + 秘钥管理 #########################################

# url = ip +  '/zhugeleida/admin/company/author_status'   # 验证通过
# get_data['company_id'] = 1
# ret = requests.get(url, data=post_data,params=get_data)



# url = ip +  '/zhugeleida/admin/company/add_company/0'   # 后台增加公司
# post_data['name'] = '大麦公司'
# post_data['charging_start_time'] = '2018-08-01'
# post_data['open_length_time'] = 2
# post_data['mingpian_available_num'] = 5
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/company/update_company/1'   # 后台增加用户
# post_data['name'] = '大麦公司11'
# post_data['charging_start_time'] = '2018-09-01'
# post_data['open_length_time'] = 4
# post_data['mingpian_available_num'] = 10
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/company/update_agent/1'   # 后台增加用户
# post_data['name'] = 'AI雷达'
# post_data['app_type'] = 1
# post_data['agent_id'] = 1000002
# post_data['app_secret'] = '48m2h1e2DRcA55yfKqHa083UpbJy-30u30ypy4zPr8E'
# ret = requests.post(url, data=post_data,params=get_data)




# url = ip +  '/zhugeleida/admin/company/update_tongxunlu/1'   # 后台增加用户
# post_data['corp_id'] = 'wx81159f52aff62388'
# post_data['tongxunlu_secret'] = '-pkF6u6vdXRbapZNb-fdQc16DXBhGCgDmyfa0OUuOgk'
# ret = requests.post(url, data=post_data,params=get_data)



############################# 修改用户状态 ####################################

# url = ip +  '/zhugeleida/admin/user/add/0'   # 后台增加用户
# post_data['username'] = '我是你爸爸15'
# post_data['password'] = '123456xx'
# post_data['role_id'] = 1
# post_data['position'] = '运维TTT'
# post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# post_data['phone'] = 13256718366
# post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/admin_userprofile/add/0'   # 后台增加用户
# post_data['login_user'] = 'fsdfsa'
# post_data['username'] = 'sdfsadf'
# post_data['password'] = '123456'
# post_data['role_id'] = 1
# post_data['position'] = '运维TTT'
# # post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# #post_data['phone'] = 13256718366
# #post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)




# url = ip +  '/zhugeleida/admin/admin_userprofile/update/3'   # 后台增加用户
# post_data['login_user'] = '34vvvv'
# post_data['username'] = 'v55544'
# post_data['password'] = 'qwert'
# post_data['role_id'] = 1
# post_data['position'] = 'fff'
# # post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# #post_data['phone'] = 13256718366
# #post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/admin_userprofile/delete/4'   # 后台增加用户
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/admin_userprofile'    #后台用户展示嗯嗯。
# ret = requests.get(url, params=get_data)



# url = ip +  '/zhugeleida/admin/user/create_small_program_qr_code/0'   # 后台增加用户
# post_data['user_id'] = 75
#
# ret = requests.post(url, data=post_data,params=get_data)










##############################################################################

# url = ip + '/zhugeleida/admin/article/add/0' # 添加产品
# post_data['title'] = 'jajjaj'
# post_data['summary'] = '摘要'
# post_data['cover_picture'] = 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png'
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/article/delete/3'   # 删除文章
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/article/update/9' # 添加产品
# post_data['title'] = 'xxxxx'
# post_data['summary'] = 'sss摘要'
# post_data['cover_picture'] = 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png'
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)


###################################### 插件 名片 #######################################

# url = ip + '/zhugeleida/admin/plugin_mingpian' # 添加产品
# ret = requests.get(url,params=get_data)



# url = ip + '/zhugeleida/admin/plugin_mingpian/add/0' # 添加
# post_data['name'] = 'hahhhha'
# post_data['avatar'] = 'xxxxxx'
# post_data['username'] = 'jjsfjadjfka'
# post_data['phone'] = 121231323
# post_data['webchat_code'] = 'fsafsaww23'
# post_data['position'] = '运维'
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/plugin_mingpian/update/1' # 添加产品
# post_data['name'] = '回家哈哈哈'
# post_data['avatar'] = '232323'
# post_data['username'] = '方法的'
# post_data['phone'] = 6767676
# post_data['webchat_code'] = 'fsafsaww23'
# post_data['position'] = '运维x'
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/plugin_mingpian/delete/1' # 添加产品
# ret = requests.post(url, params=get_data)


#############################  插件- 名片管理 活动报名 商品管理   ################################

# url = ip + '/zhugeleida/admin/plugin_report' # 添加产品
# ret = requests.get(url,params=get_data)


# url = ip + '/zhugeleida/admin/plugin_report/add/0' # 添加活动
# post_data['ad_slogan'] = '你值得拥有'   #广告语
# post_data['sign_up_button'] = '对方发送的发生'   #报名按钮
# post_data['title'] = '范德萨发生'    #活动标题
# post_data['introduce'] = 'dsfasfas的发生的发生'   #活动说明
# post_data['is_get_phone_code'] = False    #是否获取手机验证码
# post_data['skip_link'] = 'xxxxx'  #跳转链接
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/update/1' # 修改活动
# post_data['ad_slogan'] = '范德萨发生'
# post_data['sign_up_button'] = '是是是'
# post_data['title'] = '范德萨发生'
# post_data['introduce'] = 'SOUI金丰鼓酒行'
# post_data['is_get_phone_code'] = True
# post_data['skip_link'] = 'TTTT'
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/delete/4' # 修改活动
# ret = requests.post(url, params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/sign_up_activity/1' # 修改活动
# post_data['customer_name'] = 'FFFFF'
# post_data['phone'] =  1234425212
# post_data['phone_verify_code'] = 1231
# post_data['leave_message'] = 'e'
# ret = requests.post(url, data=post_data,params=get_data)

#############################  插件- 名片管理 活动报名 商品管理   ################################

# url = ip + '/zhugeleida/admin/plugin_goods/plugin_goods_list' # 添加产品
# ret = requests.get(url,params=get_data)




# content =  {
#     'goods_data':[
#
# 		{
#             'price': 128,
# 			'introduce': '本场演出将于【7月26日 10:55】开启销售，请提前下载大麦APP，关注本场演出最新信息。',
# 			'inventory_num' : 10,
# 			'person_limit_num' : 2,
#
#         },
# 		{
#             'price': 500,
# 			'introduce': '本场演出将于【7月28日 10:55】开启销售，请提前下载大麦APP，关注本场演出最新信息。',
# 			'inventory_num' : 10,
# 			'person_limit_num' : 2,
#
#         }
#     ],
#     'cover_data':[
#         {
#             'data':[
#                 'statics/zhugeleida/imgs/qiyeweixin/product/pbmh_s1.png'
#             ],
#             'type':'picture_url'
#         },
#         {
#             'type':'picture_url',
#             'data':[
#                 'statics/zhugeleida/imgs/qiyeweixin/product/1532484232056.png'
#             ]
#         }
#     ]
# }



# url = ip + '/zhugeleida/admin/plugin_goods/add/0' # 添加活动
# post_data['title'] = '林俊杰门票'
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_goods/update/1' # 添加活动
# post_data['title'] = '林俊杰门票1'
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_goods/delete/5' # 修改活动
# ret = requests.post(url, params=get_data)



############################ 官网编辑 #################################

# url = ip + '/zhugeleida/admin/website/edit/1' # 编辑官网
# website_content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_4.png']
# 		}
# 	]
# }
# post_data['website_content'] = json.dumps(website_content)
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/website' # 编辑官网
# get_data['company_id'] = 1
# ret = requests.get(url, params=get_data)



#######################################################################################

# url = ip + '/zhugeleida/admin/website/edit/1' # 编辑官网
# website_content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/gongzhonghao/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/gongzhonghao/website/Content_4.png']
# 		}
# 	]
# }
# post_data['website_content'] = json.dumps(website_content)
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/website' # 编辑官网
# get_data['company_id'] = 1
# ret = requests.get(url, params=get_data)



# url = ip + '/zhugeleida/admin/website_template'      # 编辑官网
# ret = requests.get(url, params=get_data)

# url = ip + '/zhugeleida/admin/website_template/add/0'      # 编辑官网
# post_data['name'] = '模板1'
# post_data['template_content'] = 'xxxx'
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/website_template/update/1'      # 编辑官网
# post_data['id'] = 1
# post_data['name'] = '模板1'
# post_data['template_content'] = 'TTTT'
# ret = requests.post(url, params=get_data,data=post_data)

# url = ip + '/zhugeleida/admin/website_template/delete/1'      # 编辑官网
# ret = requests.post(url, params=get_data,data=post_data)







###########################################################################################
















# url = ip + '/zhugeleida/admin/department/add/0' # 分页获取消息列表
# post_data['name'] = '测试环境AAA'
#
# post_data['parentid'] = ''
# post_data['company_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/admin/department/update/8'   # 分页获取消息列表
# post_data['name'] = '八大胡同_A'
# post_data['parentid'] = ''
#
# post_data['company_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)
#



# url = 'http://127.0.0.1:8000/zhugeleida/admin/department/add/0'    # 分页获取消息列表
# post_data['name'] = '蓝翔技院-2'
# post_data['parentid'] = 1
# post_data['company_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)


# url = 'http://127.0.0.1:8000/zhugeleida/admin/department/delete/6' # 分页获取消息列表
# ret = requests.post(url, params=get_data,)


# url = 'http://192.168.100.20:8000/zhugeleida/qiyeweixin/tongxunlu'  # 查询-通讯录信息
# # url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tongxunlu'  # 查询-通讯录信息
# # get_data['customer__source'] =1
#
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/qiyeweixin/follow_language'  # 查询-跟进用语
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language/add/0'  # 新增-跟进用语
# post_data['custom_language'] = '这个客户可能是个Gay'
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language/delete/12'  # 删除-跟进用语
# ret = requests.post(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_info/add/1'  # 发送-跟进信息。
# post_data['follow_info'] = '这个客户我惹不起！！！！'
# ret = requests.post(url, params=get_data,data=post_data)

# url = ip + '/zhugeleida/qiyeweixin/follow_info'  # 查询-跟进用语
# get_data['customer_id']  = 1
# ret = requests.get(url, params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/gongzhonghao/product/product_single'  # 获取产品的列表
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/gongzhonghao/product/product_list'  # 获取产品的列表
#
# get_data['uid'] =1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/gongzhonghao/product/forward_product'  # 记录转发产品动作。
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/gongzhonghao/product/forward_product'  # 记录转发产品动作。
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/product_list'  # 获取产品的列表
# get_data['status'] =1
#ret = requests.get(url, params=get_data)


print(ret.text)












