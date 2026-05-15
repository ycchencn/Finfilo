"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import requests
import unittest
from utils.data_loader import datajiji

class TestDatajiji(unittest.TestCase):

    def test_get_stocks(self):
        res = datajiji.get_stock_list()
        self.assertIsNotNone(res)

    def test_get_history(self):
        url = "https://api.finfilo.com//cn/stock/history?start_date=20260101&end_date=20260115&symbol=301358"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        # print(response.json())
        self.assertIsNotNone(response.json())


if __name__ == '__main__':
    unittest.main()
