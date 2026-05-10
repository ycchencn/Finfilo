"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest
from service import ResearchReportService

class TestResearchService(unittest.TestCase):

    def test_user_log(self):

        res = ResearchReportService.get_by_code(stock_code='600673', report_type=1)

        self.assertIsNotNone(res)
