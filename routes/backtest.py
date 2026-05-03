"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from service import BacktestTaskService, StockService
from sqlalchemy import desc
from models import BacktestTask
from flask import jsonify, Blueprint, request
from app import api_prefix, cache

backtest_bp = Blueprint('backtest', __name__)


@backtest_bp.route(f'{api_prefix}/backtest_tasks', methods=['GET'])
@cache.cached(timeout=300)
def get_backtest_tasks():
    tasks = BacktestTask.query.where(BacktestTask.finished == 1).order_by(desc(BacktestTask.id)).limit(1500)
    return jsonify([task.to_dict() for task in tasks])


@backtest_bp.route(f'{api_prefix}/backtest_tasks', methods=['POST'])
def create_backtest_tasks():
    return jsonify({})


@backtest_bp.route(f'{api_prefix}/backtest_signals', methods=['GET'])
@cache.cached(timeout=360, query_string=True)
def get_backtest_signals():
    market = request.args.get('market', 'stock')
    signals = BacktestTaskService.get_signals(market, day_delta=7)
    for signal in signals:
        signal['stock_info'] = StockService.get_stock_by_symbol(signal['stock_code'])
    return jsonify(signals)
