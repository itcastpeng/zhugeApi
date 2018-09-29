
from publicFunc import account

import time
import requests
import json

# token = '3385f306019d810ac6bdc00e9e08b0b4'
token = '90e8114abd1a309516eaa48af1d6b36a'
timestamp = str(int(time.time() * 1000))

get_data = {
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,

    'user_id': 1,
    # 'customer_id': 2,
    #  'order' : '-last_follow_time'


}

post_data = {

}

ip = 'http://127.0.0.1:8001'
# ip = 'http://192.168.100.20:8000'
# ip = 'http://api.zhugeyingxiao.com'



# url = ip + '/zhugeleida/xiaochengxu/chat/send_msg/0' # 增加聊天消息
# post_data['u_id'] = 1
# # post_data['msg'] = 'YYYYTTTTT'
# post_data['content'] = json.dumps({
#     'info_type': 1,             # 1代表发送的文字\表情\ 或 话术库里的自定义(文字表情)。
#     'msg': '这个信息是文字\表情'
#
# })
# post_data['send_type'] = 2
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/xiaochengxu/chat/getmsg/0' # 实时聊天记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/xiaochengxu/chat/query_num/0' # 实时聊天记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/xiaochengxu/chat/history_chatinfo_store_content/0' # 实时聊天记录
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/xiaochengxu/chat/encrypted_phone_number/0' # 实时聊天记录
#
# post_data['u_id'] = 18
# post_data['encryptedData'] = "Q10d07JnNold5IsikOa55mMGqAYapDe/6i43RbayjnvBgN99jpQxRu5OIE5ovfmJwJ+n7eU0K6BH+bTERl/63LpkdSNGulwyVQwHbUQQ+wMmhZLqE1b0pZdmymJATZxWAQHP6p/D/CSIIqNgfLA8e2qxhA/tGOravGQwKANjYVys+RkGJQfBfck+xB5Ze6fu7pqFzmyavGFnufNsU57Gpg=="
# post_data['iv'] = "IQBdM5LzHNBKCFD9R8ikeg=="
#
# ret = requests.post(url, params=get_data,data=post_data)



# url = ip +   '/zhugeleida/xiaochengxu/chat' # 分页 聊天信息记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/chat' # 分页 聊天信息记录
# get_data['u_id'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/contact' #
# ret = requests.get(url, params=get_data)




# url =ip +  '/zhugeleida/qiyeweixin/action/get_new_log'       #得到相应的动作的-->访问日志
# # get_data['action'] = 6
#
# ret = requests.get(url, params=get_data)


# url =ip +  '/zhugeleida/qiyeweixin/qr_code_auth'       #得到相应的动作的-->访问日志
# # get_data['action'] = 6
#
# ret = requests.get(url, params=get_data)



# url =  ip + '/zhugeleida/qiyeweixin/action/time'       #得到所有访问日志
# get_data['customer_id'] = 1
# ret = requests.get(url, params=get_data)




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



# url = ip +  '/zhugeleida/xiaochengxu/product/product_single'  # 获取产品的列表
# get_data['product_id'] = 10
# get_data['uid'] = 2
# ret = requests.get(url, params=get_data)



# url = ip + '/zhugeleida/xiaochengxu/product/product_list'  # 获取产品的列表
#
# get_data['uid'] =1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/product/forward_product'  # 记录转发产品动作。
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/product/forward_product'  # 记录转发产品动作。
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/product_list'  # 获取产品的列表
# get_data['status'] =1
#ret = requests.get(url, params=get_data)


############################# 登录 ####################################

url = ip + "/zhugeleida/xiaochengxu/login"
get_data['company_id'] = 1

ret = requests.get(url, params=get_data)



# url = ip + "/zhugeleida/xiaochengxu/login/binding"
# get_data['source'] = 1
# get_data['uid'] = 2
# get_data['pid'] = 22
#
# ret = requests.get(url, params=get_data)

#
# url = ip +  '/zhugeleida/xiaochengxu/website'  # 获取产品的列表
# get_data['uid'] = 1
#
# ret = requests.get(url, params=get_data)

# url = ip + "/zhugeleida/xiaochengxu/login/send_user_info"
# post_data['nickName'] = 1
# post_data['page'] = 2
# post_data['city'] = 22
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/xiaochengxu/login/send_form_id"
# post_data['formId'] = '发322342'
# ret = requests.post(url, params=get_data, data=post_data)

# url = ip + "/zhugeleida/xiaochengxu/login/control_mingan_info"
# ret = requests.get(url, params=get_data, data=post_data)


# content = ret.json()['data']['ret_data']

print(ret.text)












