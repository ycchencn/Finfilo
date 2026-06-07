"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
import aiohttp
from openai import AsyncOpenAI
from typing import Optional, Dict, List, Any
from config import mcp_host

class LLMBaseAsync:
    role_base = (
        '你是一个量化交易金融机构的专家,分析问题的时候尽量使用系统提供的mcp服务，这些是比较准确的数据'
    )

    client: Optional[AsyncOpenAI] = None
    model: str = 'deepseek-v4-flash'
    enable_search = True
    response_format = 'text'
    mcp_base_url = mcp_host
    _cached_tools: Optional[List[Dict[str, Any]]] = None
    session: Optional[aiohttp.ClientSession] = None  # 初始化为None

    def __init__(self, client: AsyncOpenAI):
        self.client = client
        # 不在__init__中创建session，延迟到异步上下文

    async def ensure_session(self):
        """确保异步HTTP会话已创建（延迟初始化）"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """关闭异步HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()

    def set_response_json(self):
        self.response_format = 'json_object'

    def set_response_text(self):
        self.response_format = 'text'

    def set_model(self, model):
        self.model = model

    def set_mcp_url(self, url):
        self.mcp_base_url = url

    async def _get_mcp_tools(self):
        """异步获取MCP工具元数据（带缓存）"""
        await self.ensure_session()  # 确保会话存在
        if self._cached_tools is None:
            try:
                async with self.session.get(f"{self.mcp_base_url}/tools", timeout=5) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    self._cached_tools = result['data']
                    print(f"成功加载MCP工具：{[tool['function']['name'] for tool in self._cached_tools]}")
            except Exception as e:
                print(f"获取MCP工具元数据失败：{str(e)}")
                self._cached_tools = []
        return self._cached_tools

    async def _call_mcp_tool(self, function_name: str, parameters: dict) -> dict:
        """异步调用MCP工具接口"""
        await self.ensure_session()  # 确保会话存在
        print(f"调用mcp工具：{function_name}, {parameters}")
        try:
            async with self.session.post(
                f"{self.mcp_base_url}/call",
                json={
                    "function_name": function_name,
                    "parameters": parameters
                },
                timeout=10
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            print(f"MCP工具调用失败：{str(e)}")
            return {"code": 500, "msg": f"MCP服务异常：{str(e)}", "data": None}

    def _print_token_usage(self, usage):
        """打印Token消耗统计"""
        if not usage:
            return {}
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        print(f"📊 Token统计：输入{prompt_tokens} | 输出{completion_tokens} | 总计{total_tokens}，模型：{self.model}")
        return {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }

    async def create_completion_with_tools(self, messages: list) -> dict:
        """
        异步带工具调用的对话生成：兼容Qwen/OpenAI标准格式+DeepSeek自定义格式
        :param messages: 对话历史列表（格式同OpenAI）
        :return: 包含最终回答、工具调用记录的字典
        """
        if not self.client:
            raise ValueError("LLM客户端未初始化，请传入有效的AsyncOpenAI实例")

        tool_call_history = []
        current_messages = messages.copy()
        mcp_tools = await self._get_mcp_tools()
        valid_function_names = {tool["function"]["name"] for tool in mcp_tools} if mcp_tools else set()

        while True:
            # 1. 调用大模型
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                response_format={"type": self.response_format},
                tools=mcp_tools,
                tool_choice="auto" if mcp_tools else "none",
                extra_body={"enable_search": self.enable_search},
                stream=False
            )

            assistant_message = completion.choices[0].message
            self._print_token_usage(completion.usage)

            # -------------------------- 兼容两种工具调用格式 --------------------------
            tool_calls = None

            # 处理Qwen/OpenAI标准格式
            if assistant_message.tool_calls:
                tool_calls = assistant_message.tool_calls
                print("检测到标准工具调用格式（Qwen/OpenAI）")
            elif assistant_message.content:
                # 处理DeepSeek自定义格式
                try:
                    content_json = json.loads(assistant_message.content.strip())
                    if isinstance(content_json, dict) and len(content_json) == 1:
                        function_name = next(iter(content_json.keys()))
                        if function_name in valid_function_names:
                            # 模拟标准tool_call结构
                            mock_tool_call = type('MockToolCall', (object,), {
                                'id': f'call_{hash(function_name + str(content_json))}',
                                'function': type('MockFunction', (object,), {
                                    'name': function_name,
                                    'arguments': json.dumps(content_json[function_name])
                                })()
                            })()
                            tool_calls = [mock_tool_call]
                            print(f"检测到DeepSeek格式工具调用：{function_name}")
                except json.JSONDecodeError:
                    pass

            # -------------------------- 处理工具调用或返回最终回答 --------------------------
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        print(f"工具参数解析失败：{str(e)}")
                        tool_result = {"code": 400, "msg": "参数格式错误", "data": None}
                    else:
                        tool_result = await self._call_mcp_tool(function_name, function_args)
                        tool_call_history.append({
                            "function_name": function_name,
                            "parameters": function_args,
                            "result": tool_result
                        })

                    # 将工具结果添加到对话历史
                    current_messages.extend([
                        {
                            "role": "assistant",
                            "content": assistant_message.content or "",
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "function": {
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments
                                    }
                                }
                            ] if tool_calls else []
                        },
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(
                                tool_result['data'] if tool_result['code'] == 0 else tool_result['msg'],
                                ensure_ascii=False
                            )
                        }
                    ])
            else:
                # 无工具调用，返回结果
                return {
                    "final_answer": assistant_message.content,
                    "tool_calls": tool_call_history,
                    "raw_response": completion
                }