

Based on the code map analysis, this is a FinTech platform providing financial data APIs and AI-powered analysis. Let me create a comprehensive README.

# FinFilo

FinFilo 是一个金融数据分析与投资组合管理平台，提供股票、ETF、市场行情等数据接口，并集成多种大语言模型 (LLM) 进行智能分析。

## 功能特性

### 📊 数据接口
- **市场数据**: 实时行情、ETF 信息、成分股查询
- **股票数据**: 历史行情、股票档案、技术分析、DCF 研究报告
- **投资组合**: 组合管理、每日统计、交易记录
- **回测系统**: 回测任务管理、信号生成
- **自选股**: 自选股 watchlist 管理

### 🤖 AI 智能分析
- 基于 Qwen/Doubao/VolcEngine/Zhipu 等大语言模型
- 财务分析报告自动生成
- 金融新闻智能解读
- 量化策略代码生成
- 智能交易建议

## 技术栈

- **后端**: Python Flask
- **缓存**: Flask-Caching
- **LLM 集成**: 阿里云 Qwen、字节跳动 Doubao、火山引擎、智谱 AI

## 快速开始

### 环境要求

- Python 3.8+
- Redis (用于缓存)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

复制 `.env.example` 为 `.env` 并配置相关 API Key：

```bash
cp .env.example .env
```

### 启动服务

```bash
# 开发环境
python run.py

# 或使用 Docker
docker-compose up -d
```

## API 接口

### 股票接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v