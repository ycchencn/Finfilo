"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from service import StockService, FactorValueService
from utils.common import get_today, logger
from utils.beta_calculate import calculate_beta

def job_update_stock_beta_all():

    market_index = "000001"
    stocks = StockService.search_stocks(securities_type='stock', monitoring=1, per_page=10000)
    start_date = "20260101"
    end_date = get_today()

    # 循环对个股进行每日挖掘
    for stock in stocks:
        stock_code = stock.get('symbol')
        if stock.get('market') != 'cn':
            continue
        beta = calculate_beta(stock_code, market_index, start_date=start_date, end_date=end_date)
        logger.info(f"The Beta of #({stock_code}) relative to {market_index} is: {beta:.3f}")
        FactorValueService.create(
            trade_date=get_today(_format='%Y-%m-%d'),
            ticker=stock_code,
            factor_name='beta',
            value=beta
        )

if __name__ == '__main__':

    job_update_stock_beta_all()
