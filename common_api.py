"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from datetime import datetime, timedelta

def get_date_by_n(n, format='%Y%m%d'):
    """
    返回当前日期前后 n 天的日期字符串。
    :param n: int, 天数。正数表示未来日期，负数表示过去日期。
    :param format: str, 日期格式字符串，默认为 '%Y-%m-%d'。
    :return: str, 日期字符串。
    """
    # 获取当前日期
    current_date = datetime.now()

    # 计算目标日期
    target_date = current_date + timedelta(days=n)

    # 格式化日期字符串
    formatted_date = target_date.strftime(format)

    return formatted_date


def get_date_by_years(date=None, years=1, format='%Y%m%d'):
    """
    计算给定日期加上或减去若干年后的日期，并返回格式化为 %Y%m%d 的字符串。

    :param date: 可选参数，datetime对象。如果未提供，则使用当前日期。
    :param years: 要增加或减少的年数。正数表示未来，负数表示过去。
    :return: 经过年份调整后的日期，格式为 %Y%m%d 的字符串。
    """
    if date is None:
        date = datetime.now()
    else:
        # 确保传入的是datetime对象
        if not isinstance(date, datetime):
            raise ValueError("提供的日期必须是datetime对象")

    try:
        # 尝试直接增加或减少年份
        adjusted_date = date.replace(year=date.year + years)
    except ValueError:
        # 如果遇到闰年的2月29日且目标年不是闰年，调整到2月28日
        if date.month == 2 and date.day == 29:
            if (date.year % 4 == 0 and (date.year % 100 != 0 or date.year % 400 == 0)) and \
                ((date.year + years) % 4 != 0 or ((date.year + years) % 100 == 0 and (date.year + years) % 400 != 0)):
                adjusted_date = date.replace(month=2, day=28, year=date.year + years)
            else:
                raise
        else:
            raise

    # 格式化日期为 %Y%m%d 格式
    formatted_date = adjusted_date.strftime(format)

    return formatted_date


if __name__ == '__main__':
    print(1)
