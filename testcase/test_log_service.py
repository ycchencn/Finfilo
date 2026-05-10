"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import finfilo
import unittest
from datetime import datetime, timedelta
from service.log_service import LogService
from service.log_service import LogType, LogLevel

class TestLogService(unittest.TestCase):

    def test_user_log(self):

        LogService.user_log(
            user_id=1001,
            username='john_doe',
            module='order_service',
            action='CREATE_ORDER',
            ip_address='192.168.1.100',
            content='创建订单',
            extra_data={'order_id': 5001, 'amount': 299.00}
        )

    def test_system_log(self):

        # 方式 2：使用便捷方法
        LogService.system_log(
            module='order_service',
            level=LogLevel.ERROR,
            content='订单创建失败',
            error_code='ORDER_001',
            error_message='库存不足',
            extra_data={'order_id': 5001}
        )

        # 方式 2：使用便捷方法
        LogService.system_log(
            module='llm_stock_analysis',
            level=LogLevel.INFO,
            content=f'个股分析完成，股票代码：{300001}，耗时{1}，',
        )

    def test_add_log(self):

        # 方式 1：直接添加
        LogService.add({
            'log_type': LogType.SYSTEM,
            'log_level': LogLevel.INFO,
            'module': 'auth_service',
            'action': 'USER_LOGIN',
            'user_id': 1001,
            'username': 'john_doe',
            'ip_address': '192.168.1.100',
            'content': '用户登录成功',
        })

        # 方式 3：批量添加
        log_list = [
            {
                'log_type': LogType.SYSTEM,
                'log_level': LogLevel.INFO,
                'module': 'api_gateway',
                'content': '请求处理完成',
            },
            {
                'log_type': LogType.SYSTEM,
                'log_level': LogLevel.WARN,
                'module': 'api_gateway',
                'content': '请求超时警告',
            },
        ]
        LogService.batch_add(log_list)

        # ============ 查询日志 ============

        # 根据 ID 查询
        log = LogService.get_by_id(12345)

        # 根据用户 ID 查询
        user_logs = LogService.get_by_user_id(1001, limit=50)

        # 根据模块查询
        module_logs = LogService.get_by_module('order_service')

        # 根据时间范围查询
        logs = LogService.get_by_time_range(
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow(),
            log_type=LogType.USER_ACTION,
            limit=100
        )

        # 获取错误日志
        error_logs = LogService.get_error_logs(limit=50)

        # 获取失败操作日志
        failed_logs = LogService.get_failed_operations()

        # 搜索日志
        search_results = LogService.search_logs(
            keyword='订单',
            start_time=datetime.utcnow() - timedelta(days=7)
        )

        # 根据 request_id 追踪链路
        trace_logs = LogService.get_by_request_id('req_abc123')

        # ============ 统计信息 ============

        stats = LogService.get_statistics(
            start_time=datetime.utcnow() - timedelta(days=7),
            end_time=datetime.utcnow(),
            group_by='module'  # 或 'log_level', 'status'
        )

        # ============ 清理旧日志 ============

        deleted_count = LogService.cleanup_old_logs(days_to_keep=90)
