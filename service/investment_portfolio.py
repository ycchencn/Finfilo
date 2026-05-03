"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from sqlalchemy.exc import IntegrityError
from models import InvestmentPortfolio
from models.database import db_session
from utils.common import logger


class InvestmentPortfolioService:

    @staticmethod
    def add(portfolio_data):
        """
        @brief 添加一个新的 InvestmentPortfolio 记录

        @param portfolio_data: 包含投资组合数据的字典
        @type portfolio_data: dict

        @return: 是否成功添加记录
        @rtype: bool

        @throws: IntegrityError 如果插入违反数据库完整性约束
        @throws: Exception 如果发生其他错误

        @example:
            # 示例用法
            portfolio_data = {
                'portfolio_id': '12345678-1234-5678-1234-567812345678',
                'name': 'My Portfolio',
                'total_position_pct': 80.00,
                'base_currency': 'USD'
            }
            success = InvestmentPortfolioService.add(portfolio_data)
            print(success)
        """
        try:
            portfolio = InvestmentPortfolio(**portfolio_data)
            db_session.add(portfolio)
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
    def batch_add(portfolios_data):
        """
        @brief 批量添加多个 InvestmentPortfolio 记录

        @param portfolios_data: 包含多个投资组合数据的列表
        @type portfolios_data: list

        @return: 是否成功批量添加记录
        @rtype: bool

        @throws: IntegrityError 如果插入违反数据库完整性约束
        @throws: Exception 如果发生其他错误

        @example:
            # 示例用法
            portfolios_data = [
                {
                    'portfolio_id': '12345678-1234-5678-1234-567812345678',
                    'name': 'My Portfolio 1',
                    'total_position_pct': 80.00,
                    'base_currency': 'USD'
                },
                {
                    'portfolio_id': '87654321-1234-5678-1234-876543218765',
                    'name': 'My Portfolio 2',
                    'total_position_pct': 90.00,
                    'base_currency': 'EUR'
                }
            ]
            success = InvestmentPortfolioService.batch_add(portfolios_data)
            print(success)
        """
        try:
            for portfolio_data in portfolios_data:
                portfolio = InvestmentPortfolio(**portfolio_data)
                db_session.add(portfolio)
            db_session.commit()
            return True
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Batch insertion failed: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred: {e}")
        return False

    @staticmethod
    def get_by_portfolio_id(portfolio_id):
        """
        @brief 根据 portfolio_id 获取 InvestmentPortfolio 记录

        @param portfolio_id: 投资组合唯一ID
        @type portfolio_id: str

        @return: 投资组合记录的字典表示，如果没有找到则返回 None
        @rtype: dict or None

        @throws: Exception 如果发生其他错误

        @example:
            # 示例用法
            portfolio = InvestmentPortfolioService.get_by_portfolio_id('12345678-1234-5678-1234-567812345678')
            print(portfolio)
        """
        try:
            portfolio = db_session.query(InvestmentPortfolio).filter_by(portfolio_id=portfolio_id).first()
            if portfolio:
                return portfolio.to_dict()
            else:
                return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        return None

    @staticmethod
    def update_by_portfolio_id(portfolio_id, update_data):
        """
        @brief 根据 portfolio_id 更新 InvestmentPortfolio 记录

        @param portfolio_id: 投资组合唯一ID
        @type portfolio_id: str
        @param update_data: 包含更新数据的字典
        @type update_data: dict

        @return: 是否成功更新记录
        @rtype: bool

        @throws: IntegrityError 如果更新违反数据库完整性约束
        @throws: Exception 如果发生其他错误

        @example:
            # 示例用法
            update_data = {
                'name': 'Updated Portfolio Name',
                'total_position_pct': 85.00
            }
            success = InvestmentPortfolioService.update_by_portfolio_id('12345678-1234-5678-1234-567812345678', update_data)
            print(success)
        """
        try:
            portfolio = db_session.query(InvestmentPortfolio).filter_by(portfolio_id=portfolio_id).first()
            if portfolio:
                for key, value in update_data.items():
                    setattr(portfolio, key, value)
                db_session.commit()
                return True
            else:
                logger.warning(f"InvestmentPortfolio with portfolio_id {portfolio_id} not found.")
        except IntegrityError as e:
            db_session.rollback()
            logger.error(f"Update failed: {e}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred: {e}")
        return False

    @staticmethod
    def delete_by_portfolio_id(portfolio_id):
        """
        @brief 根据 portfolio_id 删除 InvestmentPortfolio 记录

        @param portfolio_id: 投资组合唯一ID
        @type portfolio_id: str

        @return: 是否成功删除记录
        @rtype: bool

        @throws: Exception 如果发生其他错误

        @example:
            # 示例用法
            success = InvestmentPortfolioService.delete_by_portfolio_id('12345678-1234-5678-1234-567812345678')
            print(success)
        """
        try:
            portfolio = db_session.query(InvestmentPortfolio).filter_by(portfolio_id=portfolio_id).first()
            if portfolio:
                db_session.delete(portfolio)
                db_session.commit()
                return True
            else:
                logger.warning(f"InvestmentPortfolio with portfolio_id {portfolio_id} not found.")
        except Exception as e:
            db_session.rollback()
            logger.error(f"An error occurred: {e}")
        return False

    @staticmethod
    def get_all(enable=1):
        """
        获取所有投资组合
        """
        stocks = db_session.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.enable == enable
        ).all()
        return [stock.to_dict() for stock in stocks]
