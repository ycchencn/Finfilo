"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import os
from openai import OpenAI
from llms.llm_base import LLMBase

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_APIKEY'),
    base_url="https://api.deepseek.com")


class LLMBaseDeepSeek(LLMBase):
    role_base = (
        '你是一个量化交易金融机构的专家'
        '请以JSON格式输出'
    )

    model = 'deepseek-v4-pro'

    enable_search = True

    response_format = 'text'

    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('DEEPSEEK_APIKEY'), base_url="https://api.deepseek.com")
        super().__init__(self.client)