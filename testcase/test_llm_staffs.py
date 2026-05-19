"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import unittest, requests, json
from staffs.llm_base_doubao import LLMBaseDoubao
from staffs.llm_base_siliconflow import LLMBaseSiliconflow
from staffs.llm_base_aliyun import LLMBaseAliyun
from pathlib import Path

# 获取当前 Python 文件所在目录
CURRENT_DIR = Path(__file__).parent

# 构建相对于当前模块的文件路径
sample_path = CURRENT_DIR / '../job/news_sample.md'

# 解析为绝对路径并标准化（消除 ..）
sample_path = sample_path.resolve()

class TestLLMStaffs(unittest.TestCase):

    def test_qwen_mcp_call(self):
        llm = LLMBaseAliyun()
        llm.set_response_text()
        response = llm.create_completion(messages=[
            {"role": "user", "content": '获取股票A股的股票列表'}
        ])
        print(response)
        # 4. 调用MCP接口
        try:
            # 1. 用点属性访问tool_calls，而非字典下标
            assistant_message = response.choices[0].message
            if assistant_message.tool_calls:
                # 2. 遍历所有工具调用（Qwen可能返回多个）
                for tool_call in assistant_message.tool_calls:
                    # 3. 用点属性访问function的name和arguments
                    function_name = tool_call.function.name
                    # 4. 用json.loads解析arguments字符串（替代不安全的eval）
                    function_args = json.loads(tool_call.function.arguments)
                    # 调用MCP接口
                    mcp_response = requests.post(
                        "http://localhost:8081/mcp/call",
                        json={
                            "function_name": function_name,
                            "parameters": function_args
                        },
                        timeout=10  # 添加超时，避免阻塞
                    ).json()
                    # print("MCP返回结果：", mcp_response)
                    # 5. 将MCP结果返回给大模型生成最终回答
                    final_response = llm.create_completion(messages=[
                        {"role": "user", "content": '获取股票A股的股票列表'},
                        response.choices[0].message,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(mcp_response['data'])
                        }
                    ])
                    print(final_response.choices[0].message.content)

            else:
                print("模型未触发工具调用，直接回答：", assistant_message.content)
        except Exception as e:
            print(f"处理工具调用失败：{str(e)}")
            raise  # 抛出异常，让测试用例失败以便排查


    def test_silicon(self):
        news = "中科院化学所汪铭团队构建超分子靶向嵌合体，首次活体动物水平实现可编程蛋白质精准降解，成果发表于《细胞》，为疾病治疗研究开辟新路径。"
        llm = LLMBaseSiliconflow()
        print(llm.ask(question=f'分析这个新闻：{news}'))

    def test_doubao(self):
        staff_doubao = LLMBaseDoubao()
        print(staff_doubao.ask(question='今天星期几, 返回JSON'))

if __name__ == '__main__':
    unittest.main()
