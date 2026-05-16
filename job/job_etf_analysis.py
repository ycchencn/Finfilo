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

    # etfs = datagigi.get_etf_list(market='cn')
    # etfs = etfs[:8]

    etfs = [
        {"name": "中证100ETF易方达", "symbol": "159901"},
        {"name": "沪深300ETF", "symbol": "159919"},
        {"name": "家电ETF国泰", "symbol": "159996"},
        {"name": "芯片ETF华夏", "symbol": "159995"},
        {"name": "通信ETF银华", "symbol": "159994"},
        {"name": "证券ETF鹏华", "symbol": "159993"},
        {"name": "创新药ETF银华", "symbol": "159992"},
        {"name": "创业板大盘ETF招商", "symbol": "159991"}
    ]

    for etf in etfs:

        job_update_stock_greedy_data(index_code=etf['symbol'], override_all=True)

        # 计算因子
        job_update_stock_factor(stock_code=etf['symbol'], save_last=False, time_period=-1200)