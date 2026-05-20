"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
import requests
from openai import OpenAI
from config import aliyun_bailian_apikey, datajiji_host

client_aliyun = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=aliyun_bailian_apikey,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


class LLMBase:
    role_base = (
        '你是一个量化交易金融机构的专家'
        '请以JSON格式输出'
    )

    client = None

    model = 'qwen3.6-plus'

    enable_search = True

    response_format = 'json_object'

    # MCP服务配置（可根据环境修改）
    mcp_base_url = f"{datajiji_host}/mcp"

    # 缓存工具元数据，避免重复请求MCP
    _cached_tools = None

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

    def ask(self, question: str) -> str:
        """
        对外暴露的问答接口：自动处理工具调用并返回最终回答
        :param question: 用户问题
        :return: 自然语言回答
        """
        messages = [
            {'role': 'system', 'content': self.role_base},
            {'role': 'user', 'content': question}
        ]
        result = self.create_completion_with_tools(messages)
        return result['final_answer']

    def create_completion(self, messages: list) -> object:
        """
        原始对话生成接口（不带工具调用自动处理）
        :param messages: 对话历史
        :return: OpenAI格式的原始响应
        """
        tools = self._get_mcp_tools()
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": self.response_format},
            tools=tools,
            extra_body={"enable_search": self.enable_search}
        )
        self._print_token_usage(completion.usage)
        return completion

    def set_mcp_url(self, url):
        """设置MCP服务地址"""
        self.mcp_base_url = url

    def _get_mcp_tools(self):
        """获取MCP工具元数据（带缓存）"""
        if self._cached_tools is None:
            try:
                resp = requests.get(f"{self.mcp_base_url}/tools", timeout=5)
                resp.raise_for_status()
                self._cached_tools = resp.json()['data']
            except Exception as e:
                print(f"获取MCP工具元数据失败：{str(e)}")
                self._cached_tools = []
        return self._cached_tools

    def _call_mcp_tool(self, function_name: str, parameters: dict) -> dict:
        """调用MCP工具接口"""
        try:
            resp = requests.post(
                f"{self.mcp_base_url}/call",
                json={
                    "function_name": function_name,
                    "parameters": parameters
                },
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"MCP工具调用失败：{str(e)}")
            return {"code": 500, "msg": f"MCP服务异常：{str(e)}", "data": None}

    def create_completion_with_tools(self, messages: list) -> dict:
        """
        带工具调用的对话生成：自动处理工具调用循环
        :param messages: 对话历史列表（格式同OpenAI）
        :return: 包含最终回答、工具调用记录的字典
        """
        tool_call_history = []
        current_messages = messages.copy()

        while True:
            # 1. 获取MCP工具元数据
            tools = self._get_mcp_tools()
            # 2. 调用大模型
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                response_format={"type": self.response_format},
                tools=tools,
                tool_choice="auto" if tools else "none",  # 无工具时不触发调用
                extra_body={"enable_search": self.enable_search}
            )

            assistant_message = completion.choices[0].message
            # 3. 打印Token统计
            self._print_token_usage(completion.usage)

            # 4. 判断是否需要调用工具
            if not assistant_message.tool_calls:
                # 无工具调用，返回最终回答
                return {
                    "final_answer": assistant_message.content,
                    "tool_calls": tool_call_history,
                    "raw_response": completion
                }

            # 5. 处理工具调用
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"工具参数解析失败：{str(e)}")
                    tool_result = {"code": 400, "msg": "参数格式错误", "data": None}
                else:
                    # 调用MCP工具
                    tool_result = self._call_mcp_tool(function_name, function_args)
                    tool_call_history.append({
                        "function_name": function_name,
                        "parameters": function_args,
                        "result": tool_result
                    })

                # 6. 将工具结果添加到对话历史，继续请求大模型
                current_messages.extend([
                    assistant_message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result['data'] if tool_result['code'] == 0 else tool_result['msg'],
                                              ensure_ascii=False)
                    }
                ])

    def _print_token_usage(self, usage):
        """打印Token消耗统计"""
        if usage:
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            print(f"📊 Token统计：输入{prompt_tokens} | 输出{completion_tokens} | 总计{total_tokens}")
