"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
from utils.redis_obj import redis_obj
from flask import Blueprint
from app import json_resp
from job.dump_stocks_dcf import export_dcf_to_excel

quant_bp = Blueprint('quant', __name__)


@quant_bp.route(f'/api/v1/quant/stock/get_dcf_report_snap', methods=['GET'])
def get_dcf_report_snap():
    """
    获取个股研报数据
    """
    report = redis_obj.get('dcf_valuation_report')
    if report is None:
        export_dcf_to_excel('./dcf_valuation_report.xlsx', sort_by='中性空间', ascending=False)
        return json_resp({})
    report = json.loads(report)
    return json_resp(report)
