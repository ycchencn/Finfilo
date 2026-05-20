"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest
from service import MarketDataService, FactorSelectorService, factor_descriptions, financial_factor_descriptions
from llms.quant_agent_coder import QuantAgentCoder
from datetime import date, datetime
from job.job_update_factors import update_financial_factor
from utils.beta_calculate import calculate_beta
from utils.common import get_today

"""
1. 策略 Schema 与支持范围（限定领域）
为保证生成质量，MVP 仅支持以下策略类型：

类型	示例描述
动量策略	“买入过去20日涨幅最大的10只股票”
反转策略	“买入过去5日跌幅最大的20只非ST股”
多因子策略	“按市盈率从小到大和换手率从大到小综合打分，选前30只”
均值回归	“当个股20日均线低于60日均线且RSI<30时买入”
简单机器学习	“用过去30天的开盘价、最高价、成交量预测未来5日收益率，买入预测最高的10只”
所有策略统一结构：选股 → 等权重建仓 → 持有 N 天 → 全部卖出
"""

class TestFactorService(unittest.TestCase):

    def test_llm_factor_selector(self):

        asof_date = date(2025, 12, 19)
        sample_code = ""
        with open('../job/quant_agent_sample.py', 'r', encoding='utf-8') as file:
            sample_code = file.read()
        staff = QuantAgentCoder()
        staff.role_base = f"""
        你是一个专业的量化策略工程师，请根据用户的策略描述，生成符合以下规范的 Python 策略代码：
        你可以在备注里面提出还需要哪些信息
        能成功运行的代码：
        ------------
        {sample_code}
        ------------
        以下是动量因子的定义：{factor_descriptions}
        以下是财务因子的定义：{financial_factor_descriptions}""" + """

        选股方法：FactorSelectorService.select_stocks_by_factors_asof(asof_date, conditions, limit=5)
        conditions 格式：{'roe': {'operator': '>=', 'value': 15}}'}

        【平台规则】
        - 回测函数 def run_strategy(data: dict) -> dict
        - 只能使用 pandas, numpy, sklearn（如需）
        - 禁止使用：os, sys, eval, exec, requests

        【输出格式】
        ```python
        # YOUR CODE HERE

        """

        question = """
        高分红低波动策略，高ROE
        毛利率要求10%以上，净利润不能为负数
        技术指标是底部反转的走势
        """

        content = staff.ask(question=question)
        print(content)

    def test_update_financial_factor(self):
        stock_code = '002555'
        res = update_financial_factor(stock_code)
        self.assertTrue(res)

    def test_calculate_beta(self):

        stock_code = '300124'
        market_index = "000001"
        start_date = "20251101"
        end_date = get_today()

        beta = calculate_beta(stock_code, market_index, start_date=start_date, end_date=end_date)

        print(beta)

        self.assertIsNotNone(beta)

if __name__ == '__main__':
    unittest.main()
