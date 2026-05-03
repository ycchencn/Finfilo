"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import pandas as pd
import akshare as ak
from models import FuturesBasisWide
from flask import current_app
from models.database import db_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from service.index_daily_data_service import IndexDailyDataService
from utils.common import logger, df_cache


@df_cache()
def get_futures_daily_cached(start_date, end_date, market='CFFEX'):
    return ak.get_futures_daily(start_date=start_date, end_date=end_date, market=market)


class FuturesBasisWideService:

    @staticmethod
    def get_basis_on_date(trade_date: str, index_code: str, future_prefix: str):
        """
        计算指定交易日的股指期货贴水

        参数:
            trade_date: 字符串，格式 "YYYYMMDD"，如 "20251218"
            index_code: 现货指数代码，如 "000300"（沪深300）
            future_prefix: 期货前缀，如 "IF", "IH", "IC"

        返回:
            dict: 包含合约、期货价、现货价、贴水、贴水率
        """
        # 1. 获取中金所当天所有期货数据
        futures_df = get_futures_daily_cached(start_date=trade_date, end_date=trade_date, market="CFFEX")

        if futures_df.empty:
            raise ValueError(f"{trade_date} 中金所无数据，请确认是否为交易日")

        # 2. 筛选目标品种（如 IF 开头）并找到成交量最大的为主力
        target_futures = futures_df[futures_df['symbol'].str.startswith(future_prefix)].copy()
        if target_futures.empty:
            raise ValueError(f"{trade_date} 未找到 {future_prefix} 合约数据")

        # 转换成交量为数值（部分版本是字符串）
        target_futures['volume'] = pd.to_numeric(target_futures['volume'], errors='coerce')
        main_contract_row = target_futures.loc[target_futures['volume'].idxmax()]
        main_symbol = main_contract_row['symbol']
        future_close = main_contract_row['close']

        # 3. 获取现货指数收盘价
        index_df = IndexDailyDataService.get_history(symbol=index_code, start_date=trade_date, end_date=trade_date)

        if index_df.empty:
            raise ValueError(f"{trade_date} 未获取到指数 {index_code} 数据")

        spot_close = index_df.iloc[0]['close']

        # 4. 计算基差（现货 - 期货）
        basis = spot_close - future_close
        basis_rate = basis / spot_close * 100

        return {
            "日期": trade_date,
            "主力合约": main_symbol,
            "期货收盘": round(future_close, 2),
            "现货收盘": round(spot_close, 2),
            "基差": round(basis, 2),  # >0 表示贴水，<0 表示升水
            "基差率(%)": round(basis_rate, 4)
        }

    @staticmethod
    def create(
        trade_date,
        index_name,
        future_symbol,
        future_close=None,
        spot_close=None,
        basis=None,
        basis_rate_pct=None,
        source='akshare_cffex'
    ):
        """
        创建一条完整的贴水记录。
        """
        try:
            record = FuturesBasisWide(
                trade_date=trade_date,
                index_name=index_name,
                future_symbol=future_symbol,
                future_close=future_close,
                spot_close=spot_close,
                basis=basis,
                basis_rate_pct=basis_rate_pct,
                source=source
            )
            db_session.add(record)
            db_session.commit()
            return record
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in create: {e}")
            db_session.rollback()
            return None

    @staticmethod
    def bulk_create(records):
        """
        批量插入多条记录（推荐用于每日3条：IF/IH/IC）
        :param records: list of dict 或 FuturesBasisWide 对象
        """
        try:
            obj_list = []
            for r in records:
                if isinstance(r, dict):
                    obj = FuturesBasisWide(**r)
                else:
                    obj = r
                obj_list.append(obj)
            db_session.add_all(obj_list)
            db_session.commit()
            return len(obj_list)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in bulk_create: {e}")
            db_session.rollback()
            return -1

    @staticmethod
    def get_by_date_and_index(trade_date, index_name):
        """
        查询某日某指数的完整贴水数据。
        :return: dict or None
        """
        try:
            record = db_session.query(FuturesBasisWide).filter(
                and_(
                    FuturesBasisWide.trade_date == trade_date,
                    FuturesBasisWide.index_name == index_name
                )
            ).first()
            return record.to_dict() if record else None
        except Exception as e:
            logger.error(f"Error in get_by_date_and_index: {e}")
            return None

    @staticmethod
    def get_by_date(trade_date):
        """
        获取某日所有指数的贴水数据。
        :return: list of dict
        """
        try:
            records = db_session.query(FuturesBasisWide).filter(
                FuturesBasisWide.trade_date == trade_date
            ).all()
            return [r.to_dict() for r in records] if records else []
        except Exception as e:
            logger.error(f"Error in get_by_date: {e}")
            return []

    @staticmethod
    def update(trade_date, index_name, **kwargs):
        """
        更新某日某指数的记录。
        :param kwargs: 可更新字段：future_symbol, future_close, spot_close, basis, basis_rate_pct, source
        """
        try:
            record = db_session.query(FuturesBasisWide).filter(
                and_(
                    FuturesBasisWide.trade_date == trade_date,
                    FuturesBasisWide.index_name == index_name
                )
            ).first()

            if not record:
                return None

            for key, value in kwargs.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            db_session.commit()
            return record.to_dict()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in update: {e}")
            db_session.rollback()
            return None

    @staticmethod
    def delete_by_date_and_index(trade_date, index_name):
        """删除某日某指数记录"""
        try:
            record = db_session.query(FuturesBasisWide).filter(
                and_(
                    FuturesBasisWide.trade_date == trade_date,
                    FuturesBasisWide.index_name == index_name
                )
            ).first()
            if record:
                db_session.delete(record)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in delete: {e}")
            db_session.rollback()
            return False
