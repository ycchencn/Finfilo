


"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest

# 假设这是你的原始模块名
from utils.common import is_etf, fix_stock_symbol

from backtest.strategy.run_portfolio_daily import StrategyRunner

class TestStrategy(unittest.TestCase):

    def test_load_market_data(self):

        res = StrategyRunner._fetch_market_data(stock_codes=['688008'], trading_date='2026-06-18')

        print(res)