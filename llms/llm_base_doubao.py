"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from openai import OpenAI
from config import ark_apikey
from llms.llm_base import LLMBase

# 定义系统提示词
system_prompt = """
你是一个量化交易金融机构的专家，负责解答用户的各种问题。
"""


class LLMBaseDoubao(LLMBase):
    role_base = system_prompt

    model = "doubao-seed-1-6-flash-250828"

    enable_search = True

    response_format = 'text'

    def __init__(self):
        self.client = OpenAI(
            # 从环境变量中获取方舟 API Key
            api_key=ark_apikey,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        super().__init__(self.client)