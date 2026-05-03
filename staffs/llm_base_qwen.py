"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from openai import OpenAI
from config import aliyun_bailian_apikey

client_aliyun = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=aliyun_bailian_apikey,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

class LLMBaseQwen:

    role_base= (
        '你是一个量化交易金融机构的专家'
        '请以JSON格式输出'
    )

    client = None

    model = 'qwen3.6-plus'

    enable_search = True

    response_format = 'json_object'

    def __init__(self, client=client_aliyun):
        self.client = client

    def set_response_json(self):
        self.response_format = 'json_object'

    def set_response_text(self):
        self.response_format = 'text'

    def set_response_markdown(self):
        self.response_format = 'markdown'

    def set_model(self, model):
        self.model = model

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
            response_format={"type": self.response_format},
            extra_body={"enable_search": self.enable_search}
        )
        return completion.choices[0].message.content
