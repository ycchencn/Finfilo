"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
from staffs import get_staff
from utils.data_loader import datajiji
from utils.common import logger, send_feishu_markdown_message, dict_to_markdown_recursive, get_now
from utils.common import get_today, get_date_by_n
from service import StockService, FactorValueService, MarketNewsService
from service import JobService, CompanyProfileService, ResearchReportService
from service.log_service import LogService
from datetime import date, datetime
from pathlib import Path
from string import Template

# 获取当前 Python 文件所在目录
CURRENT_DIR = Path(__file__).parent

prompt_quant_decision2 = """
'你现在是一名金融分析师，你对股票市场、金融市场、投资策略和财务规划有深厚的理解。'
'你能基于用户的基础数据给出股票投资决策帮助，请在这个角色下为我解答以下问题。'
'请以JSON格式输出'
"""

prompt_template = Path(CURRENT_DIR / './prompt_stock_analysis.md').read_text(encoding='utf-8')

# 定义映射字典：将中文阶段映射为数字
PHASE_MAPPING = {
    "吸筹阶段": 1,
    "洗盘阶段": 2,
    "拉升阶段": 3,
    "出货阶段(初期)": 5,
    "出货阶段 (初期)": 5,
    "出货阶段(末期)": 6,
    "出货阶段 (末期)": 6
}

def job_market_digging_daily(override=False):

    stocks = StockService.search_stocks(securities_type='stock', monitoring=1, per_page=10000)

    # 循环对个股进行每日挖掘
    for stock in stocks:

        last_analysis_date_str = stock.get('last_llm_analysis')

        # 日期为None，默认触发
        if last_analysis_date_str is None or last_analysis_date_str == '':
            # 发送分析任务到MQ
            send_job(_stock_code=stock['symbol'])
            continue

        """
        2026-01-06 20:59:28
        """

        # 解析字符串为 datetime 对象
        try:
            last_analysis_dt = datetime.strptime(last_analysis_date_str, "%Y-%m-%d %H:%M:%S")
            last_analysis_date = last_analysis_dt.date()  # 转为 date 对象，只保留日期
        except ValueError:
            # 解析失败，也触发分析（防止脏数据卡住）
            send_job(_stock_code=stock['symbol'])
            continue

        # 分析间隔
        llm_analysis_interval = stock.get('llm_analysis_interval')

        days_diff = (date.today() - last_analysis_date).days

        # 距上一次分析还有N天，跳过
        if days_diff <= llm_analysis_interval and override is False:
            continue

        # 发送分析任务到MQ
        send_job(_stock_code=stock['symbol'])

def get_stock_detail(_stock_code):
    stock_detail = CompanyProfileService.get_by_stock_code(stock_code=_stock_code)
    return stock_detail

def job_market_digging(_stock_code, sync_history=False, send_notification=False):

    staff = get_staff(llm_base='deepseek')
    # staff.set_model(model='qwen3.6-plus')
    staff.set_response_json()

    trade_date = FactorValueService.get_latest_trading_date()
    staff.role_base = prompt_quant_decision2

    stock_info = StockService.get_stock_by_symbol(symbol=_stock_code)
    assert stock_info is not None

    stock_name = stock_info.get('name')
    start_date = get_date_by_n(-120, _format='%Y%m%d') # 获取120天的行情
    end_date = FactorValueService.get_latest_trading_date().strftime('%Y%m%d')

    # 1 数据预处理 - 入库行情、新闻、题材、财报、技术因子、动量数据
    try:
        market_data = datajiji.get_history(
            symbol=_stock_code,
            start_date=start_date,
            end_date=end_date,
            market=stock_info.get('market')
        )
        # 需要重置索引，否则输出的数据没有日期
        market_data = market_data.reset_index()
    except Exception as e:
        raise f"数据获取失败: {e}"

    # 2 获取股票基础信息
    stock_detail = get_stock_detail(_stock_code=_stock_code)

    # 3 获取关联新闻供LLM分析
    relative_news = MarketNewsService.search(stock_code=_stock_code, page_size=30)

    # 4 大模型汇总输出分析报告
    template = Template(prompt_template)

    prompt = template.safe_substitute(
        stock_name=stock_name,
        stock_code=_stock_code,
        stock_detail=stock_detail,
        today=trade_date,
        market_data=market_data.to_csv(),
        relative_news=relative_news,
    )

    logger.info(f"传入大模型进行分析：{stock_name}【{_stock_code}】，大模型版本：{staff.model}")

    content = staff.ask(question=prompt)
    content = content.replace('```json', '')
    content_raw = content.replace('```', '')
    content_json = json.loads(content_raw)

    # 更新入库
    StockService.upsert_stock({
        'symbol': _stock_code,
        'llm_analysis': content_raw,
        'concepts': ", ".join(content_json.get('所属题材')),
        'company_desc': content_json.get('公司简介', ''),
        'last_llm_analysis': get_now(),
        'monitoring': 1
    })

    # 1. 单条插入
    common_report = {
        "report_type": 3,
        "stock_code": _stock_code,
        "stock_name": stock_name,
        "title": f"{_stock_code}-{stock_name}-common-report.md",
        "broker_name": staff.model,
        "analyst_name": "llm",
        "publish_time": get_today(),
        "content_text": content_raw,
        "rating": "-",
    }

    result = ResearchReportService.add(common_report)

    # "吸筹阶段|洗盘阶段|拉升阶段|出货阶段"
    main_force_behavior_phase_str = content_json.get('主力行为阶段', '')
    main_force_behavior_phase_str = main_force_behavior_phase_str.replace(' ', '')
    # 如果匹配不到，默认设为 0 (代表未知/其他)
    main_force_behavior_phase_int = PHASE_MAPPING.get(main_force_behavior_phase_str, 0)
    # 主力行为阶段写入因子库
    FactorValueService.create(
        trade_date,
        ticker=_stock_code,
        factor_name='main_force_behavior_phase',
        value=main_force_behavior_phase_int
    )

    LogService.info(
        module='llm_stock_analysis',
        content=f'个股分析完成，股票代码：{_stock_code}',
    )

    # logger.info(dict_to_markdown_recursive(content_json))
    # logger.info(content_json)

    if send_notification:
        send_feishu_markdown_message(
            f'AI个股日内复盘分析 - {_stock_code} {stock_name}',
            markdown_text=dict_to_markdown_recursive(content_json)
        )


def send_job(_stock_code, send_notification=False):
    logger.info(f"send analysis job, stock_code:{_stock_code}")
    JobService.send_job({
        'job_func': 'job_market_digging',
        'job_args': {
            '_stock_code': _stock_code,
            'sync_history': True,
            'send_notification': send_notification,
        }
    })


if __name__ == '__main__':

    # job_market_digging_daily(override=True)

    stock_code = '600150'
    job_market_digging(stock_code, sync_history=False, send_notification=False)
