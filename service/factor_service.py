"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import pandas as pd
# from fontTools.misc.cython import returns

from models import FactorValue
# from flask import current_app
from models.database import db_session
from models.database import db_session as session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import case, and_, func, Date, Float
from utils.common import logger
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from utils.common import get_today
from service.factor_desc import ALL_FACTOR_FIELDS, technical_fields

class FactorSelectorService:

    @staticmethod
    def get_tech_factors_for_stock(ticker: str, asof_date) -> Dict[str, Optional[float]]:
        """
        获取指定股票在指定日期的最新全部因子数据。

        Args:
            ticker (str): 股票代码，如 '600519.SH'
            asof_date (date): 截止日期

        Returns:
            dict: {factor_name: value, ...}。如果股票或因子不存在，value为None。
        """

        # 2. 第二步：复用原有的“最新值”逻辑，但针对特定股票和所有因子
        # 使用窗口函数获取每个因子的最新值（截至 asof_date）
        try:
            latest_factor_values = (
                session.query(
                    FactorValue.factor_name,
                    FactorValue.value,
                    func.row_number().over(
                        partition_by=FactorValue.factor_name,  # 注意：这里只按因子名分区，因为我们只查一只股票
                        order_by=FactorValue.trade_date.desc()
                    ).label('rn')
                )
                .filter(
                    FactorValue.factor_name.in_(technical_fields),
                    FactorValue.ticker == ticker,  # 限定股票代码
                    FactorValue.trade_date <= asof_date,
                    FactorValue.value.isnot(None)
                )
                .subquery()
            )

            # 3. 第三步：提取 rn=1 的记录，并转换为字典
            result_query = (
                session.query(
                    latest_factor_values.c.factor_name,
                    latest_factor_values.c.value.cast(Float)
                )
                .filter(latest_factor_values.c.rn == 1)
            )

            results = result_query.all()

            # 4. 第四步：格式化结果
            # 结果格式: {factor_name: value}
            factor_dict = {row[0]: float(row[1]) if row[1] is not None else None for row in results}

            return factor_dict

        except Exception as e:
            logger.error(f"Error fetching all factors for {ticker} as of {asof_date}: {e}")
            return {}

    @staticmethod
    def get_all_factors_for_stock_asof(ticker: str, asof_date: date) -> Dict[str, Optional[float]]:
        """
        获取指定股票在指定日期的最新全部因子数据。

        Args:
            ticker (str): 股票代码，如 '600519.SH'
            asof_date (date): 截止日期

        Returns:
            dict: {factor_name: value, ...}。如果股票或因子不存在，value为None。
        """

        # 2. 第二步：复用原有的“最新值”逻辑，但针对特定股票和所有因子
        # 使用窗口函数获取每个因子的最新值（截至 asof_date）
        try:
            latest_factor_values = (
                session.query(
                    FactorValue.factor_name,
                    FactorValue.value,
                    func.row_number().over(
                        partition_by=FactorValue.factor_name,  # 注意：这里只按因子名分区，因为我们只查一只股票
                        order_by=FactorValue.trade_date.desc()
                    ).label('rn')
                )
                .filter(
                    FactorValue.factor_name.in_(ALL_FACTOR_FIELDS),
                    FactorValue.ticker == ticker,  # 限定股票代码
                    FactorValue.trade_date <= asof_date,
                    FactorValue.value.isnot(None)
                )
                .subquery()
            )

            # 3. 第三步：提取 rn=1 的记录，并转换为字典
            result_query = (
                session.query(
                    latest_factor_values.c.factor_name,
                    latest_factor_values.c.value.cast(Float)
                )
                .filter(latest_factor_values.c.rn == 1)
            )

            results = result_query.all()

            # 4. 第四步：格式化结果
            # 结果格式: {factor_name: value}
            factor_dict = {row[0]: float(row[1]) if row[1] is not None else None for row in results}

            return factor_dict

        except Exception as e:
            logger.error(f"Error fetching all factors for {ticker} as of {asof_date}: {e}")
            return {}

    @staticmethod
    def select_stocks_by_factors_asof(
        asof_date: date,
        conditions: Dict[str, Dict[str, Any]],
        limit: Optional[int] = None
    ):
        """
        高效地根据多个因子条件筛选股票（截至 asof_date 的最新值）。

        Args:
            asof_date: 截止日期
            conditions: 因子条件字典，如 {'roe': {'operator': '>=', 'value': 15}, ...}
            limit: 最多返回多少只股票（可选）

        Returns:
            dict: {"selected_tickers": [...], "details": {...}}
        """
        factor_names = list(conditions.keys())
        if not factor_names:
            return {"selected_tickers": [], "details": {}}

        # 第一步：为每个 ticker 获取每个因子的最新值（截至 asof_date）
        # 使用窗口函数 + 条件聚合
        latest_factor_values = (
            session.query(
                FactorValue.ticker,
                FactorValue.factor_name,
                FactorValue.value,
                func.row_number().over(
                    partition_by=[FactorValue.ticker, FactorValue.factor_name],
                    order_by=FactorValue.trade_date.desc()
                ).label('rn')
            )
            .filter(
                FactorValue.factor_name.in_(factor_names),
                FactorValue.trade_date <= asof_date,
                FactorValue.value.isnot(None)
            )
            .subquery()
        )

        # 第二步：只取 rn = 1 的记录（即每个 ticker 每个因子的最新值）
        valid_latest = session.query(
            latest_factor_values.c.ticker,
            latest_factor_values.c.factor_name,
            latest_factor_values.c.value.cast(Float).label('value')
        ).filter(latest_factor_values.c.rn == 1).subquery()

        # 第三步：按 ticker 分组，用条件聚合提取每个因子的值，并应用 WHERE/HAVING 过滤
        group_cols = [valid_latest.c.ticker]
        select_cols = [valid_latest.c.ticker]

        # 构建每个因子的条件表达式（用于 HAVING）
        having_conditions = []

        for fname, cond in conditions.items():
            op = cond['operator']
            threshold = float(cond['value'])

            # 条件聚合：提取该因子的值
            factor_expr = func.max(
                case((valid_latest.c.factor_name == fname, valid_latest.c.value), else_=None)
            ).label(f"factor_{fname}")

            select_cols.append(factor_expr)

            # 构建 HAVING 条件
            if op == '>=':
                having_cond = factor_expr >= threshold
            elif op == '<=':
                having_cond = factor_expr <= threshold
            elif op == '>':
                having_cond = factor_expr > threshold
            elif op == '<':
                having_cond = factor_expr < threshold
            elif op == '==':
                having_cond = func.abs(factor_expr - threshold) < 1e-8
            else:
                raise ValueError(f"Unsupported operator: {op}")

            having_conditions.append(having_cond)

        # 构建主查询
        query = session.query(*select_cols) \
            .group_by(valid_latest.c.ticker) \
            .having(and_(*having_conditions))

        # 应用 limit
        if limit is not None:
            query = query.limit(limit)

        # 执行查询
        results = query.all()

        if not results:
            return {"selected_tickers": [], "details": {}}

        # 整理结果
        selected_tickers = []
        details = {}

        for row in results:
            ticker = row[0]
            selected_tickers.append(ticker)
            ticker_detail = {}
            for i, fname in enumerate(factor_names, start=1):
                val = getattr(row, f"factor_{fname}", None)
                ticker_detail[fname] = float(val) if val is not None else None
            details[ticker] = ticker_detail

        return {
            "selected_tickers": selected_tickers,
            "details": details
        }

class FactorValueService:

    @staticmethod
    def create(trade_date: date, ticker: str, factor_name: str, value: float = None, source: str = 'custom') -> Optional[FactorValue]:
        """
        创建一条因子记录。

        :param trade_date: 交易日期（date 对象）
        :param ticker: 股票代码（如 '600519.SH'）
        :param factor_name: 因子名称（如 'pe_ttm'）
        :param value: 因子值（float 或 None）
        :param source: 数据来源
        :return: 成功返回 FactorValue 实例，失败返回 None
        """
        try:
            if isinstance(trade_date, str):
                trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()

            # 将 float 转为 Decimal 以匹配 MySQL DECIMAL(18,6)
            db_value = Decimal(str(round(value, 6))) if value is not None else None

            record = FactorValue(
                trade_date=trade_date,
                ticker=str(ticker),
                factor_name=str(factor_name),
                value=db_value,
                source=source
            )
            db_session.add(record)
            db_session.commit()
            return record
        except IntegrityError as e:
            # 主键或唯一约束冲突：静默处理
            logger.debug(f"Duplicate record ignored in FactorValueService.create: "
                         f"trade_date={trade_date}, ticker={ticker}, factor_name={factor_name}. Error: {e}")
            db_session.rollback()
        except SQLAlchemyError as e:
            logger.error(f"Database error in FactorValueService.create: {e}")
            db_session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error in FactorValueService.create: {e}")
            db_session.rollback()
            return None

    @staticmethod
    def bulk_create(records: List[Dict[str, Any]]) -> Optional[int]:
        """
        批量插入因子数据（高效方式）。

        :param records: 列表，每个 dict 包含 keys: trade_date, ticker, factor_name, value, [source]
        :return: 成功插入数量，失败返回 None
        """
        try:
            # objs = []
            for r in records:
                trade_date = r['trade_date']
                if isinstance(trade_date, str):
                    trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
                elif not isinstance(trade_date, date):
                    continue  # 跳过非法日期

                value = r.get('value')
                db_value = Decimal(str(round(value, 6))) if value is not None else None

                obj = FactorValue(
                    trade_date=trade_date,
                    ticker=str(r['ticker']),
                    factor_name=str(r['factor_name']),
                    value=db_value,
                    source=r.get('source', 'custom')
                )
                # objs.append(obj)
                db_session.add(obj)

            db_session.commit()
            return len(records)
        except SQLAlchemyError as e:
            logger.error(f"Database error during bulk create factors: {e}")
            db_session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error in FactorValueService.bulk_create: {e}")
            db_session.rollback()
            return None

    @staticmethod
    def get_factor_snapshot(factor_name: str, trade_date: date, page: int = 1, page_size: int = 200) -> dict:
        """
        获取某因子在某交易日的全市场截面快照（分页）。

        :param factor_name: 因子名称
        :param trade_date: 交易日期
        :param page: 页码（从1开始）
        :param page_size: 每页数量（最大500）
        :return: 分页结果字典
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 500:
            page_size = 200

        try:
            query = db_session.query(FactorValue).filter(
                FactorValue.factor_name == factor_name,
                FactorValue.trade_date == trade_date
            )
            total = query.count()
            items = (
                query
                .order_by(FactorValue.ticker)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [item.to_dict() for item in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_more": (page * page_size) < total
            }
        except Exception as e:
            logger.error(f"Error fetching factor snapshot for {factor_name} on {trade_date}: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "has_more": False
            }

    @staticmethod
    def get_stock_factor_series(ticker: str, factor_name: str, start_date: date = None, end_date: date = None) -> List[dict]:
        """
        获取单只股票某个因子的时间序列。

        :param ticker: 股票代码
        :param factor_name: 因子名称
        :param start_date: 开始日期（可选）
        :param end_date: 结束日期（可选，默认今天）
        :return: 因子时间序列列表（按日期升序）
        """
        try:
            query = db_session.query(FactorValue).filter(
                FactorValue.ticker == ticker,
                FactorValue.factor_name == factor_name
            )
            if start_date:
                query = query.filter(FactorValue.trade_date >= start_date)
            if end_date:
                query = query.filter(FactorValue.trade_date <= end_date)

            results = query.order_by(FactorValue.trade_date).all()
            return [r.to_dict() for r in results]
        except Exception as e:
            logger.error(f"Error fetching factor series for {ticker}/{factor_name}: {e}")
            return []

    @staticmethod
    def delete_by_ticker(stock_code: str):
        """
        :param stock_code:
        :return:
        """
        try:
            deleted_count = db_session.query(FactorValue).filter(
                FactorValue.ticker == stock_code,
            ).delete(synchronize_session=False)
            db_session.commit()
            logger.info(f"Deleted {deleted_count} records for symbol: {stock_code}")
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to delete data for symbol {stock_code}: {e}")
            return False

    @staticmethod
    def delete_by_factor_and_date(factor_name: str, trade_date: date) -> bool:
        """
        删除某因子在某日的所有记录（用于重算覆盖）。
        """
        try:
            count = db_session.query(FactorValue).filter(
                FactorValue.factor_name == factor_name,
                FactorValue.trade_date == trade_date
            ).delete(synchronize_session=False)
            db_session.commit()
            logger.info(f"Deleted {count} records for factor '{factor_name}' on {trade_date}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"DB error deleting factor {factor_name} on {trade_date}: {e}")
            db_session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error in delete_by_factor_and_date: {e}")
            db_session.rollback()
            return False

    @staticmethod
    def get_latest_factor_date(factor_name: str) -> Optional[date]:
        """
        获取某因子最新计算日期（用于增量更新判断）。
        """
        try:
            latest = (
                db_session.query(FactorValue.trade_date)
                .filter(FactorValue.factor_name == factor_name)
                .order_by(FactorValue.trade_date.desc())
                .first()
            )
            return latest[0] if latest else None
        except Exception as e:
            logger.error(f"Error getting latest date for factor {factor_name}: {e}")
            return None

    @staticmethod
    def get_latest_factor_value(ticker, factor_name: str) -> Optional[date]:
        """
        获取某因子最新计算日期（用于增量更新判断）。
        """
        try:
            latest = (
                db_session.query(FactorValue.value)
                .filter(FactorValue.factor_name == factor_name, FactorValue.ticker == ticker)
                .order_by(FactorValue.trade_date.desc())
                .first()
            )
            return latest[0] if latest else None
        except Exception as e:
            logger.error(f"Error getting latest date for factor {factor_name}: {e}")
            return None

    @staticmethod
    def get_latest_trading_date(factor_name = 'cn_trading_date') -> Optional[date]:
        """
        获取最新的交易日数据
        """
        try:
            latest = (
                db_session.query(FactorValue.trade_date, FactorValue.value)
                .filter(FactorValue.factor_name == factor_name, FactorValue.trade_date <= get_today(_format='%Y-%m-%d'), FactorValue.value == '1.0')
                .order_by(FactorValue.trade_date.desc())
                .first()
            )
            return latest[0] if latest else None
        except Exception as e:
            logger.error(f"Error getting latest date for factor {factor_name}: {e}")
            return None

    @staticmethod
    def is_trading_day(factor_name = 'cn_trading_date') -> Optional[date]:
        """
        判断今天是不是交易日
        """
        return FactorValueService.get_latest_trading_date(factor_name=factor_name).strftime('%Y-%m-%d') == get_today(_format='%Y-%m-%d')

    @staticmethod
    def df_to_records(df: pd.DataFrame, factor_name: str, source: str = 'custom') -> List[Dict[str, Any]]:
        """
        将 pandas DataFrame 转换为因子记录列表（便于 bulk_create）。
        要求 df.index 为 trade_date（datetime），columns 为 ticker，值为因子值。

        示例：
            df = pd.DataFrame({
                '600519.SH': [28.1, 28.5],
                '000001.SZ': [6.2, 6.3]
            }, index=[date(2024,12,1), date(2024,12,2)])

        :param df: 因子宽表 DataFrame
        :param factor_name: 因子名称
        :param source: 数据来源
        :return: 记录列表
        """
        records = []
        for trade_date, row in df.iterrows():
            if isinstance(trade_date, pd.Timestamp):
                trade_date = trade_date.date()
            for ticker, value in row.items():
                if pd.notna(value):
                    records.append({
                        'trade_date': trade_date,
                        'ticker': str(ticker),
                        'factor_name': factor_name,
                        'value': float(value),
                        'source': source
                    })
        return records

# 使用示例
if __name__ == "__main__":

    asof_date = date(2026, 5, 1)

    # print(FactorValueService.get_latest_trading_date())

    conditions = {
        # 盈利能力（Quality）
        'roe': {'operator': '>=', 'value': 15},  # 净资产收益率 ≥ 15%
        'gross_margin': {'operator': '>=', 'value': 30},  # 毛利率 ≥ 30%

        # 成长性（Growth）
        'revenue_growth_yoy': {'operator': '>=', 'value': 10},  # 营业总收入同比增长 ≥ 10%
        'net_profit_parent_growth_yoy': {'operator': '>=', 'value': 15},  # 归母净利润同比增长 ≥ 15%

        # 财务稳健性（Safety）
        'debt_to_asset_ratio': {'operator': '<=', 'value': 60},  # 资产负债率 ≤ 60%
        'current_ratio': {'operator': '>=', 'value': 1.2},  # 流动比率 ≥ 1.2
        'ocf_to_net_profit_parent': {'operator': '>=', 'value': 0.8},  # 经营现金流/归母净利润 ≥ 0.8（盈利质量高）

        # 规模与持续性（可选）
        'operating_revenue': {'operator': '>=', 'value': 1e9},  # 营业总收入 ≥ 10亿元（排除微小公司）
    }

    result = FactorSelectorService.select_stocks_by_factors_asof(asof_date, conditions, limit=5)

    for stock in result['selected_tickers']:
        print(stock)
        print(result['details'][stock])
        print()
