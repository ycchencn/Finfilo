"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from models.rabbitmq import get_publisher

queue_name = 'finfilo-job'

class JobService:

    @staticmethod
    def send_job(job):

        # 将消息转为 JSON 字符串
        publisher = get_publisher()
        publisher.publish(job)

if __name__ == '__main__':

    JobService.send_job({
        'job_func': 'job_update_market_data_all',
        'job_args': {
            'stock_code_override': '688332',
            'delete_old_data': True,
        }
    })
