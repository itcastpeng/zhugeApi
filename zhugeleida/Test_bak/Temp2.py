import requests,json


# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_qr_code'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/create_user_or_customer_poster'
# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/crontab_create_user_to_customer_qrCode_poster'
#
# get_data = {
#     'data': json.dumps({"user_id": 87, "customer_id": 1090})
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
import datetime
import os

# ## 下载图片链接
# qrcode_url = 'http://wx.qlogo.cn/mmopen/Oic0uTcibguuSMlpaHLGsQbFib0DAUicZBIpibFVIEBBRRgWphYGeWibQaAF1jkgtBYAgcgsNibaU4olEQddHMr5ibZv5gjEibib9EWWah/0'
#
#
# s = requests.session()
# s.keep_alive = False  # 关闭多余连接
# html = s.get(qrcode_url)
#
# # html = requests.get(qrcode_url)
#
# now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
# filename = "/%s_%s.jpg" % ('YYYYY', now_time)
# file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'qr_code') + filename
# with open(file_dir, 'wb') as file:
#     file.write(html.content)

mima = '8sCAJ3YuU6EfYWxI'

len_num =  len(mima)


zhongjian_num =  divmod(len_num, 2)[0]

start_num = zhongjian_num - 3
end_num = zhongjian_num + 3

















