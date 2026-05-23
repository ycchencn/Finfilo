"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import ipaddress
from datetime import datetime
from flask import Flask, request
from models import db
from config import database_conn_str, redis_host, redis_port
# from werkzeug.middleware.proxy_fix import ProxyFix
from typing import Optional
from flask_caching import Cache
from redis import ConnectionPool
from flask import json, Response

# 初始化Flask应用和数据库连接
app = Flask(__name__, static_folder="../dist", static_url_path='')

app.config['SQLALCHEMY_DATABASE_URI'] = database_conn_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 创建 Redis 连接池
redis_pool = ConnectionPool(host=redis_host, port=redis_port, db=0)
# 配置缓存使用 Redis
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_CONNECTION_POOL'] = redis_pool
app.config['CACHE_REDIS_URL'] = f'redis://{redis_host}:{redis_port}/0'

# 配置信任的代理 IP 段（内网/可信代理）
TRUSTED_PROXIES = [
    '127.0.0.1',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
    # 添加你的负载均衡器/CDN IP 段
    # '203.0.113.0/24',  # 示例：Cloudflare IP 段
]


def is_trusted_proxy(ip: str) -> bool:
    """检查 IP 是否在可信代理列表中"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        for trusted in TRUSTED_PROXIES:
            if '/' in trusted:
                if ip_obj in ipaddress.ip_network(trusted, strict=False):
                    return True
            else:
                if ip_obj == ipaddress.ip_address(trusted):
                    return True
        return False
    except ValueError:
        return False


def get_real_ip(trusted_only: bool = True) -> Optional[str]:
    """
    获取用户真实 IP 地址（带安全验证）

    Args:
        trusted_only: 是否只信任来自可信代理的头部信息

    Returns:
        真实 IP 地址，如果验证失败则返回 None
    """
    remote_addr = request.remote_addr

    # 如果要求只信任可信代理，检查 remote_addr
    if trusted_only and not is_trusted_proxy(remote_addr):
        # 请求不是来自可信代理，直接使用 remote_addr
        return remote_addr

    # 按优先级检查各种头部
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',  # Akamai
        'X-Client-IP',
        'Forwarded',
    ]

    for header in headers_to_check:
        value = request.headers.get(header)
        if value:
            # X-Forwarded-For 可能包含多个 IP
            if header == 'X-Forwarded-For':
                ips = [ip.strip() for ip in value.split(',')]
                # 取第一个非空的 IP
                for ip in ips:
                    if ip:
                        return ip
            else:
                return value.strip()

    # fallback 到 remote_addr
    return remote_addr


def get_client_info() -> dict:
    """获取完整的客户端信息"""
    return {
        'real_ip': get_real_ip(),
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'forwarded_for': request.headers.get('X-Forwarded-For'),
        'is_trusted': is_trusted_proxy(request.remote_addr),
    }


def json_resp(ctx):
    return Response(
        json.dumps(ctx, ensure_ascii=False),
        mimetype='application/json'
    )


def trading_cache_key(*args, **kwargs):
    """
    动态生成缓存键：盘前/交易中正常缓存，盘后(15:00~09:00)强制换Key回源
    ⚠️ 注意：使用自定义 make_cache_key 后，decorator 中的 query_string=True 将失效
    """
    now = datetime.now()
    # 盘后时段判定
    is_after_hours = now.hour >= 15 or now.hour < 9
    # 基于当前请求的完整路径+查询参数生成键（无需依赖内部参数）
    base = request.full_path or request.path
    return f"{base}_{'PH' if is_after_hours else 'TRD'}"


cache = Cache(app)

db.init_app(app)  # 初始化db实例

api_prefix = '/api/v1'
