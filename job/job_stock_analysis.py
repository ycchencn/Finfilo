"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from service.stock import StockService
from service.user_watchlist_service import UserWatchlistService
from job.job_stock_llm_analysis import job_market_digging
from job.job_stock_dcf_model_analysis import job_stock_dcf_model_analysis
from job.job_update_stock_greedy_data import job_update_stock_greedy_data
from job.signal.job_check_signal import job_check_signal
from job.job_update_factors import job_update_stock_factor

def job_stock_analysis(stock_code, sync_history=False, send_notification=False):

    # 计算走势指标
    job_update_stock_greedy_data(index_code=stock_code, override_all=True)

    # 计算因子
    job_update_stock_factor(stock_code=stock_code, save_last=False, time_period=-360)

    # DCF模型分析
    job_stock_dcf_model_analysis(stock_code, send_notification=send_notification)

    # 技术分析
    job_check_signal(stock_code)

    # 旧版分析
    job_market_digging(stock_code, sync_history=False, send_notification=send_notification)

if __name__ == '__main__':

    # items = UserWatchlistService.get_all()
    # # 将对象转换为字典列表
    # watchlist = [item.to_dict() for item in items] if items else []
    # for item in watchlist:
    #     # print(item['stock_code'])
    #     stock_info = StockService.get_stock_by_symbol(symbol=item['stock_code'])
    #     if stock_info['llm_analysis'] is not None:
    #         continue
    #     job_stock_analysis(item['stock_code'], sync_history=False)

    stock_code = '688777'
    job_stock_analysis(stock_code, sync_history=False)
