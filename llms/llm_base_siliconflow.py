"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from openai import OpenAI
from config import siliconflow_apikey

# 定义系统提示词
system_prompt = """
你是一个量化交易金融机构的专家，负责解答用户的各种问题。
"""

class LLMBaseSiliconflow:

    role_base = system_prompt

    client = OpenAI(
        # 从环境变量中获取 API Key
        api_key=siliconflow_apikey,
        base_url="https://api.siliconflow.cn",
    )

    model = "MiniMaxAI/MiniMax-M2.5"

    enable_search = True

    response_format = 'text'

    def set_model(self, model):
        self.model = model

    def set_response_json(self):
        self.response_format = 'json_object'

    def set_response_text(self):
        self.response_format = 'text'

    def ask(self, question):
        """
        ask ai
        :param question:
        :return:
        """
        # 调用方舟模型生成响应
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': self.role_base},
                {'role': 'user', 'content': question}
            ],
            response_format={"type": self.response_format},
            extra_body={
                "thinking": {
                    "type": "disabled"  # 不使用深度思考能力
                    # "type": "enabled" # 使用深度思考能力
                }
            },
        )
        return completion.choices[0].message.content
