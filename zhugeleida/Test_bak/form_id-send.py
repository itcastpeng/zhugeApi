import requests
import datetime
import json


post_template_data = {}

# form_id = '1532592694827'
# openid = 'o2ZPb4qqMYgrK0K3VUMHo5L-7ySw'

# openid = 'o2ZPb4pUJZxQtlW4NVpzIrb8hIIA'
# form_id = '7627cffd5fc27b58ff511990c44bfbca'


# post_template_data['touser'] = openid
# 
# post_template_data['template_id'] = 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE'
# 
# path = 'pages/mingpian/index?source=2&uid=1&pid='
# 
# post_template_data['page'] = path
# post_template_data['form_id'] = form_id
# 
# user_name = '韩新颖'
# 
# now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# # 留言回复通知
# data = {
#     'keyword1': {
#         'value': user_name  # 回复者
#     },
#     'keyword2': {
#         'value': now_time   # 回复时间
#     },
#     'keyword3': {
#         'value': '您有未读消息,点击小程序查看哦。'  # 回复内容
#     }
# }
# post_template_data['data'] = data
# select * from zhugeleida_zgld_customer  where id = 24  \G

access_token = "12_THDsYNgh2AIipUL9Cki2PLTW6vo9nfThoUfXANDTCmzEwJ9gf6IzJ9E68tK8uOm5qQHmKWCM5N8JGUMvLZjXR-qwByrgEoXs1GpyOAV6zMw4_kgShnjK_A24pCSCF-wM5O8yjmJURsDznFqiOHHeACASLL"
touser = 'o2ZPb4qqMYgrK0K3VUMHo5L-7ySw'
form_id = 'c076ee5863b71602a050ad9ddf954368'


get_template_data = {
    "access_token": access_token
}
# https://developers.weixin.qq.com/miniprogram/dev/api/notice.html#发送模板消息
template_msg_url  = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send'

post_template_data_ju = {
    'form_id': form_id, 'touser': touser,
     'template_id': 'yoPCOozUQ5Po3w4D63WhKkpGndOKFk986vdqEZMHLgE',
     'data': {'keyword1': {'value': '张炬-测试接口Y'}, 'keyword3': {'value': '您有未读消息,点击小程序查看哦。'},
              'keyword2': {'value': '2018-08-15 20:31:32'}}, 'page': 'pages/mingpian/index?source=2&uid=55&pid='
     }

print('------ post_template_data_ju ------>>',json.dumps(post_template_data_ju))

data = json.dumps(post_template_data_ju,ensure_ascii=False).encode('utf-8')
template_ret = requests.post(template_msg_url, params=get_template_data, data=data)
template_ret = template_ret.json()

print('--------企业用户 send to 小程序 Template 接口返回数据--------->' ,template_ret)