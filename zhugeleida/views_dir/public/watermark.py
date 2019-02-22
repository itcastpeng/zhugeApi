from PIL import Image

import os, random, time, hashlib, base64
from PIL import ImageDraw
from PIL import ImageFont


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
    def generate_watermark_img(self, watermark_text):

        # 打开底版图片
        imageFile = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', 'wuzi.png')  # 已打水印图片路径
        im1 = Image.open(imageFile)

        # 在图片上添加文字 1
        draw = ImageDraw.Draw(im1)
        font = ImageFont.truetype("arial.ttf", size=100) # 设置字体

        text = str(watermark_text.encode('utf8'))
        # text = watermark_text.encode('utf8')
        # print('watermark_text-------> ', text, watermark_text)

        draw.text((0, 0), text, (255, 255, 0), font=font) # 设置 坐标 文字 颜色 字体


        # save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', encryption() + '.png')  # 已打水印图片路径
        save_path = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', '1.png')  # 已打水印图片路径
        # 保存
        im1.save(save_path)


    # 覆盖水印图片
    def cover_watermark(self, img_path, watermark_path):
        image = Image.open(img_path)  # 原图
        shuiyin = Image.open(watermark_path)  # 水印
        r, g, b, a = shuiyin.split()
        image.paste(shuiyin, mask=a)
        lujing = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'watermark', encryption() + '.png')  # 已打水印图片路径
        image.save(lujing)
        return lujing






if __name__ == '__main__':
    obj = watermark()
    text = '哈哈哈哈哈哈'
    obj.generate_watermark_img(text)
