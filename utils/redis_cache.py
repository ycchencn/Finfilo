"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import hashlib
import functools
import pickle
from cachetools import LRUCache
from .redis_obj import redis_obj as redis_client

# 自定义缓存类，继承自 LRUCache
class RedisLRUCache(LRUCache):

    def __init__(self, maxsize, expire_time, method_name, *args, **kwargs):
        super().__init__(maxsize)
        self.expire_time = expire_time
        self.method_name = method_name

    def generate_key(self, args, kwargs):
        # 组合参数和方法名，并生成其md5值
        key = self.method_name + '__' + hashlib.md5((self.method_name + repr(args) + repr(kwargs)).encode('utf-8')).hexdigest()
        return key

    def __getitem__(self, key_args_kwargs):
        args, kwargs = key_args_kwargs
        # 生成md5后的key
        key_str = self.generate_key(args, kwargs)
        # 先从 Redis 中获取
        value = redis_client.get(key_str)
        if value is not None:
            return pickle.loads(value)
        # 如果 Redis 中没有，则从内存缓存中获取
        return super().__getitem__(key_str)

    def __setitem__(self, key_args_kwargs, value):
        args, kwargs = key_args_kwargs
        # 生成md5后的key
        key_str = self.generate_key(args, kwargs)
        # 序列化值
        value_serialized = pickle.dumps(value)
        # 设置到 Redis，并设置过期时间
        redis_client.set(key_str, value_serialized, ex=self.expire_time)
        # 同时设置到内存缓存
        super().__setitem__(key_str, value)

    def __delitem__(self, key_args_kwargs):
        args, kwargs = key_args_kwargs
        # 生成md5后的key
        key_str = self.generate_key(args, kwargs)
        # 从 Redis 中删除
        redis_client.delete(key_str)
        # 从内存缓存中删除
        super().__delitem__(key_str)

# 使用自定义的缓存装饰器
def lru_redis_cache(expire_time=3600, maxsize=100):
    def decorator(func):
        cache = RedisLRUCache(maxsize, expire_time, func.__name__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key_args_kwargs = (args, kwargs)
            try:
                return cache[key_args_kwargs]
            except KeyError:
                result = func(*args, **kwargs)
                cache[key_args_kwargs] = result
                return result
        return wrapper
    return decorator

