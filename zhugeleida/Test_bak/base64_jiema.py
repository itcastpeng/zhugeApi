import requests

# import time
#
# import base64
#
# with open('11111111111.jpg', 'rb') as f:
#     base64_data = base64.b64encode(f.read()).decode()
#
#
# print(int(time.time() * 1000))
#
# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/add_picture/0'
# post_data = {
#     'task': 'dsfdsafdsa',
#     'chunk': 0,
#     'file': base64_data,
#
# }
# ret = requests.post(url, data=post_data)

import os
import base64
from django import forms

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from django.db.models import Q
BasePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# print(BASE_DIR,'\n',BasePath)

import base64
username = ''
for name in  ['张聪','过客丶','诸葛营销','做自己','Ju do it','西门庆豪|董庆豪|合众','豆豆','🌻李汉杰👵','🌿张聪','卢俊义','公孙胜','秦明','假如','关胜','过客❤','ju do it','西门庆豪|董庆豪|合众','梦忆🍁','吴用','青春不散场@',
              '诸葛营销','武松','刘鹏','林敏','张清','柴进','李应','花荣','硕子😁 🏀','胡蓉','夏宏伟：品牌良医','许艳','贺～丹','余宏亮']:
    encodestr = base64.b64encode(name.encode('utf-8'))
    username = str(encodestr, 'utf-8')
    print('%s : %s' % (name,username))



username = base64.b64decode(username)
print('------- jie -------->>',str(username,'utf-8'))

    # username = base64.b64decode('5a6B57y65q+L5rul')
    # print(str(username,'utf-8'))





# str= '%F0%9F%8C%B5%20%E5%81%9A%E8%87%AA%E5%B7%B1'
# s = str.encode("utf-8")
#
# print("UTF-8 解码：", s.decode('UTF-8','strict'))

# encodestr = base64.b64encode('abcr34r344r'.encode('utf-8'))
# print('---str encodestr----->, str(encodestr','utf-8')



