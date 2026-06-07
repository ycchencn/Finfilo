"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest, requests, json
from llms.llm_base_doubao import LLMBaseDoubao
from llms.llm_base_siliconflow import LLMBaseSiliconflow
from llms.llm_base_aliyun import LLMBaseAliyun
from llms.llm_base_deepseek import LLMBaseDeepSeek
from pathlib import Path

# 获取当前 Python 文件所在目录
CURRENT_DIR = Path(__file__).parent

# 构建相对于当前模块的文件路径
sample_path = CURRENT_DIR / '../job/news_sample.md'

# 解析为绝对路径并标准化（消除 ..）
sample_path = sample_path.resolve()

class TestLLMStaffs(unittest.TestCase):

    def test_qwen_mcp_call(self):
        llm = LLMBaseAliyun()
        # 直接调用ask方法，自动完成工具调用+最终回答生成
        prompt = '获取股票A股的股票列表，返回前50支的代码和名称'

        completion_resp = llm.create_completion_with_tools(messages=[
            {'role': 'system', 'content': llm.role_base},
            {'role': 'user', 'content': prompt}
        ], )

        final_answer = completion_resp.get('final_answer')

        print("最终回答：\n", final_answer)

        # 验证回答是否包含有效数据（可根据实际业务调整断言）
        self.assertIn("代码", final_answer)
        self.assertIn("名称", final_answer)


    def test_silicon(self):
        news = "中科院化学所汪铭团队构建超分子靶向嵌合体，首次活体动物水平实现可编程蛋白质精准降解，成果发表于《细胞》，为疾病治疗研究开辟新路径。"
        llm = LLMBaseSiliconflow()
        print(llm.ask(question=f'分析这个新闻：{news}'))

    def test_doubao(self):
        staff_doubao = LLMBaseDoubao()
        print(staff_doubao.ask(question='今天星期几, 返回JSON'))

    def test_deepseek_mcp(self):
        llm = LLMBaseDeepSeek()
        llm.set_response_text()
        llm.set_model('deepseek-v4-flash')
        # 直接调用ask方法，自动完成工具调用+最终回答生成
        final_answer = llm.ask('获取股票A股的股票列表，返回前10支符合国家155规划的代码和名称')
        print("最终回答：\n", final_answer)

    def test_deepseek_ask(self):
        llm = LLMBaseDeepSeek()
        print(llm.ask(question='今天星期几, 返回JSON'))

if __name__ == '__main__':
    unittest.main()
