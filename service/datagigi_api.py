"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""
import pandas
import requests
import pandas as pd


class DataGigi:
    BASE_URL = "https://api.finfilo.com"  # 可根据实际部署调整

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_etf_list(
            self,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        获取股票历史数据
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/etfs"
        params = {

        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_etf_composition(
            self,
            symbol: str,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        获取ETF成分股清单

        :param symbol: 股票代码，如 "000001"
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/etf_composition"
        params = {
            "symbol": symbol
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_stock_list(
            self,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        获取股票历史数据

        :param symbol: 股票代码，如 "000001"
        :param start_date: 开始日期，格式 YYYYMMDD，如 "20260101"
        :param end_date: 结束日期，格式 YYYYMMDD，如 "20260115"
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/stocks"
        params = {

        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_stock_info(
            self,
            symbol: str,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        获取股票历史数据

        :param symbol: 股票代码，如 "000001"
        :param start_date: 开始日期，格式 YYYYMMDD，如 "20260101"
        :param end_date: 结束日期，格式 YYYYMMDD，如 "20260115"
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/stock/info"
        params = {
            "symbol": symbol
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_last_tick(
            self,
            symbol: str,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        实时行情Tick

        :param symbol: 股票代码，如 "000001"
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/stock/tick"
        params = {
            "symbol": symbol
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_history(
            self,
            symbol: str,
            start_date: str,
            end_date: str,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        获取股票历史数据

        :param symbol: 股票代码，如 "000001"
        :param start_date: 开始日期，格式 YYYYMMDD，如 "20260101"
        :param end_date: 结束日期，格式 YYYYMMDD，如 "20260115"
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/stock/history"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "symbol": symbol
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            df = pd.DataFrame(response.json())
            df['date'] = pd.to_datetime(df['date'])
            df.set_index("date", inplace=True)
            return df
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return pd.DataFrame()

    def get_etf_history(
            self,
            symbol: str,
            start_date: str,
            end_date: str,
            market: str = "cn"
    ) -> pandas.DataFrame:
        """
        获取股票历史数据

        :param symbol: 股票代码，如 "000001"
        :param start_date: 开始日期，格式 YYYYMMDD，如 "20260101"
        :param end_date: 结束日期，格式 YYYYMMDD，如 "20260115"
        :param market: 市场代码，默认 "cn"（中国）
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/{market}/etf/history"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "symbol": symbol
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            df = pd.DataFrame(response.json())
            df['date'] = pd.to_datetime(df['date'])
            df.set_index("date", inplace=True)
            return df
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return pd.DataFrame()

    def get_stock_financial_data(
            self,
            symbol: str,
            start_date: str,
            end_date: str,
            report_type: str
    ) -> pandas.DataFrame:
        """
        获取股票历史数据

        :param symbol: 股票代码，如 "000001"
        :param start_date: 开始日期，格式 YYYYMMDD，如 "20260101"
        :param end_date: 结束日期，格式 YYYYMMDD，如 "20260115"
        :param report_type: 报告类型
        :return: API 返回的原始文本（JSON 字符串），失败时返回 None
        """
        url = f"{self.BASE_URL}/cn/stock/financial_data"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "symbol": symbol,
            "report_type": report_type
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 如果你的 API 需要 token 鉴权
            # 或者用其他方式，如 "X-API-Key": self.api_key
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 抛出 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {}