from dateutil.parser import parse
import time

import datetime


def deal_time(create_time):

    # 获取输入时间的 datetime 对象
    input_dateTime = datetime.datetime.strptime(str(create_time), "%Y-%m-%d %H:%M:%S.%f")

    # 获取当前时间的 datetime 对象
    now_dateTime = datetime.datetime.now()


    if now_dateTime.year != input_dateTime.year:  # 判断年是否不一致
        create_time = input_dateTime.strftime('%Y')

    elif now_dateTime.day - 1 == input_dateTime.day : # 表示是不是昨天
        create_time = '昨天'

    elif now_dateTime.day == input_dateTime.day: # 表示是今天的时间
        create_time = input_dateTime.strftime('%H:%M')

    else: # 年一致
        create_time = input_dateTime.strftime('%m-%d')

    return create_time


if __name__ == '__main__':
    create_time = '2018-06-02 20:40:00'
    ret = deal_time(create_time)
    print(ret)


