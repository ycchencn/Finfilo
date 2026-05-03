"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils.common import logger
from models import CompanyProfile  # 请确保导入路径正确
from models.database import db_session  # 请确保导入你的数据库 session


class CompanyProfileService:
    """
    上市公司档案数据的服务层，封装了对 CompanyProfile 表的业务逻辑。
    """

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[CompanyProfile]:
        """
        创建一条上市公司档案记录。
        """
        try:
            # 数据清洗：确保关键字段存在，防止 KeyError
            required_fields = ['stock_code', 'company_name']
            for field in required_fields:
                if field not in data or not data[field]:
                    logger.error(f"缺少关键字段 {field}，数据: {data}")
                    return None

            # 检查股票代码是否已存在
            existing = CompanyProfileService.get_by_stock_code(data['stock_code'])
            if existing:
                logger.warning(f"股票代码 {data['stock_code']} 已存在，执行更新操作或跳过。")
                # 如果你想更新已存在的数据，可以调用 update 方法
                # CompanyProfileService.update(data['stock_code'], data)
                return existing

            # 构造对象 (SQLAlchemy 会自动忽略 Model 中未定义的多余字段)
            record = CompanyProfile(**data)
            db_session.add(record)
            db_session.commit()
            # logger.info(f"成功插入公司档案: {record.company_name} ({record.stock_code})")
            return record
        except Exception as e:
            db_session.rollback()
            logger.error(f"插入公司档案失败: {e}, 数据: {data}")
            return None

    @staticmethod
    def bulk_create(records: List[Dict[str, Any]]) -> int:
        """
        批量插入上市公司档案数据（高效方式）。

        Args:
            records: 字典列表，每个字典代表一条记录。

        Returns:
            成功插入的数量。
        """
        success_count = 0
        try:
            for data in records:
                # 简单的去重检查和数据清洗
                if not data.get('stock_code'):
                    continue

                # 检查是否已存在
                if db_session.query(CompanyProfile).filter_by(stock_code=data['stock_code']).first():
                    logger.debug(f"跳过已存在的股票代码: {data['stock_code']}")
                    continue

                # 构造对象并添加（使用 add 而非 add_all 以便在出错时记录位置）
                obj = CompanyProfile(**data)
                db_session.add(obj)
                success_count += 1

            db_session.commit()
            logger.info(f"批量插入完成，成功插入 {success_count} 条记录。")
            return success_count
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"数据库错误 (Bulk Create): {e}")
            return success_count  # 返回目前已处理成功的数量，或者直接返回 0
        except Exception as e:
            db_session.rollback()
            logger.error(f"未知错误 (Bulk Create): {e}")
            return success_count

    @staticmethod
    def get_by_stock_code(stock_code: str) -> Optional[CompanyProfile]:
        """
        根据股票代码查询公司档案。

        Args:
            stock_code: 股票代码，如 '688599'

        Returns:
            CompanyProfile 实例或 None。
        """
        try:
            return db_session.query(CompanyProfile).filter_by(stock_code=stock_code).first()
        except Exception as e:
            logger.error(f"查询错误 (Get by stock_code): {e}")
            return None

    @staticmethod
    def get_all_paginated(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        分页获取所有公司档案（通常用于管理后台或全量导出）。

        Args:
            page: 页码 (从1开始)
            page_size: 每页数量

        Returns:
            包含 items, total, page, page_size 的字典。
        """
        try:
            query = db_session.query(CompanyProfile)
            total = query.count()
            items = (
                query
                .order_by(CompanyProfile.stock_code)  # 按股票代码排序
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [item.to_dict() for item in items],  # 假设 Model 有 to_dict 方法
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_more": (page * page_size) < total
            }
        except Exception as e:
            logger.error(f"分页查询错误: {e}")
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "has_more": False}

    @staticmethod
    def update(stock_code: str, update_data: Dict[str, Any]) -> bool:
        """
        更新公司档案信息。

        Args:
            stock_code: 股票代码
            update_data: 要更新的字段字典

        Returns:
            是否更新成功。
        """
        try:
            record = db_session.query(CompanyProfile).filter_by(stock_code=stock_code).first()
            if not record:
                logger.warning(f"更新失败，未找到股票代码: {stock_code}")
                return False

            # 动态更新字段
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
                else:
                    logger.debug(f"字段 {key} 不存在于 CompanyProfile 模型中，跳过更新。")

            # SQLAlchemy 会自动检测更改，显式标记为已更改（可选）
            db_session.add(record)
            db_session.commit()
            logger.info(f"成功更新公司档案: {stock_code}")
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"数据库错误 (Update): {e}")
            return False
        except Exception as e:
            db_session.rollback()
            logger.error(f"未知错误 (Update): {e}")
            return False

    @staticmethod
    def delete_by_stock_code(stock_code: str) -> bool:
        """
        根据股票代码删除记录。

        Args:
            stock_code: 股票代码

        Returns:
            是否删除成功。
        """
        try:
            count = db_session.query(CompanyProfile).filter_by(stock_code=stock_code).delete()
            db_session.commit()
            logger.info(f"删除了 {count} 条关于 {stock_code} 的记录")
            return count > 0
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"数据库错误 (Delete): {e}")
            return False
        except Exception as e:
            db_session.rollback()
            logger.error(f"未知错误 (Delete): {e}")
            return False
