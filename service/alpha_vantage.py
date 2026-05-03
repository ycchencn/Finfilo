"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import requests

class AlphaVantageClient:
    """
    封装 Alpha Vantage API 的客户端类
    """
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, apikey):
        self.apikey = apikey

    def search(self, keywords):
        """
        SYMBOL_SEARCH 功能：根据关键词搜索股票/证券代码
        """
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.apikey
        }
        return self._make_request(params)

    def get_daily_time_series(self, symbol):
        """
        TIME_SERIES_DAILY 功能：获取日线数据
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact", # 可根据需要改为 full
            "apikey": self.apikey
        }
        return self._make_request(params)

    def get_cpi_data(self, interval="monthly"):
        """
        CPI 功能：获取消费者价格指数数据
        """
        params = {
            "function": "CPI",
            "interval": interval,
            "apikey": self.apikey
        }
        return self._make_request(params)

    def _make_request(self, params):
        """
        私有方法：封装请求逻辑，处理异常
        """
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status() # 检查 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 请求错误: {e}")
            return None
