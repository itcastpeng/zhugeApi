from publicFunc import account

import time
import requests
import json

token = '93b5f91eb56b8a4f8d96b7182920d68d'
# token = '32fcf789342b766a0a5a764380a34180'  # 线上
# token = '90e8114abd1a309516eaa48af1d6b36a'  # 线上


timestamp = str(int(time.time() * 1000))

get_data = {
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 55,  # 线上
    # 'user_id': 1,  # 线上

}

post_data = {

}

# ip = 'http://127.0.0.1:8001'
# ip = 'http://192.168.100.20:8000'
ip = 'http://api.zhugeyingxiao.com'





# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/role'  # 查询角色
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/role/add/0?' # 增加角色
# post_data['name'] = 'xxx'
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/role/delete/3' # 删除角色
# ret = requests.post(url,params=get_data) #params 传 get值,reques.GET.get('timestamp')

# url = 'http://127.0.0.1:8000/zhugeleida/role/update/4?' # 修改角色
# get_data['name'] = 'YYY'
# ret = requests.post(url,params=get_data) #params 传 get值,reques.GET.get('timestamp')


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/mingpian'  # 查询用户    admin后台添加用户信息要填写全了
#
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/create_poster'  # 查询用户    admin后台添加用户信息要填写全了
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/mingpian/save_phone'  # 查询用户    admin后台添加用户信息要填写全了
# post_data['mingpian_phone'] = 159317889741
# post_data['is_show_phone'] = False
# ret = requests.post(url, params=get_data, data=post_data)

# url = 'http://127.0.0.1:8001/zhugeleida/qiyeweixin/mingpian/save_info'  # 查询用户    admin后台添加用户信息要填写全了
#
# post_data['wechat'] = 'ndfakfjak'
# post_data['mingpian_phone'] = 15931788975
# post_data['telephone'] = 159317889741
# post_data['email'] = '12133@qq.com'
# post_data['country'] = 1
# post_data['area'] = '北京市 北京 八大胡同'
# post_data['address'] = '东四一条'
#
# ret = requests.post(url, params=get_data, data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/mingpian/save_sign'  # 查询用户    admin后台添加用户信息要填写全了
#
# post_data['sign'] = '一生所爱~~~'
# ret = requests.post(url, params=get_data, data=post_data)



# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/mingpian/show_photo'  # 查询用户    admin后台添加用户信息要填写全了
# ret = requests.get(url, params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/mingpian/delete_photo'  # 查询用户    admin后台添加用户信息要填写全了
# post_data['photo_id'] = 9
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/mingpian/upload_photo'  # 查询用户    admin后台添加用户信息要填写全了
# files = {
#           'photo':  [
#                       ('ewm.jpg', open('ewm.jpg', 'rb')),
#                       ('ewm.jpg', open('ewm.jpg', 'rb')),
#                     ]
#          }
# ret = requests.post(url, params=get_data, files=files)

import json

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/add_picture/0'  # 查询用户    admin后台添加用户信息要填写全了
#
# files =   {
#           "cover_picture":  ("setAvator.jpg", open("setAvator.jpg", "rb")),
#
#           }
#
#
#
# ret = requests.post(url, params=get_data, data=post_data, files=files)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/add/0'   # 添加产品
# post_data['name'] = '门票'
# post_data['price'] = '128'
# post_data['reason'] = '有理想-不讲究'
# post_data['cover_picture_id'] = json.dumps([8, 9])
# article_data = [
#     {'title': '我是标题1', 'order': 1},
#     {'content': '我是内容1', 'order': 4},
#     {'title': '我是标题2', 'order': 2},
#     {'content': '我是标题2', 'order': 5},
#     {'picture_id': 15, 'order': 3},
#     {'picture_id': 16, 'order': 6},
# ]
# post_data['article_data'] = json.dumps(article_data)
# #
# # print('post_data -->', post_data)
# ret = requests.post(url, params=get_data, data=post_data)

# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
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
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }




# url = 'http://127.0.0.1:8001/zhugeleida/qiyeweixin/product/add/0'   # 添加产品
# post_data['name'] = '门票1'
# post_data['price'] = '128'
# post_data['reason'] = '有理想-不讲究'
# post_data['content'] = json.dumps(content)
#
# # print('post_data -->', post_data)
# ret = requests.post(url, params=get_data, data=post_data)



# url = 'http://127.0.0.1:8001/zhugeleida/qiyeweixin/product/update/10'   # 添加产品
# post_data['name'] = '门票2'
# post_data['price'] = '128'
# post_data['reason'] = '有理想-不讲究'
# post_data['content'] = json.dumps(content)
# # print('post_data -->', post_data)
# ret = requests.post(url, params=get_data, data=post_data)



# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/update/23'   # 添加产品
# post_data['name'] = '门票-2222'
# post_data['price'] = '129'
# post_data['reason'] = '232323'
# post_data['cover_picture_id'] = json.dumps([8,10])
# article_data = [
#     {'article_id':21 ,'title': '我是标题1', 'order': 1},
#     {'article_id':22 , 'content': '我是内容1', 'order': 3},
#     {'article_id':24 ,'title': '我是标题2', 'order': 4},
#     {'article_id':23  ,'content': '我是标题2', 'order': 6},
#     {'picture_id': 16, 'order': 2},
#     {'picture_id': 14, 'order': 5},
# ]
# post_data['article_data'] = json.dumps(article_data)
#
# ret = requests.post(url, params=get_data, data=post_data)



# url = ip + '/zhugeleida/qiyeweixin/product/delete_article/1'  # 删除图片
# post_data['product_id'] = 11
# ret = requests.post(url, params=get_data, data=post_data)

# url = ip + '/zhugeleida/qiyeweixin/product/change_status/1'  # 删除图片
# post_data['status'] = 3
# ret = requests.post(url, params=get_data, data=post_data)



# url = ip + '/zhugeleida/qiyeweixin/product/delete_picture/25'  # 删除图片
# post_data['product_id'] = 11
# ret = requests.post(url, params=get_data, data=post_data)
#

# url = ip + '/zhugeleida/qiyeweixin/product/shelves/10'  # 下架产品
# ret = requests.post(url, params=get_data,)


# url = ip + '/zhugeleida/qiyeweixin/product/publish/10'  # 下架产品
# ret = requests.post(url, params=get_data,)


# url = ip + '/zhugeleida/qiyeweixin/product/delete/10'  # 下架产品
# ret = requests.post(url, params=get_data,)




# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/delete_picture/12'  # 删除图片
# ret = requests.post(url, params=get_data, data=post_data)


# url =  ip + '/zhugeleida/qiyeweixin/product/product_list'  # 获取产品的列表
# # get_data['status_code'] = 2
# ret = requests.get(url, params=get_data)

# url =  ip + '/zhugeleida/qiyeweixin/product/product_single'  # 获取产品的列表
# get_data['product_id'] = 10
# ret = requests.get(url, params=get_data)


# url =  ip + '/zhugeleida/xiaochengxu/mingpian'  # 选择名片，显示单个用户的信息    admin后台添加用户信息要填写全了
# get_data['uid'] = 2 # 所属用户的ID
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/xiaochengxu/mingpian/all'  # 选择名片，显示单个用户的信息    admin后台添加用户信息要填写全了

# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/calling'  # 记录日志用户正在拨打你的手机
# get_data['uid'] = 2  # 指的是用户的 ID。
# get_data['action'] = 10
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/praise'  # 记录日志用户正在拨打你的手机
# get_data['uid'] = 2     # 指的是用户的 ID。
# #get_data['action'] = 9
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/forward'  # 记录日志用户正在拨打你的手机
# get_data['uid'] = 2     # 指的是用户的 ID。
# get_data['action'] = 6
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/up_sign'  # 记录日志用户正在拨打你的手机
# get_data['uid'] = 2     # 指的是用户的 ID。
#
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/admin/user/add/0' # 增加用户
# post_data['username'] = '我是你爸爸13'
# post_data['password'] = '123456xx'
# post_data['role_id'] = 1
# post_data['position'] = '运维TTT'
# post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# post_data['phone'] = 13256718366
# post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/admin/user/update/29' # 修改用户
# post_data['username'] = '发送到发送到'
# post_data['password'] = '123456'
# post_data['role_id'] = 1
# post_data['position'] = '开发'
# post_data['department_id'] = '[2000]'
# post_data['company_id'] = 1
# post_data['mingpian_phone'] = 15931788950
# post_data['phone'] = 15931788950
#
# ret = requests.post(url, data=post_data,params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/admin/user/delete/32' # 删除用户
# ret = requests.post(url,params=get_data)                                    #params 传 get值,reques.GET.get('timestamp')

# url = 'http://127.0.0.1:8000/zhugeleida/user/update/5' # 修改用户
# post_data['username'] = 'XXXX'
# post_data['role_id'] = 1
# post_data['company_id'] = 1
# ret = requests.post(url,params=get_data,data=post_data) #params 传 get值,reques.GET.get('timestamp')

# url = 'http://127.0.0.1:8000/zhugeleida/quanxian'  # 展示权限条目
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/quanxian/add/0' # 增加权限表
# post_data['path'] = '/admin/zhugeleida/quanxian/1111/'
# post_data['icon'] = 'xxx'
# post_data['title'] = '发的发的'
# post_data['pid_id'] = '1'
# post_data['order_num'] = '2'
# ret = requests.post(url,data=post_data ,params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/quanxian/delete/3' # 删除权限
# ret = requests.post(url,params=get_data)   #params 传 get值,reques.GET.get('timestamp')

# url = 'http://127.0.0.1:8000/zhugeleida/quanxian/update/2?' # 修改权限
# post_data['path'] = '/admin/zhugeleida/quanxian/22222/'
# post_data['icon'] = 'RRRR'
# post_data['title'] = '弄弄弄'
# post_data['pid_id'] = '1'
# post_data['order_num'] = '2'
# ret = requests.post(url,data=post_data ,params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/role/add/0?' # 增加角色
# get_data['name'] = 'xxx'
# ret = requests.post(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/company'  # 查询公司
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/add/0' # 增加公司
# post_data['name'] = '合众康桥2'
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/delete/3' # 删除公司
# ret = requests.post(url,params=get_data)    #params 传 get值,reques.GET.get('timestamp')

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/update/2?' # 修改公司
# post_data['name'] = '北京图为先科技有限公司_clone'
# ret = requests.post(url,params=get_data,data=post_data) #params 传 get值,reques.GET.get('timestamp')
#

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_customer'  # 查询标签 or 查询标签用户
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_customer/add/0' # 增加标签 or 标签用户
# post_data['name'] = '跟进客户'
# post_data['customer_list'] = '[2,3]'
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_list'  # 查询标签 or 查询标签用户
# get_data['customer_id'] = 1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_list/add_tag/2' # 增加标签 or 标签用户
# post_data['name'] = '大傻子客户'
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_list/customer_tag/2' # 给客户添加标签
# # post_data['name'] = '大傻子客户'
# post_data['tag_list'] = '[14,15]'
#
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/search/get_tag'  # 搜索指定的标签 [展示top9条数据]
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/search/get_user'  # 搜索指定的标签 [展示top9条数据]
# get_data['username'] = '张炬'
# ret = requests.get(url, params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user'  # 查询标签 or 查询标签用户
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/add'  # 查询标签 or 查询标签用户
# post_data['name'] = '上善若水'
# ret = requests.post(url, params=get_data,data=post_data )

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/save'  # 查询标签 or 查询标签用户
# post_data['tag_list'] = '[1,2,3]'
# ret = requests.post(url, params=get_data,data=post_data )


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/delete'  # 查询标签 or 查询标签用户
# post_data['id'] = 3
# ret = requests.post(url, params=get_data,data=post_data )







'''
{
   "tag_id": 12,
   "user_list": [ 1,2]
}
'''
# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag/update/2?' # 修改标签 or 标签用户
# post_data['name'] = '合众康桥1'
# post_data['user_list'] = [1,2]
# ret = requests.post(url,params=get_data,data=post_data) #params 传 get值,reques.GET.get('timestamp')
#

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag/delete/1' # 删除标签
# ret = requests.post(url,params=get_data)  #params 传 get值,reques.GET.get('timestamp')


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag'  # 查询【标签成员】
# ret = requests.get(url, params=get_data)

# {
#     "code":200,
#     "msg":"",
#     "data":{
#         "ret_data":[
#             {
#                 "name":"合众康桥",
#                 "tag_id":3,
#                 "user_list":[
#                     1,
#                     2
#                 ]
#             },
#             {
#                 "name":"东方银谷",
#                 "tag_id":2,
#                 "user_list":[
#                     1
#                 ]
#             }
#         ],
#         "data_count":2
#     }
# }


##添加标签成员 json格式
# {
#    "tag_id": 12,
#    "user_list":[ "user1","user2"],
#
# }


# user 企业微信接口
# url = 'http://127.0.0.1:8000/zhugeleida/work_weixin_auth/1'  # 企业微信调用
# get_data['code'] = 'pm4Mp2zwTb0GOxcJ3hhYETNaWhPWF5lDwDZ_mHWHOqQ'
# ret = requests.get(url, params=get_data)

# customer 企业微信接口
# url = 'http://127.0.0.1:8000/zhugeleida/work_weixin_auth/1'  # 企业微信调用
# get_data['code'] = 'pm4Mp2zwTb0GOxcJ3hhYETNaWhPWF5lDwDZ_mHWHOqQ'
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/qiyeweixin/work_weixin_auth/create_gongzhonghao_share_auth_url'  # SDK使用权限签名算法
# get_data['article_id'] = 1
# get_data['company_id'] = 1
# ret = requests.get(url, params=get_data)


# url =  ip + '/zhugeleida/qiyeweixin/article/thread_base_info/1'  # 公众号文章基础信息
# get_data['uid'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)
#


# url =  ip + '/zhugeleida/qiyeweixin/article/customer_effect_ranking_by_level/2'  # 获取产品的列表
#
# get_data['level'] = 0
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/qiyeweixin/article/query_customer_transmit_path/2'  # 获取产品的列表
# get_data['level'] =  5 # 用户所在层级
# get_data['customer_id'] = 898  # 客户ID
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/qiyeweixin/article/hide_customer_data/2'  # 获取产品的列表
#
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/qiyeweixin/article/get_article_access_log/2'  # 获取产品的列表
# get_data['customer_id'] = 854  # 客户ID
# get_data['pid'] = ''  # 客户ID
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/qiyeweixin/article/get_article_forward_info/2'  # 获取产品的列表
# get_data['customer_id'] = 854   # 客户ID
# get_data['pid'] = ''            # 客户ID
# ret = requests.get(url, data = post_data ,params=get_data)



# url = ip + '/zhugeleida/qiyeweixin/customer'  # 查询-客户信息
# get_data['customer_id'] = 1
# ret = requests.get(url, params=get_data)



# url =  ip + '/zhugeleida/qiyeweixin/action/customer' # 查看客户信息
# # get_data['create_date__gte'] = '2018-06-06'
# # get_data['create_date__lt'] = '2018-06-20'
# ret = requests.get(url, params=get_data)


# url = ip +  '/zhugeleida/qiyeweixin/action/customer_detail' # 查看客户信息
# get_data['customer_id'] = 2
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/action/count'     #统计动作访问
# get_data['create_date__gte'] = '2018-06-09'
# get_data['create_date__lt'] = '2018-06-09'
# ret = requests.get(url, params=get_data)




################################################


# url = ip + '/zhugeleida/boosleida/home_page/acount_data' # 统计-名片状态+账号状态
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/admin/home_page' # 统计-数据概览
# ret = requests.get(url, params=get_data)

# url = ip + '/zhugeleida/boosleida/home_page/line_info' # 统计-曲折图数据
# # post_data['days'] = 30
# # post_data['index_type'] = 6
# '''
# 'days': 7 | 15        # 按7天 或者 按照15天搜索 'index_type': 1 | 2 | 3 | 4 | 5 | 6 , # 1 客户总数  2 咨询客户数  3 跟进客户数  4 [客户活跃度]
# '''
# ret = requests.get(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/boosleida/home_page/sales_ranking_customer_num' # 统计-名片状态+账号状态
# ret = requests.get(url, params=get_data)




# url = ip + '/zhugeleida/boosleida/home_page/hudong_pinlv_customer_num' # 统计-名片状态+账号状态
# ret = requests.get(url, params=get_data)


#
# url = ip + '/zhugeleida/boosleida/home_page/expect_chengjiaolv_customer_num' # 统计-名片状态+账号状态
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/boosleida/home_page/query_have_customer_detail_people' # 统计-名片状态+账号状态
# post_data['query_user_id']=17
# post_data['days']=0
# get_data['length']=5
# get_data['current_page']= 2
#
# # post_data['expedted_pr']='1_50_pr'
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/boosleida/home_page/query_hudong_have_customer_detail_people' # 统计-名片状态+账号状态
# post_data['type']= 'chat' #  chat
# post_data['query_user_id']= 55
# post_data['days']=30
# ret = requests.post(url, params=get_data,data=post_data)






##############################################






# url = 'http://127.0.0.1:8000/zhugeleida/customer/update_information/2' # 修改-客戶信息表
# post_data['openid'] = 'dfasdcdafwcdgavrasc'
# post_data['username'] = '张三丰'
# post_data['expected_time'] = '2018-06-5'
# post_data['belonger'] = 1
# post_data['superior'] = 1
#
# post_data['source'] = 1
# post_data['memo_name'] = '太乙真人'
# post_data['phone'] = '15931788974'
# post_data['email'] = '1224423@qq.com'
# post_data['company'] = '合众康桥'
# post_data['position'] = '开发TTT'
# post_data['address'] = '通州区xxx'
# post_data['mem'] = '我是一个兵'
# post_data['birthday'] = '2018-06-1'
# ret = requests.post(url, params=get_data,data=post_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_expected_time/1' # 修改-客户预计成交时间
# post_data['expected_time'] = '2018-06-14'
# ret = requests.post(url, params=get_data,data=post_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_expected_pr/1' # 修改-客户预计成交概率
# post_data['expedted_pr'] = '80%'
# ret = requests.post(url, params=get_data,data=post_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_tag/1' # 修改-客户的标签
# post_data['tag_list'] = '[1,2]'
# ret = requests.post(url, params=get_data,data=post_data)





# url = 'http://127.0.0.1:8000/zhugeleida/customer/delete/3' # 删除-客户
# ret = requests.post(url,params=get_data)  #params 传 get值,reques.GET.get('timestamp')
#


# '''
# {
#  'to': contact_id,
#  'msg': msg_text
#  'from': "{{request.user.userprofile.id}}",
#  'from_name': "{{request.user.userprofile.name}}",
# }
# '''
# #
# url = ip + '/zhugeleida/qiyeweixin/chat/send_msg/0' # 增加聊天消息
# post_data['customer_id'] = 1
# post_data['content'] = json.dumps({
#     'info_type': 1,             # 1代表发送的文字\表情\ 或 话术库里的自定义(文字表情)。
#     'msg': '这个信息是文字\表情'
#
# })
# post_data['user_id'] = 55
# post_data['send_type'] = 1
# ret = requests.post(url, data=post_data,params=get_data)


# get_data['customer_id'] = 1
# get_data['user_id'] = 55
# url =  ip + '/zhugeleida/qiyeweixin/chat/getmsg/0'
# ret = requests.get(url, params=get_data)

# url = ip +   '/zhugeleida/qiyeweixin/chat' # 分页 聊天信息记录
# get_data['customer_id'] = 1
# get_data['u_id'] = 55
# ret = requests.get(url, params=get_data)
# ret = requests.get(url, data=get_data)  // data 传 post 值   params 传 get值


#
# url = ip + '/zhugeleida/qiyeweixin/mingpian/feedback'   # 添加产品
# post_data['problem_type'] = 1
# content =  [
#       {
# 		'type': 'phone',
# 		'data': '13020006631'
# 	  },
# 	  {
# 		'type': 'picture_url',
# 		'data':  ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png',
# 			'statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png'
# 		 ]
# 	  },
# 	  {
# 		'type': 'content',
# 		'data': '孙贼，用户体验不够好，请你们费心优化'
# 	  }
#    ]
#
# post_data['content'] = json.dumps(content)
#
# ret = requests.post(url, params=get_data, data=post_data)
#


url = ip +   '/zhugeleida/mycelery/user_send_gongzhonghao_template_msg' # 分页 聊天信息记录
get_data['data'] = json.dumps({'user_id': 55, 'customer_id' : 854})

ret = requests.get(url, params=get_data)



print(ret.text)


