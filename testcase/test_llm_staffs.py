"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest
from staffs.llm_base_doubao import LLMBaseDoubao
from staffs.llm_base_siliconflow import LLMBaseSiliconflow
from pathlib import Path

# 获取当前 Python 文件所在目录
CURRENT_DIR = Path(__file__).parent

# 构建相对于当前模块的文件路径
sample_path = CURRENT_DIR / '../job/news_sample.md'

# 解析为绝对路径并标准化（消除 ..）
sample_path = sample_path.resolve()

class TestLLMStaffs(unittest.TestCase):

    def test_silicon(self):
        news = "中科院化学所汪铭团队构建超分子靶向嵌合体，首次活体动物水平实现可编程蛋白质精准降解，成果发表于《细胞》，为疾病治疗研究开辟新路径。"
        llm = LLMBaseSiliconflow()
        print(llm.ask(question=f'分析这个新闻：{news}'))

    def test_doubao(self):
        staff_doubao = LLMBaseDoubao()
        print(staff_doubao.ask(question='今天星期几, 返回JSON'))

if __name__ == '__main__':
    unittest.main()
