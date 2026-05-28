"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import random
from llms.llm_base_doubao import LLMBaseDoubao
from llms.llm_base_volcengine import LLMBaseVolcEngine
from llms.llm_base_zhipu import LLMBaseZhipu
from llms.llm_base_siliconflow import LLMBaseSiliconflow
from llms.llm_base_aliyun import LLMBaseAliyun
from llms.llm_base_deepseek import LLMBaseDeepSeek
from config import llm_model_setting


def get_model_by_setting(_setting_name='stock_dcf_analysis', _setting=None):
    _staff = None
    if _setting is None:
        _setting = llm_model_setting.get(_setting_name)

    if _setting.get('platform') == 'deepseek':
        _staff = LLMBaseDeepSeek()

    if _setting.get('platform') == 'volcengine':
        _staff = LLMBaseVolcEngine()

    if _setting.get('platform') == 'siliconflow':
        _staff = LLMBaseSiliconflow()

    if _setting.get('platform') == 'aliyun':
        _staff = LLMBaseAliyun()

    if _setting.get('platform') == 'zhipu':
        _staff = LLMBaseZhipu()

    assert _staff is not None

    if isinstance(_setting.get('model'), str):
        _staff.set_model(model=_setting.get('model'))
    else:
        # 支持随机选模型
        _staff.set_model(model=random.choice(_setting.get('model')))

    return _staff
