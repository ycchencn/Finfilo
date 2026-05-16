"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from utils.data_loader import datagigi
from job.job_update_stock_greedy_data import job_update_stock_greedy_data
from job.job_update_factors import job_update_stock_factor

if __name__ == '__main__':
    """
    对ETF进行分析
    """
    etfs = datagigi.get_etf_list(market='cn')
    etfs = etfs[:8]
    for etf in etfs:

        # job_update_stock_greedy_data(index_code=etf['symbol'], override_all=True)

        # 计算因子
        job_update_stock_factor(stock_code=etf['symbol'], save_last=False, time_period=-1200)