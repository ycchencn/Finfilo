"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from job.job_stock_dcf_model_analysis import job_stock_dcf_model_analysis
from job.job_update_stock_greedy_data import job_update_stock_greedy_data
from job.signal.job_check_signal import job_check_signal
from job.job_update_stock_market_data import job_update_stock_market_data
from job.job_update_factors import job_update_stock_factor
from utils.common import get_today

def job_stock_analysis(stock_code, sync_history=False, send_notification=False):

    if sync_history:
        end_date = get_today()
        job_update_stock_market_data(stock_code, None, end_date, delete_old_data=True)

    # 计算走势指标
    job_update_stock_greedy_data(index_code=stock_code, override_all=sync_history)

    # 计算因子
    job_update_stock_factor(stock_code=stock_code, save_last=False, time_period=-360)

    # DCF模型分析
    job_stock_dcf_model_analysis(stock_code, send_notification=send_notification)

    # 技术分析
    job_check_signal(stock_code)

if __name__ == '__main__':

    stock_code = '002812'
    sync_history = False

    job_stock_analysis(stock_code, sync_history=sync_history)
