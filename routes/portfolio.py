"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from datetime import datetime
from flask import jsonify, Blueprint, request
from app import api_prefix, cache
from service import InvestmentPortfolioService, PortfolioAssetsService
from service import (
    DailyPnLRecordService,
    PortfolioDailySummaryService,
    PortfolioTransactionService
)
from utils.common import logger

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route(f'{api_prefix}/investment_portfolios', methods=['GET'])
# @cache.cached(timeout=360, query_string=True)
def get_investment_portfolios():
    # 获取策略列表数据
    portfolios = InvestmentPortfolioService.get_all()
    for prof in portfolios:
        # 获取持仓最新统计信息
        prof['summary'] = PortfolioDailySummaryService.get_last_by_portfolio_id(prof.get('portfolio_id'))
        if prof['summary'] is None:
            prof['summary'] = {
                'total_unrealized_pnl': 0,
                'total_assets': 0
            }
        # prof['summary_list'] = PortfolioDailySummaryService.get_all_by_portfolio_id(prof.get('portfolio_id'))
        # 获取持仓最新信息
        prof['assets'] = PortfolioAssetsService.get_all_by_portfolio_id(prof.get('portfolio_id'))
        # 删除无用字段
        del prof['llm_prompt']
        del prof['position_plan']
    return jsonify(portfolios)


@portfolio_bp.route(f'{api_prefix}/investment_portfolios_info/<string:portfolio_id>', methods=['GET'])
# @cache.cached(timeout=360, query_string=True)
def get_investment_portfolios_info(portfolio_id):
    # 获取策略详情
    prof = InvestmentPortfolioService.get_by_portfolio_id(portfolio_id)
    prof['portfolio_id'] = portfolio_id
    prof['summary'] = PortfolioDailySummaryService.get_last_by_portfolio_id(portfolio_id)
    if prof['summary'] is None:
        prof['summary'] = {
            'total_unrealized_pnl': 0,
            'total_assets': 0
        }
    prof['assets'] = PortfolioAssetsService.get_all_by_portfolio_id(portfolio_id)
    prof['daily_pnl'] = DailyPnLRecordService.get_all_by_portfolio_id(portfolio_id)
    return jsonify(prof)


@portfolio_bp.route(f'{api_prefix}/portfolio_daily_summary/<string:portfolio_id>', methods=['GET'])
# @cache.cached(timeout=360, query_string=True)
def get_portfolio_daily_summary(portfolio_id):
    # 获取策略每日统计数据
    summary_list = PortfolioDailySummaryService.get_all_by_portfolio_id(portfolio_id)
    return jsonify(summary_list)

@portfolio_bp.route(f'{api_prefix}/portfolio_transaction/<string:portfolio_id>', methods=['GET'])
def get_portfolio_transaction(portfolio_id):
    # 获取策略交易记录
    _list = PortfolioTransactionService.get_by_portfolio_id(portfolio_id)
    return jsonify(_list)

@portfolio_bp.route(f'{api_prefix}/portfolio/<string:portfolio_id>', methods=['PUT'])
def update_portfolio(portfolio_id):
    """
    更新组合信息
    """
    update_data = request.get_json(silent=True)

    # 1. 检查请求体是否为有效 JSON
    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 400
    if update_data is None:
        return jsonify({'message': 'Invalid JSON'}), 400

    # 2. 校验 symbol（可选：格式校验，如长度、字符集）
    if not portfolio_id or not isinstance(portfolio_id, str):
        return jsonify({'message': 'Invalid symbol'}), 400

    # 获取个股信息
    portfolio = InvestmentPortfolioService.get_by_portfolio_id(portfolio_id)

    if not portfolio:
        return jsonify({'message': 'No stock found!'}), 404

    # 执行更新
    InvestmentPortfolioService.update_by_portfolio_id(portfolio_id, update_data)

    return jsonify({'code': 0, 'message': 'Stock updated successfully!'})
