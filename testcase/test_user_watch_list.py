import unittest

# 引入被测试的文件
from service.user_watchlist_service import UserWatchlistService

class TestUserWatchlistService(unittest.TestCase):
    """
    UserWatchlistService 单元测试
    """

    def setUp(self):
        """
        [每个测试方法执行前执行]
        准备数据和 Session
        """

        # 准备测试用的 Mock 数据
        self.mock_stock_data = {
            "stock_code": "00700",
            "stock_name": "Tencent",
            "topic": "Internet",
            "desc": "Tencent Holdings",
            "price": 340.50,
            "diff": -1.20,
            "from_ai": 0
        }

    # ================= 测试用例开始 =================

    def test_01_add_success(self):
        """测试：成功添加股票"""

        dlist = ['600549', '002851', '688248', 'TSLA']

        for item in dlist:
            _data = {
                "stock_code": item,
                "stock_name": "Tencent",
                "topic": "Internet",
                "desc": "Tencent Holdings",
                "price": 340.50,
                "diff": -1.20,
                "from_ai": 0
            }
            result = UserWatchlistService.add(_data)

        # 断言 1: 返回值为 True
        self.assertTrue(result)

    def test_02_add_duplicate_failure(self):
        """测试：添加重复的股票代码 (应失败)"""
        # 1. 先添加一次
        UserWatchlistService.add(self.mock_stock_data)

        # 2. 再次添加相同的代码
        result = UserWatchlistService.add(self.mock_stock_data)

        # 断言: 返回值应为 False (因为触发了 IntegrityError)
        self.assertFalse(result)

    def test_03_get_by_code_found(self):
        """测试：查询存在的股票"""

        # 调用 Service 方法
        result = UserWatchlistService.get_by_code("00700")

        self.assertIsNotNone(result)
        self.assertEqual(result.stock_name, "Tencent")

    def test_04_get_by_code_not_found(self):
        """测试：查询不存在的股票"""
        result = UserWatchlistService.get_by_code("INVALID_CODE")
        self.assertIsNone(result)

    def test_05_update_price_diff_success(self):
        """测试：成功更新价格和涨跌幅"""

        # 2. 调用更新方法
        update_result = UserWatchlistService.update_price_diff("00700", 360.00, 5.50)

        # 3. 验证返回值
        self.assertTrue(update_result)

    def test_06_update_price_diff_not_found(self):
        """测试：更新不存在的股票 (应返回 False)"""
        result = UserWatchlistService.update_price_diff("NOT_EXIST", 100.0, 0.0)
        self.assertFalse(result)

    def test_07_delete_success(self):

        # 2. 调用删除方法
        delete_result = UserWatchlistService.delete_by_code("00700")

        # 3. 验证返回值
        self.assertTrue(delete_result)

    def test_08_delete_not_found(self):
        """测试：删除不存在的股票"""
        result = UserWatchlistService.delete_by_code("NOT_EXIST")
        self.assertFalse(result)

if __name__ == '__main__':
    # 运行测试
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
