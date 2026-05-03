"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import pandas as pd
import numpy as np

"""

恐惧贪婪指数（Fear and Greed Index）通常的范围是在0到100之间。这个范围可以被划分为：

0-20：表示市场处于“极度恐惧”（Extreme Fear）状态。这可能是一个买入信号，因为市场可能已经过度反应，导致资产价格低于其真实价值。
20-50：表示市场处于“恐惧”（Fear）或“中性偏恐惧”状态。
50：通常被认为是中立（Neutral），意味着市场既不过于恐惧也不过于贪婪。
50-80：表示市场处于“贪婪”（Greed）或“中性偏贪婪”状态。
80-100：表示市场处于“极度贪婪”（Extreme Greed）状态。这可能是一个卖出信号，因为市场可能已经过度乐观，导致资产价格高于其真实价值。

"""


def safe_normalize(series, min_series, max_series):
    """
    安全归一化到 [0, 1]，避免除零和 NaN
    """
    range_val = max_series - min_series
    # 避免除零：当 range 为 0 时，设 raw_score = 0.5（中性）
    normalized = np.where(
        range_val != 0,
        (series - min_series) / range_val,
        0.5
    )
    return np.clip(normalized, 0, 1)


def calculate_volatility_score(df, window=20):
    """
    波动率恐惧分（反向指标）
    """
    if len(df) < window:
        df['vol_score'] = 50.0  # 数据不足时返回中性值
        return df

    # 计算对数收益率
    df['return'] = np.log(df['close'] / df['close'].shift(1))
    # 滚动波动率（年化）
    df['volatility'] = df['return'].rolling(window=window, min_periods=1).std() * np.sqrt(252)

    # 动态 lookback：取 min(60, 数据长度的一半)
    lookback = min(60, max(10, len(df) // 2))

    min_vol = df['volatility'].rolling(window=lookback, min_periods=1).min()
    max_vol = df['volatility'].rolling(window=lookback, min_periods=1).max()

    vol_raw = safe_normalize(df['volatility'], min_vol, max_vol)
    df['vol_score'] = (1 - vol_raw) * 100  # 反转：波动越大越恐惧
    df['vol_score'] = df['vol_score'].clip(0, 100)
    return df


def calculate_momentum_score(df, window=20):
    """
    动量贪婪分（正向指标）
    """
    if len(df) < window:
        df['mom_score'] = 50.0
        return df

    # 价格相对于均线的位置
    ma = df['close'].rolling(window=window, min_periods=1).mean()
    pos_vs_ma = (df['close'] - ma) / ma

    # 近期涨跌幅
    pct_change = df['close'].pct_change(periods=min(10, len(df) // 2)).fillna(0)

    momentum_factor = (pos_vs_ma + pct_change) / 2

    # 归一化
    lookback = min(60, max(10, len(df) // 2))
    min_mom = momentum_factor.rolling(window=lookback, min_periods=1).min()
    max_mom = momentum_factor.rolling(window=lookback, min_periods=1).max()

    mom_raw = safe_normalize(momentum_factor, min_mom, max_mom)
    df['mom_score'] = mom_raw * 100
    df['mom_score'] = df['mom_score'].clip(0, 100)
    return df


def calculate_volume_score(df, window=10):
    """
    成交量情绪分（正向指标）
    """
    if len(df) < window:
        df['volm_score'] = 50.0
        return df

    vol_ma = df['volume'].rolling(window=window, min_periods=1).mean()
    vol_ratio = df['volume'] / vol_ma
    vol_ratio = vol_ratio.replace([np.inf, -np.inf], 1.0).fillna(1.0)

    lookback = min(60, max(10, len(df) // 2))
    min_ratio = vol_ratio.rolling(window=lookback, min_periods=1).min()
    max_ratio = vol_ratio.rolling(window=lookback, min_periods=1).max()

    volm_raw = safe_normalize(vol_ratio, min_ratio, max_ratio)
    df['volm_score'] = volm_raw * 100
    df['volm_score'] = df['volm_score'].clip(0, 100)
    return df


def build_fear_greed_index(df, weights=None):
    """
    构建 0-100 恐惧贪婪指数
    输入: DataFrame 必须包含 'close', 'volume' 列，索引为日期
    输出: 原始 df + 新增列 ['fear_greed', 'vol_score', 'mom_score', 'volm_score']
    """

    if df is None:
        return None

    # --- 输入校验 ---
    if df.empty:
        raise ValueError("输入 DataFrame 为空")
    if 'close' not in df.columns or 'volume' not in df.columns:
        raise ValueError("缺少必要字段: 'close' 或 'volume'")

    # --- 合成总分（等权）---
    if weights is None:
        weights = {'vol_score': 0.33, 'mom_score': 0.33, 'volm_score': 0.34}

    # 确保数值类型
    df = df.copy()
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    if df['close'].isnull().any() or df['volume'].isnull().any():
        raise ValueError("价格或成交量包含非数值数据")

    if (df['close'] <= 0).any():
        raise ValueError("价格必须为正数")

    # --- 计算各维度分数 ---
    df = calculate_volatility_score(df)
    df = calculate_momentum_score(df)
    df = calculate_volume_score(df)

    df['fear_greed_raw'] = (
        df['vol_score'] * weights['vol_score'] +
        df['mom_score'] * weights['mom_score'] +
        df['volm_score'] * weights['volm_score']
    )

    # --- 平滑处理 ---
    df['fear_greed'] = df['fear_greed_raw'].ewm(span=2, min_periods=1).mean()
    df['fear_greed'] = df['fear_greed'].clip(0, 100)

    return df
