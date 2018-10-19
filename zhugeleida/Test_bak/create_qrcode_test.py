

# 生成二维码
# import qrcode
# qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
# qr.add_data('http://www.cnblogs.com/sfnz/')
# qr.make(fit=True)
# img = qr.make_image()
# img.show()
# img.save('test.jpg')


url = 'http://mmbiz.qpic.cn/mmbiz_jpg/ToibUibDOYglV5HK4DBCUDgY7dSOv9Tu1d8KQMq0KU4W0dAAlU90JDgdibNhsyUxJ3CsJPyxaC2h26HEYKjyqTh0w/0'

import requests

html = requests.get(url)
with open('zhugeleida_gzh_qrcode.jpg', 'wb') as file:
    file.write(html.content)

