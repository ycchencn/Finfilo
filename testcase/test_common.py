"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest

# 假设这是你的原始模块名
from utils.common import is_etf, fix_stock_symbol

def kelly_criterion(p, b):
    """
    判断凯利公式的结果是否为正数
    :param p: 获胜概率
    :param b: 赔率
    :return: 是否为正数
    """
    if b <= 0:
        return False  # 赔率必须为正
    q = 1 - p
    f_star = (b * p - q) / b
    return f_star

class TestStockDataIntegration(unittest.TestCase):

    def test_fix_symbol_for_eodhd(self):

        # --- 测试用例 ---
        test_codes = [
            '300750',  # 宁德时代 (深市) -> 应加 .SHE
            '159688',
            '512680',
            '561980',
            '601991.SHG',
            '601991.shg',
            '000001',  # 平安银行 (深市) -> 应加 .SHE
            '600519',  # 贵州茅台 (沪市) -> 应加 .SHG
            '688001',  # 华兴源创 (沪市科创) -> 应加 .SHG
            '00700',  # 腾讯控股 (港股) -> 应加 .HK
            '00005',  # 腾讯控股 (港股) -> 应加 .HK
            '09988',  # 阿里巴巴 (港股) -> 应加 .HK
            'AAPL',  # 苹果 (美股) -> 应加 .us
            'TSLA',  # 特斯拉 (美股) -> 应加 .us
            'BABA',  # 阿里美股 -> 应加 .us
            'BABA.US',  # 阿里美股 -> 应加 .us
            300750,  # 测试整数输入
        ]

        print(f"{'原始代码':<10} | {'修复后代码':<15}")
        print("-" * 30)
        for code in test_codes:
            fixed = fix_stock_symbol(code)
            print(f"{str(code):<10} | {fixed:<15}")


    def test_kelly(self):

        # 测试不同参数组合
        test_cases = [
            {"p": 0.92, "b": 0.1},
            {"p": 0.85, "b": 0.2},
            {"p": 0.70, "b": 0.5},
            {"p": 0.60, "b": 1.0},
            {"p": 0.40, "b": 0.1},
            {"p": 0.40, "b": 2.0},
            {"p": 0.50, "b": 0.1},
        ]

        print()

        for case in test_cases:
            p, b = case["p"], case["b"]
            result = kelly_criterion(p, b)
            print(f"获胜的概率 p={p}, 赔率 b={b}: 凯利公式结果为: {round(result, 2)}")

    def test_is_etf(self):
        test_cases = {
            "510050": "上证50ETF",
            "159915": "创业板ETF",
            "588000": "科创50ETF",
            "600519": "贵州茅台（非ETF）",
            "000001": "平安银行（非ETF）",
            "123456": "错误代码（非ETF）",
            "516620": "影视ETF"
        }

        # 遍历测试用例并输出结果
        for code, description in test_cases.items():
            result = is_etf(code)
            print(f"股票代码: {code} ({description}) -> 是ETF吗？ {result}")
        return

if __name__ == '__main__':
    unittest.main()
