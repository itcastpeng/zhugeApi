
import qrcode
qr=qrcode.QRCode(version =7,error_correction = qrcode.constants.ERROR_CORRECT_L,box_size=4,border=3)
qr.add_data('http://www.cnblogs.com/sfnz/')
qr.make(fit=True)
img = qr.make_image()
img.show()
img.save('test.jpg')