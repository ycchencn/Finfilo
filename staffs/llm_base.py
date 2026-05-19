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

class LLMBase:

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

    def create_completion(self, messages):
        """
        创建对话
        :param messages:
        :return:
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": self.response_format},
            extra_body={"enable_search": self.enable_search}
        )

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
        # ---------------- 新增：提取/打印Token用量 ----------------
        # 打印完整返回结构（方便你查看所有字段）
        # print("完整响应数据：\n", completion.model_dump_json(indent=2, ensure_ascii=False))
        # 单独提取各类Token消耗
        prompt_tokens = completion.usage.prompt_tokens  # 输入Token：系统提示词 + 用户问题的总Token数
        completion_tokens = completion.usage.completion_tokens  # 输出Token：模型生成回复的Token数
        total_tokens = completion.usage.total_tokens  # 本次请求总消耗Token（计费依据）
        print(f"本次调用Token统计：输入{prompt_tokens} + 输出{completion_tokens} = 总计{total_tokens}")
        # ----------------------------------------------------------
        return completion.choices[0].message.content
