"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from flask import jsonify, Blueprint
from app import api_prefix, cache
from utils.data_loader import datagigi
from service import FactorValueService
from config import cache_setting

etf_bp = Blueprint('etf', __name__)


@etf_bp.route(f'{api_prefix}/etfs', methods=['GET'])
@cache.cached(timeout=cache_setting.get('stock_history'), query_string=True)
def get_etfs():
    """
    获取ETF监控列表
    """
    etfs = datagigi.get_etf_list(market='cn')[:8]
    for etf in etfs:
        etf['52week_low'] = FactorValueService.get_latest_factor_value(
            ticker=etf['symbol'],
            factor_name='52week_low'
        )
        etf['52week_high'] = FactorValueService.get_latest_factor_value(
            ticker=etf['symbol'],
            factor_name='52week_high'
        )
        etf['composition'] = datagigi.get_etf_composition(symbol=etf['symbol'])
        etf['composition'] = etf['composition']['data']
        etf['ohlc_last'] = datagigi.get_last_tick(symbol=etf['symbol'])
        etf['ohlc_last']['chg_pct'] = (etf['ohlc_last']['lastPrice'] - etf['ohlc_last']['lastClose']) / etf['ohlc_last']['lastClose'] * 100
    return jsonify(etfs)