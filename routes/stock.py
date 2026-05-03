"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
from models import Stock, db
from flask import request, jsonify, Blueprint
from config import cache_setting
from app import api_prefix, cache
from service import StockService, FactorValueService
from service import JobService, MarketFearGreedService, ResearchReportService, CompanyProfileService
from common_api import get_date_by_years, datajiji
from utils.common import get_today, dict_to_markdown_recursive

stock_bp = Blueprint('stock', __name__)


@stock_bp.route(f'{api_prefix}/stock/dcf_research_report/<string:stock_code>', methods=['GET'])
def get_dcf_research_report(stock_code):
    """
    获取个股研报数据
    """
    report = ResearchReportService.get_by_code(stock_code=stock_code, report_type=1)
    return jsonify(report)


@stock_bp.route(f'{api_prefix}/stock/tech_analysis_report/<string:stock_code>', methods=['GET'])
def get_tech_analysis_report(stock_code):
    """
    获取个股研报数据
    """
    report = ResearchReportService.get_by_code(stock_code=stock_code, report_type=2)
    # report['content_json'] = json.loads(report.get('content_text'))
    # del report['content_text']
    return jsonify(report)


@stock_bp.route(f'{api_prefix}/stocks/<string:symbol>', methods=['PUT'])
def update_stock(symbol):
    """
    更新股票信息
    """

    data = request.get_json(silent=True)

    # 1. 检查请求体是否为有效 JSON
    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 400
    if data is None:
        return jsonify({'message': 'Invalid JSON'}), 400

    # 2. 校验 symbol（可选：格式校验，如长度、字符集）
    if not symbol or not isinstance(symbol, str):
        return jsonify({'message': 'Invalid symbol'}), 400

    # 获取个股信息
    stock = StockService.get_stock_by_symbol(symbol)

    if not stock:
        return jsonify({'message': 'No stock found!'}), 404

    if stock.get('securities_type') != 'stock':
        return jsonify({'code': 0, 'message': '该代码不属于股票类型'}), 404

    data['symbol'] = symbol
    StockService.upsert_stock(data)
    is_update_history = request.args.get('is_update_history', type=int, default=1)

    # 提交个股分析任务
    if is_update_history:
        _stock_reanalysis(symbol, sync_history=True, send_notification=True)

    return jsonify({'code': 0, 'message': 'Stock updated successfully!'})


# @lru_redis_cache()
def get_main_force_behavior_phase(code):
    greed_data = MarketFearGreedService.get_latest_by_index(index_code=code)
    if greed_data is None:
        greed_data = {
            "fear_greed": 0
        }
    # 获取 main_force_behavior_phase
    main_force_behavior_phase = FactorValueService.get_latest_factor_value(ticker=code,
                                                                           factor_name='main_force_behavior_phase')
    return greed_data, main_force_behavior_phase


@stock_bp.route(f'{api_prefix}/stocks_monitored', methods=['GET'])
@cache.cached(timeout=cache_setting.get('stock_list'), query_string=True)
def get_stocks_monitored():
    """
    获取个股监控列表
    """
    page = request.args.get('page', default=1, type=int)
    market = request.args.get('market', default='cn', type=str)
    page_size = request.args.get('page_size', default=300, type=int)
    stocks = StockService.get_monitoring_stock_pool(per_page=page_size, market=market)

    for stock in stocks:
        # 获取恐惧贪婪数据
        stock['greed_data'], stock['main_force_behavior_phase'] = get_main_force_behavior_phase(stock['symbol'])
        stock['52week_low'] = FactorValueService.get_latest_factor_value(ticker=stock['symbol'], factor_name='52week_low')
        stock['52week_high'] = FactorValueService.get_latest_factor_value(ticker=stock['symbol'], factor_name='52week_high')

        del stock['llm_analysis']

    return jsonify(stocks)


@stock_bp.route(f'{api_prefix}/etfs', methods=['GET'])
def get_etfs():
    """
    获取ETF监控列表
    """

    page = request.args.get('page', default=1, type=int)
    market = request.args.get('market', default='cn', type=str)
    page_size = request.args.get('page_size', default=300, type=int)
    stocks = StockService.get_etfs(per_page=page_size, market=market)

    return jsonify(stocks)


@stock_bp.route(f'{api_prefix}/stock/greed_data/<string:stock_code>', methods=['GET'])
def get_stocks_greed_data(stock_code):
    """
    获取个股恐惧贪婪数据
    """
    greed_data = MarketFearGreedService.get_by_index_all(index_code=stock_code)
    return jsonify(greed_data)


@stock_bp.route(f'/{api_prefix}/stocks', methods=['POST'])
def add_stock():
    data = request.get_json()
    new_stock = Stock(**data)
    db.session.add(new_stock)
    db.session.commit()
    return jsonify({'message': 'Stock added successfully!'}), 201


@stock_bp.route(f'{api_prefix}/stocks/<string:symbol>', methods=['GET'])
def get_stock(symbol):
    stock = StockService.get_stock_by_symbol(symbol)
    if stock['llm_analysis'] != "":
        stock['llm_analysis'] = json.loads(stock['llm_analysis'])
        stock['llm_analysis_markdown'] = dict_to_markdown_recursive(stock['llm_analysis'])
    stock['tech_indicator'] = {
        '52week_low': FactorValueService.get_latest_factor_value(ticker=symbol, factor_name='52week_low'),
        '52week_high': FactorValueService.get_latest_factor_value(ticker=symbol, factor_name='52week_high'),
    }
    return jsonify(stock)


@stock_bp.route('/api/v1/stock_history_db/<string:stock_code>', methods=['GET'])
@cache.cached(timeout=cache_setting.get('stock_history'), query_string=True)
def get_stock_history_db(stock_code):

    # 获取查询参数
    start_date = request.args.get('start_date', default=get_date_by_years(years=-3))
    end_date = request.args.get('end_date', default=get_today())
    securities_data = datajiji.get_stock_history(stock_code, start_date, end_date)

    # 将DataFrame转换为字典列表
    securities_data_dict = securities_data.to_dict(orient='records')

    return jsonify(securities_data_dict)


@stock_bp.route(f'{api_prefix}/stock/re_analysis/<string:symbol>', methods=['PUT'])
def stock_re_analysis(symbol):
    _stock_reanalysis(symbol)
    return jsonify({'code': 0, 'message': 'Stock updated successfully!'})


@stock_bp.route(f'{api_prefix}/stock/re_analysis_dcf/<string:symbol>', methods=['PUT'])
def stock_re_analysis_dcf(symbol):
    if StockService.get_stock_by_symbol(symbol) is None:
        return jsonify({'code': -1, 'message': 'Stock not found!'})

    # 提交任务
    JobService.send_job({
        'job_func': 'job_stock_dcf_model_analysis',
        'job_args': {
            '_stock_code': symbol,
            'send_notification': False
        }
    })

    return jsonify({'code': 0, 'message': 'Stock updated successfully!'})


@stock_bp.route(f'{api_prefix}/stocks/get_stock_profile/<string:symbol>', methods=['GET'])
def get_stock_profile(symbol):
    profile = CompanyProfileService.get_by_stock_code(stock_code=symbol)
    profile = profile.to_dict()
    beta = FactorValueService.get_latest_factor_value(ticker=symbol, factor_name='beta')
    profile['beta'] = beta
    return jsonify(profile)


def _stock_reanalysis(symbol, sync_history=False, send_notification=False):
    stock = StockService.get_stock_by_symbol(symbol)

    if stock is None:
        return

    # job_stock_analysis(stock_code, sync_history=True, send_notification=False)

    # 重新计算恐惧贪婪指标
    JobService.send_job({
        'job_func': 'job_stock_analysis',
        'job_args': {
            'stock_code': symbol,
            'sync_history': sync_history,
            'send_notification': send_notification
        }
    })
