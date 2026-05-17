"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
from utils.redis_obj import redis_obj
from flask import jsonify, Blueprint, request
from app import json_resp

quant_bp = Blueprint('quant', __name__)

@quant_bp.route(f'/api/v1/quant/stock/get_dcf_report_snap', methods=['GET'])
def get_dcf_report_snap():
    """
    获取个股研报数据
    """
    report = redis_obj.get('dcf_valuation_report')
    report = json.loads(report)
    return json_resp(report)