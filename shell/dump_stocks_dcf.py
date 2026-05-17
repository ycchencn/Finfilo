"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from service.stock import StockService

if __name__ == '__main__':

    stocks = StockService.get_monitoring_stock_pool(market='cn')

    # job_stock_dcf_model_analysis_daily(override=True)