"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from staffs.qianwen_trader import QianWenTrader
from staffs.llm_base_doubao import LLMBaseDoubao
from staffs.llm_base_volcengine import LLMBaseVolcEngine
from staffs.llm_base_zhipu import LLMBaseZhipu
from staffs.llm_base_siliconflow import LLMBaseSiliconflow
from staffs.llm_base_aliyun import LLMBaseAliyun
from config import llm_model_setting


def get_analysis_model_by_setting(_setting_name='stock_analysis'):
    _staff = None
    _setting = llm_model_setting.get(_setting_name)

    if _setting.get('platform') == 'volcengine':
        _staff = LLMBaseVolcEngine()

    if _setting.get('platform') == 'aliyun':
        _staff = LLMBaseAliyun()

    assert _staff is not None

    _staff.set_model(model=_setting.get('model'))
    return _staff


def get_staff(llm_base='doubao', model=None):
    _staff = None

    if llm_base == 'doubao':
        _staff = LLMBaseDoubao()

    if llm_base == 'qwen':
        _staff = QianWenTrader()

    if llm_base == 'zhipu':
        _staff = LLMBaseZhipu()

    if llm_base == 'siliconflow':
        _staff = LLMBaseSiliconflow()

    if llm_base == 'deepseek':
        _staff = LLMBaseVolcEngine()
        _staff.set_model(model='deepseek-v3-2-251201')

    assert _staff is not None

    if model is not None:
        _staff.set_model(model=model)

    return _staff
