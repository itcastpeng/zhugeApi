from PIL import Image

import os, random, time, hashlib, base64

from PIL import Image,ImageFont,ImageDraw
# import numpy as np
# from pylab import *

# import cv2

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
    def generate_watermark_img(self, company_id, mark_text):
        if __name__ == "__main__":
            imageFile = 'wuzi.png'
            save_path = 'test/wz.png'
        else:
            imageFile = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', 'mylg_reproduction.png')  # 已打水印图片路径
            save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', encryption() + '.png')  # 已打水印图片路径
        # 打开底版图片
        print('imageFile------------------> ', imageFile)
        im1 = Image.open(imageFile)
        draw = ImageDraw.Draw(im1)               # 绘图句柄

        font = ImageFont.truetype('/usr/share/fonts/chinese/simsun.ttc', 24)  # 使用自定义的字体，第二个参数表示字符大小
        # 文字rgb颜色
        if int(company_id) == 12: # 米扬丽格
            rgb_color = (132,127,131, 10)
        else:
            rgb_color = (233, 233, 233, 30) # 白色

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
                draw.line([(x - 60, y - 100), (x + 30, y - 10)], fill=rgb_color, width=2)
                draw.line([(x + 150, y - 100), (x + 60, y - 10)], fill=rgb_color, width=2)
                if num > 4:
                    draw.line([(x - 60, y + 113), (x + 23, y + 30)], fill=rgb_color, width=2)
                    draw.line([(x + 156, y + 113), (x + 73, y + 30)], fill=rgb_color, width=2)
                draw.text((x, y) , mark_text, rgb_color, font=font)       # 绘图
                x += 280
            num += 1


        im1.save(save_path)
        return save_path

    # 覆盖水印图片
    def cover_watermark(self, img_path, watermark_path):
        image = Image.open(img_path)  # 原图
        shuiyin = Image.open(watermark_path)  # 水印
        r, g, b, a = shuiyin.split()
        image.paste(shuiyin, mask=a)

        if __name__ == "__main__":
            lujing = 'test/tttt.png'
        else:
            lujing = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark',
                encryption() + '.png')  # 已打水印图片路径
        image.save(lujing)
        os.remove(watermark_path) # 删除水印
        return lujing


if __name__ == '__main__':
    obj = watermark()
    mark_text = '米扬丽格'
    path = obj.generate_watermark_img(mark_text)
    print(path)
    obj.cover_watermark('test/111.jpg', path)
