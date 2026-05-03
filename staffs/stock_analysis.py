"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from .llm_base_qwen import LLMBaseQwen
from .prompts import prompt_quant_decision

class StockAnalysis(LLMBaseQwen):

    role_base= prompt_quant_decision

    model = 'qwen3-max'

    def __init__(self):
        super().__init__()

    def ask(self, question):
        """
        ask ai
        :param question:
        :return:
        """
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': self.role_base},
                {'role': 'user', 'content': question}
            ],
            extra_body={"enable_search": self.enable_search}
        )
        return completion.choices[0].message.content
