"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from datetime import datetime


def generate_feishu_report(data):
    """
    将交易数据字典转换为飞书友好的Markdown报告
    """

    # --- 辅助函数：根据操作生成Emoji ---
    def get_action_emoji(action):
        emoji_map = {
            'buy': '📈',
            'sell': '📉',
            'hold': '⏸️'
        }
        return emoji_map.get(action, '')

    # --- 辅助函数：格式化日期 ---
    def format_date(date_str):
        try:
            # 尝试解析 YYYYMMDD
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            return date_obj.strftime('%Y年%m月%d日')
        except:
            return date_str

    # --- 开始构建Markdown字符串 ---
    md_lines = []

    # 1. 标题与概览
    md_lines.append(f"# 📊 {format_date(data['date'])} 交易复盘与策略")
    md_lines.append("")
    md_lines.append("### 📈 市场概览")
    md_lines.append(f"> {data['market_context']}")
    md_lines.append("")
    md_lines.append("### 🧭 仓位风格")
    md_lines.append(f"- **策略核心**：{data['position_style']}")
    md_lines.append("")

    # 2. 交易操作明细 (表格形式)
    md_lines.append("### 🛒 交易操作")
    md_lines.append("| 操作 | 代码 | 名称 | 数量 | 理由 |")
    md_lines.append("| :---: | :---: | :--- | :---: | --- |")

    for action in data['actions']:
        emoji = get_action_emoji(action['action'])
        qty = action['quantity'] if action['quantity'] > 0 else '-'
        # 对于持仓不动的，理由加粗提示
        reason = f"**{action['reason']}**" if action['action'] == 'hold' else action['reason']

        md_lines.append(
            f"| {emoji} {action['action'].upper()} | {action['stock_code']} | {action['stock_name']} | {qty} | {reason} |")

    md_lines.append("")

    # 3. 策略复盘与调整
    md_lines.append("### 🛠️ 策略复盘与调整")
    md_lines.append(f"**今日复盘**：{data['trading_review']}")
    md_lines.append("")
    md_lines.append(f"**规则调整**：{data['trading_rule_adjust']}")

    return "\n".join(md_lines)


# --- 示例数据 (你提供的数据) ---
sample_data = {
    'date': '20260204',
    'market_context': '上证指数高位震荡，AI与电网设备主线延续，贵金属避险情绪升温但资源股波动加剧。',
    'position_style': '聚焦十五五硬科技（AI算力、电网设备）与政策驱动主线，控制单票仓位，规避高波动资源类资产。',
    'actions': [
        {'stock_code': '300308', 'stock_name': '中际旭创', 'action': 'sell', 'quantity': 100,
         'reason': '短期回撤超7%，且融资买入后动能减弱，存在更优AI算力替代标的。'},
        {'stock_code': '603993', 'stock_name': '洛阳钼业', 'action': 'hold', 'quantity': 0,
         'reason': '已降仓至观察状态，铜价基本面支撑但波动率仍高，暂不加仓。'},
        {'stock_code': '002339', 'stock_name': '积成电子', 'action': 'hold', 'quantity': 0,
         'reason': '符合电网设备主线，政策催化明确，技术面维持强势。'},
        {'stock_code': '600089', 'stock_name': '特变电工', 'action': 'hold', 'quantity': 0,
         'reason': '十五五电网投资核心受益，订单饱满，量价齐升逻辑未变。'},
        {'stock_code': '002156', 'stock_name': '通富微电', 'action': 'buy', 'quantity': 300,
         'reason': 'AI芯片封测龙头，受益英伟达200亿投资OpenAI及国产替代加速。'},
        {'stock_code': '300274', 'stock_name': '阳光电源', 'action': 'buy', 'quantity': 200,
         'reason': '十五五新能源+储能核心标的，光伏出口与海外储能订单持续放量。'},
        {'stock_code': '601100', 'stock_name': '恒立液压', 'action': 'buy', 'quantity': 200,
         'reason': '高端装备核心部件国产化，受益十五五智能制造与工程机械更新政策。'}
    ],
    'trading_rule_adjust': '新增规则：对AI算力链标的，若单日融资买入额超30亿元且板块集体走强，可提升单票仓位至8%；对电网设备类，若政策催化明确且技术面突破，允许分批建仓至目标仓位。',
    'trading_review': '2月2日调仓及时规避了黄金与铜钴资源股系统性风险，但中际旭创未在融资高峰前止盈，略显滞后。当前应强化对AI算力链资金流监控，优先布局具备业绩支撑的细分龙头。'
}

# --- 生成报告 ---
if __name__ == "__main__":
    report_md = generate_feishu_report(sample_data)
    print(report_md)

    # 如果你想保存到文件
    # with open("trading_report.md", "w", encoding="utf-8") as f:
    #     f.write(report_md)
