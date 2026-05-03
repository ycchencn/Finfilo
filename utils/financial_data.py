"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

def build_indicator_name_mapper():
    """
    构建中文财务指标到英文 snake_case 因子名的映射表
    """
    return {
        '归母净利润': 'net_profit_parent',
        '营业总收入': 'operating_revenue',
        '营业成本': 'operating_cost',
        '净利润': 'net_profit',
        '扣非净利润': 'net_profit_excl_non_recurring',
        '股东权益合计(净资产)': 'total_equity',
        '商誉': 'goodwill',
        '经营现金流量净额': 'operating_cash_flow',
        '基本每股收益': 'basic_eps',
        '每股净资产': 'bps',  # Book Value Per Share
        '每股现金流': 'cash_flow_per_share',
        '净资产收益率(ROE)': 'roe',
        '总资产报酬率(ROA)': 'roa',
        '毛利率': 'gross_margin',
        '销售净利率': 'net_profit_margin',
        '期间费用率': 'period_expense_ratio',
        '资产负债率': 'debt_to_asset_ratio',
        '稀释每股收益': 'diluted_eps',
        '摊薄每股收益_最新股数': 'fully_diluted_eps_latest_shares',
        '摊薄每股净资产_期末股数': 'fully_diluted_bps_end_shares',
        '调整每股净资产_期末股数': 'adjusted_bps_end_shares',
        '每股净资产_最新股数': 'bps_latest_shares',
        '每股经营现金流': 'operating_cash_flow_per_share',
        '每股现金流量净额': 'net_cash_flow_per_share',
        '每股企业自由现金流量': 'fcff_per_share',  # Free Cash Flow to Firm
        '每股股东自由现金流量': 'fcfe_per_share',  # Free Cash Flow to Equity
        '每股未分配利润': 'retained_earnings_per_share',
        '每股资本公积金': 'capital_reserve_per_share',
        '每股盈余公积金': 'surplus_reserve_per_share',
        '每股留存收益': 'retained_surplus_per_share',
        '每股营业收入': 'revenue_per_share',
        '每股营业总收入': 'operating_revenue_per_share',
        '每股息税前利润': 'ebit_per_share',
        '摊薄净资产收益率': 'fully_diluted_roe',
        '净资产收益率_平均': 'avg_roe',
        '净资产收益率_平均_扣除非经常损益': 'avg_roe_excl_non_recurring',
        '摊薄净资产收益率_扣除非经常损益': 'fully_diluted_roe_excl_non_recurring',
        '息税前利润率': 'ebit_margin',
        '总资产报酬率': 'roa_alt',  # 注意：与前面 ROA 可能重复，保留区分
        '总资本回报率': 'return_on_capital',
        '投入资本回报率': 'roic',  # Return on Invested Capital
        '息前税后总资产报酬率_平均': 'after_tax_roa_avg',
        '成本费用利润率': 'cost_expense_profit_ratio',
        '营业利润率': 'operating_profit_margin',
        '总资产净利率_平均': 'net_asset_return_avg',
        '总资产净利率_平均(含少数股东损益)': 'net_asset_return_avg_with_minority',
        '营业总收入增长率': 'revenue_growth_yoy',
        '归属母公司净利润增长率': 'net_profit_parent_growth_yoy',
        '经营活动净现金/销售收入': 'ocf_to_revenue',
        '经营性现金净流量/营业总收入': 'ocf_to_operating_revenue',
        '成本费用率': 'cost_expense_ratio',
        '销售成本率': 'cost_of_sales_ratio',
        '经营活动净现金/归属母公司的净利润': 'ocf_to_net_profit_parent',
        '所得税/利润总额': 'income_tax_to_total_profit',
        '流动比率': 'current_ratio',
        '速动比率': 'quick_ratio',
        '保守速动比率': 'conservative_quick_ratio',
        '权益乘数': 'equity_multiplier',
        '权益乘数(含少数股权的净资产)': 'equity_multiplier_with_minority',
        '产权比率': 'equity_ratio',  # 或 debt_to_equity_ratio，但此处按字段直译
        '现金比率': 'cash_ratio',
        '应收账款周转率': 'ar_turnover',
        '应收账款周转天数': 'ar_turnover_days',
        '存货周转率': 'inventory_turnover',
        '存货周转天数': 'inventory_turnover_days',
        '总资产周转率': 'total_asset_turnover',
        '总资产周转天数': 'total_asset_turnover_days',
        '流动资产周转率': 'current_asset_turnover',
        '流动资产周转天数': 'current_asset_turnover_days',
        '应付账款周转率': 'ap_turnover',
    }

# 全局映射表（可复用）
INDICATOR_NAME_MAP = build_indicator_name_mapper()
