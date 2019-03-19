
import datetime


# 时间筛选
def time_screen(number_days):
    now_datetime = datetime.datetime.today()
    now_date = datetime.datetime.strftime(now_datetime, '%Y-%m-%d')  # 今天年月日
    stop_time = now_date + ' 23:59:59'
    if number_days == 'all_days':  # 全部
        start_time = '1970-01-01 00:00:00'
    else:
        if number_days == 'today':  # 今天
            days = 0
        elif number_days == 'seven_days':  # 近七天
            days = 7
        elif number_days == 'thirty_days':  # 近三十天
            days = 30
        else:  # 默认昨天
            # if number_days == 'yesterday':  # 昨天
            days = 1
            deletion = datetime.datetime.strftime((now_datetime - datetime.timedelta(days=days)), '%Y-%m-%d')
            stop_time = deletion + ' 23:59:59'

        deletionTime = (now_datetime - datetime.timedelta(days=days))
        now_date = datetime.datetime.strftime(deletionTime, '%Y-%m-%d')
        start_time = now_date + ' 00:00:00'

    return start_time, stop_time