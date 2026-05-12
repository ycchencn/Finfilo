"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

# models/rabbitmq.py

import pika
import logging
import json

from config import rabbitmq_config

logger = logging.getLogger(__name__)

class RabbitMQPublisher:
    def __init__(self, config=None):
        self.config = config or rabbitmq_config
        self._connection = None
        self._channel = None

    def _connect(self):
        """建立连接和信道"""
        if self._connection and self._connection.is_open:
            return

        credentials = pika.PlainCredentials(
            self.config['username'],
            self.config['password']
        )
        parameters = pika.ConnectionParameters(
            host=self.config['host'],
            port=self.config['port'],
            virtual_host=self.config['virtual_host'],
            credentials=credentials,
            heartbeat=600,          # 启用心跳（秒）
            blocked_connection_timeout=300
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(
            queue=self.config['queue_name'],
            durable=True  # 队列持久化
        )

    def _ensure_connection(self):
        """确保连接有效，否则重连"""
        try:
            if self._connection is None or self._connection.is_closed:
                self._connect()
            elif self._channel is None or self._channel.is_closed:
                self._channel = self._connection.channel()
                self._channel.queue_declare(
                    queue=self.config['queue_name'],
                    durable=True
                )
        except Exception as e:
            logger.error(f"Failed to ensure RabbitMQ connection: {e}")
            self._connection = None
            self._channel = None
            raise

    def publish(self, message: dict):
        """安全地发布消息"""
        try:
            self._ensure_connection()
            body = json.dumps(message, ensure_ascii=False)
            self._channel.basic_publish(
                exchange='',
                routing_key=self.config['queue_name'],
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化消息
                )
            )
            logger.info(f" [x] Sent message: {body}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            # 可选：在此处重试一次
            try:
                self._connect()  # 强制重建
                self._channel.basic_publish(
                    exchange='',
                    routing_key=self.config['queue_name'],
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                logger.info(f" [✓] Retried and sent: {body}")
            except Exception as e2:
                logger.error(f"Retry failed: {e2}")
                raise

    def close(self):
        if self._channel and self._channel.is_open:
            self._channel.close()
        if self._connection and self._connection.is_open:
            self._connection.close()

# 全局单例（可选，注意线程安全）
_publisher = None

def get_publisher():
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
    return _publisher
