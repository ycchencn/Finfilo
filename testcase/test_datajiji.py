"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import requests
import unittest

from utils.data_loader import datagigi

class TestDatajiji(unittest.TestCase):

    def test_get_stocks(self):
        res = datagigi.get_stock_list()
        self.assertIsNotNone(res)

    def test_get_history(self):
        url = "https://api.finfilo.com//cn/stock/history?start_date=20260101&end_date=20260115&symbol=301358"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        # print(response.json())
        self.assertIsNotNone(response.json())

    def test_get_index_history(self):
        index_code = '000300'
        res = datagigi.get_index_history(index_code, start_date='20210101', end_date='20210115')
        # print(res)
        self.assertIsNotNone(res)

    def test_get_tick(self):
        code = '399001'
        res = datagigi.get_last_tick(code, tick_type='index')
        self.assertIsNotNone(res)

if __name__ == '__main__':
    unittest.main()
