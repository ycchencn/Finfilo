"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from staffs.qianwen_trader import QianWenTrader
from staffs.llm_base_doubao import LLMBaseDoubao
from staffs.llm_base_volcengine import LLMBaseVolcEngine
from staffs.llm_base_zhipu import LLMBaseZhipu

def get_staff(llm_base='doubao'):

    _staff = None

    if llm_base == 'doubao':
        _staff = LLMBaseDoubao()

    if llm_base == 'qwen':
        _staff = QianWenTrader()

    if llm_base == 'zhipu':
        _staff = LLMBaseZhipu()

    if llm_base == 'deepseek':
        _staff = LLMBaseVolcEngine()
        _staff.set_model(model='deepseek-v3-2-251201')

    return _staff
