"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from datetime import datetime
from flask import jsonify, Blueprint, request
from app import api_prefix, cache
from service import MarketNewsService
from service.etf_service import EtfInfoService, EtfComponentService
from utils.common import logger
from job.job_news_feed_analysis import search_digest_keyword

market_bp = Blueprint('market', __name__)


@market_bp.route(f'{api_prefix}/market/news', methods=['GET'])
@cache.cached(timeout=60 * 5, query_string=True)
def get_news():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=20, type=int)
    news = MarketNewsService.get_by_time_range(limit=page_size)
    return jsonify(news)


@market_bp.route(f'{api_prefix}/market/search_news', methods=['GET'])
def search_news():
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', type=str, default='')
        stock_code = request.args.get('stock_code', type=str)
        start_time_str = request.args.get('start_time', type=str)
        end_time_str = request.args.get('end_time', type=str)
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=20, type=int)

        # 解析时间（ISO 格式）
        start_time = None
        end_time = None
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

        # 调用服务层搜索
        es_res = search_digest_keyword(keyword, top_k=page_size, sort_field="news_time.keyword", sort_order="desc")

        result = {
            "items": es_res['hits'],
            "total": es_res['total'],
            "page": page,
            "page_size": page_size,
            "has_more": False
        }
        # result = MarketNewsService.search(
        #     keyword=keyword,
        #     stock_code=stock_code,
        #     start_time=start_time,
        #     end_time=end_time,
        #     page=page,
        #     page_size=page_size
        # )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Unexpected error in search_news endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


def make_response_json(data=None, msg="success", code=200):
    """
    统一返回格式辅助函数
    """
    return jsonify({
        'code': code,
        'msg': msg,
        'data': data
    })


@market_bp.route(f'{api_prefix}/etf/<string:etf_code>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_etf_info(etf_code):
    """
    获取单只 ETF 的基本信息

    Path Param:
        etf_code (str): ETF 代码，如 '510500'

    Query Params:
        with_components (bool): 是否同时返回成分股，默认 False

    Returns:
        {
            "code": 200,
            "msg": "success",
            "data": { ... }
        }
    """
    try:
        with_components = request.args.get('with_components', 'false').lower() == 'true'

        etf_info = EtfInfoService.get_by_code(etf_code)
        if not etf_info:
            return make_response_json(msg=f"ETF {etf_code} not found", code=404)

        result = etf_info
        if with_components:
            components = EtfComponentService.get_by_etf_code(etf_code)
            result['components'] = components

        return make_response_json(data=result)
    except Exception as e:
        logger.error(f"Error fetching ETF info for {etf_code}: {e}")
        return make_response_json(msg=str(e), code=500)


@market_bp.route(f'{api_prefix}/etf/<string:etf_code>/components', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_etf_components(etf_code):
    """
    获取某 ETF 的所有成分股

    Path Param:
        etf_code (str): ETF 代码

    Returns:
        {
            "code": 200,
            "msg": "success",
            "data": [ {...}, {...} ]
        }
    """
    try:
        components = EtfComponentService.get_by_etf_code(etf_code)
        if not components:
            # 不报错，可能 ETF 无成分或不存在
            pass
        return make_response_json(data=components)
    except Exception as e:
        logger.error(f"Error fetching components for ETF {etf_code}: {e}")
        return make_response_json(msg=str(e), code=500)


@market_bp.route(f'{api_prefix}/etf/containing/<string:stock_code>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_etfs_containing_stock(stock_code):
    """
    查询包含某股票的所有 ETF（反向查询）

    Path Param:
        stock_code (str): 股票代码，如 '002568.SZ'

    Returns:
        {
            "code": 200,
            "msg": "success",
            "data": [ {...}, {...} ]
        }
    """
    try:
        etfs = EtfComponentService.get_etfs_by_stock_code(stock_code)
        return make_response_json(data=etfs)
    except Exception as e:
        logger.error(f"Error finding ETFs containing stock {stock_code}: {e}")
        return make_response_json(msg=str(e), code=500)
