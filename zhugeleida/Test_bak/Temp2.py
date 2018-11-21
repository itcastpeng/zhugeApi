import requests,json


# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_create_user_to_customer_qrCode_poster'

get_data = {
    'data': json.dumps({"user_id": 87, "customer_id": 1090})
}

# print(get_data)

s = requests.session()
s.keep_alive = False  # 关闭多余连接
ret = s.get(url, params=get_data)

# ret = requests.get(url, params=get_data)


print(json.dumps(ret.json()))
