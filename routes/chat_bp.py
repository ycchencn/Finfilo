from flask import Blueprint, request, Response, jsonify
from flask_cors import CORS
import redis
import json
import openai
from typing import List, Dict

# 创建对话蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# 跨域配置（允许前端域名访问，生产环境替换为具体域名）
CORS(chat_bp, resources={r"/*": {"origins": "*"}})

# 初始化Redis会话存储（请根据你的Redis配置修改）
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    password=None  # 如果有密码请添加
)

# 配置OpenAI API密钥（替换为你的密钥）
openai.api_key = "your_openai_api_key"


# -------------------------- 会话管理工具函数 --------------------------
def get_session_history(session_id: str) -> List[Dict]:
    """
    @brief 获取会话历史

    @param session_id: 会话唯一ID
    @type session_id: str

    @return: 包含角色和内容的对话历史列表
    @rtype: List[Dict]
    """
    history_str = redis_client.get(f"session:{session_id}")
    if history_str:
        return json.loads(history_str)
    # 默认系统提示词
    return [{"role": "system", "content": "你是一个友好专业的AI助手"}]


def save_session_history(session_id: str, history: List[Dict]):
    """
    @brief 保存会话历史（设置1天过期时间）

    @param session_id: 会话唯一ID
    @type session_id: str
    @param history: 对话历史列表
    @type history: List[Dict]
    """
    redis_client.setex(f"session:{session_id}", 86400, json.dumps(history))


# -------------------------- 流式对话接口 --------------------------
@chat_bp.route('/stream', methods=['POST'])
async def chat_stream():
    """
    @brief 流式对话接口，支持多轮会话上下文

    @param message: 用户输入消息
    @type message: str
    @param session_id: 会话唯一ID（由前端生成）
    @type session_id: str

    @return: 流式返回AI响应内容
    @rtype: Response

    @throws: 400-参数缺失；500-服务异常
    """
    # 1. 解析请求参数
    req_data = request.get_json()
    if not req_data or 'message' not in req_data or 'session_id' not in req_data:
        return jsonify({"error": "参数缺失：message和session_id为必填项"}), 400

    user_message = req_data['message'].strip()
    session_id = req_data['session_id']

    if not user_message:
        return jsonify({"error": "消息内容不能为空"}), 400

    # 2. 获取并更新会话历史
    session_history = get_session_history(session_id)
    session_history.append({"role": "user", "content": user_message})

    # 3. 定义流式响应生成器
    async def response_generator():
        assistant_reply = ""
        try:
            # 调用OpenAI流式API
            stream = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=session_history,
                stream=True
            )
            # 逐块返回响应内容
            async for chunk in stream:
                content = chunk.choices[0].delta.get("content", "")
                if content:
                    assistant_reply += content
                    yield content.encode('utf-8')

            # 4. 保存更新后的会话历史
            session_history.append({"role": "assistant", "content": assistant_reply})
            save_session_history(session_id, session_history)
        except Exception as e:
            # 异常时返回错误信息
            yield f"出错了：{str(e)}".encode('utf-8')

    # 返回流式响应
    return Response(response_generator(), mimetype='text/plain')


# -------------------------- 清空会话接口（可选） --------------------------
@chat_bp.route('/clear', methods=['POST'])
def clear_session():
    """
    @brief 清空指定会话的历史记录

    @param session_id: 会话唯一ID
    @type session_id: str

    @return: 操作结果
    @rtype: jsonify
    """
    session_id = request.get_json().get('session_id')
    if not session_id:
        return jsonify({"error": "session_id必填"}), 400
    redis_client.delete(f"session:{session_id}")
    return jsonify({"success": True, "message": "会话历史已清空"})