"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from models import MarketDailyLimit
from models.database import db_session


class MarketDailyLimitService:

    @staticmethod
    def add_market_daily_limit(date, rising, limit_up, falling, limit_down, flat):
        """
        添加新的市场每日限制记录
        :param date: 日期
        :param rising: 上涨数量
        :param limit_up: 涨停数量
        :param falling: 下跌数量
        :param limit_down: 跌停数量（可选）
        :param flat: 平盘数量（可选）
        """
        new_entry = MarketDailyLimit(date=date, rising=rising, limit_up=limit_up, falling=falling,
                                     limit_down=limit_down, flat=flat)
        db_session.add(new_entry)
        db_session.commit()

    @staticmethod
    def get_market_daily_limit_by_date(date):
        """
        根据日期获取市场每日限制记录
        :param date: 日期
        :return: MarketDailyLimit 对象或 None
        """
        return db_session.query(MarketDailyLimit).filter(MarketDailyLimit.date == date).first()

    def update_market_daily_limit(self, date, **kwargs):
        """
        更新市场每日限制记录
        :param date: 日期
        :param kwargs: 需要更新的字段及其值
        """
        entry = self.get_market_daily_limit_by_date(date)
        if entry:
            for key, value in kwargs.items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
            db_session.commit()

    def delete_market_daily_limit(self, date):
        """
        删除市场每日限制记录
        :param date: 日期
        """
        entry = self.get_market_daily_limit_by_date(date)
        if entry:
            db_session.delete(entry)
            db_session.commit()

    @staticmethod
    def get_market_daily_limit_as_dict(date):
        """
        根据日期获取市场每日限制记录并转换为字典
        :param date: 日期
        :return: 字典或 None
        """
        entry = MarketDailyLimitService.get_market_daily_limit_by_date(date)
        if entry:
            return entry.to_dict()
        return None
