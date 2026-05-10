"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest
from job.job_news_feed_analysis import llm_news_summarize

class TestNewsFeed(unittest.TestCase):

    def test_llm_news_analysis(self):

        news = "中科院化学所汪铭团队构建超分子靶向嵌合体，首次活体动物水平实现可编程蛋白质精准降解，成果发表于《细胞》，为疾病治疗研究开辟新路径。"
        res = llm_news_summarize(
            news,
            news_time='2026-01-17T07:02:27',
            news_type='news',
            sources='stock_star',
            url='https://wallstreetcn.com/articles/3763450',
            debug=True
        )

        print(res)

if __name__ == '__main__':
    unittest.main()
