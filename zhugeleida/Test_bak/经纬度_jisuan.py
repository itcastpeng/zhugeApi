

import requests

import json
#
# r = requests.get(url='http://api.map.baidu.com/geocoder/v2/', params={'location':'39.934,116.329','ak':'yourAK','output':'json'})
#
# result = r.json()
# # city = result['result']['addressComponent']['city']
# print(result)


import requests
import json


def find_street(location):
    url = 'http://api.map.baidu.com/geocoder/v2'
    ak = 'NLVvUqThVdf38Gkyb1kizrqRC2yxa7t7'
    real_url = url + '/?callback=renderReverse&location=' + location + '&output=json&pois=1&ak=' + ak
    req = requests.get(real_url)
    print(req.text)
    t=req.text[29:-1]
    print(t)
    data = json.loads(t)
    # street = data  # 输出街道名称
    # print(street)
    return data


if __name__ == '__main__':

        location = '34.264642646862,108.95108518068'
        data = find_street(location)
        formatted_address = data.get('result').get('formatted_address')
        print('---- 解析出的具体位置 formatted_address ----->>')  # 输出街道名称




# import os,subprocess
# from  ffmpy import FFmpeg
# from io import BytesIO
# def transformat_voice():
#     from_fn = 'customer_854_user_17_20181212_195908431044.amr'
#     to_fn = 'target.mp3'
#     mp3_file = BytesIO()
#     # with open(from_fn, 'wb') as f_from:
#     #     f_from.write(amr_voice_b.getvalue())
#     ff =  FFmpeg(inputs={from_fn: None}, outputs={to_fn: None})
#     ff.run()
#
#     with open(to_fn, 'rb') as f_to:
#         f_to.seek(0)
#         mp3_file.write(f_to.read())
#
#     os.remove(from_fn)
#     os.remove(to_fn)
#     mp3_file.seek(0)
#
#     return mp3_file
#
# transformat_voice()

# import subprocess,os
#
# def amr2mp3(amr_path, mp3_path=None):
#     path, name = os.path.split(amr_path)
#     if name.split('.')[-1] != 'amr':
#         print ('not a amr file')
#         return 0
#     if mp3_path is None or mp3_path.split('.')[-1] != 'mp3':
#         mp3_path = os.path.join(path, name.split('.')[0] + '.mp3')
#     error = subprocess.call(['/usr/bin/ffmpeg', '-i', amr_path, mp3_path])
#     print (error)
#     if error:
#         return 0
#
#     print ('success')
#     return mp3_path
#
#
# if __name__ == '__main__':
#     amr_path = 'demo.amr'
#     amr2mp3(amr_path)










