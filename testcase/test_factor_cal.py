"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest
from utils.common import get_today, get_date_by_n

from service.factor_cal_service import FactorCalService

class TestFactorCal(unittest.TestCase):

    def test_atr_factor(self):
        stock_code = '688362'
        start_date = get_date_by_n(-365)
        end_date = get_today(_format='%Y%m%d')
        cls = FactorCalService()
        df = cls._prepare_data(stock_code, start_date, end_date)
        atr = FactorCalService.update_atr_factor(df)
        self.assertIsNotNone(atr)

if __name__ == '__main__':
    unittest.main()
