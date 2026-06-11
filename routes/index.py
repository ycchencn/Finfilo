"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from flask import jsonify, Blueprint
from app import api_prefix
from utils.data_loader import datagigi
from app import cache

index_bp = Blueprint('index', __name__)


@index_bp.route(f'{api_prefix}/index/last_tick', methods=['GET'])
@cache.cached(timeout=3600)
def get_index_last():
    """
    获取指数最新行情
    """
    index_codes = ['000001', '399001', '399006', '000688', '000692']
    index_ticks = []
    for code in index_codes:
        res = datagigi.get_last_tick(code, tick_type='index', market='cn')
        res['index_code'] = code
        index_ticks.append(res)
    return jsonify(index_ticks)