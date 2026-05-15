"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from service.stock import StockService
from utils.data_loader import datajiji
from utils.common import logger

def job_sync_stock_data():

    stock_list = datajiji.get_stock_list()

    for stock in stock_list['data']:
        logger.info(f"更新个股信息, {stock['symbol']}")
        StockService.upsert_stock({
            'symbol': stock['symbol'],
            'name': stock['name'],
        })

if __name__ == '__main__':

    job_sync_stock_data()