
import random

# 医生图片 百度资源
def cover():
    data_list = [
        'statics/zhugeleida/imgs/admin/watermark/5e7c0e9ee62b7ad63fc059870ae81245.png',
        'statics/zhugeleida/imgs/admin/watermark/abb239a48f73b42ba691b2f79e828a9a.png',
        'statics/zhugeleida/imgs/admin/watermark/1ccbefb964a71ba4299616f93bbcc709.png'
                 ]

    random.shuffle(data_list) # 打乱列表
    return data_list[0]