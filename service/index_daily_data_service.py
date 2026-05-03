"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""
import pandas
import pandas as pd
from sqlalchemy.exc import IntegrityError
from models import IndexDailyData
from datetime import date as dt_date
from models.database import db_session
from utils.common import logger

class IndexDailyDataService:

    @staticmethod
    def get_history(symbol: str, start_date=None, end_date=None) -> pandas.DataFrame:
        """
        根据股票代码获取日线数据，可选时间范围。

        :param symbol: 股票代码
        :param start_date: 起始日期 (str 或 date)，格式如 '2025-01-01'
        :param end_date: 结束日期 (str 或 date)，格式如 '2025-12-31'
        :return: 列表 of dict，按日期升序排列
        """
        raw_data = IndexDailyDataService.get_all_by_symbol(symbol, start_date, end_date)
        df = pd.DataFrame(raw_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index("date", inplace=True)
        return df

    @staticmethod
    def get_all_by_symbol(symbol: str, start_date=None, end_date=None):
        """
        根据股票代码获取日线数据，可选时间范围。

        :param symbol: 股票代码
        :param start_date: 起始日期 (str 或 date)，格式如 '2025-01-01'
        :param end_date: 结束日期 (str 或 date)，格式如 '2025-12-31'
        :return: 列表 of dict，按日期升序排列
        """
        try:
            query = db_session.query(IndexDailyData).filter(IndexDailyData.symbol == symbol)

            # 处理日期范围
            if start_date:
                if isinstance(start_date, str):
                    start_date = dt_date.fromisoformat(start_date)
                query = query.filter(IndexDailyData.date >= start_date)

            if end_date:
                if isinstance(end_date, str):
                    end_date = dt_date.fromisoformat(end_date)
                query = query.filter(IndexDailyData.date <= end_date)

            # 倒序：最新日期在前
            results = query.order_by(IndexDailyData.date).all()
            return [stock.to_dict() for stock in results]

        except Exception as e:
            logger.error(f"Failed to fetch data for symbol {symbol} between {start_date} and {end_date}: {e}")
            return []

    @staticmethod
    def add(daily_data):
        try:
            stock = IndexDailyData(**daily_data)
            db_session.add(stock)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Insertion failed: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred: {e}")
        return False

    @staticmethod
    def batch_add(daily_data_list):
        try:
            for daily_data in daily_data_list:
                stock = IndexDailyData(**daily_data)
                db_session.add(stock)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Batch insertion failed: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred: {e}")
        return False
