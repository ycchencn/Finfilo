"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from openai import OpenAI
from config import aliyun_bailian_apikey

DASHSCOPE_API_KEY = aliyun_bailian_apikey
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
EMBEDDING_MODEL = "text-embedding-v4" # 阿里最新的 Embedding 模型

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL
)

def get_embedding(text: str):
    """
    调用阿里 DashScope API 获取文本向量
    Args:
        text: 输入文本
    Returns:
        向量列表 (List[float])
    """
    # DashScope 的 text-embedding-v4 支持 dimensions 参数
    # 这里我们使用默认维度（通常为 1024），你也可以显式指定 dimensions=1024
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        # dimensions=1024, # 如果需要指定维度可以取消注释
    )
    # 返回 embedding 向量
    return response.data[0].embedding
