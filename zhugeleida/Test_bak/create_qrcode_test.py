

# 生成二维码
# import qrcode
# qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
# qr.add_data('http://www.cnblogs.com/sfnz/')
# qr.make(fit=True)
# img = qr.make_image()
# img.show()
# img.save('test.jpg')


url = 'http://mmbiz.qpic.cn/mmbiz_jpg/pfdFlZRbI4F05DuMfyZrjjS5KdaJJwpV8Ww4BfYmINzzlP7R1SibOVqQv0JgibPzhm9WwdOIgYAEyQK0oOa0zAXw/0'

import requests

html = requests.get(url)
with open('zhugeleida_gzh_qrcode.jpg', 'wb') as file:
    file.write(html.content)

