"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from .llm_base_qwen import LLMBaseQwen
from .prompts import prompt_quant_decision

class FinancialAnalysis(LLMBaseQwen):

    role_base= prompt_quant_decision

    model = 'qwen3-max'

    def __init__(self):
        super().__init__()
