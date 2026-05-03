"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from sqlalchemy.exc import SQLAlchemyError
from models import MarketTemperature
from models.database import db_session
from sqlalchemy import asc, and_, desc

class MarketTemperatureService:
    @staticmethod
    def create(temperature, ai_suggestion, created_at=None):
        """
        创建一个新的 MarketTemperature 记录。
        :param temperature: 温度值
        :param ai_suggestion: AI suggestion
        :param created_at: 创建日期，默认为 None
        :return: 新创建的对象或 None 如果发生错误
        """
        try:
            new_entry = MarketTemperature(temperature=temperature, ai_suggestion=ai_suggestion, created_at=created_at)
            db_session.add(new_entry)
            db_session.commit()
            return new_entry
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Database error occurred: {e}")
            return None

    @staticmethod
    def get_first():
        """
        获取所有 MarketTemperature 记录。
        :return: 包含所有记录的列表
        """
        data = MarketTemperature.query.order_by(desc(MarketTemperature.created_at)).first()
        return data.to_dict() if data else None

    @staticmethod
    def get_all(limit=30):
        """
        获取所有 MarketTemperature 记录。
        :return: 包含所有记录的列表
        """
        datas = MarketTemperature.query.order_by(desc(MarketTemperature.created_at)).limit(limit)
        return [data.to_dict() for data in datas]

    @staticmethod
    def update(id, **kwargs):
        """
        更新指定 ID 的 MarketTemperature 记录。
        :param id: 要更新的记录ID
        :param kwargs: 要更新的字段名和值
        :return: 更新后的对象或 None 如果没有找到对应的记录
        """
        entry = MarketTemperature.query.get(id)
        if entry is None:
            return None

        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        try:
            db_session.commit()
            return entry
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Database error occurred: {e}")
            return None

    @staticmethod
    def delete(id):
        """
        删除指定 ID 的 MarketTemperature 记录。
        :param id: 要删除的记录ID
        :return: True 如果删除成功，否则 False
        """
        entry = MarketTemperature.query.get(id)
        if entry is not None:
            try:
                db_session.delete(entry)
                db_session.commit()
                return True
            except SQLAlchemyError as e:
                db_session.rollback()
                print(f"Database error occurred: {e}")
        return False
