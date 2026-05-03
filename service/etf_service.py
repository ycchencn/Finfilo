"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from sqlalchemy.exc import IntegrityError
from models import EtfInfo, EtfComponent
from models.database import db_session
from utils.common import logger
from typing import Dict, Any, List, Optional


class EtfInfoService:

    @staticmethod
    def add(etf_data: Dict[str, Any]) -> bool:
        """
        @brief 添加一条 ETF 基本信息记录

        @param etf_data: 包含 ETF 信息的字典，需包含 etf_code 等字段
        @type etf_data: dict

        @return: 是否成功添加
        @rtype: bool

        @throws: IntegrityError 如果 ETF 代码已存在
        @throws: Exception 其他数据库错误
        """
        try:
            etf = EtfInfo(**etf_data)
            db_session.add(etf)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Insertion failed due to integrity constraint (duplicate etf_code?): {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred during ETF info insertion: {e}")
        return False

    @staticmethod
    def batch_add(etfs_data: List[Dict[str, Any]]) -> bool:
        """
        @brief 批量添加多条 ETF 基本信息记录

        @param etfs_data: 多条 ETF 记录的列表
        @type etfs_data: list of dict

        @return: 是否全部成功添加
        @rtype: bool
        """
        try:
            for data in etfs_data:
                etf = EtfInfo(**data)
                db_session.add(etf)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Batch insertion of ETF info failed due to integrity constraint: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred during batch ETF info insertion: {e}")
        return False

    @staticmethod
    def get_by_code(etf_code: str) -> Optional[Dict[str, Any]]:
        """
        @brief 根据 ETF 代码获取 ETF 信息

        @param etf_code: ETF 代码，如 '510500'
        @return: ETF 信息字典或 None
        """
        try:
            etf = db_session.query(EtfInfo).filter_by(etf_code=etf_code).first()
            return etf.to_dict() if etf else None
        except Exception as e:
            logger.error(f"Failed to fetch ETF info by code={etf_code}: {e}")
        return None

    @staticmethod
    def get_all_by_exchange_and_date(exchange: str, trading_day: str) -> List[Dict[str, Any]]:
        """
        @brief 获取某交易所某交易日的所有 ETF 清单

        @param exchange: 交易所代码，如 'SH' 或 'SZ'
        @param trading_day: 交易日期（'YYYY-MM-DD'）
        @return: ETF 信息列表
        """
        try:
            etfs = db_session.query(EtfInfo).filter_by(
                etf_exch_id=exchange,
                trading_day=trading_day
            ).all()
            return [e.to_dict() for e in etfs]
        except Exception as e:
            logger.error(f"Failed to fetch ETFs for exchange={exchange} on date={trading_day}: {e}")
        return []    @staticmethod

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        @brief 获取某交易所某交易日的所有 ETF 清单

        @param exchange: 交易所代码，如 'SH' 或 'SZ'
        @param trading_day: 交易日期（'YYYY-MM-DD'）
        @return: ETF 信息列表
        """
        try:
            etfs = db_session.query(EtfInfo).filter_by().all()
            return [e.to_dict() for e in etfs]
        except Exception as e:
            logger.error(f"Failed to fetch ETFs: {e}")
        return []

    @staticmethod
    def update_by_code(etf_code: str, update_data: Dict[str, Any]) -> bool:
        """
        @brief 根据 ETF 代码更新基本信息

        @param etf_code: ETF 代码
        @param update_data: 要更新的字段字典
        @return: 是否成功更新
        """
        try:
            etf = db_session.query(EtfInfo).filter_by(etf_code=etf_code).first()
            if not etf:
                logger.warning(f"ETF not found for update: {etf_code}")
                return False

            for key, value in update_data.items():
                if hasattr(etf, key):
                    setattr(etf, key, value)
                else:
                    logger.warning(f"Ignoring unknown field in ETF update: {key}")
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"ETF update failed due to integrity constraint: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred during ETF update: {e}")
        return False

    @staticmethod
    def delete_by_code(etf_code: str) -> bool:
        """
        @brief 删除指定 ETF 及其所有成分股（因外键 CASCADE）

        @param etf_code: ETF 代码
        @return: 是否成功删除
        """
        try:
            etf = db_session.query(EtfInfo).filter_by(etf_code=etf_code).first()
            if not etf:
                logger.warning(f"ETF not found for deletion: {etf_code}")
                return False
            db_session.delete(etf)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to delete ETF {etf_code}: {e}")
        return False


class EtfComponentService:

    @staticmethod
    def add(component_data: Dict[str, Any]) -> bool:
        """
        @brief 添加一条 ETF 成分股记录

        @param component_data: 包含成分股信息的字典，必须含 etf_code 和 component_code
        @return: 是否成功添加
        """
        try:
            comp = EtfComponent(**component_data)
            db_session.add(comp)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Insertion failed due to duplicate component or missing ETF: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred during component insertion: {e}")
        return False

    @staticmethod
    def batch_add(components_data: List[Dict[str, Any]]) -> bool:
        """
        @brief 批量添加 ETF 成分股记录

        @param components_data: 成分股记录列表
        @return: 是否全部成功添加
        """
        try:
            for data in components_data:
                comp = EtfComponent(**data)
                db_session.add(comp)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Batch component insertion failed: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred during batch component insertion: {e}")
        return False

    @staticmethod
    def get_by_etf_code(etf_code: str) -> List[Dict[str, Any]]:
        """
        @brief 获取某 ETF 的所有成分股

        @param etf_code: ETF 代码
        @return: 成分股列表（按 component_code 排序）
        """
        try:
            components = db_session.query(EtfComponent)\
                .filter_by(etf_code=etf_code)\
                .order_by(EtfComponent.component_code)\
                .all()
            return [c.to_dict() for c in components]
        except Exception as e:
            logger.error(f"Failed to fetch components for ETF {etf_code}: {e}")
        return []

    @staticmethod
    def get_etfs_by_stock_code(stock_code: str) -> List[Dict[str, Any]]:
        """
        @brief 查询包含某股票的所有 ETF（反向查询）

        @param stock_code: 股票代码，如 '002568.SZ'
        @return: ETF 信息列表（仅基本信息）
        """
        try:
            # 先查出所有包含该股票的 ETF 代码
            etf_codes = db_session.query(EtfComponent.etf_code)\
                .filter_by(component_code=stock_code)\
                .distinct()\
                .all()
            etf_codes = [row[0] for row in etf_codes]

            if not etf_codes:
                return []

            etfs = db_session.query(EtfInfo)\
                .filter(EtfInfo.etf_code.in_(etf_codes))\
                .all()
            return [e.to_dict() for e in etfs]
        except Exception as e:
            logger.error(f"Failed to find ETFs containing stock {stock_code}: {e}")
        return []

    @staticmethod
    def delete_all_by_etf_code(etf_code: str) -> bool:
        """
        @brief 删除某 ETF 的所有成分股（通常在重建篮子前调用）

        @param etf_code: ETF 代码
        @return: 是否删除成功
        """
        try:
            deleted_count = db_session.query(EtfComponent)\
                .filter_by(etf_code=etf_code)\
                .delete(synchronize_session=False)
            db_session.commit()
            logger.info(f"Deleted {deleted_count} components for ETF {etf_code}")
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to delete components for ETF {etf_code}: {e}")
        return False

    @staticmethod
    def replace_components(etf_code: str, new_components: List[Dict[str, Any]]) -> bool:
        """
        @brief 替换某 ETF 的全部成分股（先删后插），用于每日篮子更新

        @param etf_code: ETF 代码
        @param new_components: 新的成分股列表
        @return: 是否成功替换
        """
        try:
            # Step 1: 删除旧成分
            db_session.query(EtfComponent).filter_by(etf_code=etf_code).delete(synchronize_session=False)
            # Step 2: 插入新成分
            for comp in new_components:
                comp['etf_code'] = etf_code  # 确保关联
                db_session.add(EtfComponent(**comp))
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to replace components for ETF {etf_code}: {e}")
        return False
