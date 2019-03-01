from PIL import Image

import os, random, time, hashlib, base64

from PIL import Image,ImageFont,ImageDraw
import numpy as np
# from pylab import *

import cv2

# 加密名字
def encryption():
    string = str(random.randint(10, 99)) + str(int(time.time())) + str(random.randint(10, 99))
    pwd = str(string)
    hash = hashlib.md5()
    hash.update(pwd.encode())
    return hash.hexdigest()


class watermark(object):
    def __init__(self):
        pass

    # 生成水印图片
    def generate_watermark_img(self, mark_text):
        imageFile = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', 'wuzi.png')  # 已打水印图片路径
        # 打开底版图片
        im1 = Image.open(imageFile)
        draw = ImageDraw.Draw(im1)               # 绘图句柄
        font = ImageFont.truetype('/usr/share/fonts/chinese/simsun.ttc', 24)  # 使用自定义的字体，第二个参数表示字符大小

        color = (233, 233, 233)

        num = 1
        for i in range(10):
            x = 140
            y = 60
            if num % 2 == 0:
                x = 3
                y = 200

            if num > 4:
                y += 560
            elif num > 2:
                y += 280

            for i in range(5):
                draw.text((x, y) , mark_text, color, font=font)       # 绘图
                x += 280
            num += 1

        save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', encryption() + '.png')  # 已打水印图片路径
        im1.save(save_path)
        return save_path



    # 覆盖水印图片
    def cover_watermark(self, img_path, watermark_path):
        image = Image.open(img_path)  # 原图
        shuiyin = Image.open(watermark_path)  # 水印
        r, g, b, a = shuiyin.split()
        image.paste(shuiyin, mask=a)
        lujing = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', encryption() + '.png')  # 已打水印图片路径
        image.save(lujing)
        return lujing


