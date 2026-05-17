"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""
import json

from staffs import get_analysis_model_by_setting
from utils.common import logger
from utils.common import get_today, get_date_by_n
from service import StockService, FactorValueService, MarketNewsService
from service import ResearchReportService, JobService
from utils.data_loader import datagigi
from pathlib import Path
from string import Template

# 获取当前 Python 文件所在目录
CURRENT_DIR = Path(__file__).parent

prompt_template = Path(CURRENT_DIR / './prompt_stock_dcf_analysis.md').read_text(encoding='utf-8')


def get_stock_detail(_stock_code, market):
    stock = datagigi.get_stock_info(_stock_code, market)
    profile = stock.get('profile', {})
    return profile


def job_stock_dcf_model_analysis(_stock_code, send_notification=False):
    staff = get_analysis_model_by_setting(_setting_name='stock_dcf_analysis')
    staff.role_base = '你需要根据客户提供的资料对股票进行DCF估值分析，请使用Markdown输出'
    staff.set_response_text()

    trade_date = FactorValueService.get_latest_trading_date()
    stock_info = StockService.get_stock_by_symbol(symbol=_stock_code)
    stock_name = stock_info.get('name')
    start_date = get_date_by_n(-120, _format='%Y%m%d')  # 获取120天的行情
    end_date = FactorValueService.get_latest_trading_date().strftime('%Y%m%d')

    # 1 数据预处理 - 入库行情、新闻、题材、财报、技术因子、动量数据
    try:
        market_data = datagigi.get_history(
            symbol=_stock_code,
            start_date=start_date,
            end_date=end_date)
        # 需要重置索引，否则输出的数据没有日期
        market_data = market_data.reset_index()
    except Exception as e:
        raise f"数据获取失败: {e}"

    # 2 获取股票基础信息
    stock_detail = get_stock_detail(_stock_code=_stock_code, market=stock_info.get('market'))

    # 3 获取关联新闻供LLM分析
    relative_news = MarketNewsService.search(stock_code=_stock_code, page_size=30)

    # 获取财务报告数据
    report_balance = datagigi.get_stock_financial_data(symbol=_stock_code, start_date=get_date_by_n(-960), end_date=get_today(), report_type='Balance')
    report_income = datagigi.get_stock_financial_data(symbol=_stock_code, start_date=get_date_by_n(-960), end_date=get_today(), report_type='Income')
    report_cashflow = datagigi.get_stock_financial_data(symbol=_stock_code, start_date=get_date_by_n(-960), end_date=get_today(), report_type='CashFlow')
    report_capital = datagigi.get_stock_financial_data(symbol=_stock_code, start_date=get_date_by_n(-960), end_date=get_today(), report_type='Capital')

    # 4 大模型汇总输出分析报告
    template = Template(prompt_template)

    prompt = template.safe_substitute(
        stock_name=stock_name,
        stock_code=_stock_code,
        stock_detail=stock_detail,
        today=trade_date,
        market_data=market_data.to_csv(),
        relative_news=relative_news,
        report_balance=report_balance,
        report_income=report_income,
        report_capital=report_capital,
        report_cashflow=report_cashflow
    )

    logger.info(f"传入大模型进行DCF分析：{stock_name}【{_stock_code}】，大模型版本：{staff.model}")

    content = staff.ask(question=prompt)

    # 提取报告里面的股价预测数据
    report_extra = dcf_report_extra(_stock_code, content)

    # 1. 单条插入
    data = {
        "report_type": 1,
        "stock_code": _stock_code,
        "stock_name": stock_name,
        "title": f"{_stock_code}-{stock_name}-dcf-report.md",
        "broker_name": staff.model,
        "analyst_name": "llm",
        "publish_time": get_today(),
        "content_text": content,
        "content_json": report_extra,
        "rating": "-",
    }

    result = ResearchReportService.add(data)

    # print(content)

    return True


def job_stock_dcf_model_analysis_daily(override=False):
    stocks = StockService.search_stocks(securities_type='stock', monitoring=1, per_page=10000)

    # 循环对个股进行每日挖掘
    for stock in stocks:
        # 发送分析任务到MQ
        # send_job(_stock_code=stock['symbol'])
        JobService.send_job({
            'job_func': 'job_stock_dcf_model_analysis',
            'job_args': {
                '_stock_code': stock['symbol'],
                'send_notification': False
            }
        })
        logger.info(f"send dcf analysis of {stock['symbol']}")


def dcf_report_extra(_stock_code, report_content):
    """
    从dcf报告提取股价预期
    :param _stock_code:
    :param report_content:
    :return:
    """
    staff = get_analysis_model_by_setting(_setting_name='stock_dcf_analysis_extra')
    staff.role_base = '你需要从dcf报告提取股价预期，使用JSON输出'
    question = f"""
    请严格输出具体的价格，不要给35-40这样子模棱两可的数据
    报告原文：{report_content},"""
    question += """输出JSON格式参考！
    {
        "每股内在价值": {
          "中性情景": "40",
          "保守情景": "28",
          "乐观情景": "55"
        }，
        "当前股价": "54.77",
        "估值判断": "当前股价合理偏低，但未出现显著低估，安全边际较薄。建议逢低布局，关注回调至40-45元区间的加仓机会。"
    }
    """
    staff.set_response_json()
    res_json = staff.ask(question)
    return json.loads(res_json)


if __name__ == '__main__':

    stock_code = '603186'
    job_stock_dcf_model_analysis(stock_code)

    # job_stock_dcf_model_analysis_daily(override=True)
